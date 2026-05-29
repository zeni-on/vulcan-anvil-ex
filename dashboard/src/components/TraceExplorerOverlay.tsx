'use client'

import { useEffect, useMemo, useState } from 'react'
import { Network, RefreshCw, Search, X } from 'lucide-react'
import MermaidBlock from './MermaidBlock'

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

export function extractTraceIds(content: string): string[] {
  const seen = new Set<string>()
  for (const match of content.matchAll(TRACE_ID_PATTERN)) {
    seen.add(match[0].toUpperCase())
  }
  return Array.from(seen).slice(0, 48)
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

function formatEdgeType(type: string): string {
  const labels: Record<string, string> = {
    decomposes: '분해',
    satisfies: '충족',
    implements: '구현',
    verifies: '검증',
    evidence_of: '증적',
    impacts: '영향',
    documents: '문서화',
  }
  return labels[type] ?? type
}

function directEdgesFor(result: TraceContextResult): TraceEdge[] {
  const seed = result.seed_id
  const edges = result.edges ?? []
  const direct = edges.filter((edge) => edge.source === seed || edge.target === seed)
  return (direct.length > 0 ? direct : edges).slice(0, 20)
}

function mermaidLabel(value: string): string {
  return value.replace(/"/g, '&quot;')
}

function buildTraceMermaid(result: TraceContextResult): string {
  const edges = directEdgesFor(result)
  if (edges.length === 0) return ''

  const ids = Array.from(new Set(edges.flatMap((edge) => [edge.source, edge.target])))
  const nodeNames = new Map(ids.map((id, index) => [id, `N${index}`]))
  const lines = ['flowchart LR']

  for (const id of ids) {
    const node = nodeNames.get(id)
    if (!node) continue
    lines.push(`  ${node}["${mermaidLabel(id)}"]`)
  }

  for (const edge of edges) {
    const source = nodeNames.get(edge.source)
    const target = nodeNames.get(edge.target)
    if (!source || !target) continue
    lines.push(`  ${source} -->|"${mermaidLabel(formatEdgeType(edge.type))}"| ${target}`)
  }

  return lines.join('\n')
}

interface TraceExplorerOverlayProps {
  projectId: string
  content: string
  initialId: string
  isOpen: boolean
  onClose: () => void
}

export default function TraceExplorerOverlay({
  projectId,
  content,
  initialId,
  isOpen,
  onClose,
}: TraceExplorerOverlayProps) {
  const detectedIds = useMemo(() => extractTraceIds(content), [content])
  const [query, setQuery] = useState(initialId)
  const [direction, setDirection] = useState<'downstream' | 'upstream' | 'both'>('downstream')
  const [depth, setDepth] = useState<'1' | '2' | '3'>('1')
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
        depth,
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

  useEffect(() => {
    if (!isOpen) return
    const seed = initialId || detectedIds[0] || ''
    setQuery(seed)
    setResult(null)
    setError(null)
    if (seed) void runSearch(seed)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, initialId])

  useEffect(() => {
    if (!isOpen) return
    const handler = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const directEdges = result ? directEdgesFor(result) : []
  const mermaid = result ? buildTraceMermaid(result) : ''

  return (
    <div className="fixed inset-0 z-[70]">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} aria-hidden="true" />
      <section
        role="dialog"
        aria-modal="true"
        aria-label="Trace Explorer"
        className="absolute bottom-4 right-4 top-4 flex w-[min(960px,calc(100vw-2rem))] flex-col overflow-hidden rounded-lg border border-slate-600 bg-slate-950 shadow-2xl"
      >
        <header className="flex items-center gap-3 border-b border-slate-800 bg-slate-900 px-4 py-3">
          <div className="flex min-w-0 items-center gap-2">
            <Network className="h-4 w-4 text-cyan-300" aria-hidden="true" />
            <div>
              <div className="text-xs font-semibold uppercase tracking-widest text-slate-400">Trace Explorer</div>
              <div className="truncate font-mono text-sm font-semibold text-slate-100">
                {result?.seed_id ?? query ?? detectedIds[0] ?? 'ID'}
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="ml-auto rounded p-1 text-slate-400 transition-colors hover:bg-slate-800 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
            aria-label="Trace Explorer 닫기"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </header>

        <div className="grid min-h-0 flex-1 grid-cols-[260px_minmax(0,1fr)]">
          <aside className="min-h-0 overflow-y-auto border-r border-slate-800 bg-slate-900/80 p-4">
            <div className="mb-3 flex items-center gap-2">
              <select
                value={depth}
                onChange={(event) => setDepth(event.target.value as typeof depth)}
                className="h-8 rounded border border-slate-700 bg-slate-950 px-2 text-xs text-slate-100"
                aria-label="Trace depth"
                title="탐색 깊이"
              >
                <option value="1">depth 1</option>
                <option value="2">depth 2</option>
                <option value="3">depth 3</option>
              </select>
              <select
                value={direction}
                onChange={(event) => setDirection(event.target.value as typeof direction)}
                className="h-8 rounded border border-slate-700 bg-slate-950 px-2 text-xs text-slate-100"
                aria-label="Trace direction"
              >
                <option value="downstream">downstream</option>
                <option value="upstream">upstream</option>
                <option value="both">both</option>
              </select>
            </div>
            <div className="mb-4 flex h-9 overflow-hidden rounded border border-slate-700 bg-slate-950">
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value.toUpperCase())}
                onKeyDown={(event) => {
                  if (event.key === 'Enter') void runSearch()
                }}
                className="min-w-0 flex-1 border-0 bg-transparent px-2 font-mono text-xs text-slate-100 outline-none"
                placeholder="REQ-001-01"
                aria-label="Trace ID"
              />
              <button
                type="button"
                onClick={() => void runSearch()}
                disabled={isLoading}
                className="inline-flex w-9 items-center justify-center border-l border-slate-800 text-slate-300 transition-colors hover:bg-slate-800 disabled:opacity-50"
                aria-label="Trace Context 조회"
              >
                {isLoading ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
                ) : (
                  <Search className="h-3.5 w-3.5" aria-hidden="true" />
                )}
              </button>
            </div>
            <div className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
              Document IDs
            </div>
            <div className="flex flex-wrap gap-1.5">
              {detectedIds.map((id) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => void runSearch(id)}
                  className={`rounded border px-1.5 py-0.5 font-mono text-[11px] font-semibold transition-colors ${
                    id === result?.seed_id
                      ? 'border-cyan-300 bg-cyan-400/15 text-cyan-100'
                      : 'border-slate-700 bg-slate-950 text-slate-300 hover:border-cyan-400 hover:text-cyan-100'
                  }`}
                  title={id}
                >
                  {id}
                </button>
              ))}
              {detectedIds.length === 0 && (
                <div className="rounded border border-slate-800 bg-slate-950 px-2 py-1.5 text-xs text-slate-500">
                  감지된 ID가 없습니다.
                </div>
              )}
            </div>
          </aside>

          <main className="min-h-0 overflow-y-auto p-4">
            {error && (
              <div className="mb-4 rounded border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-100">
                {error}
              </div>
            )}

            {result ? (
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
                  <span className="font-mono font-semibold text-cyan-100">{result.seed_id}</span>
                  <span>direct {directEdges.length}</span>
                  <span>related {result.related_ids?.length ?? 0}</span>
                  <span>edges {result.edges?.length ?? 0}</span>
                  <span>depth {depth}</span>
                </div>

                <div className="rounded-md border border-slate-800 bg-slate-900/70 p-3">
                  {mermaid ? (
                    <MermaidBlock code={mermaid} />
                  ) : (
                    <div className="rounded border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-500">
                      표시할 edge가 없습니다.
                    </div>
                  )}
                </div>

                <div className="rounded-md border border-slate-800 bg-slate-900/70 p-3">
                  <div className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                    Direct Edges
                  </div>
                  <div className="space-y-1.5">
                    {directEdges.map((edge, index) => (
                      <div
                        key={`${edge.source}-${edge.type}-${edge.target}-${index}`}
                        className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-2 rounded border border-slate-800 bg-slate-950 px-2 py-1.5 text-[11px]"
                      >
                        <span
                          className={`truncate font-mono font-semibold ${edge.source === result.seed_id ? 'text-cyan-200' : 'text-slate-300'}`}
                          title={edge.source}
                        >
                          {edge.source}
                        </span>
                        <span className="rounded border border-slate-700 bg-slate-900 px-1.5 py-0.5 text-slate-400">
                          {formatEdgeType(edge.type)} →
                        </span>
                        <span
                          className={`truncate font-mono font-semibold ${edge.target === result.seed_id ? 'text-cyan-200' : 'text-slate-300'}`}
                          title={edge.target}
                        >
                          {edge.target}
                        </span>
                      </div>
                    ))}
                    {directEdges.length === 0 && (
                      <div className="rounded border border-slate-800 bg-slate-950 px-2 py-1.5 text-xs text-slate-500">
                        직접 연결 edge가 없습니다.
                      </div>
                    )}
                  </div>
                </div>

                {result.target_contracts && (
                  <div className="grid gap-3 lg:grid-cols-2">
                    {Object.entries(result.target_contracts)
                      .filter(([, ids]) => ids.length > 0)
                      .map(([key, ids]) => (
                        <div key={key} className="rounded-md border border-slate-800 bg-slate-900/70 p-3">
                          <div className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                            {formatContractLabel(key)}
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {ids.slice(0, 14).map((id) => (
                              <span key={id} className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[11px] text-slate-200">
                                {id}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                  </div>
                )}

                {result.related_documents && result.related_documents.length > 0 && (
                  <div className="rounded-md border border-slate-800 bg-slate-900/70 p-3">
                    <div className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                      Documents
                    </div>
                    <div className="space-y-1">
                      {result.related_documents.slice(0, 8).map((doc) => (
                        <div key={doc.path} className="truncate font-mono text-[11px] text-slate-400" title={doc.path}>
                          {doc.path}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="rounded-md border border-slate-800 bg-slate-900/70 px-3 py-2 text-sm text-slate-400">
                ID를 선택하거나 입력하세요.
              </div>
            )}
          </main>
        </div>
      </section>
    </div>
  )
}
