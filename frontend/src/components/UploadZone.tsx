import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload } from 'lucide-react'

interface UploadZoneProps {
  onUpload: (files: { school: File | null; portal: File | null }) => void
}

export default function UploadZone({ onUpload }: UploadZoneProps) {
  const [schoolFile, setSchoolFile] = useState<File | null>(null)
  const [portalFile, setPortalFile] = useState<File | null>(null)

  const onSchoolDrop = useCallback((accepted: File[]) => {
    if (accepted.length) {
      setSchoolFile(accepted[0])
      onUpload({ school: accepted[0], portal: portalFile })
    }
  }, [portalFile, onUpload])

  const onPortalDrop = useCallback((accepted: File[]) => {
    if (accepted.length) {
      setPortalFile(accepted[0])
      onUpload({ school: schoolFile, portal: accepted[0] })
    }
  }, [schoolFile, onUpload])

  const acceptTypes = {
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'application/vnd.ms-excel': ['.xls'],
    'text/csv': ['.csv'],
  }
  const school = useDropzone({ onDrop: onSchoolDrop, accept: acceptTypes })
  const portal = useDropzone({ onDrop: onPortalDrop, accept: acceptTypes })

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <DropBox zone={school} file={schoolFile} label="School Records" hint="school.xlsx / .xls / .csv" />
      <DropBox zone={portal} file={portalFile} label="Portal Records" hint="portal.xlsx / .xls / .csv" />
    </div>
  )
}

function DropBox({ zone, file, label, hint }: { zone: ReturnType<typeof useDropzone>; file: File | null; label: string; hint: string }) {
  return (
    <div
      {...zone.getRootProps()}
      className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
        zone.isDragActive
          ? 'border-indigo-300 bg-indigo-50'
          : file
            ? 'border-emerald-200 bg-emerald-50/50'
            : 'border-slate-200 hover:border-indigo-200 hover:bg-slate-50'
      }`}
    >
      <input {...zone.getInputProps()} />
      <div className={`w-10 h-10 rounded-xl mx-auto mb-3 flex items-center justify-center transition-colors ${
        file ? 'bg-emerald-100' : 'bg-slate-100'
      }`}>
        <Upload className={`w-5 h-5 ${file ? 'text-emerald-500' : 'text-slate-400'}`} />
      </div>
      <p className="text-sm font-medium text-slate-700">{label}</p>
      <p className="text-xs text-slate-400 mt-1.5">{file ? file.name : `Drop ${hint} here`}</p>
      {file && <p className="text-xs text-slate-400 mt-1">{(file.size / 1024).toFixed(1)} KB</p>}
    </div>
  )
}
