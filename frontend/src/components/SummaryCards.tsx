import { CheckCircle2, ArrowDown, ArrowUpRight, Sparkles } from 'lucide-react'

export default function SummaryCards({ matched, missing, modified, newStudents }: any) {
  const items = [
    { label: 'Matched', value: matched, icon: CheckCircle2, color: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-900/20', bar: 'bg-emerald-500' },
    { label: 'Missing', value: missing, icon: ArrowDown, color: 'text-red-600 dark:text-red-400', bg: 'bg-red-50 dark:bg-red-900/20', bar: 'bg-red-500' },
    { label: 'Modified', value: modified, icon: ArrowUpRight, color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-900/20', bar: 'bg-amber-500' },
    { label: 'New', value: newStudents, icon: Sparkles, color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-900/20', bar: 'bg-blue-500' },
  ]

  const total = matched + missing + modified + newStudents

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {items.map(item => (
        <div key={item.label} className={`${item.bg} border border-neutral-200 dark:border-neutral-800 rounded-lg p-4`}>
          <div className="flex items-center justify-between mb-1">
            <span className={`text-xs font-medium ${item.color}`}>{item.label}</span>
            <item.icon className={`w-4 h-4 ${item.color}`} />
          </div>
          <p className="text-xl font-bold text-neutral-900 dark:text-neutral-100">{item.value.toLocaleString()}</p>
          <div className="mt-2 h-1 bg-neutral-200/50 dark:bg-neutral-700/50 rounded-full overflow-hidden">
            <div className={`h-full rounded-full ${item.bar}`} style={{ width: `${total > 0 ? (item.value / total) * 100 : 0}%` }} />
          </div>
        </div>
      ))}
    </div>
  )
}
