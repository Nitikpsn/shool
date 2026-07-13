import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import SummaryCards from '../components/SummaryCards'
import Dashboard from '../components/Dashboard'
import ComparisonTable from '../components/ComparisonTable'
import AIChat from '../components/AIChat'
import { compare, getStats } from '../services/api'
import { ArrowLeft, BarChart3 } from 'lucide-react'

export default function Compare() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [result, setResult] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!sessionId) return
    setLoading(true)
    Promise.all([
      getStats(sessionId).catch(() => null),
      compare(sessionId),
    ])
      .then(([s, r]) => { setStats(s); setResult(r) })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="w-6 h-6 border-2 border-neutral-300 border-t-neutral-600 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-neutral-400">Comparing...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto py-16 text-center">
        <div className="card p-6">
          <p className="text-sm text-red-600 dark:text-red-400 mb-3">{error}</p>
          <Link to="/" className="btn-primary"><ArrowLeft className="w-4 h-4" /> Back</Link>
        </div>
      </div>
    )
  }

  if (!result) return null

  return (
    <div className="max-w-6xl mx-auto space-y-5">
      <div className="flex items-center gap-3">
        <Link to="/" className="p-1 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300"><ArrowLeft className="w-5 h-5" /></Link>
        <div>
          <h1 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Comparison</h1>
          <p className="text-xs text-neutral-400 font-mono">{sessionId?.slice(0, 8)}</p>
        </div>
        <div className="flex-1" />
        <Link to={`/reports/${sessionId}`} className="btn-secondary text-sm">
          <ArrowLeft className="w-3.5 h-3.5 rotate-180" /> Report
        </Link>
      </div>

      <SummaryCards matched={result.matched} missing={result.missing} modified={result.modified} newStudents={result.new} />
      {stats && <Dashboard stats={stats} />}
      <ComparisonTable modifications={result.modifications} newRecords={result.new_records} missingRecords={result.missing_records} />
      <AIChat sessionId={sessionId || null} />
    </div>
  )
}
