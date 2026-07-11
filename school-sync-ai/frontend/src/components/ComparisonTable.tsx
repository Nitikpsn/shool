import { useMemo, useState } from 'react'
import { Modification, StudentRecord } from '../types'

interface ComparisonTableProps {
  modifications: Modification[]
  newRecords: StudentRecord[]
  missingRecords: StudentRecord[]
}

type Tab = 'modified' | 'new' | 'missing'

export default function ComparisonTable({ modifications, newRecords, missingRecords }: ComparisonTableProps) {
  const [tab, setTab] = useState<Tab>('modified')

  const tabs = [
    { key: 'modified' as Tab, label: 'Modified', count: modifications.length },
    { key: 'new' as Tab, label: 'New Students', count: newRecords.length },
    { key: 'missing' as Tab, label: 'Missing', count: missingRecords.length },
  ]

  return (
    <div className="mt-6 bg-white rounded-xl border">
      <div className="border-b flex">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              tab === t.key ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label} ({t.count})
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        {tab === 'modified' && <ModificationsTable data={modifications} />}
        {tab === 'new' && <SimpleTable records={newRecords} />}
        {tab === 'missing' && <SimpleTable records={missingRecords} />}
      </div>
    </div>
  )
}

function ModificationsTable({ data }: { data: Modification[] }) {
  if (!data.length) return <p className="p-4 text-gray-500 text-sm">No modifications found</p>

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b bg-gray-50">
          <th className="text-left px-4 py-2 font-medium text-gray-600">Admission No</th>
          <th className="text-left px-4 py-2 font-medium text-gray-600">Student</th>
          <th className="text-left px-4 py-2 font-medium text-gray-600">Field</th>
          <th className="text-left px-4 py-2 font-medium text-gray-600">Old Value</th>
          <th className="text-left px-4 py-2 font-medium text-gray-600">New Value</th>
        </tr>
      </thead>
      <tbody>
        {data.map((m, i) => (
          <tr key={i} className="border-b hover:bg-gray-50">
            <td className="px-4 py-2 font-mono">{m.admission_no}</td>
            <td className="px-4 py-2">{m.student_name}</td>
            <td className="px-4 py-2">
              <span className="bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded text-xs">{m.field_name}</span>
            </td>
            <td className="px-4 py-2 text-red-600">{m.old_value || '—'}</td>
            <td className="px-4 py-2 text-green-600">{m.new_value || '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function SimpleTable({ records }: { records: StudentRecord[] }) {
  if (!records.length) return <p className="p-4 text-gray-500 text-sm">No records</p>

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b bg-gray-50">
          <th className="text-left px-4 py-2 font-medium text-gray-600">Admission No</th>
          <th className="text-left px-4 py-2 font-medium text-gray-600">Name</th>
          <th className="text-left px-4 py-2 font-medium text-gray-600">Class</th>
          <th className="text-left px-4 py-2 font-medium text-gray-600">Gender</th>
          <th className="text-left px-4 py-2 font-medium text-gray-600">Category</th>
        </tr>
      </thead>
      <tbody>
        {records.map((r, i) => (
          <tr key={i} className="border-b hover:bg-gray-50">
            <td className="px-4 py-2 font-mono">{r.admission_no}</td>
            <td className="px-4 py-2">{r.student_name}</td>
            <td className="px-4 py-2">{r.class_name}</td>
            <td className="px-4 py-2">{r.gender}</td>
            <td className="px-4 py-2">{r.category}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}