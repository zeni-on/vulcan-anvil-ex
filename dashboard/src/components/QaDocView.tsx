'use client'

import { useMemo, useState, type ReactNode } from 'react'
import { ChevronDown, Images, X } from 'lucide-react'
import { QaDocModel, QaEvidenceRow, QaFindingRow, QaResultRow } from '@/lib/qaDoc'

function EmptyValue({ children }: { children?: string }) {
  return children ? <>{children}</> : <span className="text-slate-400">-</span>
}

function encodeDocPath(path: string): string {
  return path.split('/').map(encodeURIComponent).join('/')
}

function imageUrl(projectId: string, path: string): string {
  return `/api/projects/${encodeURIComponent(projectId)}/raw/${encodeDocPath(path)}`
}

function StatPill({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm">
      <div className="text-[11px] font-medium text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-slate-950">{value}</div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="space-y-3">
      <h3 className="border-l-4 border-blue-500 pl-2 text-sm font-semibold text-slate-950">
        {title}
      </h3>
      {children}
    </section>
  )
}

function StatusBadge({ value }: { value?: string }) {
  const normalized = value?.toLowerCase() ?? ''
  const className = normalized.includes('pass') || normalized.includes('fixed')
    ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
    : normalized.includes('fail') || normalized.includes('open')
      ? 'border-amber-200 bg-amber-50 text-amber-700'
      : 'border-slate-200 bg-slate-50 text-slate-600'

  return (
    <span className={`rounded border px-1.5 py-0.5 text-[11px] font-medium ${className}`}>
      {value || '-'}
    </span>
  )
}

