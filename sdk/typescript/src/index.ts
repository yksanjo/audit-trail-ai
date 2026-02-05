/**
 * Audit Trail AI TypeScript SDK
 * 
 * Tamper-proof logging for AI decisions with SOC2/ISO27001/GDPR compliance.
 * 
 * @example
 * ```typescript
 * import { AuditClient, ComplianceStandard, DecisionType } from '@audit-trail-ai/sdk';
 * 
 * const client = new AuditClient({
 *   apiKey: 'your-api-key',
 *   baseURL: 'http://localhost:8000'
 * });
 * 
 * const log = await client.logLLMInteraction({
 *   modelName: 'gpt-4',
 *   prompt: 'What is 2+2?',
 *   response: '4',
 *   decisionType: DecisionType.GENERATION,
 *   complianceStandards: [ComplianceStandard.SOC2]
 * });
 * ```
 */

export { AuditClient } from './client';
export { AuditClient as default } from './client';

export {
  ComplianceStandard,
  DecisionType,
  DataClassification,
} from './types';

export type {
  AuditClientConfig,
  LogLLMInteractionParams,
  LLMInteraction,
  DecisionContext,
  ComplianceMarker,
  AuditLogEntry,
  ExportParams,
  GDPRDeletionParams,
  VerificationResult,
  DecisionLineage,
} from './types';

export {
  hashString,
  hashObject,
  verifyMerkleProof,
  generateMerkleProof,
  formatHash,
} from './crypto';
