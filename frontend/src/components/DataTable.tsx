import { useState, useMemo } from 'react'
import { Search, ArrowUpDown } from 'lucide-react'

export default function DataTable({ columns, data, pageSize = 50, emptyMessage = 'No records' }: {
  columns: { key: string; label: string; render?: (v: string, row: any) => any }[]
  data: any[]
  pageSize?: number
  emptyMessage?: string
}) {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortAsc, setSortAsc] = useState(true)
  const [page, setPage] = useState(0)

  const filtered = useMemo(() => {
    let list = [...data]
    if (search) {
      const q = search.toLowerCase()
      list = list.filter(row => columns.some(col => String(row[col.key] || '').toLowerCase().includes(q)))
    }
    if (sortKey) {
      list.sort((a, b) => {
        const av = (a[sortKey] || '').toLowerCase()
        const bv = (b[sortKey] || '').toLowerCase()
        return sortAsc ? av.localeCompare(bv) : bv.localeCompare(av)
      })
    }
    return list
  }, [data, search, sortKey, sortAsc])

  const totalPages = Math.ceil(filtered.length / pageSize)
  const paged = filtered.slice(page * pageSize, (page + 1) * pageSize)

  if (!data.length) {
    return <div className="card py-10 text-center"><p className="text-sm text-neutral-400">{emptyMessage}</p></div>
  }

  return (
    <div className="card">
      <div className="px-4 py-3 border-b border-neutral-100 dark:border-neutral-800">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0) }}
            placeholder="Search..."
            className="w-full pl-9 pr-3 py-1.5 text-sm border border-neutral-200 dark:border-neutral-700 rounded-md bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-neutral-400"
          />
        </div>
        <p className="text-xs text-neutral-400 mt-1.5">{filtered.length} of {data.length} records</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/50">
              {columns.map(col => (
                <th
                  key={col.key}
                  className="text-left px-4 py-2.5 font-medium text-neutral-500 dark:text-neutral-400 text-xs uppercase tracking-wider cursor-pointer select-none hover:text-neutral-700 dark:hover:text-neutral-300"
                  onClick={() => {
                    if (sortKey === col.key) setSortAsc(!sortAsc)
                    else { setSortKey(col.key); setSortAsc(true) }
                  }}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.label}
                    <ArrowUpDown className={`w-3 h-3 ${sortKey === col.key ? 'text-neutral-700 dark:text-neutral-300' : 'opacity-30'}`} />
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paged.map((row, i) => (
              <tr key={i} className="border-b border-neutral-50 dark:border-neutral-800/50 hover:bg-neutral-50 dark:hover:bg-neutral-800/30">
                {columns.map(col => (
                  <td key={col.key} className="px-4 py-2 text-neutral-700 dark:text-neutral-300">
                    {col.render ? col.render(row[col.key] || '', row) : row[col.key] || '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="px-4 py-2.5 border-t border-neutral-100 dark:border-neutral-800 flex items-center justify-between text-xs text-neutral-400">
          <span>Page {page + 1} of {totalPages}</span>
          <div className="flex gap-1">
            <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="btn-secondary !px-3 !py-1 !text-xs">Prev</button>
            <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} className="btn-secondary !px-3 !py-1 !text-xs">Next</button>
          </div>
        </div>
      )}
    </div>
  )
}
