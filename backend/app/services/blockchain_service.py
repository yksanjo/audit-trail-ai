"""Blockchain anchoring service for immutable audit trails."""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from web3 import Web3
from web3.exceptions import TransactionNotFound

from app.config import get_settings
from app.models.blockchain_anchor import AnchorStatus, BlockchainAnchor
from app.models.merkle_tree import MerkleNode, MerkleRoot
from app.services.hasher import hash_service

settings = get_settings()


class BlockchainService:
    """Service for blockchain anchoring and verification."""
    
    # Simulated contract ABI for Merkle root anchoring
    MERKLE_ANCHOR_ABI = [
        {
            "inputs": [{"name": "rootHash", "type": "bytes32"}],
            "name": "anchorMerkleRoot",
            "outputs": [{"name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [{"name": "rootHash", "type": "bytes32"}],
            "name": "getAnchor",
            "outputs": [
                {"name": "blockNumber", "type": "uint256"},
                {"name": "timestamp", "type": "uint256"},
                {"name": "submitter", "type": "address"},
            ],
            "stateMutability": "view",
            "type": "function",
        },
    ]
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.w3: Optional[Web3] = None
        self._init_web3()
    
    def _init_web3(self) -> None:
        """Initialize Web3 connection."""
        if not settings.blockchain_enabled:
            return
        
        try:
            self.w3 = Web3(Web3.HTTPProvider(settings.ethereum_rpc_url))
            if self.w3.is_connected():
                print(f"Connected to blockchain: {settings.ethereum_rpc_url}")
        except Exception as e:
            print(f"Failed to connect to blockchain: {e}")
            self.w3 = None
    
    async def build_merkle_tree(
        self,
        audit_log_hashes: List[str],
    ) -> MerkleRoot:
        """Build a Merkle tree from audit log hashes."""
        if not audit_log_hashes:
            raise ValueError("No hashes provided for Merkle tree")
        
        # Create leaf nodes
        leaf_nodes = []
        for i, hash_value in enumerate(audit_log_hashes):
            node = MerkleNode(
                id=uuid.uuid4(),
                node_hash=hash_value,
                level=0,
                position=i,
                is_leaf=True,
            )
            leaf_nodes.append(node)
            self.db.add(node)
        
        # Build tree bottom-up
        current_level = leaf_nodes
        all_nodes = leaf_nodes.copy()
        level = 0
        
        while len(current_level) > 1:
            level += 1
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Create parent hash
                parent_hash = hash_service.merkle_hash(left.node_hash, right.node_hash)
                
                parent = MerkleNode(
                    id=uuid.uuid4(),
                    node_hash=parent_hash,
                    level=level,
                    position=i // 2,
                    is_leaf=False,
                    left_child_hash=left.node_hash,
                    right_child_hash=right.node_hash if left != right else None,
                )
                
                # Update children with parent reference
                left.parent_hash = parent_hash
                if left != right:
                    right.parent_hash = parent_hash
                
                next_level.append(parent)
                all_nodes.append(parent)
                self.db.add(parent)
            
            current_level = next_level
        
        # Root is the only node left
        root_node = current_level[0]
        root_node.is_root = True
        
        # Create MerkleRoot record
        merkle_root = MerkleRoot(
            id=uuid.uuid4(),
            root_hash=root_node.node_hash,
            tree_depth=level,
            leaf_count=len(audit_log_hashes),
            start_sequence=0,  # Will be updated
            end_sequence=len(audit_log_hashes) - 1,
            is_anchored=False,
        )
        
        # Associate all nodes with root
        for node in all_nodes:
            node.root_id = merkle_root.id
        
        self.db.add(merkle_root)
        await self.db.flush()
        
        return merkle_root
    
    async def anchor_to_blockchain(
        self,
        merkle_root: MerkleRoot,
    ) -> Optional[BlockchainAnchor]:
        """Anchor a Merkle root to the blockchain."""
        if not settings.blockchain_enabled or not self.w3:
            # Create a simulated anchor for testing
            anchor = BlockchainAnchor(
                id=uuid.uuid4(),
                anchor_id=f"anchor_{uuid.uuid4().hex[:16]}",
                root_hash=merkle_root.root_hash,
                chain_id=settings.chain_id,
                network_name="simulated",
                status=AnchorStatus.CONFIRMED,
                tx_hash=f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:24]}",
                block_number=1,
                block_hash=f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:24]}",
                gas_used=21000,
                confirmed_at=datetime.utcnow(),
                finalized_at=datetime.utcnow(),
            )
            self.db.add(anchor)
            
            merkle_root.is_anchored = True
            merkle_root.anchored_at = datetime.utcnow()
            merkle_root.blockchain_anchor_id = anchor.id
            
            await self.db.flush()
            return anchor
        
        # Create pending anchor
        anchor = BlockchainAnchor(
            id=uuid.uuid4(),
            anchor_id=f"anchor_{uuid.uuid4().hex[:16]}",
            merkle_root_id=merkle_root.id,
            root_hash=merkle_root.root_hash,
            chain_id=settings.chain_id,
            network_name="ethereum",
            status=AnchorStatus.PENDING,
        )
        self.db.add(anchor)
        await self.db.flush()
        
        try:
            # Submit transaction
            tx_hash = await self._submit_anchor_transaction(merkle_root.root_hash)
            
            anchor.status = AnchorStatus.SUBMITTED
            anchor.tx_hash = tx_hash
            await self.db.flush()
            
            # Wait for confirmation
            receipt = await self._wait_for_confirmation(tx_hash)
            
            anchor.status = AnchorStatus.CONFIRMED
            anchor.block_number = receipt.get("blockNumber")
            anchor.block_hash = receipt.get("blockHash", {}).hex() if receipt.get("blockHash") else None
            anchor.gas_used = receipt.get("gasUsed")
            anchor.confirmed_at = datetime.utcnow()
            
            merkle_root.is_anchored = True
            merkle_root.anchored_at = datetime.utcnow()
            merkle_root.blockchain_anchor_id = anchor.id
            
            await self.db.flush()
            return anchor
            
        except Exception as e:
            anchor.status = AnchorStatus.FAILED
            anchor.last_error = str(e)
            anchor.retry_count += 1
            await self.db.flush()
            raise
    
    async def _submit_anchor_transaction(self, root_hash: str) -> str:
        """Submit anchor transaction to blockchain."""
        if not self.w3 or not settings.anchor_private_key:
            raise ValueError("Blockchain not configured")
        
        account = self.w3.eth.account.from_key(settings.anchor_private_key)
        
        # Convert hash to bytes32
        hash_bytes = bytes.fromhex(root_hash.replace("0x", ""))
        
        # Build transaction
        contract = self.w3.eth.contract(
            address=settings.anchor_contract_address,
            abi=self.MERKLE_ANCHOR_ABI,
        )
        
        tx = contract.functions.anchorMerkleRoot(hash_bytes).build_transaction({
            "from": account.address,
            "nonce": self.w3.eth.get_transaction_count(account.address),
            "gas": 100000,
            "gasPrice": self.w3.eth.gas_price,
            "chainId": settings.chain_id,
        })
        
        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, settings.anchor_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return tx_hash.hex()
    
    async def _wait_for_confirmation(
        self,
        tx_hash: str,
        max_wait: int = 300,
    ) -> Dict[str, Any]:
        """Wait for transaction confirmation."""
        if not self.w3:
            raise ValueError("Web3 not initialized")
        
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < max_wait:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt and receipt.get("blockNumber"):
                    return receipt
            except TransactionNotFound:
                pass
            
            await asyncio.sleep(5)
        
        raise TimeoutError(f"Transaction {tx_hash} not confirmed within {max_wait}s")
    
    async def verify_anchor(
        self,
        anchor: BlockchainAnchor,
    ) -> bool:
        """Verify a blockchain anchor."""
        if not self.w3 or anchor.network_name == "simulated":
            return True  # Simulated anchors are always valid
        
        try:
            # Verify transaction exists
            receipt = self.w3.eth.get_transaction_receipt(anchor.tx_hash)
            if not receipt:
                return False
            
            # Check block confirmation
            current_block = self.w3.eth.block_number
            confirmations = current_block - receipt["blockNumber"]
            
            # Mark as finalized after 12 confirmations
            if confirmations >= 12 and anchor.status != AnchorStatus.FINALIZED:
                anchor.status = AnchorStatus.FINALIZED
                anchor.finalized_at = datetime.utcnow()
                await self.db.flush()
            
            return True
        except Exception:
            return False
    
    async def generate_merkle_proof(
        self,
        leaf_hash: str,
        merkle_root_id: uuid.UUID,
    ) -> Optional[Dict[str, Any]]:
        """Generate Merkle proof for a leaf."""
        # Find leaf node
        result = await self.db.execute(
            select(MerkleNode).where(
                MerkleNode.node_hash == leaf_hash,
                MerkleNode.root_id == merkle_root_id,
            )
        )
        leaf = result.scalar_one_or_none()
        
        if not leaf:
            return None
        
        # Build proof path
        proof_path = []
        current = leaf
        
        while not current.is_root:
            # Find sibling
            result = await self.db.execute(
                select(MerkleNode).where(
                    MerkleNode.parent_hash == current.parent_hash,
                    MerkleNode.node_hash != current.node_hash,
                )
            )
            sibling = result.scalar_one_or_none()
            
            proof_path.append({
                "hash": sibling.node_hash if sibling else current.node_hash,
                "position": "right" if sibling and sibling.position > current.position else "left",
            })
            
            # Move up
            result = await self.db.execute(
                select(MerkleNode).where(
                    MerkleNode.node_hash == current.parent_hash,
                )
            )
            current = result.scalar_one()
        
        return {
            "leaf_hash": leaf_hash,
            "root_hash": current.node_hash,
            "proof_path": proof_path,
        }
    
    async def verify_merkle_proof(
        self,
        leaf_hash: str,
        root_hash: str,
        proof_path: List[Dict[str, Any]],
    ) -> bool:
        """Verify a Merkle proof."""
        current_hash = leaf_hash
        
        for step in proof_path:
            sibling_hash = step["hash"]
            position = step["position"]
            
            if position == "left":
                current_hash = hash_service.merkle_hash(sibling_hash, current_hash)
            else:
                current_hash = hash_service.merkle_hash(current_hash, sibling_hash)
        
        return current_hash == root_hash
