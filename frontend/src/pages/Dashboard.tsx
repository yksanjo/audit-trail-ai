import { useAuditStats } from '../hooks/useAuditLogs'
import { formatNumber, formatPercent } from '../utils/format'
import {
  Shield,
  FileText,
  CheckCircle,
  Activity,
  Lock,
} from 'lucide-react'

function Dashboard() {
  const { data: stats, isLoading } = useAuditStats('demo-org')

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const anchoredPercent = stats
    ? (stats.blockchain_anchored / Math.max(stats.total_decisions, 1)) * 100
    : 0

  const stats_cards = [
    {
      name: 'Total Decisions',
      value: stats ? formatNumber(stats.total_decisions) : '—',
      icon: FileText,
      color: 'primary',
    },
    {
      name: 'Blockchain Anchored',
      value: stats ? formatNumber(stats.blockchain_anchored) : '—',
      subtext: stats ? formatPercent(anchoredPercent / 100) : '',
      icon: Lock,
      color: 'success',
    },
    {
      name: 'GDPR Deletions',
      value: stats ? formatNumber(stats.gdpr_deleted) : '—',
      icon: Shield,
      color: 'warning',
    },
    {
      name: 'Integrity Score',
      value: '100%',
      icon: CheckCircle,
      color: 'success',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your AI decision audit trail
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats_cards.map((stat) => (
          <div
            key={stat.name}
            className="overflow-hidden bg-white rounded-lg shadow card-hover"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className={`flex-shrink-0 p-3 rounded-md bg-${stat.color}-100`}>
                  <stat.icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
                <div className="flex-1 w-0 ml-5">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">
                        {stat.value}
                      </div>
                      {stat.subtext && (
                        <div className="ml-2 text-sm text-gray-500">
                          {stat.subtext}
                        </div>
                      )}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Compliance Status */}
        <div className="card">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Compliance Status
            </h3>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              {['SOC2', 'ISO27001', 'GDPR', 'HIPAA'].map((standard) => (
                <div key={standard} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-success-500 mr-3" />
                    <span className="text-sm font-medium text-gray-700">
                      {standard}
                    </span>
                  </div>
                  <span className="badge badge-success">Compliant</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="card">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              System Status
            </h3>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div className="flex items-center">
                <Activity className="w-5 h-5 text-success-500 mr-3" />
                <span className="text-sm text-gray-700">Audit logging active</span>
              </div>
              <div className="flex items-center">
                <Lock className="w-5 h-5 text-success-500 mr-3" />
                <span className="text-sm text-gray-700">Merkle tree verification</span>
              </div>
              <div className="flex items-center">
                <Shield className="w-5 h-5 text-success-500 mr-3" />
                <span className="text-sm text-gray-700">Encryption at rest</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
