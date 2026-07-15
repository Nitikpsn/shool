import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'

export default function HowToUse() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-1">
        How to Use CTFT
      </h1>
      <p className="text-sm text-neutral-500 mb-10">
        A quick walkthrough of the three steps to compare your school data.
      </p>

      {/* Step 1 */}
      <section className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 text-xs font-bold">
            1
          </span>
          <h2 className="text-base font-semibold text-neutral-900 dark:text-neutral-100">
            Upload Records
          </h2>
        </div>
        <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed ml-8">
          Go to the Upload page and drag-and-drop two Excel files. File 1 is your
          school's internal records (Hindi or English). File 2 is the Government
          portal snapshot you want to compare against. Both formats are supported
          side-by-side.
        </p>
      </section>

      {/* Step 2 */}
      <section className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 text-xs font-bold">
            2
          </span>
          <h2 className="text-base font-semibold text-neutral-900 dark:text-neutral-100">
            AI Schema Sync
          </h2>
        </div>
        <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed ml-8">
          After uploading, click <strong>Compare</strong>. The engine automatically
          matches columns across both files — SC/ST, OBC, RTE, Gender, etc. — even
          when they are named differently or in different languages. No manual
          mapping needed.
        </p>
      </section>

      {/* Step 3 */}
      <section className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 text-xs font-bold">
            3
          </span>
          <h2 className="text-base font-semibold text-neutral-900 dark:text-neutral-100">
            Compare & Chat
          </h2>
        </div>
        <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed ml-8">
          View matched, modified, and missing records. Go to Reports to download a
          multi-sheet CBSE/KVS formatted Excel. Use the AI Chat at the bottom of the
          Compare page to ask questions in English or Hindi — for example: "How many
          SC students are missing?" or "कितने छात्र अनुपस्थित हैं?"
        </p>
      </section>

      {/* Note */}
      <div className="text-xs text-neutral-400 dark:text-neutral-500 border-t border-neutral-200 dark:border-neutral-800 pt-6 mb-8">
        This tool is intended for KV teachers to compare Excel student data. Do not
        upload sensitive or confidential information.
      </div>

      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-neutral-900 dark:text-neutral-100 hover:underline"
      >
        Start Uploading <ArrowRight className="w-4 h-4" />
      </Link>
    </div>
  )
}
