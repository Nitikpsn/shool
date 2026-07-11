import React, { useCallback, useState } from 'react'
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
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <DropBox zone={school} file={schoolFile} label="School File" hint="school.xlsx / .xls / .csv" />
      <DropBox zone={portal} file={portalFile} label="Portal File" hint="portal.xlsx / .xls / .csv" />
    </div>
  )
}

function DropBox({ zone, file, label, hint }: { zone: ReturnType<typeof useDropzone>; file: File | null; label: string; hint: string }) {
  return (
    <div
      {...zone.getRootProps()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
        zone.isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <input {...zone.getInputProps()} />
      <Upload className="mx-auto h-10 w-10 text-gray-400 mb-3" />
      <p className="text-sm font-medium text-gray-700">{label}</p>
      <p className="text-xs text-gray-500 mt-1">{file ? file.name : `Drop ${hint} here`}</p>
      {file && <p className="text-xs text-green-600 mt-2">{(file.size / 1024).toFixed(1)} KB</p>}
    </div>
  )
}