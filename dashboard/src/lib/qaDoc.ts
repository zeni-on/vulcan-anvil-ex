import { DocNode } from '@/lib/types'

export interface QaEvidenceRow {
  id: string
  label: string
  path: string
}

export interface QaResultRow {
  id: string
  target: string
  method: string
  result: string
  evidence: string
}

export interface QaFindingRow {
  id: string
  title: string
  severity: string
  status: string
  crRequired: string
  relatedIds: string
}

export interface QaDocModel {
  title: string
  documentKind: 'finding' | 'result' | 'qa'
  project?: string
  status?: string
  updatedAt?: string
  findings: QaFindingRow[]
  results: QaResultRow[]
  evidences: QaEvidenceRow[]
  judgement?: string
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
    const key = keys.find((candidate) => normalizeKey(candidate) === normalizeKey(alias))
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

function tableAfterHeading(content: string, headingPattern: RegExp): MarkdownTable | undefined {
  const match = headingPattern.exec(content)
  if (!match) return undefined
  const rest = content.slice(match.index)
  return extractTables(rest)[0]
}

function keyValueFromTable(table?: MarkdownTable): Record<string, string> {
  const result: Record<string, string> = {}
  if (!table || table.headers.length < 2) return result
  const keyHeader = table.headers[0]
  const valueHeader = table.headers[1]
  for (const row of table.rows) {
    const key = row[keyHeader]?.trim()
    if (key) result[key] = row[valueHeader] ?? ''
  }
  return result
}

function extractJudgement(content: string): string | undefined {
  const codeBlock = content.match(/판정:\s*\n\n```text\n([\s\S]*?)\n```/)
  if (codeBlock?.[1]) return codeBlock[1].trim()

  const section = content.match(/##\s+\d+\.\s+판정\s*\n\n([\s\S]*?)(?:\n##\s+\d+\.|\s*$)/)
  return section?.[1]?.trim()
}

function isImagePath(value: string): boolean {
  return /\.(png|jpe?g|webp|gif)$/i.test(value)
}

function splitEvidencePaths(value: string): string[] {
  return value
    .split(/[,，\n]/)
    .map((item) => item.trim())
    .map((item) => item.replace(/^`|`$/g, ''))
    .filter(isImagePath)
}

function evidenceFileName(value: string): string {
  return value.replace(/\\/g, '/').split('/').pop()?.toLowerCase() ?? value.toLowerCase()
}

function resolveEvidencePath(value: string, knownEvidences: QaEvidenceRow[]): string {
  if (value.includes('/') || value.includes('\\')) return value.replace(/\\/g, '/')

  const fileName = evidenceFileName(value)
  const known = knownEvidences.find((evidence) => evidenceFileName(evidence.path) === fileName)
  if (known) return known.path

  return `docs/artifacts/04-review/evidence/ui/${value}`
}

function splitRelatedIds(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function evidenceMatchesRelatedIds(evidence: QaEvidenceRow, relatedIds: Set<string>): boolean {
  for (const relatedId of relatedIds) {
    if (evidence.id === relatedId || evidence.id.startsWith(`${relatedId}-`)) return true
  }
  return false
}

export function isQaDoc(doc: DocNode, content: string): boolean {
  const joinedSlug = doc.slug.join('/').toLowerCase()
  const name = doc.name.toLowerCase()
  return (
    joinedSlug.includes('04-review') ||
    name.includes('qa-finding') ||
    name.includes('test-result') ||
    content.includes('document_id: DOC-QA-G4-001') ||
    content.includes('document_id: DOC-QA-G4-002')
  )
}

export function parseQaDoc(content: string): QaDocModel {
  const tables = extractTables(content)
  const findingTable = firstTable(tables, ['FIND-ID', '제목', '심각도', '상태'])
  const findingOverview = keyValueFromTable(tableAfterHeading(content, /^##\s+1\.\s+발견사항\s+개요.*$/m))
  const resultTable = firstTable(tables, ['테스트 ID', '관련 REQ', '명령/방법', '결과', '증적'])
    ?? firstTable(tables, ['REQ-ID', '검증 항목', '관련 테스트', '결과', '증적'])
    ?? firstTable(tables, ['검증 ID', '명령/방법', '결과', '요약'])
  const reviewEvidenceTable = firstTable(tables, ['UI-ID', '설명', '캡처 경로'])
  const resultEvidenceTable = firstTable(tables, ['증적 ID', '화면', '경로'])
    ?? firstTable(tables, ['증적 ID', '관련 UI', '파일', '설명'])
  const title = extractMetadata(content, 'title_ko') ?? 'QA 문서'
  const documentId = extractMetadata(content, 'document_id') ?? ''
  const normalizedTitle = `${title} ${extractMetadata(content, 'title') ?? ''} ${content.slice(0, 120)}`.toLowerCase()
  const documentKind: QaDocModel['documentKind'] =
    documentId === 'DOC-QA-G4-001' || normalizedTitle.includes('qa finding') || normalizedTitle.includes('qa 발견사항')
      ? 'finding'
      : documentId === 'DOC-QA-G4-002' || normalizedTitle.includes('test result') || normalizedTitle.includes('테스트 결과')
        ? 'result'
        : 'qa'

  const tableEvidences = [
    ...(reviewEvidenceTable?.rows ?? []).map((row) => ({
      id: getCell(row, ['UI-ID']),
      label: getCell(row, ['설명']),
      path: getCell(row, ['캡처 경로']),
    })),
    ...(resultEvidenceTable?.rows ?? []).map((row) => ({
      id: getCell(row, ['증적 ID']),
      label: getCell(row, ['화면', '관련 UI', '설명']),
      path: getCell(row, ['경로', '파일']),
    })),
  ].filter((row) => isImagePath(row.path))

  const resultEvidences = (resultTable?.rows ?? []).flatMap((row) => {
    const rowId = getCell(row, ['테스트 ID', 'REQ-ID', '검증 ID'])
    return splitEvidencePaths(getCell(row, ['증적'])).map((path, index) => ({
      id: index === 0 ? rowId : `${rowId}-${index + 1}`,
      label: rowId,
      path: resolveEvidencePath(path, tableEvidences),
    }))
  })

  const tableFindings = (findingTable?.rows ?? []).map((row) => ({
    id: getCell(row, ['FIND-ID']),
    title: getCell(row, ['제목']),
    severity: getCell(row, ['심각도']),
    status: getCell(row, ['상태']),
    crRequired: getCell(row, ['CR 필요 여부']),
    relatedIds: getCell(row, ['관련 ID']),
  }))
  const overviewFinding = findingOverview['FIND-ID']
    ? [{
        id: findingOverview['FIND-ID'],
        title: findingOverview['제목'] ?? '',
        severity: findingOverview['심각도'] ?? '',
        status: findingOverview['상태'] ?? '',
        crRequired: findingOverview['CR 필요 여부'] ?? '',
        relatedIds: [
          keyValueFromTable(tableAfterHeading(content, /^##\s+2\.\s+관련\s+추적\s+ID.*$/m))['증적'],
          keyValueFromTable(tableAfterHeading(content, /^##\s+2\.\s+관련\s+추적\s+ID.*$/m))['테스트'],
        ].filter(Boolean).join(', '),
      }]
    : []
  const findings = tableFindings.length > 0 ? tableFindings : overviewFinding
  const allEvidences = [...tableEvidences, ...resultEvidences]
  const relatedEvidenceIds = new Set(
    findings
      .flatMap((finding) => splitRelatedIds(finding.relatedIds))
      .filter((id) => /^(?:UI|EV-UI)-\d+/i.test(id)),
  )
  const relevantFindingEvidences = allEvidences.filter((evidence) =>
    evidenceMatchesRelatedIds(evidence, relatedEvidenceIds),
  )
  const evidences = documentKind === 'finding' && relevantFindingEvidences.length > 0
    ? relevantFindingEvidences
    : allEvidences

  return {
    title,
    documentKind,
    project: extractMetadata(content, 'project'),
    status: extractMetadata(content, 'status'),
    updatedAt: extractMetadata(content, 'updated_at'),
    findings,
    results: (resultTable?.rows ?? []).map((row) => ({
      id: getCell(row, ['테스트 ID', 'REQ-ID', '검증 ID']),
      target: getCell(row, ['관련 REQ', 'REQ-ID']),
      method: getCell(row, ['명령/방법']),
      result: getCell(row, ['결과']),
      evidence: getCell(row, ['증적', '요약']),
    })),
    evidences,
    judgement: extractJudgement(content),
  }
}
