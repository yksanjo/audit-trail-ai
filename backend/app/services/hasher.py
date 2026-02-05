"""Cryptographic hashing service for immutability."""
import hashlib
import hmac
import json
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

from app.config import get_settings

settings = get_settings()


class HashService:
    """Service for cryptographic hashing and verification."""
    
    HASH_ALGORITHM = hashlib.sha3_256
    
    def __init__(self):
        self._encryption_key: Optional[bytes] = None
        if settings.encryption_key:
            self._encryption_key = settings.encryption_key.encode()
    
    @staticmethod
    def hash_string(data: str) -> str:
        """Hash a string using SHA3-256."""
        return HashService.HASH_ALGORITHM(data.encode("utf-8")).hexdigest()
    
    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """Hash bytes using SHA3-256."""
        return HashService.HASH_ALGORITHM(data).hexdigest()
    
    @staticmethod
    def hash_dict(data: Dict[str, Any]) -> str:
        """Hash a dictionary deterministically."""
        # Sort keys for deterministic hashing
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        return HashService.hash_string(canonical)
    
    def compute_audit_hash(
        self,
        input_data: str,
        output_data: str,
        context: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Dict[str, str]:
        """Compute all hashes for an audit log entry."""
        input_hash = self.hash_string(input_data)
        output_hash = self.hash_string(output_data)
        context_hash = self.hash_dict(context)
        
        # Full hash combines all components
        full_data = {
            "input_hash": input_hash,
            "output_hash": output_hash,
            "context_hash": context_hash,
            "metadata": metadata,
        }
        full_hash = self.hash_dict(full_data)
        
        return {
            "input_hash": input_hash,
            "output_hash": output_hash,
            "context_hash": context_hash,
            "full_hash": full_hash,
        }
    
    def verify_audit_hash(
        self,
        input_data: str,
        output_data: str,
        context: Dict[str, Any],
        metadata: Dict[str, Any],
        expected_full_hash: str,
    ) -> bool:
        """Verify that computed hash matches expected hash."""
        computed = self.compute_audit_hash(input_data, output_data, context, metadata)
        return hmac.compare_digest(computed["full_hash"], expected_full_hash)
    
    def merkle_hash(self, left: str, right: str) -> str:
        """Compute parent hash from two child hashes."""
        combined = left + right
        return self.hash_string(combined)
    
    def create_tombstone_hash(
        self,
        original_hash: str,
        deletion_timestamp: str,
        deleted_by: str,
        reason: str,
    ) -> str:
        """Create cryptographic tombstone hash."""
        data = {
            "original_hash": original_hash,
            "deletion_timestamp": deletion_timestamp,
            "deleted_by": deleted_by,
            "reason": reason,
            "type": "TOMBSTONE",
        }
        return self.hash_dict(data)
    
    def generate_hmac(self, data: str, key: Optional[str] = None) -> str:
        """Generate HMAC for data integrity."""
        key_bytes = (key or settings.secret_key).encode()
        return hmac.new(
            key_bytes,
            data.encode(),
            hashlib.sha3_256,
        ).hexdigest()
    
    def verify_hmac(self, data: str, signature: str, key: Optional[str] = None) -> bool:
        """Verify HMAC signature."""
        expected = self.generate_hmac(data, key)
        return hmac.compare_digest(expected, signature)
    
    def encrypt_sensitive_data(self, data: str) -> Optional[str]:
        """Encrypt sensitive data if encryption is enabled."""
        if not settings.enable_encryption or not self._encryption_key:
            return None
        
        f = Fernet(self._encryption_key)
        encrypted = f.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data."""
        if not settings.enable_encryption or not self._encryption_key:
            return None
        
        f = Fernet(self._encryption_key)
        decrypted = f.decrypt(encrypted_data.encode())
        return decrypted.decode()


# Global instance
hash_service = HashService()
