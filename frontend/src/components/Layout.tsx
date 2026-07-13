import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Upload, GitCompare, FileSpreadsheet, Menu, LayoutDashboard, Moon, Sun, X } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || ''

const navItems = [
  { path: '/', label: 'Upload', icon: Upload },
  { path: '/compare', label: 'Compare', icon: GitCompare },
  { path: '/reports', label: 'Reports', icon: FileSpreadsheet },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const [sessions, setSessions] = useState<any[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [dark, setDark] = useState(() => localStorage.getItem('theme') === 'dark')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  useEffect(() => {
    fetch(`${API_BASE}/api/sessions`)
      .then(r => r.json())
      .then(d => setSessions(d.sessions || []))
      .catch(() => {})
  }, [location.pathname])

  useEffect(() => { setSidebarOpen(false) }, [location.pathname])

  const sessionId = location.pathname.split('/')[2]

  const sidebarClass = sidebarOpen ? 'translate-x-0' : '-translate-x-full'

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-[#1a1a1a] flex">
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/40 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      <aside className={`fixed inset-y-0 left-0 z-50 w-60 bg-white dark:bg-[#222] border-r border-neutral-200 dark:border-neutral-800 flex flex-col transform transition-transform lg:translate-x-0 lg:static lg:z-auto ${sidebarClass}`}>
        <div className="h-12 flex items-center px-4 border-b border-neutral-100 dark:border-neutral-800">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-neutral-900 dark:bg-neutral-100 flex items-center justify-center">
              <LayoutDashboard className="w-4 h-4 text-white dark:text-neutral-900" />
            </div>
            <span className="font-semibold text-neutral-800 dark:text-neutral-200">DataSync</span>
          </Link>
          <button onClick={() => setSidebarOpen(false)} className="ml-auto lg:hidden p-1 text-neutral-400">
            <X className="w-4 h-4" />
          </button>
        </div>

        <nav className="flex-1 py-2 px-2 space-y-0.5 overflow-y-auto">
          {navItems.map(item => {
            const isActive = item.path === '/' ? location.pathname === '/' : location.pathname.startsWith(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2.5 px-3 py-2 text-sm rounded-md ${
                  isActive
                    ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 font-medium'
                    : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/50'
                }`}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </Link>
            )
          })}

          {sessions.length > 0 && (
            <div className="mt-6">
              <p className="px-3 text-xs font-medium text-neutral-400 dark:text-neutral-500 mb-1">
                Recent Sessions
              </p>
              {sessions.map(s => {
                const active = s.session_id === sessionId
                return (
                  <Link
                    key={s.session_id}
                    to={`/compare/${s.session_id}`}
                    className={`flex items-center gap-2.5 px-3 py-2 text-sm rounded-md ${
                      active
                        ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100'
                        : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/50'
                    }`}
                  >
                    <div className={`w-1.5 h-1.5 rounded-full ${active ? 'bg-neutral-900 dark:bg-neutral-100' : 'bg-neutral-300 dark:bg-neutral-600'}`} />
                    <div className="truncate">
                      <p className="text-xs font-mono truncate">{s.session_id.slice(0, 8)}</p>
                      <p className="text-xs text-neutral-400 dark:text-neutral-500 truncate">{s.created}</p>
                    </div>
                  </Link>
                )
              })}
            </div>
          )}
        </nav>

        <div className="border-t border-neutral-100 dark:border-neutral-800 px-4 py-3 text-center">
          <p className="text-xs text-neutral-400">Made by <a href="https://github.com/Nitikpsn" target="_blank" rel="noopener noreferrer" className="text-neutral-600 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-neutral-100 underline underline-offset-2">Nitik Paswan</a></p>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-12 bg-white dark:bg-[#222] border-b border-neutral-200 dark:border-neutral-800 flex items-center px-4 lg:px-6 sticky top-0 z-30">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden p-1.5 -ml-1.5 text-neutral-500 dark:text-neutral-400">
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1" />
          <button onClick={() => setDark(!dark)} className="p-1.5 text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-300">
            {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </header>

        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
