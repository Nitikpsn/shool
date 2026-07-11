import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { generateReport } from '../services/api'
import { ReportResult } from '../types'
import { ArrowLeft, Download, FileSpreadsheet } from 'lucide-react'

export default function Reports() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [report, setReport] = useState<ReportResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!sessionId) return
    setLoading(true)
    setError('')
    try {
      const res = await generateReport(sessionId)
      setReport(res)
    } catch (err: any) {
      setError(err.message)
    }
    setLoading(false)
  }

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link to="/" className="text-gray-500 hover:text-gray-700">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-xl font-bold">CBSE/KVS Report Generator</h1>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl border p-6">
          <div className="flex items-center gap-3 mb-4">
            <FileSpreadsheet className="w-8 h-8 text-green-600" />
            <div>
              <h2 className="font-semibold">Generate Comprehensive Report</h2>
              <p className="text-sm text-gray-500">
                Class-wise strength, category-wise, gender-wise, language medium summary, missing records & mismatch report
              </p>
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Report'}
          </button>

          {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

          {report && (
            <div className="mt-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm font-medium text-green-800">{report.message}</p>
              </div>

              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
                <StatBox label="Total Portal" value={report.summary.total_portal} />
                <StatBox label="Matched" value={report.summary.matched} />
                <StatBox label="New" value={report.summary.new} />
                <StatBox label="Missing" value={report.summary.missing} />
                <StatBox label="Modified" value={report.summary.modified} />
              </div>

              <a
                href={`${API_BASE}${report.download_url}`}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
              >
                <Download className="w-4 h-4" />
                Download Report (Excel)
              </a>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

function StatBox({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white border rounded-lg p-3 text-center">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-lg font-bold">{value}</p>
    </div>
  )
}