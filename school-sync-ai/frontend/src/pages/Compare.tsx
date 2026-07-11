import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import SummaryCards from '../components/SummaryCards'
import Dashboard from '../components/Dashboard'
import ComparisonTable from '../components/ComparisonTable'
import AIChat from '../components/AIChat'
import { compare, getStats } from '../services/api'
import { CompareResult, StatsResult } from '../types'
import { ArrowLeft } from 'lucide-react'

export default function Compare() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [result, setResult] = useState<CompareResult | null>(null)
  const [stats, setStats] = useState<StatsResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!sessionId) return
    Promise.all([
      getStats(sessionId).catch(() => null),
      compare(sessionId),
    ])
      .then(([s, r]) => {
        setStats(s)
        setResult(r)
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-500">Loading...</div>
  if (error) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-red-600">{error}</div>
  if (!result) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link to="/" className="text-gray-500 hover:text-gray-700">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-xl font-bold">Comparison Results</h1>
          <span className="text-xs text-gray-400 font-mono">{sessionId?.slice(0, 8)}</span>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <SummaryCards
          matched={result.matched}
          missing={result.missing}
          modified={result.modified}
          newStudents={result.new}
        />

        {stats && <Dashboard stats={stats} />}

        <ComparisonTable
          modifications={result.modifications}
          newRecords={result.new_records}
          missingRecords={result.missing_records}
        />

        <AIChat sessionId={sessionId || null} />
      </main>
    </div>
  )
}