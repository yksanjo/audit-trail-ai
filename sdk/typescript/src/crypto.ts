/**
 * Cryptographic utilities for Merkle tree verification
 */

import CryptoJS from 'crypto-js';
import { MerkleProofStep } from './types';

/**
 * Hash a string using SHA3-256
 */
export function hashString(data: string): string {
  return CryptoJS.SHA3(data, { outputLength: 256 }).toString();
}

/**
 * Hash a JavaScript object deterministically
 */
export function hashObject(obj: Record<string, unknown>): string {
  const keys = Object.keys(obj).sort();
  const canonical: Record<string, unknown> = {};
  keys.forEach((key) => {
    canonical[key] = obj[key];
  });
  return hashString(JSON.stringify(canonical));
}

/**
 * Compute parent hash from two child hashes
 */
export function merkleHash(left: string, right: string): string {
  return hashString(left + right);
}

/**
 * Verify a Merkle proof
 * @param leafHash - The hash of the leaf node
 * @param rootHash - The expected root hash
 * @param proofPath - Array of proof steps
 * @returns boolean indicating if proof is valid
 */
export function verifyMerkleProof(
  leafHash: string,
  rootHash: string,
  proofPath: MerkleProofStep[]
): boolean {
  let currentHash = leafHash;

  for (const step of proofPath) {
    if (step.position === 'left') {
      currentHash = merkleHash(step.hash, currentHash);
    } else {
      currentHash = merkleHash(currentHash, step.hash);
    }
  }

  return currentHash === rootHash;
}

/**
 * Generate Merkle proof for a leaf
 * @param leafIndex - Index of the leaf
 * @param leafHashes - All leaf hashes
 * @returns Array of proof steps
 */
export function generateMerkleProof(
  leafIndex: number,
  leafHashes: string[]
): MerkleProofStep[] {
  const proofPath: MerkleProofStep[] = [];
  let currentIndex = leafIndex;
  let currentLevel = [...leafHashes];

  while (currentLevel.length > 1) {
    const isRight = currentIndex % 2 === 1;
    const siblingIndex = isRight ? currentIndex - 1 : currentIndex + 1;

    if (siblingIndex < currentLevel.length) {
      proofPath.push({
        hash: currentLevel[siblingIndex],
        position: isRight ? 'left' : 'right',
      });
    }

    // Build next level
    const nextLevel: string[] = [];
    for (let i = 0; i < currentLevel.length; i += 2) {
      const left = currentLevel[i];
      const right = currentLevel[i + 1] || left;
      nextLevel.push(merkleHash(left, right));
    }

    currentIndex = Math.floor(currentIndex / 2);
    currentLevel = nextLevel;
  }

  return proofPath;
}

/**
 * Build a Merkle tree from leaf hashes
 * @param leafHashes - Array of leaf hashes
 * @returns The root hash and all levels
 */
export function buildMerkleTree(leafHashes: string[]): {
  rootHash: string;
  levels: string[][];
} {
  if (leafHashes.length === 0) {
    throw new Error('Cannot build Merkle tree from empty array');
  }

  const levels: string[][] = [leafHashes];
  let currentLevel = leafHashes;

  while (currentLevel.length > 1) {
    const nextLevel: string[] = [];

    for (let i = 0; i < currentLevel.length; i += 2) {
      const left = currentLevel[i];
      const right = currentLevel[i + 1] || left;
      nextLevel.push(merkleHash(left, right));
    }

    levels.push(nextLevel);
    currentLevel = nextLevel;
  }

  return {
    rootHash: currentLevel[0],
    levels,
  };
}

/**
 * Format a hash for display (truncate with ellipsis)
 */
export function formatHash(
  hash: string,
  prefixLength = 8,
  suffixLength = 8
): string {
  if (hash.length <= prefixLength + suffixLength + 3) {
    return hash;
  }
  return `${hash.slice(0, prefixLength)}...${hash.slice(-suffixLength)}`;
}

/**
 * Generate HMAC for data integrity
 */
export function generateHMAC(data: string, key: string): string {
  return CryptoJS.HmacSHA3(data, key).toString();
}

/**
 * Verify HMAC signature
 */
export function verifyHMAC(data: string, signature: string, key: string): boolean {
  const expected = generateHMAC(data, key);
  return expected === signature;
}

/**
 * Create a cryptographic tombstone hash
 */
export function createTombstoneHash(
  originalHash: string,
  deletionTimestamp: string,
  deletedBy: string,
  reason: string
): string {
  const data = {
    original_hash: originalHash,
    deletion_timestamp: deletionTimestamp,
    deleted_by: deletedBy,
    reason,
    type: 'TOMBSTONE',
  };
  return hashObject(data);
}

/**
 * Calculate integrity score from verification results
 */
export function calculateIntegrityScore(
  verified: number,
  tampered: number,
  total: number
): number {
  if (total === 0) return 1.0;
  return (total - tampered) / total;
}
