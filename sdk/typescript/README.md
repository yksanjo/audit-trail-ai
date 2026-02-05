# Audit Trail AI TypeScript SDK

Tamper-proof logging for AI decisions with SOC2/ISO27001/GDPR compliance.

## Installation

```bash
npm install @audit-trail-ai/sdk
# or
yarn add @audit-trail-ai/sdk
```

## Quick Start

```typescript
import { AuditClient, ComplianceStandard, DecisionType } from '@audit-trail-ai/sdk';

// Initialize client
const client = new AuditClient({
  apiKey: 'your-api-key',
  baseURL: 'http://localhost:8000',
  organizationId: 'your-org'
});

// Log an LLM interaction
const log = await client.logLLMInteraction({
  modelName: 'gpt-4',
  prompt: 'What is the capital of France?',
  response: 'Paris',
  provider: 'openai',
  decisionType: DecisionType.GENERATION,
  promptTokens: 10,
  completionTokens: 1,
  latencyMs: 500,
  complianceStandards: [ComplianceStandard.SOC2, ComplianceStandard.ISO27001]
});

console.log(`Decision logged: ${log.decisionId}`);
console.log(`Hash: ${log.fullHash}`);

// Verify integrity
const verification = await client.verifyDecision(log.decisionId);
console.log(`Integrity score: ${verification.integrityScore}`);
```

## React Integration

```typescript
import { useAuditLogs } from './hooks/useAuditLogs';

function AuditLogList() {
  const { data, isLoading } = useAuditLogs({
    organization_id: 'your-org',
    page: 1,
    page_size: 20
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <ul>
      {data?.items.map(log => (
        <li key={log.id}>{log.decisionId}</li>
      ))}
    </ul>
  );
}
```

## GDPR Compliance

```typescript
// Request user data deletion
const result = await client.requestGDPRDeletion({
  userId: 'user_123',
  reason: 'User requested deletion'
});
console.log(`Deleted ${result.affectedDecisions} records`);
```

## Export for Auditors

```typescript
// Export last 30 days
const export = await client.exportAuditLogs({
  startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
  endDate: new Date(),
  format: 'xlsx'
});
console.log(`Export ID: ${export.exportId}`);
```

## Cryptographic Verification

```typescript
import { verifyMerkleProof, formatHash } from '@audit-trail-ai/sdk';

// Get and verify Merkle proof
const proof = await client.getMerkleProof(decisionId);
const isValid = verifyMerkleProof(
  proof.leafHash,
  proof.rootHash,
  proof.proofPath
);
console.log(`Proof valid: ${isValid}`);
```

## License

MIT
