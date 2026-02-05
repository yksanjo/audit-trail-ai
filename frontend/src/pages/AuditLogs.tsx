import { useState } from 'react'
import { useAuditLogs } from '../hooks/useAuditLogs'
import { formatDate, formatHash, formatTokens, formatDuration, formatCost } from '../utils/format'
import { FileText, ChevronLeft, ChevronRight, Search, Filter } from 'lucide-react'
import type { AuditLog } from '../types'

function AuditLogDetail({ log, onClose }: { log: AuditLog; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/50">
      <div className="w-full max-w-4xl max-h-[90vh] overflow-auto bg-white rounded-lg shadow-xl">
        <div className="sticky top-0 flex items-center justify-between px-6 py-4 bg-white border-b">
          <h2 className="text-lg font-semibold text-gray-900">Audit Log Details</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Basic Info */}
          <section>
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
              Basic Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-gray-500">Decision ID</label>
                <p className="mono text-sm">{log.decision_id}</p>
              </div>
              <div>
                <label className="text-xs text-gray-500">Timestamp</label>
                <p className="text-sm">{formatDate(log.created_at)}</p>
              </div>
              <div>
                <label className="text-xs text-gray-500">Model</label>
                <p className="text-sm">{log.model_name} ({log.model_version})</p>
              </div>
              <div>
                <label className="text-xs text-gray-500">Provider</label>
                <p className="text-sm">{log.provider}</p>
              </div>
            </div>
          </section>

          {/* Hashes */}
          <section>
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
              Cryptographic Hashes
            </h3>
            <div className="space-y-2 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="text-xs text-gray-500">Full Hash</label>
                <p className="mono text-sm break-all">{log.full_hash}</p>
              </div>
              {log.merkle_root && (
                <div>
                  <label className="text-xs text-gray-500">Merkle Root</label>
                  <p className="mono text-sm break-all">{log.merkle_root}</p>
                </div>
              )}
              {log.blockchain_tx_hash && (
                <div>
                  <label className="text-xs text-gray-500">Blockchain TX</label>
                  <p className="mono text-sm break-all">{log.blockchain_tx_hash}</p>
                </div>
              )}
            </div>
          </section>

          {/* LLM Interaction */}
          {log.interaction && (
            <section>
              <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                LLM Interaction
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-500">Prompt</label>
                  <div className="mt-1 p-3 bg-gray-50 rounded text-sm font-mono whitespace-pre-wrap">
                    {log.interaction.prompt}
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Response</label>
                  <div className="mt-1 p-3 bg-gray-50 rounded text-sm font-mono whitespace-pre-wrap">
                    {log.interaction.response}
                  </div>
                </div>
                <div className="grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <label className="text-xs text-gray-500">Tokens</label>
                    <p>{formatTokens(log.interaction.total_tokens)}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Latency</label>
                    <p>{formatDuration(log.interaction.latency_ms)}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Cost</label>
                    <p>{formatCost(log.interaction.estimated_cost_usd)}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Temperature</label>
                    <p>{log.interaction.temperature ?? '—'}</p>
                  </div>
                </div>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}

function AuditLogs() {
  const [page, setPage] = useState(1)
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null)
  
  const { data, isLoading } = useAuditLogs({
    organization_id: 'demo-org',
    page,
    page_size: 20,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const logs = data?.items || []
  const totalPages = data?.pages || 1

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
          <p className="mt-1 text-sm text-gray-500">
            Browse and search all AI decision logs
          </p>
        </div>
        <div className="flex space-x-2">
          <button className="btn-secondary flex items-center">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </button>
          <button className="btn-primary flex items-center">
            <Search className="w-4 h-4 mr-2" />
            Search
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Decision ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Model
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hash
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log) => (
                <tr
                  key={log.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => setSelectedLog(log)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="w-4 h-4 text-gray-400 mr-2" />
                      <span className="mono text-sm text-gray-900">
                        {formatHash(log.decision_id, 6)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(log.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.model_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="badge badge-info">
                      {log.decision_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap mono text-xs text-gray-500">
                    {formatHash(log.full_hash)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {log.blockchain_tx_hash ? (
                      <span className="badge badge-success">Anchored</span>
                    ) : (
                      <span className="badge badge-warning">Pending</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200">
          <div className="text-sm text-gray-500">
            Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data?.total || 0)} of{' '}
            {formatNumber(data?.total || 0)} results
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="btn-secondary disabled:opacity-50"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="btn-secondary disabled:opacity-50"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedLog && (
        <AuditLogDetail log={selectedLog} onClose={() => setSelectedLog(null)} />
      )}
    </div>
  )
}

export default AuditLogs
