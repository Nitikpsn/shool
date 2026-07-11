import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import UploadZone from '../components/UploadZone'
import { uploadFiles } from '../services/api'
import { School } from 'lucide-react'
import { UploadResult } from '../types'

export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<UploadResult | null>(null)

  const handleUpload = useCallback(async (files: { school: File | null; portal: File | null }) => {
    if (!files.school || !files.portal) return
    setLoading(true)
    try {
      const res = await uploadFiles(files.school, files.portal)
      setResult(res)
    } catch (err: any) {
      alert(err.message)
    }
    setLoading(false)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-2">
          <School className="w-6 h-6 text-blue-600" />
          <h1 className="text-xl font-bold">School Sync AI</h1>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-1">Upload Excel Files</h2>
          <p className="text-sm text-gray-500">Upload school.xlsx (your records) and portal.xlsx (official records)</p>
        </div>

        <UploadZone onUpload={handleUpload} />

        {loading && (
          <div className="mt-6 text-center text-sm text-gray-500">Processing files...</div>
        )}

        {result && (
          <div className="mt-6 bg-white rounded-xl border p-6">
            <h3 className="font-semibold mb-3">Upload Successful</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Session:</span>
                <span className="ml-2 font-mono">{result.session_id.slice(0, 8)}...</span>
              </div>
              <div>
                <span className="text-gray-500">School rows:</span>
                <span className="ml-2 font-medium">{result.school_rows}</span>
              </div>
              <div>
                <span className="text-gray-500">Portal rows:</span>
                <span className="ml-2 font-medium">{result.portal_rows}</span>
              </div>
              <div>
                <span className="text-gray-500">Columns mapped:</span>
                <span className="ml-2 font-mono text-xs">{result.columns_mapped.join(', ')}</span>
              </div>
            </div>

            {result.errors && result.errors.length > 0 && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-sm font-medium text-red-700">Validation Errors ({result.errors.length})</p>
                {result.errors.slice(0, 5).map((e, i) => (
                  <p key={i} className="text-xs text-red-600 mt-1">Row {e.row}: {e.message}</p>
                ))}
              </div>
            )}

            <div className="mt-4 flex gap-3">
              <button
                onClick={() => navigate(`/compare/${result.session_id}`)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
              >
                Compare Files
              </button>
              <button
                onClick={() => navigate(`/reports/${result.session_id}`)}
                className="px-4 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50"
              >
                Generate Report
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}