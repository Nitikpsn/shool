import { Link } from 'react-router-dom'
import { Upload, GitCompare, FileSpreadsheet, MessageSquare, AlertTriangle, ArrowRight, CheckCircle2 } from 'lucide-react'

const steps = [
  {
    icon: Upload,
    title: 'Upload Excel Files',
    description: 'Go to the Upload page and drag-and-drop (or click to select) two Excel files:',
    details: [
      'File 1 — Your school student data (e.g. admission register, class list)',
      'File 2 — The portal data you want to compare against',
    ],
    color: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
  },
  {
    icon: GitCompare,
    title: 'Compare Records',
    description: 'After uploading, click "Compare" to see the differences between both files.',
    details: [
      'Matched — Students found in both files with identical data',
      'Modified — Students found in both files but with differences',
      'Missing — Students in File 1 but not in File 2',
      'New — Students in File 2 but not in File 1',
    ],
    color: 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400',
  },
  {
    icon: FileSpreadsheet,
    title: 'Category Summary',
    description: 'Switch to the "Category Summary" tab for a breakdown by gender, category, and other fields.',
    details: [
      'View category-wise counts for both files side by side',
      'Identify mismatches in category distribution',
    ],
    color: 'bg-violet-50 dark:bg-violet-900/20 text-violet-600 dark:text-violet-400',
  },
  {
    icon: MessageSquare,
    title: 'AI Chat',
    description: 'Use the AI Chat at the bottom of the Compare page to ask questions in plain English or Hindi.',
    details: [
      'e.g. "How many SC students are missing?"',
      'e.g. "Show me all modified records for Class 10"',
      'e.g. "कितने छात्र अनुपस्थित हैं?"',
    ],
    color: 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400',
  },
  {
    icon: FileSpreadsheet,
    title: 'Generate Report',
    description: 'Go to the Reports page to generate and download a detailed Excel report.',
    details: [
      'Click "Generate Report" to create the summary',
      'Download the Excel file with all comparison details',
    ],
    color: 'bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400',
  },
]

export default function HowToUse() {
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">How to Use</h1>
        <p className="text-sm text-neutral-500 mt-1">A step-by-step guide for KV teachers</p>
      </div>

      <div className="card border border-amber-200 dark:border-amber-800/30 bg-amber-50 dark:bg-amber-900/10">
        <div className="p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-amber-800 dark:text-amber-300">Disclaimer</p>
            <p className="text-xs text-amber-700 dark:text-amber-400 mt-0.5">
              This app is only for KV teachers for comparing Excel student data. Do not upload sensitive or confidential data.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={index} className="card">
            <div className="p-5">
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${step.color}`}>
                  <step.icon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-neutral-400 dark:text-neutral-500">Step {index + 1}</span>
                  </div>
                  <h3 className="text-sm font-semibold text-neutral-900 dark:text-neutral-100 mb-1">{step.title}</h3>
                  <p className="text-sm text-neutral-500 dark:text-neutral-400 mb-3">{step.description}</p>
                  <ul className="space-y-1.5">
                    {step.details.map((detail, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs text-neutral-600 dark:text-neutral-400">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mt-0.5 flex-shrink-0" />
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="text-center pt-4 pb-8">
        <Link to="/" className="btn-primary inline-flex">
          <Upload className="w-4 h-4" /> Start Uploading <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  )
}
