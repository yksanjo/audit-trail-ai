import { useState } from 'react'
import { Download, FileJson, FileSpreadsheet, FileText, FileCode, File } from 'lucide-react'
import { formatDate, formatFileSize } from '../utils/format'

type ExportFormat = 'json' | 'csv' | 'xlsx' | 'pdf' | 'xml'

interface ExportJob {
  id: string
  format: ExportFormat
  status: 'pending' | 'processing' | 'completed' | 'failed'
  requestedAt: string
  completedAt?: string
  recordCount: number
  fileSize?: number
  checksum?: string
}

function Export() {
  const [format, setFormat] = useState<ExportFormat>('json')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [evidenceLevel, setEvidenceLevel] = useState<'full' | 'summary' | 'hash_only'>('full')
  const [includeDeleted, setIncludeDeleted] = useState(false)
  const [signed, setSigned] = useState(true)

  const [exportJobs] = useState<ExportJob[]>([
    {
      id: 'exp_001',
      format: 'json',
      status: 'completed',
      requestedAt: '2024-01-15T10:00:00Z',
      completedAt: '2024-01-15T10:05:00Z',
      recordCount: 15000,
      fileSize: 2500000,
      checksum: 'sha256:abc123...',
    },
    {
      id: 'exp_002',
      format: 'xlsx',
      status: 'processing',
      requestedAt: '2024-01-16T14:30:00Z',
      recordCount: 50000,
    },
  ])

  const formats: { id: ExportFormat; name: string; icon: typeof FileJson; description: string }[] = [
    { id: 'json', name: 'JSON', icon: FileJson, description: 'Machine-readable format with full metadata' },
    { id: 'csv', name: 'CSV', icon: FileSpreadsheet, description: 'Spreadsheet format for analysis' },
    { id: 'xlsx', name: 'Excel', icon: FileSpreadsheet, description: 'Excel workbook with multiple sheets' },
    { id: 'pdf', name: 'PDF', icon: FileText, description: 'Formatted report for auditors' },
    { id: 'xml', name: 'XML', icon: FileCode, description: 'Structured data format' },
  ]

  const handleExport = () => {
    // Trigger export
    console.log('Exporting...', { format, startDate, endDate, evidenceLevel, includeDeleted, signed })
  }

  const getFormatIcon = (fmt: ExportFormat) => {
    const f = formats.find((f) => f.id === fmt)
    const Icon = f?.icon || File
    return <Icon className="w-5 h-5" />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Export</h1>
        <p className="mt-1 text-sm text-gray-500">
          Export audit logs for compliance audits and analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Export Configuration */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Export Configuration
            </h3>

            {/* Format Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Export Format
              </label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {formats.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => setFormat(f.id)}
                    className={`p-4 border-2 rounded-lg text-center transition-colors ${
                      format === f.id
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <f.icon
                      className={`w-6 h-6 mx-auto mb-2 ${
                        format === f.id ? 'text-primary-600' : 'text-gray-400'
                      }`}
                    />
                    <span
                      className={`text-sm font-medium ${
                        format === f.id ? 'text-primary-900' : 'text-gray-700'
                      }`}
                    >
                      {f.name}
                    </span>
                  </button>
                ))}
              </div>
              <p className="mt-2 text-sm text-gray-500">
                {formats.find((f) => f.id === format)?.description}
              </p>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="input"
                />
              </div>
            </div>

            {/* Evidence Level */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Evidence Level
              </label>
              <select
                value={evidenceLevel}
                onChange={(e) => setEvidenceLevel(e.target.value as typeof evidenceLevel)}
                className="input"
              >
                <option value="full">Full - Complete audit log data</option>
                <option value="summary">Summary - Key fields only</option>
                <option value="hash_only">Hash Only - Verification hashes</option>
              </select>
            </div>

            {/* Options */}
            <div className="space-y-3 mb-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeDeleted}
                  onChange={(e) => setIncludeDeleted(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Include GDPR deleted records (tombstones)
                </span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={signed}
                  onChange={(e) => setSigned(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Cryptographically sign export
                </span>
              </label>
            </div>

            {/* Submit */}
            <button
              onClick={handleExport}
              className="btn-primary w-full flex items-center justify-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Generate Export
            </button>
          </div>

          {/* Compliance Standards */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Compliance Standards
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Select the compliance standards this export should satisfy:
            </p>
            <div className="grid grid-cols-2 gap-3">
              {['SOC2', 'ISO27001', 'GDPR', 'HIPAA', 'PCI DSS', 'CCPA'].map(
                (standard) => (
                  <label key={standard} className="flex items-center">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">{standard}</span>
                  </label>
                )
              )}
            </div>
          </div>
        </div>

        {/* Export History */}
        <div className="lg:col-span-1">
          <div className="card">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Export History</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {exportJobs.map((job) => (
                <div key={job.id} className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      {getFormatIcon(job.format)}
                      <span className="ml-2 font-medium text-gray-900">
                        {job.format.toUpperCase()}
                      </span>
                    </div>
                    <span
                      className={`badge ${
                        job.status === 'completed'
                          ? 'badge-success'
                          : job.status === 'processing'
                          ? 'badge-warning'
                          : job.status === 'pending'
                          ? 'badge-info'
                          : 'badge-danger'
                      }`}
                    >
                      {job.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mb-1">
                    {formatDate(job.requestedAt)}
                  </p>
                  <p className="text-sm text-gray-600">
                    {job.recordCount.toLocaleString()} records
                    {job.fileSize && ` • ${formatFileSize(job.fileSize)}`}
                  </p>
                  {job.status === 'completed' && (
                    <button className="mt-2 text-sm text-primary-600 hover:text-primary-700 font-medium">
                      Download
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Help */}
          <div className="card p-4 bg-blue-50 border-blue-200">
            <h4 className="font-medium text-blue-900 mb-2">Export Guidelines</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Exports include all cryptographic proofs</li>
              <li>• Signed exports include HMAC signature</li>
              <li>• SOC2 exports include control mappings</li>
              <li>• GDPR exports include deletion history</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Export
