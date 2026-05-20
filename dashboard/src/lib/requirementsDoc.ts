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

export interface DetailRequirementDefinitionRow {
  id: string
  name: string
  description: string
  priority?: string
  related?: string
  openQuestion?: string
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

export interface RequirementStatusRow {
  type: string
  count: string
  ids: string
  status: string
}

export interface GlossaryRow {
  term: string
  definition: string
  note?: string
}

export interface IncludedScopeRow {
  no: string
  content: string
  relatedId: string
}

export interface ExcludedScopeRow {
  no: string
  content: string
  reason: string
  note?: string
}

export interface DataStandardRow {
  name: string
  requirementId: string
  standardTerm: string
  abbreviation: string
  domain: string
  compliance: string
  note?: string
}

export interface ChangeHistoryRow {
  version: string
  date: string
  change: string
  author: string
  reviewer?: string
  approver?: string
}

export interface ReviewChecklistRow {
  item: string
  checked: string
}

export interface RequirementsDocModel {
  title: string
  project?: string
  status?: string
  updatedAt?: string
  purpose: string[]
  writingCriteria: string[]
  scopeSummary: Record<string, string>
  requirementStatus: RequirementStatusRow[]
  projectOverview: Record<string, string>
  glossary: GlossaryRow[]
  functionalRequirements: RequirementRow[]
  detailRequirementDefinitions: DetailRequirementDefinitionRow[]
  detailRequirements: DetailRequirementRow[]
  acceptanceCriteria: AcceptanceCriteriaRow[]
  nonFunctionalRequirements: NonFunctionalRequirementRow[]
  securityConsiderations: SecurityConsiderationRow[]
  decisions: DecisionRow[]
  includedScope: IncludedScopeRow[]
  excludedScope: ExcludedScopeRow[]
  dataStandardConsiderations: DataStandardRow[]
  changeHistory: ChangeHistoryRow[]
  reviewChecklist: ReviewChecklistRow[]
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

function firstTableByHeading(
  tables: MarkdownTable[],
  heading: string,
  headers: string[],
): MarkdownTable | undefined {
  const normalizedHeading = normalizeKey(heading)
  return tables.find(
    (table) => normalizeKey(table.heading).includes(normalizedHeading) && hasHeaders(table, headers),
  )
}

function tablesByHeaders(tables: MarkdownTable[], headers: string[]): MarkdownTable[] {
  return tables.filter((table) => hasHeaders(table, headers))
}

function rowsByIdPrefix(tables: MarkdownTable[], idAlias: string, prefixes: string[]) {
  return tables
    .flatMap((table) => table.rows)
    .filter((row) => {
      const id = getCell(row, [idAlias, 'ID'])
      return prefixes.some((prefix) => id.startsWith(prefix))
    })
}

function extractSectionContent(content: string, heading: string): string[] {
  const lines = content.split(/\r?\n/)
  const headingPattern = new RegExp(`^#{2,6}\\s+${heading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*$`)
  const startIndex = lines.findIndex((line) => headingPattern.test(line.trim()))
  if (startIndex === -1) return []

  const startLevel = lines[startIndex].match(/^(#{2,6})/)?.[1].length ?? 2
  const collected: string[] = []

  for (let index = startIndex + 1; index < lines.length; index += 1) {
    const line = lines[index]
    const nextHeading = line.match(/^(#{2,6})\s+/)
    if (nextHeading && nextHeading[1].length <= startLevel) break

    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('|') || isDividerRow(trimmed)) continue
    collected.push(trimmed.replace(/^-+\s*/, ''))
  }

  return collected
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
  const scopeTable = firstTableByHeading(tables, '범위 요약', ['항목', '내용']) ?? firstTable(tables, ['항목', '내용'])
  const requirementStatusTable = firstTable(tables, ['구분', '수량', '주요 ID', '상태/비고'])
  const projectOverviewTable = firstTableByHeading(tables, '프로젝트 개요', ['항목', '내용'])
  const glossaryTable = firstTable(tables, ['용어', '정의', '비고'])
  const functionalTable = firstTable(tables, ['REQ-ID', '요구사항명', '설명'])
  const detailDefinitionTables = tablesByHeaders(tables, [
    '상세 REQ-ID',
    '상세 요구사항명',
    '관련 NREQ/SEC',
  ])
  const detailTable =
    firstTable(tables, ['상세 REQ-ID', '상세 요구사항명', '관련 AC-ID']) ??
    firstTable(tables, ['REQ-ID', '상세 요구사항명', '관련 AC-ID'])
  const acTable = firstTable(tables, ['AC-ID', '관련 요구사항', '인수기준', '검증 방식'])
  const nreqTable = firstTable(tables, ['NREQ-ID', '구분', '요구사항명', '측정/검증 기준'])
  const securityTable = firstTable(tables, ['SEC-ID', '관련 요구사항', '보안 고려사항'])
  const includedScopeTable = firstTableByHeading(tables, '포함 범위', ['번호', '내용', '관련 ID'])
  const excludedScopeTable = firstTableByHeading(tables, '제외 범위', ['번호', '내용', '제외 사유'])
  const dataStandardTable = firstTable(tables, ['항목명', '관련 요구사항', '공공데이터 표준 용어'])
  const changeHistoryTable = firstTable(tables, ['버전', '일자', '변경내용', '작성자'])
  const reviewChecklistTable = firstTableByHeading(tables, '검토 체크리스트', ['항목', '확인'])
  const decisionRows = rowsByIdPrefix(tables, 'ID', ['DEC-', 'ASM-'])

  const scopeSummary = Object.fromEntries(
    (scopeTable?.rows ?? [])
      .map((row) => [getCell(row, ['항목']), getCell(row, ['내용'])])
      .filter(([key]) => key),
  )

  const projectOverview = Object.fromEntries(
    (projectOverviewTable?.rows ?? [])
      .map((row) => [getCell(row, ['항목']), getCell(row, ['내용'])])
      .filter(([key]) => key),
  )

  return {
    title: extractMetadata(content, 'title_ko') ?? '요구사항정의서',
    project: extractMetadata(content, 'project'),
    status: extractMetadata(content, 'status'),
    updatedAt: extractMetadata(content, 'updated_at'),
    purpose: extractSectionContent(content, '1. 문서 목적'),
    writingCriteria: extractSectionContent(content, '2. 작성 기준'),
    scopeSummary,
    requirementStatus: (requirementStatusTable?.rows ?? [])
      .map((row) => ({
        type: getCell(row, ['구분']),
        count: getCell(row, ['수량']),
        ids: getCell(row, ['주요 ID']),
        status: getCell(row, ['상태/비고']),
      }))
      .filter((row) => row.type),
    projectOverview,
    glossary: (glossaryTable?.rows ?? [])
      .map((row) => ({
        term: getCell(row, ['용어']),
        definition: getCell(row, ['정의']),
        note: getCell(row, ['비고']),
      }))
      .filter((row) => row.term),
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
    detailRequirementDefinitions: detailDefinitionTables
      .flatMap((table) => table.rows)
      .map((row) => ({
        id: getCell(row, ['상세 REQ-ID']),
        name: getCell(row, ['상세 요구사항명']),
        description: getCell(row, ['설명']),
        priority: getCell(row, ['우선순위']),
        related: getCell(row, ['관련 NREQ/SEC']),
        openQuestion: getCell(row, ['확인 필요 사항']),
      }))
      .filter((row) => /^REQ-\d{3}-\d{2}$/.test(row.id)),
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
    includedScope: (includedScopeTable?.rows ?? [])
      .map((row) => ({
        no: getCell(row, ['번호']),
        content: getCell(row, ['내용']),
        relatedId: getCell(row, ['관련 ID']),
      }))
      .filter((row) => row.no || row.content),
    excludedScope: (excludedScopeTable?.rows ?? [])
      .map((row) => ({
        no: getCell(row, ['번호']),
        content: getCell(row, ['내용']),
        reason: getCell(row, ['제외 사유']),
        note: getCell(row, ['비고']),
      }))
      .filter((row) => row.no || row.content),
    dataStandardConsiderations: (dataStandardTable?.rows ?? [])
      .map((row) => ({
        name: getCell(row, ['항목명']),
        requirementId: getCell(row, ['관련 요구사항']),
        standardTerm: getCell(row, ['공공데이터 표준 용어']),
        abbreviation: getCell(row, ['영문 약어']),
        domain: getCell(row, ['도메인']),
        compliance: getCell(row, ['표준 준용 여부']),
        note: getCell(row, ['비고']),
      }))
      .filter((row) => row.name),
    changeHistory: (changeHistoryTable?.rows ?? [])
      .map((row) => ({
        version: getCell(row, ['버전']),
        date: getCell(row, ['일자']),
        change: getCell(row, ['변경내용']),
        author: getCell(row, ['작성자']),
        reviewer: getCell(row, ['검토자']),
        approver: getCell(row, ['승인자']),
      }))
      .filter((row) => row.version || row.change),
    reviewChecklist: (reviewChecklistTable?.rows ?? [])
      .map((row) => ({
        item: getCell(row, ['항목']),
        checked: getCell(row, ['확인']),
      }))
      .filter((row) => row.item),
  }
}
