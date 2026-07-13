import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, CheckCircle2 } from 'lucide-react'

export default function UploadZone({ onUpload }: { onUpload: (files: { school: File | null; portal: File | null }) => void }) {
  const [file1, setFile1] = useState<File | null>(null)
  const [file2, setFile2] = useState<File | null>(null)

  const drop1 = useDropzone({
    onDrop: useCallback((accepted: File[]) => {
      if (accepted.length) {
        setFile1(accepted[0])
        onUpload({ school: accepted[0], portal: file2 })
      }
    }, [file2, onUpload]),
    accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'], 'application/vnd.ms-excel': ['.xls'], 'text/csv': ['.csv'] },
  })

  const drop2 = useDropzone({
    onDrop: useCallback((accepted: File[]) => {
      if (accepted.length) {
        setFile2(accepted[0])
        onUpload({ school: file1, portal: accepted[0] })
      }
    }, [file1, onUpload]),
    accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'], 'application/vnd.ms-excel': ['.xls'], 'text/csv': ['.csv'] },
  })

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FileBox zone={drop1} file={file1} label="File 1" hint="file1.xlsx" />
      <FileBox zone={drop2} file={file2} label="File 2" hint="file2.xlsx" />
    </div>
  )
}

function FileBox({ zone, file, label, hint }: any) {
  const active = zone.isDragActive
  return (
    <div
      {...zone.getRootProps()}
      className={`border-2 border-dashed rounded-lg p-5 text-center cursor-pointer transition-colors ${
        active ? 'border-neutral-400 bg-neutral-50 dark:bg-neutral-800/50' :
        file ? 'border-emerald-300 bg-emerald-50/50 dark:bg-emerald-900/10' :
        'border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600'
      }`}
    >
      <input {...zone.getInputProps()} />
      <div className={`w-10 h-10 rounded-xl mx-auto mb-2 flex items-center justify-center ${file ? 'bg-emerald-100 dark:bg-emerald-900/30' : 'bg-neutral-100 dark:bg-neutral-800'}`}>
        {file ? <CheckCircle2 className="w-5 h-5 text-emerald-500" /> : <Upload className={`w-5 h-5 ${active ? 'text-neutral-500' : 'text-neutral-400'}`} />}
      </div>
      <p className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{label}</p>
      {file ? (
        <p className="text-xs text-neutral-500 mt-1 truncate">{file.name}</p>
      ) : (
        <p className="text-xs text-neutral-400 mt-1">{active ? 'Drop file' : `Drop ${hint}`}</p>
      )}
    </div>
  )
}
