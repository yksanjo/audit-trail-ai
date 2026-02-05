import axios, { AxiosInstance } from 'axios';
import {
  AuditClientConfig,
  LogLLMInteractionParams,
  AuditLogEntry,
  ExportParams,
  GDPRDeletionParams,
  VerificationResult,
  DecisionLineage,
  IntegrityReport,
  MerkleProof,
} from './types';
import { DecisionType } from './types';

/**
 * Audit Trail AI Client
 * 
 * TypeScript client for the Audit Trail AI API.
 */
export class AuditClient {
  private client: AxiosInstance;
  private config: AuditClientConfig;

  constructor(config: AuditClientConfig) {
    this.config = {
      baseURL: 'http://localhost:8000',
      autoAnchor: true,
      ...config,
    };

    this.client = axios.create({
      baseURL: this.config.baseURL,
      headers: {
        'X-API-Key': this.config.apiKey,
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });
  }

  /**
   * Generate a unique decision ID
   */
  private generateDecisionId(): string {
    const timestamp = new Date().toISOString();
    const encoder = new TextEncoder();
    const data = encoder.encode(timestamp);
    
    // Simple hash for demo - use proper crypto in production
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data[i];
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    
    return `dec_${Math.abs(hash).toString(16).padStart(16, '0')}`;
  }

  /**
   * Log an LLM interaction
   */
  async logLLMInteraction(params: LogLLMInteractionParams): Promise<AuditLogEntry> {
    const orgId = params.organizationId || this.config.organizationId;
    if (!orgId) {
      throw new Error('organizationId is required');
    }

    const decisionId = this.generateDecisionId();

    const payload = {
      organization_id: orgId,
      user_id: params.userId,
      session_id: params.sessionId,
      model_name: params.modelName,
      model_version: params.modelVersion || 'unknown',
      provider: params.provider || 'openai',
      decision_type: params.decisionType || DecisionType.GENERATION,
      decision_id: decisionId,
      interaction: {
        prompt: params.prompt,
        response: params.response,
        prompt_tokens: params.promptTokens || 0,
        completion_tokens: params.completionTokens || 0,
        total_tokens: (params.promptTokens || 0) + (params.completionTokens || 0),
        latency_ms: params.latencyMs || 0,
        temperature: params.temperature,
      },
      context: {
        environment: params.context?.environment || 'production',
        data_classification: params.context?.dataClassification || 'INTERNAL',
        ...params.context,
      },
      compliance_markers: params.complianceStandards?.map((standard) => ({
        standard,
        requirement_id: `${standard}_AUDIT_001`,
      })),
    };

    const response = await this.client.post('/api/v1/audit/logs', payload);
    return response.data;
  }

  /**
   * Verify a decision's integrity
   */
  async verifyDecision(decisionId: string): Promise<{
    verified: boolean;
    results: VerificationResult[];
    integrityScore: number;
  }> {
    const response = await this.client.post('/api/v1/verify/', {
      decision_id: decisionId,
      organization_id: this.config.organizationId,
    });
    return response.data;
  }

  /**
   * Get decision lineage
   */
  async getDecisionLineage(decisionId: string): Promise<DecisionLineage> {
    const response = await this.client.get(`/api/v1/audit/lineage/${decisionId}`);
    return response.data;
  }

  /**
   * Request GDPR deletion
   */
  async requestGDPRDeletion(params: GDPRDeletionParams): Promise<{
    deletionId: string;
    status: string;
    affectedDecisions: number;
  }> {
    const orgId = params.organizationId || this.config.organizationId;
    if (!orgId) {
      throw new Error('organizationId is required');
    }

    const payload = {
      user_id: params.userId,
      organization_id: orgId,
      reason: params.reason || 'User request',
      legal_basis: params.legalBasis || 'Article 17 - Right to erasure',
      requested_by: 'sdk_client',
      request_date: new Date().toISOString(),
      specific_decision_ids: params.specificDecisionIds,
      date_range_start: params.dateRangeStart?.toISOString(),
      date_range_end: params.dateRangeEnd?.toISOString(),
    };

    const response = await this.client.post('/api/v1/compliance/gdpr/delete', payload);
    return response.data;
  }

  /**
   * Export audit logs
   */
  async exportAuditLogs(params: ExportParams): Promise<{
    exportId: string;
    status: string;
    downloadUrl?: string;
  }> {
    const orgId = params.organizationId || this.config.organizationId;
    if (!orgId) {
      throw new Error('organizationId is required');
    }

    const payload = {
      start_date: params.startDate.toISOString(),
      end_date: params.endDate.toISOString(),
      format: params.format || 'json',
      organization_id: orgId,
      include_deleted: params.includeDeleted || false,
      signed: params.signed !== false,
      evidence_level: params.evidenceLevel || 'full',
    };

    const response = await this.client.post('/api/v1/compliance/export', payload);
    return response.data;
  }

  /**
   * Get integrity report
   */
  async getIntegrityReport(
    organizationId?: string,
    startDate?: Date,
    endDate?: Date
  ): Promise<IntegrityReport> {
    const orgId = organizationId || this.config.organizationId;
    if (!orgId) {
      throw new Error('organizationId is required');
    }

    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate.toISOString();
    if (endDate) params.end_date = endDate.toISOString();

    const response = await this.client.get(`/api/v1/verify/integrity-report/${orgId}`, {
      params,
    });
    return response.data;
  }

  /**
   * Get Merkle proof for a decision
   */
  async getMerkleProof(decisionId: string): Promise<MerkleProof> {
    const response = await this.client.get(`/api/v1/verify/merkle-proof/${decisionId}`);
    return response.data;
  }

  /**
   * Get audit logs for an organization
   */
  async getAuditLogs(
    organizationId?: string,
    options: {
      page?: number;
      pageSize?: number;
      startDate?: Date;
      endDate?: Date;
    } = {}
  ): Promise<{
    items: AuditLogEntry[];
    total: number;
    page: number;
    pages: number;
  }> {
    const orgId = organizationId || this.config.organizationId;
    if (!orgId) {
      throw new Error('organizationId is required');
    }

    const params: Record<string, string | number | boolean> = {
      organization_id: orgId,
      page: options.page || 1,
      page_size: options.pageSize || 20,
    };

    if (options.startDate) params.start_date = options.startDate.toISOString();
    if (options.endDate) params.end_date = options.endDate.toISOString();

    const response = await this.client.get('/api/v1/audit/logs', { params });
    return response.data;
  }
}
