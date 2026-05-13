import { DocNode } from '@/lib/types'

export interface RequirementRow {
  id: string
  name: string
  description: string
  priority?: string
  source?: string
  status?: string
  note?: string
}

export interface DetailRequirementRow {
  id: string
  name: string
  description: string
  acId: string
  status?: string
}

export interface AcceptanceCriteriaRow {
  id: string
  requirementId: string
  criteria: string
  verification: string
  status?: string
}

export interface NonFunctionalRequirementRow {
  id: string
  category: string
  name: string
  description: string
  verification: string
  standard: string
  priority?: string
  status?: string
}

export interface SecurityConsiderationRow {
  id: string
  requirementId: string
  consideration: string
  standard: string
  target: string
  verification: string
}

export interface DecisionRow {
  id: string
  type: string
  content: string
  impact: string
  owner?: string
  targetGate?: string
}

export interface RequirementsDocModel {
  title: string
  project?: string
  status?: string
  updatedAt?: string
  scopeSummary: Record<string, string>
  functionalRequirements: RequirementRow[]
  detailRequirements: DetailRequirementRow[]
  acceptanceCriteria: AcceptanceCriteriaRow[]
  nonFunctionalRequirements: NonFunctionalRequirementRow[]
  securityConsiderations: SecurityConsiderationRow[]
  decisions: DecisionRow[]
}

interface MarkdownTable {
  heading: string
  headers: string[]
  rows: Record<string, string>[]
}

function cleanCell(cell: string): string {
  return cell
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/`/g, '')
    .replace(/\*\*/g, '')
    .trim()
}

function splitTableRow(line: string): string[] {
  const trimmed = line.trim()
  if (!trimmed.startsWith('|') || !trimmed.endsWith('|')) return []
  return trimmed
    .slice(1, -1)
    .split('|')
    .map(cleanCell)
}

function isDividerRow(line: string): boolean {
  const cells = splitTableRow(line)
  return cells.length > 0 && cells.every((cell) => /^:?-{3,}:?$/.test(cell.trim()))
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
  let heading = ''
  let index = 0

  while (index < lines.length) {
    const line = lines[index]
    const headingMatch = line.match(/^(#{2,6})\s+(.+)$/)
    if (headingMatch) heading = headingMatch[2].trim()

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

      tables.push({ heading, headers, rows })
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

function rowsByIdPrefix(tables: MarkdownTable[], idAlias: string, prefixes: string[]) {
  return tables
    .flatMap((table) => table.rows)
    .filter((row) => {
      const id = getCell(row, [idAlias, 'ID'])
      return prefixes.some((prefix) => id.startsWith(prefix))
    })
}

export function isRequirementsDoc(doc: DocNode, content: string): boolean {
  const joinedSlug = doc.slug.join('/').toLowerCase()
  const name = doc.name.toLowerCase()
  return (
    joinedSlug.includes('01-requirements') ||
    name.includes('requirements-spec') ||
    content.includes('document_id: DOC-CORE-G1-001') ||
    content.includes('# 요구사항정의서')
  )
}

export function parseRequirementsDoc(content: string): RequirementsDocModel {
  const tables = extractTables(content)
  const scopeTable = firstTable(tables, ['항목', '내용'])
  const functionalTable = firstTable(tables, ['REQ-ID', '요구사항명', '설명'])
  const detailTable =
    firstTable(tables, ['상세 REQ-ID', '상세 요구사항명', '관련 AC-ID']) ??
    firstTable(tables, ['REQ-ID', '상세 요구사항명', '관련 AC-ID'])
  const acTable = firstTable(tables, ['AC-ID', '관련 요구사항', '인수기준', '검증 방식'])
  const nreqTable = firstTable(tables, ['NREQ-ID', '구분', '요구사항명', '측정/검증 기준'])
  const securityTable = firstTable(tables, ['SEC-ID', '관련 요구사항', '보안 고려사항'])
  const decisionRows = rowsByIdPrefix(tables, 'ID', ['DEC-', 'ASM-'])

  const scopeSummary = Object.fromEntries(
    (scopeTable?.rows ?? [])
      .map((row) => [getCell(row, ['항목']), getCell(row, ['내용'])])
      .filter(([key]) => key),
  )

  return {
    title: extractMetadata(content, 'title_ko') ?? '요구사항정의서',
    project: extractMetadata(content, 'project'),
    status: extractMetadata(content, 'status'),
    updatedAt: extractMetadata(content, 'updated_at'),
    scopeSummary,
    functionalRequirements: (functionalTable?.rows ?? [])
      .map((row) => ({
        id: getCell(row, ['REQ-ID']),
        name: getCell(row, ['요구사항명']),
        description: getCell(row, ['설명']),
        priority: getCell(row, ['우선순위']),
        source: getCell(row, ['출처/외부 ID', '외부 ID']),
        status: getCell(row, ['상태']),
        note: getCell(row, ['비고']),
      }))
      .filter((row) => row.id.startsWith('REQ-') && row.id !== 'REQ-NNN'),
    detailRequirements: (detailTable?.rows ?? [])
      .map((row) => ({
        id: getCell(row, ['상세 REQ-ID', 'REQ-ID']),
        name: getCell(row, ['상세 요구사항명']),
        description: getCell(row, ['설명']),
        acId: getCell(row, ['관련 AC-ID']),
        status: getCell(row, ['상태']),
      }))
      .filter((row) => /^REQ-\d{3}-\d{2}$/.test(row.id)),
    acceptanceCriteria: (acTable?.rows ?? [])
      .map((row) => ({
        id: getCell(row, ['AC-ID']),
        requirementId: getCell(row, ['관련 요구사항']),
        criteria: getCell(row, ['인수기준']),
        verification: getCell(row, ['검증 방식']),
        status: getCell(row, ['상태']),
      }))
      .filter((row) => row.id.startsWith('AC-') && row.id !== 'AC-NNN-NN'),
    nonFunctionalRequirements: (nreqTable?.rows ?? [])
      .map((row) => ({
        id: getCell(row, ['NREQ-ID']),
        category: getCell(row, ['구분']),
        name: getCell(row, ['요구사항명']),
        description: getCell(row, ['설명']),
        verification: getCell(row, ['측정/검증 기준']),
        standard: getCell(row, ['참조 표준']),
        priority: getCell(row, ['우선순위']),
        status: getCell(row, ['상태']),
      }))
      .filter((row) => row.id.startsWith('NREQ-') && row.id !== 'NREQ-NNN'),
    securityConsiderations: (securityTable?.rows ?? [])
      .map((row) => ({
        id: getCell(row, ['SEC-ID']),
        requirementId: getCell(row, ['관련 요구사항']),
        consideration: getCell(row, ['보안 고려사항']),
        standard: getCell(row, ['참조 표준']),
        target: getCell(row, ['적용 대상']),
        verification: getCell(row, ['검증 방향']),
      }))
      .filter((row) => row.id.startsWith('SEC-') && Boolean(row.consideration || row.standard)),
    decisions: decisionRows
      .map((row) => ({
        id: getCell(row, ['ID']),
        type: getCell(row, ['구분']),
        content: getCell(row, ['내용']),
        impact: getCell(row, ['영향']),
        owner: getCell(row, ['확인 주체']),
        targetGate: getCell(row, ['목표 Gate']),
      }))
      .filter((row) => row.content || row.impact),
  }
}
