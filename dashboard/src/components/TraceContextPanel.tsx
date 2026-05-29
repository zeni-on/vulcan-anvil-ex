'use client'

import { useMemo, useState } from 'react'
import { Network, RefreshCw, Search } from 'lucide-react'

const TRACE_ID_PATTERN =
  /\b(?:REQ-\d{3}(?:-\d{2})?|NREQ-\d{3}(?:-\d{2})?|AC-\d{3}-\d{2}|FUNC-\d{3}|SCR-\d{3}|UIREF-\d{3}|UICON-\d{3}|API-\d{3}|PGM-\d{3}|IF-\d{3}|MTH-\d{3}|DB-\d{3}|SEC-\d{3}|UT-\d{3}|IT-\d{3}|PT-\d{3}|UI-\d{3}(?:-\d{2})?|EV-[A-Z0-9-]+|FIND-\d{3}|CR-\d{3}|DEC-\d{3}|BL-\d{3}|ISSUE-[A-Z0-9-]+|RUN-\d{3}|RV-\d{3})\b/gi

interface TraceEdge {
  source: string
  target: string
  type: string
}

interface TraceDocument {
  path: string
  ids: string[]
}

interface TraceContextResult {
  seed_id: string
  related_ids: string[]
  target_contracts?: Record<string, string[]>
  edges?: TraceEdge[]
  related_documents?: TraceDocument[]
  warnings?: string[]
}

function extractTraceIds(content: string): string[] {
  const seen = new Set<string>()
  for (const match of content.matchAll(TRACE_ID_PATTERN)) {
    seen.add(match[0].toUpperCase())
  }
  return Array.from(seen).slice(0, 36)
}

function formatContractLabel(key: string): string {
  const labels: Record<string, string> = {
    req: 'REQ',
    nreq: 'NREQ',
    ac: 'AC',
    func: 'FUNC',
    scr: 'SCR',
    pgm: 'PGM',
    api: 'API',
    db: 'DB',
    sec: 'SEC',
    test: 'TEST',
    ui: 'UI',
    other: 'OTHER',
  }
  return labels[key] ?? key.toUpperCase()
}

export default function TraceContextPanel({
  projectId,
  content,
}: {
  projectId: string
  content: string
}) {
  const detectedIds = useMemo(() => extractTraceIds(content), [content])
  const [query, setQuery] = useState(detectedIds[0] ?? '')
  const [direction, setDirection] = useState<'downstream' | 'upstream' | 'both'>('downstream')
  const [result, setResult] = useState<TraceContextResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const runSearch = async (seed = query) => {
    const normalized = seed.trim().toUpperCase()
    if (!normalized) return
    setQuery(normalized)
    setIsLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({
        id: normalized,
        depth: '2',
        direction,
      })
      const res = await fetch(`/api/projects/${encodeURIComponent(projectId)}/trace-context?${params.toString()}`)
      const body = await res.json()
      if (!res.ok) {
        throw new Error(body?.error ?? `trace-context failed (${res.status})`)
      }
      setResult(body as TraceContextResult)
    } catch (err) {
      setResult(null)
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="mb-4 rounded-md border border-slate-300 bg-slate-50 p-3 text-slate-800 shadow-sm">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-widest text-slate-500">
          <Network className="h-3.5 w-3.5" aria-hidden="true" />
          Trace Context
        </div>
        <div className="ml-auto flex items-center gap-2">
          <select
            value={direction}
            onChange={(event) => setDirection(event.target.value as typeof direction)}
            className="h-8 rounded border border-slate-300 bg-white px-2 text-xs text-slate-700"
            aria-label="Trace direction"
          >
            <option value="downstream">downstream</option>
            <option value="upstream">upstream</option>
            <option value="both">both</option>
          </select>
          <div className="flex h-8 overflow-hidden rounded border border-slate-300 bg-white">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value.toUpperCase())}
              onKeyDown={(event) => {
                if (event.key === 'Enter') void runSearch()
              }}
              className="w-36 border-0 px-2 text-xs font-mono text-slate-800 outline-none"
              placeholder="REQ-001-01"
              aria-label="Trace ID"
            />
            <button
              type="button"
              onClick={() => void runSearch()}
              disabled={isLoading}
              className="inline-flex w-8 items-center justify-center border-l border-slate-200 text-slate-600 hover:bg-slate-100 disabled:opacity-50"
              aria-label="Trace Context 조회"
            >
              {isLoading ? (
                <RefreshCw className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
              ) : (
                <Search className="h-3.5 w-3.5" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {detectedIds.length > 0 && (
        <div className="mb-3 flex max-h-16 flex-wrap gap-1 overflow-hidden">
          {detectedIds.map((id) => (
            <button
              key={id}
              type="button"
              onClick={() => void runSearch(id)}
              className="rounded border border-blue-200 bg-white px-1.5 py-0.5 font-mono text-[11px] font-semibold text-blue-700 hover:bg-blue-50"
            >
              {id}
            </button>
          ))}
        </div>
      )}

      {error && (
        <div className="rounded border border-amber-200 bg-amber-50 px-2 py-1.5 text-xs text-amber-800">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="font-mono font-semibold text-slate-950">{result.seed_id}</span>
            <span className="text-slate-500">related {result.related_ids?.length ?? 0}</span>
            <span className="text-slate-500">edges {result.edges?.length ?? 0}</span>
          </div>

          {result.target_contracts && (
            <div className="grid gap-2 sm:grid-cols-2">
              {Object.entries(result.target_contracts)
                .filter(([, ids]) => ids.length > 0)
                .map(([key, ids]) => (
                  <div key={key} className="rounded border border-slate-200 bg-white p-2">
                    <div className="mb-1 text-[10px] font-semibold text-slate-500">
                      {formatContractLabel(key)}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {ids.slice(0, 10).map((id) => (
                        <span key={id} className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px] text-slate-700">
                          {id}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
            </div>
          )}

          {result.related_documents && result.related_documents.length > 0 && (
            <div className="rounded border border-slate-200 bg-white p-2">
              <div className="mb-1 text-[10px] font-semibold text-slate-500">DOCUMENTS</div>
              <div className="space-y-1">
                {result.related_documents.slice(0, 6).map((doc) => (
                  <div key={doc.path} className="truncate font-mono text-[11px] text-slate-600" title={doc.path}>
                    {doc.path}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
