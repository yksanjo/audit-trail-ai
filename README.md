# 🔒 Audit Trail AI

> **Tamper-proof logging system for AI decisions with SOC2/ISO27001/GDPR compliance**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

Audit Trail AI provides a complete, production-ready system for capturing, verifying, and auditing AI/LLM interactions. Built for regulated industries (finance, healthcare, legal), it ensures every AI decision is:

- **Immutable**: Cryptographic hashing prevents tampering
- **Verifiable**: Merkle tree + blockchain anchoring provides proof of integrity
- **Compliant**: Built-in support for SOC2, ISO27001, GDPR, HIPAA, and CCPA
- **Auditable**: Complete decision lineage with full context

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Audit Trail AI                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   Frontend   │◄──►│   Backend    │◄──►│  PostgreSQL  │     │
│  │   (React)    │    │  (FastAPI)   │    │   (Data)     │     │
│  └──────────────┘    └──────┬───────┘    └──────────────┘     │
│                             │                                   │
│                    ┌────────▼────────┐                         │
│                    │  Merkle Trees   │                         │
│                    │  Hash Chains    │                         │
│                    └────────┬────────┘                         │
│                             │                                   │
│                    ┌────────▼────────┐                         │
│                    │  Blockchain     │                         │
│                    │   Anchoring     │                         │
│                    └─────────────────┘                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)

### Docker Deployment (Recommended)

```bash
# Clone the repository
cd ~/security-ai-stack/audit-trail-ai

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Access the dashboard
open http://localhost:3000
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e "."

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:5173
```

## 📖 Usage

### Python SDK

```python
from audit_trail_ai import AuditClient, ComplianceStandard, DecisionType

# Initialize client
client = AuditClient(
    api_key="your-api-key",
    base_url="http://localhost:8000",
    organization_id="acme-corp"
)

# Log an LLM interaction
log = client.log_llm_interaction(
    model_name="gpt-4",
    prompt="What is the risk score for this transaction?",
    response="Low risk - 0.23",
    decision_type=DecisionType.PREDICTION,
    prompt_tokens=15,
    completion_tokens=8,
    latency_ms=450,
    compliance_standards=[
        ComplianceStandard.SOC2,
        ComplianceStandard.ISO27001
    ]
)

print(f"Logged: {log.decision_id}")
print(f"Hash: {log.full_hash}")

# Verify integrity
verification = client.verify_decision(log.decision_id)
print(f"Integrity: {verification['integrity_score']:.1%}")
```

### TypeScript SDK

```typescript
import { AuditClient, ComplianceStandard, DecisionType } from '@audit-trail-ai/sdk';

const client = new AuditClient({
  apiKey: 'your-api-key',
  baseURL: 'http://localhost:8000',
  organizationId: 'acme-corp'
});

// Log an interaction
const log = await client.logLLMInteraction({
  modelName: 'gpt-4',
  prompt: 'Analyze this medical record',
  response: 'Patient shows no abnormalities',
  decisionType: DecisionType.ANALYSIS,
  complianceStandards: [ComplianceStandard.HIPAA]
});

// Get decision lineage
const lineage = await client.getDecisionLineage(log.decisionId);
console.log(`Related decisions: ${lineage.totalNodes}`);
```

### Using the Decorator (Python)

```python
from audit_trail_ai import audit_llm_call, AuditClient

client = AuditClient(api_key="your-api-key")

@audit_llm_call(client, model_name="gpt-4")
def analyze_risk(data: str) -> str:
    return openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Analyze: {data}"}]
    )

# Automatically logged
result = analyze_risk("Transaction #12345")
```

## 🔐 Key Features

### 1. Immutable Audit Logs

Every AI interaction is hashed using SHA3-256:

```python
{
  "input_hash": "sha3_256(prompt)",
  "output_hash": "sha3_256(response)",
  "context_hash": "sha3_256(metadata)",
  "full_hash": "sha3_256(combined)"
}
```

### 2. Merkle Tree Integrity

Logs are organized into Merkle trees for efficient verification:

```
        Root Hash
       /         \
   Hash AB      Hash CD
   /    \
Hash A  Hash B
```

- **O(log n)** verification time
- Any tampering invalidates the root hash
- Proofs can be generated for individual leaves

### 3. Blockchain Anchoring

Merkle roots are anchored to Ethereum for immutable timestamping:

```solidity
function anchorMerkleRoot(bytes32 rootHash) external {
    anchors[rootHash] = Anchor({
        blockNumber: block.number,
        timestamp: block.timestamp,
        submitter: msg.sender
    });
}
```

### 4. Decision Lineage

Trace the complete history of related decisions:

```
Decision A (root)
    └── Decision B (child)
            └── Decision C (grandchild)
```

Perfect for:
- Understanding decision context
- Root cause analysis
- Compliance investigations

### 5. GDPR/CCPA Compliance

**Right to Erasure with Cryptographic Tombstones:**

When a user requests deletion:

