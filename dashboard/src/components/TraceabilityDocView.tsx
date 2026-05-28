'use client'

import type { ReactNode } from 'react'
import {
  countTraceabilityGaps,
  SecurityTraceRow,
  TraceabilityDocModel,
  TraceabilityIssueRow,
  TraceabilityRow,
  TraceabilitySummaryRow,
} from '@/lib/traceabilityDoc'

function EmptyValue({ children }: { children?: string }) {
  return children ? <>{children}</> : <span className="text-slate-400">-</span>
}

function StatPill({
  label,
  value,
  tone = 'default',
}: {
  label: string
  value: number | string
  tone?: 'default' | 'good' | 'warn'
}) {
  const toneClass = {
    default: 'border-slate-200 bg-white text-slate-950',
    good: 'border-emerald-200 bg-emerald-50 text-emerald-900',
    warn: 'border-amber-200 bg-amber-50 text-amber-900',
  }[tone]

  return (
    <div className={`rounded-md border px-3 py-2 shadow-sm ${toneClass}`}>
      <div className="text-[11px] font-medium text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold">{value}</div>
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
  const isDone = value === 'Verified' || value === 'Closed' || value === '완료'
  const isOpen = value === 'Open' || value === 'Draft' || value === '확인필요'
  const className = isDone
    ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
    : isOpen
      ? 'border-amber-200 bg-amber-50 text-amber-700'
      : 'border-slate-200 bg-slate-50 text-slate-600'

  return (
    <span className={`rounded border px-1.5 py-0.5 text-[11px] font-medium ${className}`}>
      {value || '-'}
    </span>
  )
}

function SmallTable({
  headers,
  rows,
}: {
  headers: string[]
  rows: Array<Array<ReactNode>>
}) {
  return (
    <div className="overflow-x-auto rounded-md border border-slate-300 bg-white shadow-sm">
      <table className="w-full min-w-[920px] border-collapse text-left text-xs">
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
                <td
                  key={cellIndex}
                  className="border-r border-slate-100 px-2 py-2 align-top text-slate-700 last:border-r-0"
                >
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

function IdList({ value, tone = 'blue' }: { value: string; tone?: 'blue' | 'green' | 'red' | 'amber' }) {
  const colorClass = {
    blue: 'text-blue-700',
    green: 'text-emerald-700',
    red: 'text-red-700',
    amber: 'text-amber-700',
  }[tone]

  return (
    <span className={`whitespace-pre-wrap font-mono font-semibold ${colorClass}`}>
      {value || '-'}
    </span>
  )
}

function renderSummaryRows(rows: TraceabilitySummaryRow[]) {
  return rows.map((row) => [
    <IdList key="req" value={row.reqId} />,
    row.name || '-',
    row.acCount || '0',
    row.design || '-',
    row.test || '-',
    <StatusBadge key="status" value={row.verification} />,
    row.unresolved || '-',
  ])
}

function renderMatrixRows(rows: TraceabilityRow[]) {
  return rows.map((row) => [
    <IdList key="req" value={row.reqId} />,
    <IdList key="ac" value={row.acId} tone="green" />,
    row.funcId || '-',
    row.scrId || '-',
    row.pgmId || '-',
    row.dbId || '-',
    <IdList key="sec" value={row.secId} tone="red" />,
    row.utId || '-',
    row.itId || '-',
    <StatusBadge key="status" value={row.status} />,
    row.evidence || '-',
  ])
}

function renderSecurityRows(rows: SecurityTraceRow[]) {
  return rows.map((row) => [
    <IdList key="sec" value={row.secId} tone="red" />,
    row.item || '-',
    row.relatedIds || '-',
    row.standard || '-',
    row.tests || '-',
    <StatusBadge key="status" value={row.status} />,
  ])
}

function renderIssueRows(rows: TraceabilityIssueRow[]) {
  return rows.map((row) => [
    <IdList key="issue" value={row.id} tone={row.id.startsWith('FIND-') ? 'red' : 'amber'} />,
    row.type || '-',
    row.relatedIds || '-',
    row.description || '-',
    row.owner || '-',
    <StatusBadge key="status" value={row.status} />,
  ])
}

export default function TraceabilityDocView({
  model,
  summaryOnly = false,
}: {
  model: TraceabilityDocModel
  summaryOnly?: boolean
}) {
  const gaps = countTraceabilityGaps(model.rows)
  const verifiedCount = model.rows.filter((row) => row.status === 'Verified').length
  const openIssues = model.issues.filter((issue) => issue.status !== 'Closed').length

  return (
    <div
      className="space-y-6 rounded-md bg-slate-100 p-4 text-sm text-slate-800"
      data-testid="traceability-doc-view"
    >
      <header className="rounded-md border border-blue-200 bg-gradient-to-r from-blue-50 to-white p-4 shadow-sm">
        <div className="text-xs font-medium text-blue-700">요구사항추적표</div>
        <h2 className="mt-1 text-lg font-semibold text-slate-950">{model.title}</h2>
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">
          <span>프로젝트: <EmptyValue>{model.project}</EmptyValue></span>
          <span>상태: <EmptyValue>{model.status}</EmptyValue></span>
          <span>수정일: <EmptyValue>{model.updatedAt}</EmptyValue></span>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-6">
        <StatPill label="추적 행" value={model.rows.length} />
        <StatPill label="검증 완료" value={verifiedCount} tone={verifiedCount === model.rows.length ? 'good' : 'warn'} />
        <StatPill label="AC 누락" value={gaps.ac} tone={gaps.ac === 0 ? 'good' : 'warn'} />
        <StatPill label="설계 누락" value={gaps.design} tone={gaps.design === 0 ? 'good' : 'warn'} />
        <StatPill label="테스트 누락" value={gaps.test} tone={gaps.test === 0 ? 'good' : 'warn'} />
        <StatPill label="Open 이슈" value={openIssues} tone={openIssues === 0 ? 'good' : 'warn'} />
      </div>

      {!summaryOnly && (
        <>
          {model.summaries.length > 0 && (
            <Section title="요구사항별 검증 요약">
              <SmallTable
                headers={['REQ', '요구사항명', 'AC 수', '설계', '테스트', '검증 상태', '미해결 사항']}
                rows={renderSummaryRows(model.summaries)}
              />
            </Section>
          )}

          <Section title="요구사항 추적 매트릭스">
            <SmallTable
              headers={['REQ', 'AC', 'FUNC', 'SCR', 'PGM', 'DB', 'SEC', 'UT', 'IT', '상태', '증적']}
              rows={renderMatrixRows(model.rows)}
            />
          </Section>

          {model.securityRows.length > 0 && (
            <Section title="보안항목 추적">
              <SmallTable
                headers={['SEC', '보안항목', '관련 ID', '참조 표준', '검증 테스트', '상태']}
                rows={renderSecurityRows(model.securityRows)}
              />
            </Section>
          )}

          {model.issues.length > 0 && (
            <Section title="추적성 결함 목록">
              <SmallTable
                headers={['ID', '유형', '관련 ID', '설명', '담당', '상태']}
                rows={renderIssueRows(model.issues)}
              />
            </Section>
          )}
        </>
      )}
    </div>
  )
}
