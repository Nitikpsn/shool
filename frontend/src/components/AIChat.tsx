import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User } from 'lucide-react'
import { chatQuery } from '../services/api'

export default function AIChat({ sessionId }: { sessionId: string | null }) {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => { bottomRef.current?.scrollIntoView() }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!sessionId || !query.trim() || loading) return
    const q = query
    setQuery('')
    setMessages(m => [...m, { role: 'user', text: q }])
    setLoading(true)
    setError('')
    try {
      const res = await chatQuery(sessionId, q)
      setMessages(m => [...m, { role: 'assistant', text: res.normalized_query, data: res }])
    } catch (err: any) {
      setError(err.message)
    }
    setLoading(false)
  }

  return (
    <div className="mt-4 card">
      <div className="px-4 py-3 border-b border-neutral-100 dark:border-neutral-800">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-neutral-700 dark:text-neutral-300" />
          <h3 className="text-sm font-medium text-neutral-900 dark:text-neutral-100">AI Query</h3>
        </div>
      </div>

      <div className="max-h-72 overflow-y-auto px-4 py-3 space-y-3">
        {messages.length === 0 && !error && (
          <p className="text-xs text-neutral-400 text-center py-6">Ask something like "show records where value is X"</p>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {msg.role === 'assistant' && <Bot className="w-6 h-6 p-1 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 flex-shrink-0" />}
            <div className={`max-w-[75%] ${msg.role === 'user' ? 'order-1' : ''}`}>
              {msg.role === 'user' ? (
                <div className="bg-neutral-800 dark:bg-neutral-200 text-white dark:text-neutral-800 text-sm rounded-lg px-3 py-2">{msg.text}</div>
              ) : (
                <div className="bg-neutral-50 dark:bg-neutral-800 border border-neutral-100 dark:border-neutral-700 rounded-lg px-3 py-2 text-sm">
                  <p className="text-neutral-600 dark:text-neutral-400 italic text-xs mb-1">Normalized: <span className="not-italic font-medium text-neutral-800 dark:text-neutral-200">{msg.text}</span></p>
                  {msg.data && (
                    <>
                      <div className="flex flex-wrap gap-1.5 mb-1">
                        {Object.entries(msg.data.filter_applied || {}).map(([k, v]) => (
                          <span key={k} className="px-2 py-0.5 rounded text-xs font-medium bg-neutral-100 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-400">{k}: {v as string}</span>
                        ))}
                      </div>
                      <p className="text-xs text-neutral-500">{msg.data.total_records} records</p>
                      {msg.data.records?.length > 0 && (
                        <details className="mt-1">
                          <summary className="text-xs text-neutral-500 cursor-pointer hover:text-neutral-700 dark:hover:text-neutral-300">View results</summary>
                          <div className="mt-1 overflow-x-auto text-xs">
                            <table className="w-full">
                              <thead>
                                <tr className="border-b border-neutral-200 dark:border-neutral-700">
                                  {Object.keys(msg.data.records[0]).map(k => <th key={k} className="text-left px-2 py-1 font-medium text-neutral-500">{k}</th>)}
                                </tr>
                              </thead>
                              <tbody>
                                {msg.data.records.slice(0, 10).map((r: any, idx: number) => (
                                  <tr key={idx} className="border-b border-neutral-50 dark:border-neutral-800/50">
                                    {Object.keys(msg.data.records[0]).map(k => <td key={k} className="px-2 py-1 text-neutral-700 dark:text-neutral-300">{r[k] || '—'}</td>)}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                            {msg.data.records.length > 10 && <p className="text-xs text-neutral-400 mt-1">Showing 10 of {msg.data.records.length}</p>}
                          </div>
                        </details>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>
            {msg.role === 'user' && <User className="w-6 h-6 p-1 rounded-full bg-neutral-200 dark:bg-neutral-700 text-neutral-500 flex-shrink-0" />}
          </div>
        ))}

        {loading && (
          <div className="flex gap-2">
            <Bot className="w-6 h-6 p-1 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 flex-shrink-0" />
            <div className="bg-neutral-50 dark:bg-neutral-800 border border-neutral-100 dark:border-neutral-700 rounded-lg px-3 py-2">
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-neutral-300 dark:bg-neutral-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-1.5 h-1.5 bg-neutral-300 dark:bg-neutral-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-1.5 h-1.5 bg-neutral-300 dark:bg-neutral-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="px-4 py-3 border-t border-neutral-100 dark:border-neutral-800">
        <div className="flex gap-2">
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder='e.g. "Show records with X"'
            disabled={!sessionId}
            className="flex-1 px-3 py-1.5 text-sm border border-neutral-200 dark:border-neutral-700 rounded-md bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-neutral-400"
          />
          <button type="submit" disabled={loading || !sessionId || !query.trim()} className="btn-primary">
            {loading ? <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            Ask
          </button>
        </div>
      </form>
    </div>
  )
}
