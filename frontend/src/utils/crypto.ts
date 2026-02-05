import CryptoJS from 'crypto-js'

/**
 * Generate HMAC for data integrity
 */
export function generateHMAC(data: string, key: string): string {
  return CryptoJS.HmacSHA3(data, key).toString()
}

/**
 * Verify HMAC signature
 */
export function verifyHMAC(data: string, signature: string, key: string): boolean {
  const expected = generateHMAC(data, key)
  return CryptoJS.timingSafeEqual(
    CryptoJS.enc.Hex.parse(expected),
    CryptoJS.enc.Hex.parse(signature)
  )
}

/**
 * Hash data using SHA3-256
 */
export function hashData(data: string): string {
  return CryptoJS.SHA3(data, { outputLength: 256 }).toString()
}

/**
 * Compute audit hash from components
 */
export function computeAuditHash(
  inputHash: string,
  outputHash: string,
  contextHash: string,
  metadata: Record<string, unknown>
): string {
  const data = {
    input_hash: inputHash,
    output_hash: outputHash,
    context_hash: contextHash,
    metadata,
  }
  const canonical = JSON.stringify(data, Object.keys(data).sort())
  return hashData(canonical)
}

/**
 * Generate a random verification token
 */
export function generateVerificationToken(): string {
  return CryptoJS.lib.WordArray.random(32).toString()
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
  }
  const canonical = JSON.stringify(data, Object.keys(data).sort())
  return hashData(canonical)
}

/**
 * Verify blockchain transaction hash format
 */
export function isValidTxHash(hash: string): boolean {
  return /^0x[a-fA-F0-9]{64}$/.test(hash)
}

/**
 * Verify Ethereum address format
 */
export function isValidEthAddress(address: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(address)
}

/**
 * Encode data to Base64
 */
export function toBase64(data: string): string {
  return CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse(data))
}

/**
 * Decode Base64 data
 */
export function fromBase64(data: string): string {
  return CryptoJS.enc.Base64.parse(data).toString(CryptoJS.enc.Utf8)
}

/**
 * Calculate integrity score from verification results
 */
export function calculateIntegrityScore(
  verified: number,
  tampered: number,
  total: number
): number {
  if (total === 0) return 1.0
  return (total - tampered) / total
}

/**
 * Format bytes to human-readable size
 */
export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}
