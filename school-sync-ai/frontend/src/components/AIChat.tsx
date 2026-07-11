import { useState } from 'react'
import { Send, Bot } from 'lucide-react'
import { chatQuery } from '../services/api'
import { StudentRecord } from '../types'

interface AIChatProps {
  sessionId: string | null
}

export default function AIChat({ sessionId }: AIChatProps) {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<{
    original_query: string
    normalized_query: string
    filter_applied: Record<string, string>
    total_records: number
    records: StudentRecord[]
  } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!sessionId || !query.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await chatQuery(sessionId, query)
      setResult(res)
    } catch (err: any) {
      setError(err.message)
    }
    setLoading(false)
  }

  return (
    <div className="mt-6 bg-white rounded-xl border">
      <div className="p-4 border-b">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold">AI Query Assistant</h3>
        </div>
        <p className="text-xs text-gray-500 mt-1">Ask in natural language or Hindi — e.g., "Show SC girls in class 6"</p>
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-b flex gap-2">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Type your query..."
          className="flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={!sessionId}
        />
        <button
          type="submit"
          disabled={loading || !sessionId}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center gap-1"
        >
          {loading ? '...' : <Send className="w-4 h-4" />}
          Ask
        </button>
      </form>

      {error && <p className="p-4 text-sm text-red-600">{error}</p>}

      {result && (
        <div className="p-4">
          <div className="flex gap-4 text-sm text-gray-600 mb-3">
            <span>Normalized: <strong>{result.normalized_query}</strong></span>
            <span>Filter: <strong>{JSON.stringify(result.filter_applied)}</strong></span>
            <span>Results: <strong>{result.total_records}</strong></span>
          </div>

          {result.records.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-left px-3 py-2 font-medium">Admission</th>
                  <th className="text-left px-3 py-2 font-medium">Name</th>
                  <th className="text-left px-3 py-2 font-medium">Class</th>
                  <th className="text-left px-3 py-2 font-medium">Gender</th>
                  <th className="text-left px-3 py-2 font-medium">Category</th>
                </tr>
              </thead>
              <tbody>
                {result.records.map((r, i) => (
                  <tr key={i} className="border-b hover:bg-gray-50">
                    <td className="px-3 py-2 font-mono">{r.admission_no}</td>
                    <td className="px-3 py-2">{r.student_name}</td>
                    <td className="px-3 py-2">{r.class_name}</td>
                    <td className="px-3 py-2">{r.gender}</td>
                    <td className="px-3 py-2">{r.category}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-gray-500">No matching records found</p>
          )}
        </div>
      )}
    </div>
  )
}