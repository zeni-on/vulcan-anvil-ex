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
    .split(',')
    .map((item) => item.trim())
    .filter(isImagePath)
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
  const resultTable = firstTable(tables, ['테스트 ID', '관련 REQ', '명령/방법', '결과', '증적'])
  const reviewEvidenceTable = firstTable(tables, ['UI-ID', '설명', '캡처 경로'])
  const resultEvidenceTable = firstTable(tables, ['증적 ID', '화면', '경로'])
  const title = extractMetadata(content, 'title_ko') ?? 'QA 문서'
  const documentId = extractMetadata(content, 'document_id') ?? ''

  const tableEvidences = [
    ...(reviewEvidenceTable?.rows ?? []).map((row) => ({
      id: getCell(row, ['UI-ID']),
      label: getCell(row, ['설명']),
      path: getCell(row, ['캡처 경로']),
    })),
    ...(resultEvidenceTable?.rows ?? []).map((row) => ({
      id: getCell(row, ['증적 ID']),
      label: getCell(row, ['화면']),
      path: getCell(row, ['경로']),
    })),
  ].filter((row) => isImagePath(row.path))

  const resultEvidences = (resultTable?.rows ?? []).flatMap((row) =>
    splitEvidencePaths(getCell(row, ['증적'])).map((path, index) => ({
      id: `${getCell(row, ['테스트 ID'])}-${index + 1}`,
      label: getCell(row, ['테스트 ID']),
      path,
    })),
  )

  const findings = (findingTable?.rows ?? []).map((row) => ({
    id: getCell(row, ['FIND-ID']),
    title: getCell(row, ['제목']),
    severity: getCell(row, ['심각도']),
    status: getCell(row, ['상태']),
    crRequired: getCell(row, ['CR 필요 여부']),
    relatedIds: getCell(row, ['관련 ID']),
  }))
  const allEvidences = [...tableEvidences, ...resultEvidences]
  const relatedEvidenceIds = new Set(
    findings.flatMap((finding) => splitRelatedIds(finding.relatedIds)).filter((id) => /^UI-\d+/i.test(id)),
  )
  const relevantFindingEvidences = allEvidences.filter((evidence) =>
    evidenceMatchesRelatedIds(evidence, relatedEvidenceIds),
  )
  const evidences = documentId === 'DOC-QA-G4-001' && relevantFindingEvidences.length > 0
    ? relevantFindingEvidences
    : allEvidences

  return {
    title,
    documentKind: documentId === 'DOC-QA-G4-001' ? 'finding' : documentId === 'DOC-QA-G4-002' ? 'result' : 'qa',
    project: extractMetadata(content, 'project'),
    status: extractMetadata(content, 'status'),
    updatedAt: extractMetadata(content, 'updated_at'),
    findings,
    results: (resultTable?.rows ?? []).map((row) => ({
      id: getCell(row, ['테스트 ID']),
      target: getCell(row, ['관련 REQ']),
      method: getCell(row, ['명령/방법']),
      result: getCell(row, ['결과']),
      evidence: getCell(row, ['증적']),
    })),
    evidences,
    judgement: extractJudgement(content),
  }
}
