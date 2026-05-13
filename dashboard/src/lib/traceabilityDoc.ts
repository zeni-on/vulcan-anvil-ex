import { DocNode } from '@/lib/types'

export interface TraceabilityRow {
  reqId: string
  nreqId: string
  acId: string
  funcId: string
  scrId: string
  pgmId: string
  dbId: string
  secId: string
  standard: string
  utId: string
  itId: string
  ptId: string
  status: string
  evidence: string
  note: string
}

export interface TraceabilitySummaryRow {
  reqId: string
  name: string
  acCount: string
  design: string
  test: string
  verification: string
  unresolved: string
}

export interface SecurityTraceRow {
  secId: string
  item: string
  relatedIds: string
  standard: string
  target: string
  tests: string
  evidence: string
  status: string
}

export interface TraceabilityIssueRow {
  id: string
  type: string
  relatedIds: string
  description: string
  owner: string
  status: string
}

export interface TraceabilityDocModel {
  title: string
  project?: string
  status?: string
  updatedAt?: string
  rows: TraceabilityRow[]
  summaries: TraceabilitySummaryRow[]
  securityRows: SecurityTraceRow[]
  issues: TraceabilityIssueRow[]
}

interface MarkdownTable {
  headers: string[]
  rows: Record<string, string>[]
}

