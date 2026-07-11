import { ArrowUp, ArrowDown, Minus } from 'lucide-react'

interface SummaryCardsProps {
  matched: number
  missing: number
  modified: number
  newStudents: number
}

export default function SummaryCards({ matched, missing, modified, newStudents }: SummaryCardsProps) {
  const cards = [
    { label: 'Matched', value: matched, icon: Users, color: 'bg-green-50 text-green-700 border-green-200' },
    { label: 'Missing', value: missing, icon: ArrowDown, color: 'bg-red-50 text-red-700 border-red-200' },
    { label: 'Modified', value: modified, icon: ArrowUpRight, color: 'bg-yellow-50 text-yellow-700 border-yellow-200' },
    { label: 'New', value: newStudents, icon: ArrowUp, color: 'bg-blue-50 text-blue-700 border-blue-200' },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((c) => (
        <div key={c.label} className={`rounded-xl border p-4 ${c.color}`}>
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">{c.label}</p>
            <c.icon className="h-5 w-5 opacity-70" />
          </div>
          <p className="text-3xl font-bold mt-2">{c.value.toLocaleString()}</p>
        </div>
      ))}
    </div>
  )
}

function Users(props: any) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  )
}