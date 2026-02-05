import { useState } from 'react'
import { Shield, Trash2, Download, CheckCircle, UserX, FileText } from 'lucide-react'
import { formatDate } from '../utils/format'

interface GDPRRequest {
  id: string
  userId: string
  type: 'deletion' | 'export'
  status: 'pending' | 'completed' | 'failed'
  requestedAt: string
  completedAt?: string
  affectedRecords: number
}

function Compliance() {
  const [activeTab, setActiveTab] = useState<'overview' | 'gdpr' | 'retention'>('overview')
  const [gdprRequests] = useState<GDPRRequest[]>([
    {
      id: 'req_001',
      userId: 'user_12345',
      type: 'deletion',
      status: 'completed',
      requestedAt: '2024-01-15T10:30:00Z',
      completedAt: '2024-01-15T10:35:00Z',
      affectedRecords: 42,
    },
    {
      id: 'req_002',
      userId: 'user_67890',
      type: 'export',
      status: 'pending',
      requestedAt: '2024-01-16T14:20:00Z',
      affectedRecords: 0,
    },
  ])

  const standards = [
    {
      name: 'SOC 2 Type II',
      status: 'compliant',
      lastAudit: '2024-01-01',
      nextAudit: '2024-07-01',
      controls: 127,
      passed: 127,
    },
    {
      name: 'ISO 27001',
      status: 'compliant',
      lastAudit: '2024-02-15',
      nextAudit: '2025-02-15',
      controls: 114,
      passed: 114,
    },
    {
      name: 'GDPR',
      status: 'compliant',
      lastAudit: '2024-01-10',
      nextAudit: 'Continuous',
      controls: 89,
      passed: 89,
    },
    {
      name: 'HIPAA',
      status: 'compliant',
      lastAudit: '2024-03-01',
      nextAudit: '2025-03-01',
      controls: 75,
      passed: 75,
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Compliance</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage compliance standards, GDPR requests, and data retention
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: Shield },
            { id: 'gdpr', label: 'GDPR & Privacy', icon: UserX },
            { id: 'retention', label: 'Data Retention', icon: Trash2 },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Compliance Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {standards.map((standard) => (
              <div key={standard.name} className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {standard.name}
                  </h3>
                  <span
                    className={`badge ${
                      standard.status === 'compliant'
                        ? 'badge-success'
                        : 'badge-warning'
                    }`}
                  >
                    {standard.status}
                  </span>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Controls</span>
                    <span className="font-medium">
                      {standard.passed}/{standard.controls}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Last Audit</span>
                    <span className="font-medium">
                      {formatDate(standard.lastAudit)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Next Audit</span>
                    <span className="font-medium">
                      {standard.nextAudit === 'Continuous'
                        ? standard.nextAudit
                        : formatDate(standard.nextAudit)}
                    </span>
                  </div>
                  <div className="mt-4 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-success-500 rounded-full"
                      style={{ width: `${(standard.passed / standard.controls) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors">
                <FileText className="w-6 h-6 text-primary-600 mr-3" />
                <div className="text-left">
                  <div className="font-medium text-gray-900">Generate Report</div>
                  <div className="text-sm text-gray-500">For auditors</div>
                </div>
              </button>
              <button className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors">
                <Download className="w-6 h-6 text-primary-600 mr-3" />
                <div className="text-left">
                  <div className="font-medium text-gray-900">Export Evidence</div>
                  <div className="text-sm text-gray-500">All standards</div>
                </div>
              </button>
              <button className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors">
                <CheckCircle className="w-6 h-6 text-primary-600 mr-3" />
                <div className="text-left">
                  <div className="font-medium text-gray-900">Run Self-Assessment</div>
                  <div className="text-sm text-gray-500">Check readiness</div>
                </div>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* GDPR Tab */}
      {activeTab === 'gdpr' && (
        <div className="space-y-6">
          {/* GDPR Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Data Deletion Request
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                Submit a GDPR Article 17 (Right to erasure) request. Data will be
                replaced with cryptographic tombstones.
              </p>
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="User ID"
                  className="input"
                />
                <select className="input">
                  <option value="">Select reason...</option>
                  <option value="consent_withdrawn">Consent withdrawn</option>
                  <option value="unlawful">Unlawful processing</option>
                  <option value="legal_obligation">Legal obligation</option>
                </select>
                <button className="btn-danger w-full flex items-center justify-center">
                  <Trash2 className="w-4 h-4 mr-2" />
                  Request Deletion
                </button>
              </div>
            </div>

            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Data Portability
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                Export user data in a structured format for GDPR Article 20 requests.
              </p>
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="User ID"
                  className="input"
                />
                <select className="input">
                  <option value="json">JSON format</option>
                  <option value="csv">CSV format</option>
                  <option value="xml">XML format</option>
                </select>
                <button className="btn-primary w-full flex items-center justify-center">
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </button>
              </div>
            </div>
          </div>

          {/* Request History */}
          <div className="card">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Recent GDPR Requests
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Request ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      User ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Requested
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Records
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {gdprRequests.map((req) => (
                    <tr key={req.id}>
                      <td className="px-6 py-4 whitespace-nowrap mono text-sm">
                        {req.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {req.userId}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`badge ${
                            req.type === 'deletion'
                              ? 'badge-danger'
                              : 'badge-info'
                          }`}
                        >
                          {req.type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`badge ${
                            req.status === 'completed'
                              ? 'badge-success'
                              : req.status === 'pending'
                              ? 'badge-warning'
                              : 'badge-danger'
                          }`}
                        >
                          {req.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(req.requestedAt)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {req.affectedRecords}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Retention Tab */}
      {activeTab === 'retention' && (
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Data Retention Policy
          </h3>
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Standard Retention
                </label>
                <div className="text-2xl font-semibold text-gray-900">7 years</div>
                <p className="text-sm text-gray-500">
                  Default retention period for audit logs
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  GDPR Retention
                </label>
                <div className="text-2xl font-semibold text-gray-900">90 days</div>
                <p className="text-sm text-gray-500">
                  Tombstone retention after deletion
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Auto-Delete
                </label>
                <div className="text-2xl font-semibold text-danger-600">
                  Disabled
                </div>
                <p className="text-sm text-gray-500">
                  Manual approval required for deletions
                </p>
              </div>
            </div>

            <div className="border-t pt-6">
              <h4 className="text-sm font-medium text-gray-700 mb-4">
                Classification-Based Retention
              </h4>
              <div className="space-y-3">
                {[
                  { classification: 'Public', days: 365, description: 'Non-sensitive data' },
                  { classification: 'Internal', days: 2555, description: 'Standard business data' },
                  { classification: 'Confidential', days: 3650, description: 'Sensitive business data' },
                  { classification: 'Restricted', days: 7300, description: 'Highly sensitive data' },
                ].map((item) => (
                  <div
                    key={item.classification}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <span className="font-medium text-gray-900">
                        {item.classification}
                      </span>
                      <p className="text-sm text-gray-500">{item.description}</p>
                    </div>
                    <div className="text-right">
                      <span className="font-medium text-gray-900">
                        {item.days} days
                      </span>
                      <p className="text-sm text-gray-500">
                        ~{Math.round(item.days / 365)} years
                      </p>
                    </div>
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

export default Compliance
