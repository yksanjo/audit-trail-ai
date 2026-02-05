/** Compliance standards supported by Audit Trail AI */
export enum ComplianceStandard {
  SOC2 = 'SOC2',
  ISO27001 = 'ISO27001',
  GDPR = 'GDPR',
  CCPA = 'CCPA',
  HIPAA = 'HIPAA',
  PCI_DSS = 'PCI_DSS',
}

/** Types of AI decisions */
export enum DecisionType {
  CLASSIFICATION = 'CLASSIFICATION',
  GENERATION = 'GENERATION',
  RECOMMENDATION = 'RECOMMENDATION',
  PREDICTION = 'PREDICTION',
  ANALYSIS = 'ANALYSIS',
  SUMMARIZATION = 'SUMMARIZATION',
  CUSTOM = 'CUSTOM',
}

/** Data classification levels */
export enum DataClassification {
  PUBLIC = 'PUBLIC',
  INTERNAL = 'INTERNAL',
  CONFIDENTIAL = 'CONFIDENTIAL',
  RESTRICTED = 'RESTRICTED',
}

/** Client configuration */
export interface AuditClientConfig {
  /** API key for authentication */
  apiKey: string;
  /** Base URL of the Audit Trail AI API */
  baseURL?: string;
  /** Default organization ID */
  organizationId?: string;
  /** Automatically anchor to blockchain */
  autoAnchor?: boolean;
}

/** LLM interaction data */
export interface LLMInteraction {
  prompt: string;
  response: string;
  promptTokens?: number;
  completionTokens?: number;
  totalTokens?: number;
  estimatedCostUSD?: number;
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  latencyMs?: number;
  rawRequest?: Record<string, unknown>;
  rawResponse?: Record<string, unknown>;
}

/** Decision context */
export interface DecisionContext {
  applicationId?: string;
  applicationVersion?: string;
  environment?: string;
  requestId?: string;
  clientIp?: string;
  userAgent?: string;
  businessUnit?: string;
  projectId?: string;
  workflowId?: string;
  sourceDataIds?: string[];
  relatedDecisions?: string[];
  parentDecisionId?: string;
  dataClassification?: DataClassification;
  legalBasis?: string;
  consentReference?: string;
  contextData?: Record<string, unknown>;
}

/** Compliance marker */
export interface ComplianceMarker {
  standard: ComplianceStandard;
  requirementId: string;
  controlId?: string;
  evidenceData?: Record<string, unknown>;
  reviewerNotes?: string;
}

/** Audit log entry */
export interface AuditLogEntry {
  id: string;
  decisionId: string;
  createdAt: string;
  organizationId: string;
  userId?: string;
  modelName: string;
  decisionType: DecisionType;
  fullHash: string;
  merkleRoot?: string;
  blockchainTxHash?: string;
  isGdprDeleted: boolean;
}

/** Parameters for logging LLM interaction */
export interface LogLLMInteractionParams {
  modelName: string;
  prompt: string;
  response: string;
  provider?: string;
  modelVersion?: string;
  organizationId?: string;
  userId?: string;
  sessionId?: string;
  decisionType?: DecisionType;
  promptTokens?: number;
  completionTokens?: number;
  latencyMs?: number;
  temperature?: number;
  context?: DecisionContext;
  complianceStandards?: ComplianceStandard[];
}

/** Export parameters */
export interface ExportParams {
  startDate: Date;
  endDate: Date;
  format?: 'json' | 'csv' | 'xlsx' | 'pdf' | 'xml';
  organizationId?: string;
  includeDeleted?: boolean;
  signed?: boolean;
  evidenceLevel?: 'full' | 'summary' | 'hash_only';
  complianceStandards?: ComplianceStandard[];
}

/** GDPR deletion parameters */
export interface GDPRDeletionParams {
  userId: string;
  organizationId?: string;
  reason?: string;
  legalBasis?: string;
  specificDecisionIds?: string[];
  dateRangeStart?: Date;
  dateRangeEnd?: Date;
}

/** Verification result */
export interface VerificationResult {
  decisionId: string;
  auditLogId: string;
  hashVerified: boolean;
  merkleVerified: boolean;
  blockchainVerified: boolean;
  tampered: boolean;
  details: {
    fullHash: string;
    merkleRoot?: string;
    blockchainTxHash?: string;
  };
}

/** Decision lineage node */
export interface DecisionLineageNode {
  decisionId: string;
  parentDecisionId?: string;
  createdAt: string;
  modelName: string;
  decisionType: DecisionType;
  fullHash: string;
  verified: boolean;
}

/** Decision lineage */
export interface DecisionLineage {
  rootDecisionId: string;
  nodes: DecisionLineageNode[];
  totalNodes: number;
  verifiedIntegrity: boolean;
}

/** Merkle proof step */
export interface MerkleProofStep {
  hash: string;
  position: 'left' | 'right';
}

/** Merkle proof */
export interface MerkleProof {
  leafHash: string;
  leafIndex: number;
  proofPath: MerkleProofStep[];
  rootHash: string;
  verified: boolean;
}

/** Integrity report */
export interface IntegrityReport {
  generatedAt: string;
  organizationId: string;
  overallIntegrity: boolean;
  integrityScore: number;
  hashChainVerified: boolean;
  merkleTreeVerified: boolean;
  blockchainAnchorsVerified: boolean;
  sequenceIntegrityVerified: boolean;
  totalLogs: number;
  verifiedLogs: number;
  tamperedLogs: number;
  missingLogs: number;
  gdprDeletedLogs: number;
  recommendations: string[];
}
