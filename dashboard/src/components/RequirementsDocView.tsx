'use client'

import type { ReactNode } from 'react'
import {
  AcceptanceCriteriaRow,
  DecisionRow,
  DetailRequirementRow,
  NonFunctionalRequirementRow,
  RequirementRow,
  RequirementsDocModel,
  SecurityConsiderationRow,
} from '@/lib/requirementsDoc'

function EmptyValue({ children }: { children?: string }) {
  return children ? <>{children}</> : <span className="text-slate-400">-</span>
}

function StatPill({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm">
      <div className="text-[11px] font-medium text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-slate-950">{value}</div>
    </div>
  )
}

function Section({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <section className="space-y-3">
      <h3 className="border-l-4 border-blue-500 pl-2 text-sm font-semibold text-slate-950">
        {title}
      </h3>
      {children}
    </section>
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

function RequirementCard({ req }: { req: RequirementRow }) {
  return (
    <article className="rounded-md border border-slate-200 bg-white p-3 shadow-sm">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs font-semibold text-blue-700">{req.id}</span>
        <h4 className="text-sm font-semibold text-slate-950">{req.name || '요구사항명 미정'}</h4>
        {req.priority && (
          <span className="rounded border border-blue-200 bg-blue-50 px-1.5 py-0.5 text-[11px] font-medium text-blue-700">
            {req.priority}
          </span>
        )}
        {req.status && (
          <span className="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[11px] font-medium text-slate-600">
            {req.status}
          </span>
        )}
      </div>
      <p className="mt-2 text-xs leading-relaxed text-slate-700">
        <EmptyValue>{req.description}</EmptyValue>
      </p>
      {(req.source || req.note) && (
        <div className="mt-2 grid gap-1 border-t border-slate-100 pt-2 text-[11px] text-slate-500 sm:grid-cols-2">
          <div>출처: <EmptyValue>{req.source}</EmptyValue></div>
          <div>비고: <EmptyValue>{req.note}</EmptyValue></div>
        </div>
      )}
    </article>
  )
}

function renderDetailRows(rows: DetailRequirementRow[]) {
  return rows.map((row) => [
    <span key="id" className="font-mono font-semibold text-blue-700">{row.id}</span>,
    row.name || '-',
    row.description || '-',
    <span key="ac" className="font-mono font-semibold text-emerald-700">{row.acId || '-'}</span>,
    row.status || '-',
  ])
}

function renderAcRows(rows: AcceptanceCriteriaRow[]) {
  return rows.map((row) => [
    <span key="id" className="font-mono font-semibold text-emerald-700">{row.id}</span>,
    <span key="req" className="font-mono font-semibold text-blue-700">{row.requirementId || '-'}</span>,
    row.criteria || '-',
    row.verification || '-',
    row.status || '-',
  ])
}

function renderNreqRows(rows: NonFunctionalRequirementRow[]) {
  return rows.map((row) => [
    <span key="id" className="font-mono font-semibold text-amber-700">{row.id}</span>,
    row.category || '-',
    row.name || '-',
    row.description || '-',
    row.verification || '-',
    row.standard || '-',
  ])
}

function renderSecurityRows(rows: SecurityConsiderationRow[]) {
  return rows.map((row) => [
    <span key="id" className="font-mono font-semibold text-red-700">{row.id}</span>,
    row.requirementId || '-',
    row.consideration || '-',
    row.standard || '-',
    row.target || '-',
    row.verification || '-',
  ])
}

function renderDecisionRows(rows: DecisionRow[]) {
  return rows.map((row) => [
    <span key="id" className="font-mono font-semibold text-purple-700">{row.id}</span>,
    row.type || '-',
    row.content || '-',
    row.impact || '-',
    row.owner || '-',
    row.targetGate || '-',
  ])
}

export default function RequirementsDocView({ model }: { model: RequirementsDocModel }) {
  const summaryEntries = Object.entries(model.scopeSummary).filter(([, value]) => value)

  return (
    <div
      className="space-y-6 rounded-md bg-slate-100 p-4 text-sm text-slate-800"
      data-testid="requirements-doc-view"
    >
      <header className="rounded-md border border-blue-200 bg-gradient-to-r from-blue-50 to-white p-4 shadow-sm">
        <div className="text-xs font-medium text-blue-700">요구사항정의서</div>
        <h2 className="mt-1 text-lg font-semibold text-slate-950">{model.title}</h2>
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">
          <span>프로젝트: <EmptyValue>{model.project}</EmptyValue></span>
          <span>상태: <EmptyValue>{model.status}</EmptyValue></span>
          <span>수정일: <EmptyValue>{model.updatedAt}</EmptyValue></span>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
        <StatPill label="상위 REQ" value={model.functionalRequirements.length} />
        <StatPill label="상세 REQ" value={model.detailRequirements.length} />
        <StatPill label="AC" value={model.acceptanceCriteria.length} />
        <StatPill label="NREQ" value={model.nonFunctionalRequirements.length} />
        <StatPill label="SEC" value={model.securityConsiderations.length} />
      </div>

      {summaryEntries.length > 0 && (
        <Section title="범위 요약">
          <div className="grid gap-2 sm:grid-cols-2">
            {summaryEntries.map(([key, value]) => (
              <div key={key} className="rounded-md border border-slate-200 bg-white p-3 shadow-sm">
                <div className="text-[11px] font-medium text-slate-500">{key}</div>
                <div className="mt-1 text-xs font-medium leading-relaxed text-slate-900">{value}</div>
              </div>
            ))}
          </div>
        </Section>
      )}

      <Section title="기능 요구사항">
        {model.functionalRequirements.length > 0 ? (
          <div className="grid gap-3">
            {model.functionalRequirements.map((req) => (
              <RequirementCard key={req.id} req={req} />
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500">등록된 기능 요구사항이 없습니다.</p>
        )}
      </Section>

      {model.detailRequirements.length > 0 && (
        <Section title="상세 요구사항과 AC 매핑">
          <SmallTable
            headers={['상세 REQ', '요구사항명', '설명', 'AC', '상태']}
            rows={renderDetailRows(model.detailRequirements)}
          />
        </Section>
      )}

      {model.acceptanceCriteria.length > 0 && (
        <Section title="인수기준">
          <SmallTable
            headers={['AC', '관련 요구사항', '인수기준', '검증 방식', '상태']}
            rows={renderAcRows(model.acceptanceCriteria)}
          />
        </Section>
      )}

      {model.nonFunctionalRequirements.length > 0 && (
        <Section title="비기능 요구사항">
          <SmallTable
            headers={['NREQ', '구분', '요구사항명', '설명', '검증 기준', '참조 표준']}
            rows={renderNreqRows(model.nonFunctionalRequirements)}
          />
        </Section>
      )}

      {model.securityConsiderations.length > 0 && (
        <Section title="보안 및 개인정보 고려사항">
          <SmallTable
            headers={['SEC', '관련 요구사항', '보안 고려사항', '참조 표준', '적용 대상', '검증 방향']}
            rows={renderSecurityRows(model.securityConsiderations)}
          />
        </Section>
      )}

      {model.decisions.length > 0 && (
        <Section title="확인 필요 및 의사결정">
          <SmallTable
            headers={['ID', '구분', '내용', '영향', '확인 주체', '목표 Gate']}
            rows={renderDecisionRows(model.decisions)}
          />
        </Section>
      )}
    </div>
  )
}