1. Original data is purged
2. A cryptographic tombstone is created:
   ```
   tombstone_hash = sha3_256(
       original_hash + 
       deletion_timestamp + 
       deleted_by + 
       reason
   )
   ```
3. Tombstone is anchored to blockchain
4. Retained for audit purposes (configurable: 30-90 days)

**Data Portability:**

```python
# Export all user data
export = client.export_data_portability(
    user_id="user_123",
    format="json"
)
```

### 6. Compliance Exports

Generate auditor-ready reports:

| Standard | Features |
|----------|----------|
| **SOC2** | Control mapping, availability metrics, integrity proofs |
| **ISO27001** | Risk assessment, management review, evidence logs |
| **GDPR** | Deletion logs, consent tracking, data lineage |
| **HIPAA** | PHI access logs, audit trails, encryption verification |

## 📊 Dashboard Features

### Audit Logs
- Browse all AI decisions
- Search and filter
- View full interaction details
- Download individual logs

### Decision Lineage
- Visual tree view of related decisions
- Parent/child relationships
- Verification status at each node

### Verification
- Run integrity checks
- Verify Merkle proofs
- Generate blockchain proofs
- Schedule automated verification

### Compliance
- GDPR deletion requests
- Data portability exports
- Retention policy management
- Compliance status tracking

### Export
- JSON, CSV, Excel, PDF, XML formats
- Signed exports with HMAC
- Date range selection
- Evidence level control

## 🔍 Verification

### Verify a Single Decision

```bash
curl -X POST http://localhost:8000/api/v1/verify/ \
  -H "Content-Type: application/json" \
  -d '{"decision_id": "dec_abc123"}'
```

Response:
```json
{
  "verified": true,
  "integrity_score": 1.0,
  "results": [{
    "decision_id": "dec_abc123",
    "hash_verified": true,
    "merkle_verified": true,
    "blockchain_verified": true,
    "tampered": false
  }]
}
```

### Verify Merkle Proof

```bash
curl -X GET http://localhost:8000/api/v1/verify/merkle-proof/dec_abc123
```

## 🏛️ Compliance Standards

### SOC2 Type II

- **Availability**: 99.9% uptime with redundant storage
- **Confidentiality**: Encryption at rest and in transit
- **Processing Integrity**: Cryptographic verification of all logs
- **Security**: Role-based access control, audit trails

### ISO27001

- **A.12.4**: Logging and monitoring
- **A.12.5**: Control of operational software
- **A.16.1**: Management of information security incidents

### GDPR

- **Article 17**: Right to erasure with tombstones
- **Article 20**: Data portability
- **Article 30**: Records of processing activities
- **Article 33**: Breach notification

### HIPAA

- **§164.312(b)**: Audit controls
- **§164.312(c)(1)**: Integrity controls
- **§164.308(a)(5)**: Transmission security

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `postgres` | 5432 | PostgreSQL database |
| `backend` | 8000 | FastAPI application |
| `frontend` | 3000 | React dashboard |

## 📁 Project Structure

```
audit-trail-ai/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── routers/           # API endpoints
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # DB connection
│   │   └── main.py            # Application entry
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── alembic/               # Database migrations
│
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks
│   │   ├── utils/             # Utilities
│   │   ├── services/          # API services
│   │   ├── types/             # TypeScript types
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
│
├── sdk/
│   ├── python/                # Python SDK
│   └── typescript/            # TypeScript SDK
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🧪 API Endpoints

### Audit Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/audit/logs` | Create audit log |
| `GET` | `/api/v1/audit/logs` | List audit logs |
| `GET` | `/api/v1/audit/logs/{id}` | Get audit log |
| `GET` | `/api/v1/audit/lineage/{id}` | Get decision lineage |
| `GET` | `/api/v1/audit/stats/{org}` | Get statistics |

### Verification

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/verify/` | Verify logs |
| `GET` | `/api/v1/verify/merkle-proof/{id}` | Get Merkle proof |
| `GET` | `/api/v1/verify/integrity-report/{org}` | Get integrity report |

### Compliance

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/compliance/export` | Export logs |
| `POST` | `/api/v1/compliance/gdpr/delete` | GDPR deletion |
| `GET` | `/api/v1/compliance/standards` | List standards |

## 🔧 Configuration

See `.env.example` for all configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://audit:audit@localhost:5432/audit_trail` |
| `BLOCKCHAIN_ENABLED` | Enable blockchain anchoring | `false` |
| `ETHEREUM_RPC_URL` | Ethereum node URL | `http://localhost:8545` |
| `ENCRYPTION_KEY` | Encryption key for sensitive data | - |
| `GDPR_DELETION_RETENTION_DAYS` | Tombstone retention period | `90` |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://reactjs.org/)
- Cryptography powered by [cryptography](https://cryptography.io/) and [Web3.py](https://web3py.readthedocs.io/)
- UI components inspired by [Tailwind UI](https://tailwindui.com/)

## 📞 Support

For questions or support, please open an issue on GitHub or contact the maintainers.

---

**Built for regulated industries by engineers who care about compliance and security.** 🔒
