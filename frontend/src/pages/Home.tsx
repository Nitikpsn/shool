import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import UploadZone from '../components/UploadZone'
import { uploadFiles } from '../services/api'
import { UploadResult } from '../types'
import { CheckCircle, AlertCircle, ArrowRight, FileText, Upload, BarChart3, MessageSquare } from 'lucide-react'

export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<UploadResult | null>(null)
  const [error, setError] = useState('')

  const handleUpload = useCallback(async (files: { school: File | null; portal: File | null }) => {
    if (!files.school || !files.portal) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await uploadFiles(files.school, files.portal)
      setResult(res)
    } catch (err: any) {
      setError(err.message)
    }
    setLoading(false)
  }, [])

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-indigo-50 mb-4">
          <BarChart3 className="w-7 h-7 text-indigo-500" />
        </div>
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">School Sync AI</h1>
        <p className="text-sm text-slate-500 mt-2 max-w-md mx-auto leading-relaxed">
          Upload school and portal records to compare student data, detect mismatches, and generate CBSE/KVS reports.
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-7">
        <div className="flex items-center gap-3 mb-6 pb-5 border-b border-slate-100">
          <div className="w-9 h-9 rounded-lg bg-indigo-50 flex items-center justify-center">
            <Upload className="w-4.5 h-4.5 text-indigo-500" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-800">Upload Records</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Drop your Excel or CSV files below to get started
            </p>
          </div>
        </div>

        <UploadZone onUpload={handleUpload} />

        {loading && (
          <div className="mt-6 flex items-center justify-center gap-2.5 py-4">
            <div className="w-4 h-4 border-2 border-slate-200 border-t-indigo-500 rounded-full animate-spin" />
            <span className="text-sm text-slate-500">Processing files...</span>
          </div>
        )}

        {error && (
          <div className="mt-6 flex items-start gap-2.5 p-3.5 bg-red-50 border border-red-100 rounded-lg text-sm text-red-600">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {result && (
          <div className="mt-6">
            <div className="flex items-center gap-2 mb-5 pb-4 border-b border-slate-100">
              <div className="w-6 h-6 rounded-full bg-emerald-50 flex items-center justify-center">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
              </div>
              <span className="text-sm font-medium text-emerald-600">Upload successful</span>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-5">
              <div className="bg-slate-50 rounded-lg p-3.5">
                <p className="text-xs text-slate-400">Session</p>
                <p className="text-sm font-mono text-slate-700 mt-0.5">{result.session_id.slice(0, 8)}...</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3.5">
                <p className="text-xs text-slate-400">School records</p>
                <p className="text-sm font-semibold text-slate-700 mt-0.5">{result.school_rows}</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3.5">
                <p className="text-xs text-slate-400">Portal records</p>
                <p className="text-sm font-semibold text-slate-700 mt-0.5">{result.portal_rows}</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3.5">
                <p className="text-xs text-slate-400">Columns mapped</p>
                <p className="text-sm text-slate-700 mt-0.5 truncate">{result.columns_mapped.join(', ') || '—'}</p>
              </div>
            </div>

            {result.errors && result.errors.length > 0 && (
              <div className="mb-5 p-3.5 bg-amber-50 border border-amber-100 rounded-lg">
                <p className="text-xs font-medium text-amber-700 mb-2">
                  {result.errors.length} validation error{result.errors.length > 1 ? 's' : ''}
                </p>
                {result.errors.slice(0, 5).map((e, i) => (
                  <p key={i} className="text-xs text-amber-600 mt-1">Row {e.row}: {e.message}</p>
                ))}
              </div>
            )}

            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate(`/compare/${result.session_id}`)}
                className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
              >
                Compare Files
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => navigate(`/reports/${result.session_id}`)}
                className="inline-flex items-center gap-1.5 px-5 py-2.5 border border-slate-200 text-slate-600 text-sm font-medium rounded-lg hover:bg-slate-50 hover:text-slate-700 transition-colors"
              >
                <FileText className="w-4 h-4" />
                Generate Report
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-slate-200 p-4 text-center">
          <Upload className="w-5 h-5 text-indigo-400 mx-auto mb-2" />
          <p className="text-xs font-medium text-slate-700">Upload</p>
          <p className="text-xs text-slate-400 mt-1">Drop two Excel files</p>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4 text-center">
          <BarChart3 className="w-5 h-5 text-indigo-400 mx-auto mb-2" />
          <p className="text-xs font-medium text-slate-700">Compare</p>
          <p className="text-xs text-slate-400 mt-1">Find differences</p>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4 text-center">
          <FileText className="w-5 h-5 text-indigo-400 mx-auto mb-2" />
          <p className="text-xs font-medium text-slate-700">Report</p>
          <p className="text-xs text-slate-400 mt-1">Generate CBSE/KVS</p>
        </div>
      </div>
    </div>
  )
}
