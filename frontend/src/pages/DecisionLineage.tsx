import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useDecisionLineage } from '../hooks/useAuditLogs'
import { formatDate, formatHash } from '../utils/format'
import { GitBranch, Search, CheckCircle, XCircle, ArrowRight } from 'lucide-react'
import type { DecisionLineageNode } from '../types'

function LineageNode({
  node,
  level,
  isLast,
}: {
  node: DecisionLineageNode
  level: number
  isLast: boolean
}) {
  return (
    <div className="relative flex items-start">
      {/* Timeline line */}
      {level > 0 && (
        <>
          <div
            className="absolute left-4 top-0 w-px bg-gray-300"
            style={{ height: '50%', top: '-50%' }}
          />
          <div className="absolute left-4 top-1/2 w-8 h-px bg-gray-300" />
        </>
      )}
      
      {/* Node dot */}
      <div
        className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center border-2 ${
          node.verified
            ? 'bg-success-100 border-success-500'
            : 'bg-warning-100 border-warning-500'
        }`}
        style={{ marginLeft: `${level * 32}px` }}
      >
        {node.verified ? (
          <CheckCircle className="w-4 h-4 text-success-600" />
        ) : (
          <XCircle className="w-4 h-4 text-warning-600" />
        )}
      </div>

      {/* Node content */}
      <div className="ml-4 flex-1 pb-8">
        <div className="card p-4 card-hover">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="mono text-sm font-medium text-gray-900">
                {formatHash(node.decision_id, 8)}
              </span>
              <span className="badge badge-info text-xs">
                {node.decision_type}
              </span>
            </div>
            <span className="text-xs text-gray-500">
              {formatDate(node.created_at)}
            </span>
          </div>
          <div className="text-sm text-gray-600 mb-2">
            Model: {node.model_name}
          </div>
          <div className="mono text-xs text-gray-400">
            Hash: {formatHash(node.full_hash)}
          </div>
        </div>
      </div>
    </div>
  )
}

function DecisionLineage() {
  const { decisionId: urlDecisionId } = useParams<{ decisionId?: string }>()
  const [searchId, setSearchId] = useState(urlDecisionId || '')
  const [decisionId, setDecisionId] = useState(urlDecisionId || '')

  const { data: lineage, isLoading } = useDecisionLineage(decisionId)

  const handleSearch = () => {
    if (searchId.trim()) {
      setDecisionId(searchId.trim())
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Decision Lineage</h1>
        <p className="mt-1 text-sm text-gray-500">
          Trace the complete history and context of AI decisions
        </p>
      </div>

      {/* Search */}
      <div className="card p-4">
        <div className="flex space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Decision ID
            </label>
            <div className="relative">
              <input
                type="text"
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
                placeholder="Enter decision ID..."
                className="input pl-10"
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
          </div>
          <div className="flex items-end">
            <button onClick={handleSearch} className="btn-primary">
              Trace Lineage
            </button>
          </div>
        </div>
      </div>

      {/* Lineage Tree */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : decisionId && lineage ? (
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                Lineage Tree
              </h3>
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <span className="w-3 h-3 rounded-full bg-success-500 mr-2" />
                  <span className="text-sm text-gray-600">
                    {lineage.nodes.filter((n) => n.verified).length} Verified
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="w-3 h-3 rounded-full bg-warning-500 mr-2" />
                  <span className="text-sm text-gray-600">
                    {lineage.nodes.filter((n) => !n.verified).length} Pending
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-6">
            {lineage.nodes.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No lineage found for this decision
              </div>
            ) : (
              <div className="space-y-0">
                {lineage.nodes.map((node, index) => (
                  <LineageNode
                    key={node.decision_id}
                    node={node}
                    level={0}
                    isLast={index === lineage.nodes.length - 1}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Summary */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div>
                  <span className="text-sm text-gray-500">Total Nodes</span>
                  <p className="text-lg font-semibold text-gray-900">
                    {lineage.total_nodes}
                  </p>
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400" />
                <div>
                  <span className="text-sm text-gray-500">Root Decision</span>
                  <p className="mono text-sm text-gray-900">
                    {formatHash(lineage.root_decision_id, 8)}
                  </p>
                </div>
              </div>
              <div className="flex items-center">
                {lineage.verified_integrity ? (
                  <span className="badge badge-success flex items-center">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Integrity Verified
                  </span>
                ) : (
                  <span className="badge badge-warning flex items-center">
                    <XCircle className="w-4 h-4 mr-1" />
                    Pending Verification
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {/* Empty State */}
      {!decisionId && (
        <div className="card p-12 text-center">
          <GitBranch className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Search for a Decision
          </h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Enter a decision ID above to trace its complete lineage, including
            parent decisions, related context, and verification status.
          </p>
        </div>
      )}
    </div>
  )
}

export default DecisionLineage
