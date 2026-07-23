import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'

export default function HowToUse() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-notion-text-primary dark:text-notion-text-primary-dark mb-1 tracking-tight">
        How to Use CTFT
      </h1>
      <p className="text-sm text-notion-text-secondary mb-10 leading-relaxed">
        Three steps to find every mismatch between your school data and the portal.
      </p>

      <section className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded bg-notion-text-primary dark:bg-white text-white dark:text-notion-bg-dark text-xs font-bold">
            1
          </span>
          <h2 className="text-base font-semibold text-notion-text-primary dark:text-notion-text-primary-dark">
            Upload your files
          </h2>
        </div>
        <p className="text-sm text-notion-text-secondary leading-relaxed ml-8">
          Drag and drop two Excel files onto the upload zone. The first file is your
          school's internal records (Hindi or English columns are fine). The second
          is the government portal snapshot you want to compare against. Both
          languages and formats are handled side-by-side.
        </p>
      </section>

      <section className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded bg-notion-text-primary dark:bg-white text-white dark:text-notion-bg-dark text-xs font-bold">
            2
          </span>
          <h2 className="text-base font-semibold text-notion-text-primary dark:text-notion-text-primary-dark">
            Let AI map your columns
          </h2>
        </div>
        <p className="text-sm text-notion-text-secondary leading-relaxed ml-8">
          Hit <strong>Compare</strong> and the engine automatically matches columns
          across both files, even when they are named differently or in different
          languages. No manual renaming needed. Names are fuzzy-matched to handle
          spelling differences between the two sources.
        </p>
      </section>

      <section className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded bg-notion-text-primary dark:bg-white text-white dark:text-notion-bg-dark text-xs font-bold">
            3
          </span>
          <h2 className="text-base font-semibold text-notion-text-primary dark:text-notion-text-primary-dark">
            Review and export
          </h2>
        </div>
        <p className="text-sm text-notion-text-secondary leading-relaxed ml-8">
          Browse matched, modified, and missing records in a searchable table. Ask
          the AI chat anything about your data in English or Hindi. When you're
          ready, generate a multi-sheet CBSE/KVS formatted Excel report and download
          it directly.
        </p>
      </section>

      <div className="text-xs text-notion-text-tertiary border-t border-notion-border dark:border-notion-border-dark pt-6 mb-8 leading-relaxed">
        This tool is intended for KV teachers comparing Excel student data. Do not
        upload sensitive or confidential information.
      </div>

      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-notion-text-primary dark:text-notion-text-primary-dark hover:underline"
      >
        Start comparing <ArrowRight className="w-4 h-4" />
      </Link>
    </div>
  )
}
