'use client'

import type { ReactNode } from 'react'
import {
  ScreenDetail,
  ScreenEvidenceRow,
  ScreenListRow,
  ScreenSpecDocModel,
  ScreenTable,
} from '@/lib/screenSpecDoc'

function encodeDocPath(path: string): string {
  return path.split('/').map(encodeURIComponent).join('/')
}

function imageUrl(projectId: string, path: string) {
  return `/api/projects/${encodeURIComponent(projectId)}/raw/${encodeDocPath(path)}`
}

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

function IdText({ value, tone = 'blue' }: { value: string; tone?: 'blue' | 'red' | 'green' }) {
  const colorClass = {
    blue: 'text-blue-700',
    red: 'text-red-700',
    green: 'text-emerald-700',
  }[tone]

  return <span className={`font-mono font-semibold ${colorClass}`}>{value || '-'}</span>
}

function renderScreenRows(rows: ScreenListRow[]) {
  return rows.map((row) => [
    <IdText key="scr" value={row.scrId} />,
    row.name || '-',
    row.type || '-',
    row.funcId || '-',
    row.pgmId || '-',
    <IdText key="sec" value={row.secId} tone="red" />,
    row.status || '-',
  ])
}

function DesignTable({ table }: { table: ScreenTable }) {
  return (
    <div>
      <div className="mb-1 text-[11px] font-semibold text-slate-600">{table.title}</div>
      <SmallTable headers={table.headers} rows={table.rows} />
    </div>
  )
}

function EvidencePreview({ row, projectId }: { row: ScreenEvidenceRow; projectId: string }) {
  const isImage = /\.(png|jpe?g|gif|webp|svg)$/i.test(row.file)
  if (!isImage) return <span className="break-all">{row.file || '-'}</span>

  return (
    <div className="space-y-1">
      <span className="break-all font-mono text-[11px] text-slate-600">{row.file}</span>
      <img
        src={imageUrl(projectId, row.file)}
        alt={`${row.refId} ${row.scrId}`}
        className="max-h-28 rounded border border-slate-200 bg-white object-contain"
        loading="lazy"
      />
    </div>
  )
}

function renderEvidenceRows(rows: ScreenEvidenceRow[], projectId: string) {
  return rows.map((row) => [
    <IdText key="scr" value={row.scrId} />,
    <IdText key="ref" value={row.refId} tone="green" />,
    row.source || '-',
    <EvidencePreview key="file" row={row} projectId={projectId} />,
    row.viewport || '-',
    row.criteria || '-',
    row.status || '-',
  ])
}

function ScreenCard({ detail }: { detail: ScreenDetail }) {
  const relatedReq = detail.fields['관련 요구사항']
  const relatedAc = detail.fields['관련 인수기준']
  const auth = detail.fields['접근 권한']
  const structure = detail.fields['화면 구조']

  return (
    <article className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center gap-2">
        <IdText value={detail.scrId} />
        <h4 className="text-sm font-semibold text-slate-950">{detail.name}</h4>
        {auth && (
          <span className="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[11px] font-medium text-slate-600">
            {auth}
          </span>
        )}
      </div>

      <div className="mt-3 grid gap-2 text-xs sm:grid-cols-2">
        <div className="rounded border border-slate-200 bg-slate-50 p-2">
          <div className="text-[11px] font-medium text-slate-500">관련 요구사항</div>
          <div className="mt-1 text-slate-800"><EmptyValue>{relatedReq}</EmptyValue></div>
        </div>
        <div className="rounded border border-slate-200 bg-slate-50 p-2">
          <div className="text-[11px] font-medium text-slate-500">관련 인수기준</div>
          <div className="mt-1 text-slate-800"><EmptyValue>{relatedAc}</EmptyValue></div>
        </div>
      </div>

      {structure && (
        <div className="mt-3 rounded border border-slate-200 bg-slate-50 p-2 text-xs text-slate-800">
          <div className="mb-1 text-[11px] font-medium text-slate-500">화면 구조</div>
          {structure}
        </div>
      )}

      {detail.wireframe && (
        <div className="mt-3">
          <div className="mb-1 text-[11px] font-semibold text-slate-600">텍스트 와이어프레임</div>
          <pre className="overflow-x-auto rounded-md border border-slate-300 bg-slate-950 p-3 text-xs leading-relaxed text-slate-100">
            <code>{detail.wireframe}</code>
          </pre>
        </div>
      )}

      {detail.stateText && (
        <div className="mt-3 rounded border border-blue-200 bg-blue-50 p-2 text-xs text-slate-800">
          <span className="font-semibold text-blue-800">상태: </span>
          {detail.stateText}
        </div>
      )}

      {detail.tables.length > 0 && (
        <div className="mt-4 space-y-3">
          {detail.tables.map((table, index) => (
            <DesignTable key={`${detail.scrId}-${table.title}-${index}`} table={table} />
          ))}
        </div>
      )}
    </article>
  )
}

export default function ScreenSpecDocView({
  model,
  projectId,
}: {
  model: ScreenSpecDocModel
  projectId: string
}) {
  return (
    <div
      className="space-y-6 rounded-md bg-slate-100 p-4 text-sm text-slate-800"
      data-testid="screen-spec-doc-view"
    >
      <header className="rounded-md border border-blue-200 bg-gradient-to-r from-blue-50 to-white p-4 shadow-sm">
        <div className="text-xs font-medium text-blue-700">Screen Specification</div>
        <h2 className="mt-1 text-lg font-semibold text-slate-950">{model.title}</h2>
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">
          <span>프로젝트: <EmptyValue>{model.project}</EmptyValue></span>
          <span>상태: <EmptyValue>{model.status}</EmptyValue></span>
          <span>수정일: <EmptyValue>{model.updatedAt}</EmptyValue></span>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        <StatPill label="화면" value={model.screens.length} />
        <StatPill label="와이어프레임" value={model.details.filter((detail) => detail.wireframe).length} />
        <StatPill label="시안/증적 기준" value={model.evidences.length} />
      </div>

      <Section title="화면 목록">
        <SmallTable
          headers={['SCR', '화면명', '유형', 'FUNC', 'PGM', 'SEC', '상태']}
          rows={renderScreenRows(model.screens)}
        />
      </Section>

      {model.evidences.length > 0 && (
        <Section title="화면 시안 및 기준 증적">
          <SmallTable
            headers={['SCR', 'UIREF', '출처', '파일/URL', 'Viewport', '비교 기준', '상태']}
            rows={renderEvidenceRows(model.evidences, projectId)}
          />
        </Section>
      )}

      <Section title="화면 상세 및 와이어프레임">
        <div className="grid gap-3">
          {model.details.map((detail) => (
            <ScreenCard key={detail.scrId} detail={detail} />
          ))}
        </div>
      </Section>

      {model.extraTables.length > 0 && (
        <Section title="추가 설계 표">
          <div className="space-y-3">
            {model.extraTables.map((table, index) => (
              <DesignTable key={`${table.title}-${index}`} table={table} />
            ))}
          </div>
        </Section>
      )}
    </div>
  )
}
