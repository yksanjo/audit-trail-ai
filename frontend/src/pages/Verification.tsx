import { useState } from 'react'
import { useVerification, useIntegrityReport } from '../hooks/useVerification'
import { formatHash, formatPercent } from '../utils/format'
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Shield,
  Search,
  RefreshCw,
  Lock,
} from 'lucide-react'
import type { VerificationResult } from '../types'

function VerificationResultCard({ result }: { result: VerificationResult }) {
  return (
    <div
      className={`p-4 rounded-lg border ${
        result.tampered
          ? 'bg-danger-50 border-danger-200'
          : 'bg-success-50 border-success-200'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {result.tampered ? (
            <XCircle className="w-5 h-5 text-danger-600" />
          ) : (
            <CheckCircle className="w-5 h-5 text-success-600" />
          )}
          <div>
            <p className="mono text-sm font-medium text-gray-900">
              {formatHash(result.decision_id, 8)}
            </p>
            <p className="text-xs text-gray-500">
              {result.tampered ? 'Tampering detected' : 'Integrity verified'}
            </p>
          </div>
        </div>
        <div className="flex space-x-2">
          {result.hash_verified && (
            <span className="badge badge-success text-xs">Hash</span>
          )}
          {result.merkle_verified && (
            <span className="badge badge-success text-xs">Merkle</span>
          )}
          {result.blockchain_verified && (
            <span className="badge badge-success text-xs">Blockchain</span>
          )}
        </div>
      </div>
    </div>
  )
}

function Verification() {
  const [decisionId, setDecisionId] = useState('')
  const [orgId] = useState('demo-org')
  
  const { mutate: verify, data: verifyResult, isLoading: isVerifying } = useVerification()
  const { data: integrityReport, isLoading: isLoadingReport, refetch } = useIntegrityReport(orgId)

  const handleVerify = () => {
    if (decisionId.trim()) {
      verify({ decision_id: decisionId.trim(), organization_id: orgId })
    }
  }

  const handleVerifyAll = () => {
    verify({ organization_id: orgId })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Verification</h1>
        <p className="mt-1 text-sm text-gray-500">
          Verify the integrity of audit logs using cryptographic proofs
        </p>
      </div>

      {/* Verification Controls */}
      <div className="card p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Verify Specific Decision
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={decisionId}
                onChange={(e) => setDecisionId(e.target.value)}
                placeholder="Enter decision ID..."
                className="input flex-1"
                onKeyDown={(e) => e.key === 'Enter' && handleVerify()}
              />
              <button
                onClick={handleVerify}
                disabled={isVerifying || !decisionId.trim()}
                className="btn-primary flex items-center disabled:opacity-50"
              >
                <Search className="w-4 h-4 mr-2" />
                Verify
              </button>
            </div>
          </div>

          <div className="border-t pt-4">
            <button
              onClick={handleVerifyAll}
              disabled={isVerifying}
              className="btn-secondary w-full flex items-center justify-center disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isVerifying ? 'animate-spin' : ''}`} />
              Verify All Organization Logs
            </button>
          </div>
        </div>
      </div>

      {/* Verification Results */}
      {verifyResult && (
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                Verification Results
              </h3>
              <div className="flex items-center">
                {verifyResult.verified ? (
                  <span className="badge badge-success flex items-center">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    All Verified
                  </span>
                ) : (
                  <span className="badge badge-danger flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-1" />
                    Issues Found
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-semibold text-gray-900">
                  {verifyResult.total_checked}
                </p>
                <p className="text-sm text-gray-500">Checked</p>
              </div>
              <div className="text-center p-4 bg-success-50 rounded-lg">
                <p className="text-2xl font-semibold text-success-600">
                  {verifyResult.total_checked - verifyResult.tampered_count}
                </p>
                <p className="text-sm text-gray-500">Verified</p>
              </div>
              <div className="text-center p-4 bg-danger-50 rounded-lg">
                <p className="text-2xl font-semibold text-danger-600">
                  {verifyResult.tampered_count}
                </p>
                <p className="text-sm text-gray-500">Tampered</p>
              </div>
              <div className="text-center p-4 bg-primary-50 rounded-lg">
                <p className="text-2xl font-semibold text-primary-600">
                  {formatPercent(verifyResult.integrity_score)}
                </p>
                <p className="text-sm text-gray-500">Integrity Score</p>
              </div>
            </div>

            {verifyResult.results.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Individual Results
                </h4>
                {verifyResult.results.map((result) => (
                  <VerificationResultCard key={result.decision_id} result={result} />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Integrity Report */}
      {integrityReport && (
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              System Integrity Report
            </h3>
            <button onClick={() => refetch()} className="btn-secondary text-sm">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center mb-2">
                  <Shield className="w-5 h-5 text-primary-600 mr-2" />
                  <span className="text-sm text-gray-500">Total Logs</span>
                </div>
                <p className="text-xl font-semibold text-gray-900">
                  {integrityReport.total_logs}
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="flex items-center mb-2">
                  <Lock className="w-5 h-5 text-success-600 mr-2" />
                  <span className="text-sm text-gray-500">Verified</span>
                </div>
                <p className="text-xl font-semibold text-gray-900">
                  {integrityReport.verified_logs}
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="flex items-center mb-2">
                  <AlertTriangle className="w-5 h-5 text-warning-600 mr-2" />
                  <span className="text-sm text-gray-500">Merkle Roots</span>
                </div>
                <p className="text-xl font-semibold text-gray-900">
                  {integrityReport.merkle_roots_checked}
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="flex items-center mb-2">
                  <Lock className="w-5 h-5 text-primary-600 mr-2" />
                  <span className="text-sm text-gray-500">Blockchain</span>
                </div>
                <p className="text-xl font-semibold text-gray-900">
                  {integrityReport.blockchain_anchors_checked}
                </p>
              </div>
            </div>

            {/* Checks Status */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Verification Checks</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {[
                  { name: 'Hash Chain', passed: integrityReport.hash_chain_verified },
                  { name: 'Merkle Tree', passed: integrityReport.merkle_tree_verified },
                  { name: 'Blockchain Anchors', passed: integrityReport.blockchain_anchors_verified },
                  { name: 'Sequence Integrity', passed: integrityReport.sequence_integrity_verified },
                ].map((check) => (
                  <div
                    key={check.name}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <span className="text-sm text-gray-700">{check.name}</span>
                    {check.passed ? (
                      <CheckCircle className="w-5 h-5 text-success-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-danger-500" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Verification
