import CryptoJS from 'crypto-js'

export interface MerkleProofStep {
  hash: string
  position: 'left' | 'right'
}

/**
 * Hash a string using SHA3-256
 */
export function hashString(data: string): string {
  return CryptoJS.SHA3(data, { outputLength: 256 }).toString()
}

/**
 * Hash a JavaScript object deterministically
 */
export function hashObject(obj: Record<string, unknown>): string {
  const canonical = JSON.stringify(obj, Object.keys(obj).sort())
  return hashString(canonical)
}

/**
 * Compute parent hash from two child hashes
 */
export function merkleHash(left: string, right: string): string {
  return hashString(left + right)
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
  let currentHash = leafHash

  for (const step of proofPath) {
    if (step.position === 'left') {
      currentHash = merkleHash(step.hash, currentHash)
    } else {
      currentHash = merkleHash(currentHash, step.hash)
    }
  }

  return currentHash === rootHash
}

/**
 * Build a Merkle tree from leaf hashes
 * @param leafHashes - Array of leaf hashes
 * @returns The root hash and tree structure
 */
export function buildMerkleTree(leafHashes: string[]): {
  rootHash: string
  levels: string[][]
} {
  if (leafHashes.length === 0) {
    throw new Error('Cannot build Merkle tree from empty array')
  }

  const levels: string[][] = [leafHashes]
  let currentLevel = leafHashes

  while (currentLevel.length > 1) {
    const nextLevel: string[] = []

    for (let i = 0; i < currentLevel.length; i += 2) {
      const left = currentLevel[i]
      const right = currentLevel[i + 1] || left
      nextLevel.push(merkleHash(left, right))
    }

    levels.push(nextLevel)
    currentLevel = nextLevel
  }

  return {
    rootHash: currentLevel[0],
    levels,
  }
}

/**
 * Generate a Merkle proof for a specific leaf
 * @param leafIndex - Index of the leaf
 * @param leafHashes - All leaf hashes
 * @returns The proof path
 */
export function generateMerkleProof(
  leafIndex: number,
  leafHashes: string[]
): MerkleProofStep[] {
  const tree = buildMerkleTree(leafHashes)
  const proofPath: MerkleProofStep[] = []

  let currentIndex = leafIndex

  for (let level = 0; level < tree.levels.length - 1; level++) {
    const levelNodes = tree.levels[level]
    const isRight = currentIndex % 2 === 1
    const siblingIndex = isRight ? currentIndex - 1 : currentIndex + 1

    if (siblingIndex < levelNodes.length) {
      proofPath.push({
        hash: levelNodes[siblingIndex],
        position: isRight ? 'left' : 'right',
      })
    }

    currentIndex = Math.floor(currentIndex / 2)
  }

  return proofPath
}

/**
 * Format a hash for display (truncate with ellipsis)
 */
export function formatHash(hash: string, prefixLength = 8, suffixLength = 8): string {
  if (hash.length <= prefixLength + suffixLength + 3) {
    return hash
  }
  return `${hash.slice(0, prefixLength)}...${hash.slice(-suffixLength)}`
}

/**
 * Verify the integrity of a hash chain
 */
export function verifyHashChain(
  hashes: string[],
  expectedRootHash: string
): boolean {
  try {
    const { rootHash } = buildMerkleTree(hashes)
    return rootHash === expectedRootHash
  } catch {
    return false
  }
}