function cleanCell(cell: string): string {
  return cell.replace(/`/g, '').replace(/\*\*/g, '').trim()
}

function splitTableRow(line: string): string[] {
  const trimmed = line.trim()
  if (!trimmed.startsWith('|') || !trimmed.endsWith('|')) return []
  return trimmed.slice(1, -1).split('|').map(cleanCell)
}

function isDividerRow(line: string): boolean {
  const cells = splitTableRow(line)
  return cells.length > 0 && cells.every((cell) => /^:?-{3,}:?$/.test(cell))
}

function normalizeKey(value: string): string {
  return value.replace(/\s+/g, '').toLowerCase()
}

function getCell(row: Record<string, string>, aliases: string[]): string {
  const keys = Object.keys(row)
  for (const alias of aliases) {
    const normalizedAlias = normalizeKey(alias)
    const key = keys.find((candidate) => normalizeKey(candidate) === normalizedAlias)
    if (key) return row[key] ?? ''
  }
  return ''
}

function extractMetadata(content: string, key: string): string | undefined {
  const match = content.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'))
  return match?.[1]?.trim()
}

function extractTables(content: string): MarkdownTable[] {
  const lines = content.split(/\r?\n/)
  const tables: MarkdownTable[] = []
  let index = 0

  while (index < lines.length) {
    const line = lines[index]
    const next = lines[index + 1]
    if (line.trim().startsWith('|') && next && isDividerRow(next)) {
      const headers = splitTableRow(line)
      const rows: Record<string, string>[] = []
      index += 2

      while (index < lines.length && lines[index].trim().startsWith('|')) {
        const cells = splitTableRow(lines[index])
        if (cells.length === headers.length) {
          const row: Record<string, string> = {}
          headers.forEach((header, cellIndex) => {
            row[header] = cells[cellIndex] ?? ''
          })
          rows.push(row)
        }
        index += 1
      }

      tables.push({ headers, rows })
      continue
    }
    index += 1
  }

  return tables
}

function hasHeaders(table: MarkdownTable, headers: string[]): boolean {
  const normalized = table.headers.map(normalizeKey)
  return headers.every((header) => normalized.includes(normalizeKey(header)))
}

function firstTable(tables: MarkdownTable[], headers: string[]): MarkdownTable | undefined {
  return tables.find((table) => hasHeaders(table, headers))
}

function isPlaceholder(value: string): boolean {
  const normalized = value.trim()
  return (
    normalized === '' ||
    normalized === '미정' ||
    normalized === '확인필요' ||
    normalized === 'REQ-' ||
    normalized === 'AC-001'
  )
}

function isMissingVerification(value: string): boolean {
  const normalized = value.trim()
  return isPlaceholder(normalized) || normalized === '해당없음'
}

export function isTraceabilityDoc(doc: DocNode, content: string): boolean {
  const joinedSlug = doc.slug.join('/').toLowerCase()
  const name = doc.name.toLowerCase()
  return (
    joinedSlug.includes('02-traceability') ||
    name.includes('traceability-matrix') ||
    content.includes('document_id: DOC-CORE-G4-001') ||
    content.includes('# 요구사항추적표')
  )
}

export function parseTraceabilityDoc(content: string): TraceabilityDocModel {
  const tables = extractTables(content)
  const matrixTable = firstTable(tables, ['REQ-ID', 'AC-ID', 'FUNC-ID', 'SCR-ID', 'PGM-ID', '상태'])
  const summaryTable = firstTable(tables, ['REQ-ID', '요구사항명', '인수기준 수', '검증 상태'])
  const securityTable = firstTable(tables, ['SEC-ID', '보안항목', '관련 REQ/NREQ', '검증 테스트'])
  const issueTable = firstTable(tables, ['결함 ID', '결함 유형', '관련 ID', '상태'])

  return {
    title: extractMetadata(content, 'title_ko') ?? '요구사항추적표',
    project: extractMetadata(content, 'project'),
    status: extractMetadata(content, 'status'),
    updatedAt: extractMetadata(content, 'updated_at'),
    rows: (matrixTable?.rows ?? [])
      .map((row) => ({
        reqId: getCell(row, ['REQ-ID']),
        nreqId: getCell(row, ['NREQ-ID']),
        acId: getCell(row, ['AC-ID']),
        funcId: getCell(row, ['FUNC-ID']),
        scrId: getCell(row, ['SCR-ID']),
        pgmId: getCell(row, ['PGM-ID']),
        dbId: getCell(row, ['DB-ID']),
        secId: getCell(row, ['SEC-ID']),
        standard: getCell(row, ['참조 표준']),
        utId: getCell(row, ['UT-ID']),
        itId: getCell(row, ['IT-ID']),
        ptId: getCell(row, ['PT-ID']),
        status: getCell(row, ['상태']),
        evidence: getCell(row, ['증적']),
        note: getCell(row, ['비고']),
      }))
      .filter((row) => row.reqId.startsWith('REQ-') && row.reqId !== 'REQ-001'),
    summaries: (summaryTable?.rows ?? [])
      .map((row) => ({
        reqId: getCell(row, ['REQ-ID']),
        name: getCell(row, ['요구사항명']),
        acCount: getCell(row, ['인수기준 수']),
        design: getCell(row, ['설계 연결']),
        test: getCell(row, ['테스트 연결']),
        verification: getCell(row, ['검증 상태']),
        unresolved: getCell(row, ['미해결 사항']),
      }))
      .filter((row) => row.reqId.startsWith('REQ-')),
    securityRows: (securityTable?.rows ?? [])
      .map((row) => ({
        secId: getCell(row, ['SEC-ID']),
        item: getCell(row, ['보안항목']),
        relatedIds: getCell(row, ['관련 REQ/NREQ']),
        standard: getCell(row, ['참조 표준']),
        target: getCell(row, ['적용 대상']),
        tests: getCell(row, ['검증 테스트']),
        evidence: getCell(row, ['증적']),
        status: getCell(row, ['상태']),
      }))
      .filter((row) => row.secId.startsWith('SEC-') && Boolean(row.item || row.standard)),
    issues: (issueTable?.rows ?? [])
      .map((row) => ({
        id: getCell(row, ['결함 ID']),
        type: getCell(row, ['결함 유형']),
        relatedIds: getCell(row, ['관련 ID']),
        description: getCell(row, ['설명']),
        owner: getCell(row, ['조치 담당']),
        status: getCell(row, ['상태']),
      }))
      .filter((row) => Boolean(row.id || row.description)),
  }
}

export function countTraceabilityGaps(rows: TraceabilityRow[]) {
  return rows.reduce(
    (acc, row) => {
      if (isPlaceholder(row.acId)) acc.ac += 1
      if (isPlaceholder(row.funcId) || isPlaceholder(row.scrId) || isPlaceholder(row.pgmId)) {
        acc.design += 1
      }
      if (
        isMissingVerification(row.utId) &&
        isMissingVerification(row.itId) &&
        isMissingVerification(row.ptId)
      ) {
        acc.test += 1
      }
      if (isPlaceholder(row.evidence)) acc.evidence += 1
      return acc
    },
    { ac: 0, design: 0, test: 0, evidence: 0 },
  )
}
