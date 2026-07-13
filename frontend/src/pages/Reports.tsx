import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { generateReport } from '../services/api'
import { ArrowLeft, Download, FileSpreadsheet, CheckCircle2, BarChart3 } from 'lucide-react'

export default function Reports() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [report, setReport] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const API_BASE = import.meta.env.VITE_API_URL || ''

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

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      <div className="flex items-center gap-3">
        <Link to="/" className="p-1 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300"><ArrowLeft className="w-5 h-5" /></Link>
        <div>
          <h1 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Report</h1>
          <p className="text-xs text-neutral-400 font-mono">{sessionId?.slice(0, 8)}</p>
        </div>
        <div className="flex-1" />
        {sessionId && (
          <Link to={`/compare/${sessionId}`} className="btn-secondary text-sm">
            <BarChart3 className="w-3.5 h-3.5" /> Compare
          </Link>
        )}
      </div>

      <div className="card">
        <div className="p-4">
          <div className="flex items-start gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center flex-shrink-0">
              <FileSpreadsheet className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <h2 className="text-sm font-medium text-neutral-900 dark:text-neutral-100">Generate Summary Report</h2>
              <p className="text-sm text-neutral-500 mt-0.5">Export matching details and statistics as Excel</p>
            </div>
          </div>

          <button onClick={handleGenerate} disabled={loading} className="btn-primary">
            {loading ? (
              <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating...</>
            ) : (
              <><FileSpreadsheet className="w-4 h-4" /> Generate Report</>
            )}
          </button>

          {error && (
            <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400">{error}</div>
          )}
        </div>
      </div>

      {report && (
        <div className="card">
          <div className="px-4 py-3 border-b border-neutral-100 dark:border-neutral-800">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span className="text-sm font-medium text-emerald-700 dark:text-emerald-400">{report.message}</span>
            </div>
          </div>
          <div className="p-4">
            <div className="grid grid-cols-5 gap-2 mb-4">
              {Object.entries(report.summary).map(([k, v]) => (
                <div key={k} className="bg-neutral-50 dark:bg-neutral-800/50 rounded-lg p-3 text-center">
                  <p className="text-xs text-neutral-400 capitalize">{k.replace('_', ' ')}</p>
                  <p className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">{v as number}</p>
                </div>
              ))}
            </div>
            <a href={`${API_BASE}${report.download_url}`} className="btn-primary inline-flex">
              <Download className="w-4 h-4" /> Download
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
