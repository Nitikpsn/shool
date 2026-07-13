import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#4f46e5', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899']

export default function Dashboard({ stats }: { stats: any }) {
  if (!stats || !stats.labels || Object.keys(stats.labels).length === 0) {
    return (
      <div className="card p-8 text-center mt-4">
        <p className="text-sm text-neutral-400">No stats</p>
      </div>
    )
  }

  const entries = Object.entries(stats.labels).filter(([, v]) => (v as number) > 0) as [string, number][]
  const total = entries.reduce((a, [, v]) => a + v, 0)

  const data = entries.map(([name, value]) => ({ name, value }))
  const isSmall = entries.length <= 2

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
      <div className="card">
        <div className="px-4 py-3 border-b border-neutral-100 dark:border-neutral-800">
          <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Distribution</h3>
        </div>
        <div className="p-4">
          <ResponsiveContainer width="100%" height={260}>
            {isSmall ? (
              <PieChart>
                <Pie data={data} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                  {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
              </PieChart>
            ) : (
              <BarChart data={data}>
                <Tooltip />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Bar dataKey="value" fill="#4f46e5" radius={[3, 3, 0, 0]} />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="px-4 py-3 border-b border-neutral-100 dark:border-neutral-800">
          <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Summary</h3>
        </div>
        <div className="p-4 space-y-3">
          {entries.map(([key, value], i) => {
            const pct = total > 0 ? ((value / total) * 100).toFixed(1) : '0'
            return (
              <div key={key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-neutral-600 dark:text-neutral-400 capitalize">{key}</span>
                  <span className="font-medium text-neutral-800 dark:text-neutral-200">
                    {value.toLocaleString()} ({pct}%)
                  </span>
                </div>
                <div className="h-1.5 bg-neutral-100 dark:bg-neutral-800 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: COLORS[i % COLORS.length] }} />
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
