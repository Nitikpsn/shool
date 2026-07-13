import type { CategoryCompareResult } from '../types'
import { AlertTriangle, Info, ArrowUpDown } from 'lucide-react'

function DeltaBadge({ value }: { value: number }) {
  if (value === 0) return <span className="text-xs text-neutral-400">—</span>
  if (value > 0) return <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">+{value}</span>
  return <span className="text-xs font-medium text-red-600 dark:text-red-400">{value}</span>
}

function classDisplay(cls: string | number) {
  const prePrimary: Record<string, string> = { '-2': 'Nursery', '-1': 'LKG/Pre-primary', '0': 'UKG' }
  return prePrimary[String(cls)] || `Class ${cls}`
}

export default function CategoryComparison({ result }: { result: CategoryCompareResult }) {
  const { class_diffs, summary, flags, school_meta, govt_meta } = result

  return (
    <div className="space-y-5">
      {flags.map((f, i) => (
        <div key={i} className="flex items-start gap-2.5 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
          <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-amber-700 dark:text-amber-300">{f.message}</p>
        </div>
      ))}

      {school_meta.consistency_checks.length > 0 && (
        <div className="flex items-start gap-2.5 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-700 dark:text-blue-300">
            <p className="font-medium mb-1">Internal data gaps found in school file:</p>
            {school_meta.consistency_checks.map((c, i) => (
              <p key={i} className="text-xs">
                Class {classDisplay(c.class)}: category sum ({c.category_sum}) ≠ total ({c.students_total}), gap = {c.gap > 0 ? '+' : ''}{c.gap}
              </p>
            ))}
          </div>
        </div>
      )}

      {govt_meta.consistency_checks.length > 0 && (
        <div className="flex items-start gap-2.5 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-700 dark:text-blue-300">
            <p className="font-medium mb-1">Internal data gaps found in portal file:</p>
            {govt_meta.consistency_checks.map((c, i) => (
              <p key={i} className="text-xs">
                Class {classDisplay(c.class)}: category sum ({c.category_sum}) ≠ total ({c.students_total}), gap = {c.gap > 0 ? '+' : ''}{c.gap}
              </p>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-neutral-50 dark:bg-neutral-800/50 rounded-lg p-3">
          <p className="text-[10px] text-neutral-400 mb-0.5">Classes</p>
          <p className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">{summary.total_classes}</p>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-800/50 rounded-lg p-3">
          <p className="text-[10px] text-neutral-400 mb-0.5">Reclassifications</p>
          <p className="text-lg font-semibold text-amber-600 dark:text-amber-400">{summary.total_reclassifications}</p>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-800/50 rounded-lg p-3">
          <p className="text-[10px] text-neutral-400 mb-0.5">School total</p>
          <p className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">{summary.total_students_school.toLocaleString()}</p>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-800/50 rounded-lg p-3">
          <p className="text-[10px] text-neutral-400 mb-0.5">Portal total</p>
          <p className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">{summary.total_students_govt.toLocaleString()}</p>
        </div>
      </div>

      {school_meta.has_gender_split && (
        <p className="text-xs text-neutral-500 dark:text-neutral-400 italic">
          School file has gender-split sub-columns — they have been summed for comparison.
        </p>
      )}
      {govt_meta.has_gender_split && (
        <p className="text-xs text-neutral-500 dark:text-neutral-400 italic">
          Portal file has gender-split sub-columns — they have been summed for comparison.
        </p>
      )}

      <div className="overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-neutral-50 dark:bg-neutral-800/50">
              <th className="text-left px-3 py-2 text-[10px] font-medium text-neutral-400 uppercase tracking-wider">Class</th>
              <th className="text-left px-3 py-2 text-[10px] font-medium text-neutral-400 uppercase tracking-wider">Students</th>
              <th className="text-left px-3 py-2 text-[10px] font-medium text-neutral-400 uppercase tracking-wider">
                <span className="flex items-center gap-1"><ArrowUpDown className="w-3 h-3" /> Net Δ</span>
              </th>
              <th className="text-left px-3 py-2 text-[10px] font-medium text-neutral-400 uppercase tracking-wider">Reclass?</th>
              {class_diffs.length > 0 && Object.keys(class_diffs[0].deltas).map(cat => (
                <th key={cat} className="text-right px-2 py-2 text-[10px] font-medium text-neutral-400 uppercase tracking-wider">
                  {cat.replace('_', ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800">
            {class_diffs.map(cd => (
              <tr key={String(cd.class)} className="hover:bg-neutral-50 dark:hover:bg-neutral-800/30">
                <td className="px-3 py-2 text-xs font-medium text-neutral-800 dark:text-neutral-200">
                  {classDisplay(cd.class)}
                </td>
                <td className="px-3 py-2 text-xs text-neutral-600 dark:text-neutral-400">
                  {cd.school_total_students} → {cd.govt_total_students}
                </td>
                <td className="px-3 py-2">
                  <DeltaBadge value={cd.students_delta} />
                </td>
                <td className="px-3 py-2 text-xs">
                  {cd.is_reclassification ? (
                    <span className="text-amber-600 dark:text-amber-400 font-medium">
                      {(cd.reclassification_score * 100).toFixed(0)}%
                    </span>
                  ) : (
                    <span className="text-neutral-300 dark:text-neutral-600">—</span>
                  )}
                </td>
                {Object.entries(cd.deltas).map(([cat, val]) => (
                  <td key={cat} className="text-right px-2 py-2">
                    <DeltaBadge value={val} />
                    <div className="text-[9px] text-neutral-400 dark:text-neutral-500">
                      {cd.school_totals[cat]}→{cd.govt_totals[cat]}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