function SmallTable({ headers, rows }: { headers: string[]; rows: Array<Array<ReactNode>> }) {
  return (
    <div className="overflow-x-auto rounded-md border border-slate-300 bg-white shadow-sm">
      <table className="w-full border-collapse text-left text-xs">
        <thead className="bg-blue-100 text-blue-950">
          <tr>
            {headers.map((header) => (
              <th key={header} className="border-b border-blue-300 px-2 py-2 font-semibold">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="border-t border-slate-200 odd:bg-white even:bg-slate-50">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="border-r border-slate-100 px-2 py-2 align-top text-slate-700 last:border-r-0">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function EvidenceGrid({
  projectId,
  evidences,
  onPreview,
}: {
  projectId: string
  evidences: QaEvidenceRow[]
  onPreview: (evidence: QaEvidenceRow) => void
}) {
  return (
    <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
      {evidences.map((evidence) => (
        <button
          key={`${evidence.id}-${evidence.path}`}
          type="button"
          onClick={() => onPreview(evidence)}
          className="overflow-hidden rounded-md border border-slate-200 bg-white text-left shadow-sm transition hover:border-blue-300 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        >
          <div className="aspect-[16/9] max-h-28 bg-slate-100">
            <img
              src={imageUrl(projectId, evidence.path)}
              alt={`${evidence.id} ${evidence.label}`}
              className="h-full w-full object-contain"
              loading="lazy"
            />
          </div>
          <div className="border-t border-slate-100 p-2">
            <div className="font-mono text-xs font-semibold text-blue-700">{evidence.id}</div>
            <div className="mt-0.5 text-xs text-slate-700"><EmptyValue>{evidence.label}</EmptyValue></div>
            <div className="mt-1 truncate font-mono text-[11px] text-slate-500">{evidence.path}</div>
          </div>
        </button>
      ))}
    </div>
  )
}

function splitRelatedIds(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function evidenceMatchesFinding(evidence: QaEvidenceRow, finding: QaFindingRow): boolean {
  return splitRelatedIds(finding.relatedIds).some((relatedId) =>
    evidence.id === relatedId || evidence.id.startsWith(`${relatedId}-`),
  )
}

function evidencePurposeFor(finding: QaFindingRow): string {
  const normalized = finding.status.toLowerCase()
  if (normalized.includes('fixed') || normalized.includes('verified') || normalized.includes('closed')) {
    return '수정 후 검증 증적'
  }
  if (normalized.includes('open') || normalized.includes('progress')) {
    return '미해결 상태 확인 증적'
  }
  return '발견사항 판단 증적'
}

function FindingEvidencePanel({
  projectId,
  findings,
  evidences,
  onPreview,
}: {
  projectId: string
  findings: QaFindingRow[]
  evidences: QaEvidenceRow[]
  onPreview: (evidence: QaEvidenceRow) => void
}) {
  return (
    <div className="space-y-3">
      {findings.map((finding) => {
        const matchedEvidences = evidences.filter((evidence) => evidenceMatchesFinding(evidence, finding))
        return (
          <article key={finding.id} className="rounded-md border border-slate-200 bg-white p-3 shadow-sm">
            <div className="mb-3 flex flex-wrap items-start justify-between gap-2 border-b border-slate-100 pb-2">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-semibold text-amber-700">{finding.id}</span>
                  <StatusBadge value={finding.status} />
                  <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[11px] font-medium text-slate-600">
                    {evidencePurposeFor(finding)}
                  </span>
                </div>
                <div className="mt-1 text-sm font-medium text-slate-950">{finding.title || '-'}</div>
                <div className="mt-1 font-mono text-[11px] text-slate-500">
                  연결 ID: {finding.relatedIds || '-'}
                </div>
              </div>
              <div className="rounded border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-600">
                직접 증적 {matchedEvidences.length}개
              </div>
            </div>

            {matchedEvidences.length > 0 ? (
              <EvidenceGrid projectId={projectId} evidences={matchedEvidences} onPreview={onPreview} />
            ) : (
              <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-xs text-slate-500">
                이 발견사항에 직접 매칭된 이미지 증적이 없습니다. 필요한 경우 관련 ID에 UI/UT/IT/PT 증적 ID를 추가하거나 Test Result 문서의 증적을 연결하세요.
              </div>
            )}
          </article>
        )
      })}
    </div>
  )
}

function renderFindingRows(rows: QaFindingRow[]) {
  return rows.map((row) => [
    <span key="id" className="font-mono font-semibold text-amber-700">{row.id}</span>,
    row.title || '-',
    row.severity || '-',
    <StatusBadge key="status" value={row.status} />,
    row.crRequired || '-',
    row.relatedIds || '-',
  ])
}

function renderResultRows(rows: QaResultRow[], evidencesById: Map<string, QaEvidenceRow[]>, onPreview: (evidence: QaEvidenceRow) => void) {
  return rows.map((row) => [
    <span key="id" className="font-mono font-semibold text-blue-700">{row.id}</span>,
    row.target || '-',
    row.method || '-',
    <StatusBadge key="result" value={row.result} />,
    <div key="evidence" className="space-y-1">
      {(evidencesById.get(row.id) ?? []).map((evidence) => (
        <button
          key={evidence.path}
          type="button"
          onClick={() => onPreview(evidence)}
          className="block text-left font-mono text-[11px] text-blue-700 hover:underline"
        >
          {evidence.path}
        </button>
      ))}
      {(evidencesById.get(row.id) ?? []).length === 0 && (
        <span className="font-mono text-[11px] text-slate-500">{row.evidence || '-'}</span>
      )}
    </div>,
  ])
}

export default function QaDocView({
  model,
  projectId,
}: {
  model: QaDocModel
  projectId: string
}) {
  const [preview, setPreview] = useState<QaEvidenceRow | null>(null)
  const [showAllEvidence, setShowAllEvidence] = useState(false)
  const failedCount = model.results.filter((row) => row.result.toLowerCase().includes('fail')).length
  const openFindingCount = model.findings.filter((row) => row.status.toLowerCase() === 'open').length
  const visibleEvidenceLimit = 6
  const visibleEvidences = showAllEvidence ? model.evidences : model.evidences.slice(0, visibleEvidenceLimit)
  const hiddenEvidenceCount = Math.max(0, model.evidences.length - visibleEvidences.length)
  const shouldGroupEvidenceByFinding = model.documentKind === 'finding' && model.findings.length > 0
  const evidencesById = useMemo(() => {
    const map = new Map<string, QaEvidenceRow[]>()
    for (const evidence of model.evidences) {
      const keys = new Set<string>([evidence.id])
      const uiMatch = evidence.id.match(/^(UI-\d{3})/)
      const reqMatch = evidence.id.match(/^(REQ-\d{3}-\d{2})/)
      if (uiMatch) keys.add(uiMatch[1])
      if (reqMatch) keys.add(reqMatch[1])
      for (const key of keys) {
        const existing = map.get(key) ?? []
        existing.push(evidence)
        map.set(key, existing)
      }
    }
    return map
  }, [model.evidences])

  return (
    <div className="space-y-6 rounded-md bg-slate-100 p-4 text-sm text-slate-800" data-testid="qa-doc-view">
      <header className="rounded-md border border-blue-200 bg-gradient-to-r from-blue-50 to-white p-4 shadow-sm">
        <div className="text-xs font-medium text-blue-700">
          {model.documentKind === 'finding' ? 'QA Finding' : model.documentKind === 'result' ? 'Test Result Report' : 'QA Document'}
        </div>
        <h2 className="mt-1 text-lg font-semibold text-slate-950">{model.title}</h2>
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">
          <span>프로젝트: <EmptyValue>{model.project}</EmptyValue></span>
          <span>상태: <EmptyValue>{model.status}</EmptyValue></span>
          <span>수정일: <EmptyValue>{model.updatedAt}</EmptyValue></span>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <StatPill label="발견사항" value={model.findings.length} />
        <StatPill label="Open" value={openFindingCount} />
        <StatPill label="테스트 결과" value={model.results.length} />
        <StatPill label="이미지 증적" value={model.evidences.length} />
      </div>

      {model.judgement && (
        <Section title="판정">
          <div className="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm leading-relaxed text-emerald-950">
            {model.judgement}
          </div>
        </Section>
      )}

      {model.findings.length > 0 && (
        <Section title="발견사항">
          <SmallTable
            headers={['ID', '제목', '심각도', '상태', 'CR 필요', '관련 ID']}
            rows={renderFindingRows(model.findings)}
          />
        </Section>
      )}

      {model.results.length > 0 && (
        <Section title={`테스트 실행 결과${failedCount > 0 ? ` (실패 ${failedCount}건)` : ''}`}>
          <SmallTable
            headers={['테스트 ID', '관련 REQ', '명령/방법', '결과', '증적']}
            rows={renderResultRows(model.results, evidencesById, setPreview)}
          />
        </Section>
      )}

      {(model.evidences.length > 0 || shouldGroupEvidenceByFinding) && (
        <Section title={shouldGroupEvidenceByFinding ? '발견사항별 증적 매칭' : '이미지 증적'}>
          {shouldGroupEvidenceByFinding ? (
            <FindingEvidencePanel
              projectId={projectId}
              findings={model.findings}
              evidences={model.evidences}
              onPreview={setPreview}
            />
          ) : (
            <div className="rounded-md border border-slate-200 bg-white p-3 shadow-sm">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-xs text-slate-600">
                <Images className="h-4 w-4 text-blue-600" aria-hidden="true" />
                <span>
                  {showAllEvidence
                    ? `전체 ${model.evidences.length}개 표시 중`
                    : `처음 ${visibleEvidences.length}개 표시 중`}
                </span>
                {hiddenEvidenceCount > 0 && (
                  <span className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-500">
                    {hiddenEvidenceCount}개 숨김
                  </span>
                )}
              </div>
              {model.evidences.length > visibleEvidenceLimit && (
                <button
                  type="button"
                  onClick={() => setShowAllEvidence((value) => !value)}
                  className="inline-flex items-center gap-1 rounded border border-blue-200 bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 hover:bg-blue-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                  aria-expanded={showAllEvidence}
                >
                  <ChevronDown
                    className={`h-3.5 w-3.5 transition-transform ${showAllEvidence ? 'rotate-180' : ''}`}
                    aria-hidden="true"
                  />
                  {showAllEvidence ? '접기' : '전체 보기'}
                </button>
              )}
            </div>
            <EvidenceGrid projectId={projectId} evidences={visibleEvidences} onPreview={setPreview} />
            </div>
          )}
        </Section>
      )}

      {preview && (
        <div
          className="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 p-6"
          role="dialog"
          aria-modal="true"
          aria-label={`${preview.id} 이미지 증적`}
          onClick={() => setPreview(null)}
        >
          <div
            className="max-h-full max-w-6xl overflow-hidden rounded-md border border-slate-700 bg-slate-950 shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 px-3 py-2">
              <div>
                <div className="font-mono text-xs font-semibold text-blue-300">{preview.id}</div>
                <div className="text-xs text-slate-300">{preview.label}</div>
              </div>
              <button
                type="button"
                onClick={() => setPreview(null)}
                aria-label="이미지 미리보기 닫기"
                className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
              >
                <X className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
            <div className="max-h-[80vh] overflow-auto bg-slate-900 p-3">
              <img
                src={imageUrl(projectId, preview.path)}
                alt={`${preview.id} ${preview.label}`}
                className="max-h-[74vh] max-w-full object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
