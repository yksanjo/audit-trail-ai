# Audit Trail AI Python SDK

Tamper-proof logging for AI decisions with SOC2/ISO27001/GDPR compliance.

## Installation

```bash
pip install audit-trail-ai
```

## Quick Start

```python
from audit_trail_ai import AuditClient, ComplianceStandard, DecisionType

# Initialize client
client = AuditClient(
    api_key="your-api-key",
    base_url="http://localhost:8000",
    organization_id="your-org"
)

# Log an LLM interaction
log = client.log_llm_interaction(
    model_name="gpt-4",
    prompt="What is the capital of France?",
    response="Paris",
    provider="openai",
    decision_type=DecisionType.GENERATION,
    prompt_tokens=10,
    completion_tokens=1,
    latency_ms=500,
    compliance_standards=[ComplianceStandard.SOC2, ComplianceStandard.ISO27001]
)

print(f"Decision logged: {log.decision_id}")
print(f"Hash: {log.full_hash}")

# Verify integrity
verification = client.verify_decision(log.decision_id)
print(f"Integrity score: {verification['integrity_score']}")

# Close client
client.close()
```

## Using the Decorator

```python
from audit_trail_ai import audit_llm_call, AuditClient

client = AuditClient(api_key="your-api-key")

@audit_llm_call(client, model_name="gpt-4")
def ask_ai(prompt: str):
    return openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

# This call will be automatically logged
response = ask_ai("What is 2+2?")
```

## GDPR Compliance

```python
# Request user data deletion
result = client.request_gdpr_deletion(
    user_id="user_123",
    reason="User requested deletion"
)
print(f"Deleted {result['affected_decisions']} records")
```

## Export for Auditors

```python
from datetime import datetime, timedelta

# Export last 30 days
export = client.export_audit_logs(
    start_date=datetime.utcnow() - timedelta(days=30),
    end_date=datetime.utcnow(),
    format="xlsx"
)
print(f"Export ID: {export['export_id']}")
```

## License

MIT
