import type { UploadResult, CompareResult, StatsResult, ReportResult, ChatResult, Modification, CategoryCompareResult } from '../types'

const API_BASE = import.meta.env.VITE_API_URL || ''

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

function transformMod(m: any): Modification {
  return {
    id: m.admission_no || m.id || '',
    record_name: m.student_name || m.record_name || '',
    field_name: m.field_name || '',
    old_value: m.old_value || '',
    new_value: m.new_value || '',
    difference_type: m.difference_type || '',
  }
}

function transformStats(raw: any): StatsResult {
  if (raw.labels) return raw as StatsResult

  const labels: Record<string, number> = {}
  const fieldMap: Record<string, string> = {
    boys: 'Boys', girls: 'Girls', sc: 'SC', obc: 'OBC',
    st: 'ST', ews: 'EWS', gen: 'GEN', total: 'Total',
  }

  for (const [key, val] of Object.entries(raw)) {
    if (typeof val === 'number') {
      labels[fieldMap[key] || key] = val
    }
  }

  const excludeKeys = new Set(Object.keys(fieldMap))
  const extraLabels: Record<string, number> = {}
  for (const [key, val] of Object.entries(raw)) {
    if (!excludeKeys.has(key) && typeof val === 'number') {
      extraLabels[key] = val
    }
  }

  return { labels: { ...labels, ...extraLabels } }
}

export async function uploadFiles(
  file1: File,
  file2: File
): Promise<UploadResult> {
  const form = new FormData()
  form.append('file1', file1)
  form.append('file2', file2)
  const res = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function compare(session_id: string): Promise<CompareResult> {
  const raw: any = await apiFetch('/api/compare', {
    method: 'POST',
    body: JSON.stringify({ session_id }),
  })

  return {
    matched: raw.matched || 0,
    missing: raw.missing || 0,
    modified: raw.modified || 0,
    new: raw.new || 0,
    matched_ids: raw.matched_admissions || raw.matched_ids || [],
    modifications: (raw.modifications || []).map(transformMod),
    new_records: (raw.new_records || []).map((r: any) => {
      const { difference_type, ...rest } = r
      return rest
    }),
    missing_records: (raw.missing_records || []).map((r: any) => {
      const { difference_type, ...rest } = r
      return rest
    }),
  }
}

export async function getStats(sessionId: string): Promise<StatsResult> {
  const raw = await apiFetch<any>(`/api/stats/${sessionId}`)
  return transformStats(raw)
}

export async function generateReport(sessionId: string): Promise<ReportResult> {
  return apiFetch<ReportResult>('/api/reports', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  })
}

export async function chatQuery(sessionId: string, query: string): Promise<ChatResult> {
  return apiFetch<ChatResult>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, query }),
  })
}

export async function compareCategories(sessionId: string): Promise<CategoryCompareResult> {
  return apiFetch<CategoryCompareResult>('/api/compare/categories', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  })
}
