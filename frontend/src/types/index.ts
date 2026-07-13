export interface UploadResult {
  session_id: string
  school_rows: number
  portal_rows: number
  columns_mapped: string[]
  errors?: { row: number; field: string; message: string }[]
  school_sample: Record<string, string>[]
  portal_sample: Record<string, string>[]
}

export interface CompareResult {
  matched: number
  missing: number
  modified: number
  new: number
  matched_ids: string[]
  modifications: Modification[]
  new_records: Record<string, string>[]
  missing_records: Record<string, string>[]
}

export interface Modification {
  id: string
  field_name: string
  old_value: string
  new_value: string
  record_name: string
  difference_type: string
}

export interface StatsResult {
  labels: Record<string, number>
  charts?: ChartData[]
}

export interface ChartData {
  title: string
  type: 'pie' | 'bar'
  data: { name: string; value: number }[]
}

export interface ReportResult {
  message: string
  download_url: string
  summary: {
    total_portal: number
    matched: number
    new: number
    missing: number
    modified: number
  }
}

export interface ChatResult {
  original_query: string
  normalized_query: string
  filter_applied: Record<string, string>
  total_records: number
  records: Record<string, string>[]
}

export interface TableColumn {
  key: string
  label: string
  sortable?: boolean
  filterable?: boolean
  render?: (value: string, row: Record<string, string>) => React.ReactNode
}
