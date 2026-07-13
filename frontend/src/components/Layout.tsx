import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Upload, GitCompare, FileSpreadsheet, Home, Menu, BarChart3 } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || ''

interface Session {
  session_id: string
  files: string[]
  created: string
}

const navItems = [
  { path: '/', label: 'Upload Files', icon: Upload },
  { path: '/compare', label: 'Compare', icon: GitCompare },
  { path: '/reports', label: 'Reports', icon: FileSpreadsheet },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const [sessions, setSessions] = useState<Session[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    fetch(`${API_BASE}/api/sessions`)
      .then(r => r.json())
      .then(d => setSessions(d.sessions || []))
      .catch(() => {})
  }, [location.pathname])

  const sessionId = location.pathname.split('/')[2]

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/20 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 flex flex-col transform transition-transform duration-200 lg:translate-x-0 lg:static lg:z-auto ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="h-14 flex items-center px-5 border-b border-slate-100">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
              <BarChart3 className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-slate-800">School Sync</span>
          </Link>
        </div>

        <nav className="flex-1 py-3 px-3 space-y-0.5 overflow-y-auto">
          {navItems.map(item => {
            const isActive = item.path === '/' ? location.pathname === '/' : location.pathname.startsWith(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 font-medium'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800'
                }`}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </Link>
            )
          })}

          {sessions.length > 0 && (
            <div className="mt-6">
              <p className="px-3 text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Recent Sessions</p>
              <div className="space-y-0.5">
                {sessions.map(s => {
                  const active = s.session_id === sessionId
                  return (
                    <Link
                      key={s.session_id}
                      to={`/compare/${s.session_id}`}
                      onClick={() => setSidebarOpen(false)}
                      className={`flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                        active ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-slate-300 flex-shrink-0" />
                      <div className="truncate min-w-0 flex-1">
                        <p className="truncate text-xs font-mono">{s.session_id.slice(0, 8)}</p>
                        <p className="text-xs text-slate-400 truncate">{s.created}</p>
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          )}
        </nav>

        <div className="border-t border-slate-100 px-4 py-3 text-center">
          <p className="text-xs text-slate-400">Made by ~Nitik Paswan</p>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 lg:px-6 sticky top-0 z-30">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 -ml-2 text-slate-500 hover:text-slate-700"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1" />
          <Link
            to="/"
            className="text-sm text-slate-500 hover:text-slate-700 flex items-center gap-1.5"
          >
            <Home className="w-4 h-4" />
            <span className="hidden sm:inline">Home</span>
          </Link>
        </header>

        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
