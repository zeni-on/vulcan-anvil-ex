import { DocNode } from '@/lib/types'

export interface ScreenListRow {
  scrId: string
  name: string
  type: string
  funcId: string
  pgmId: string
  secId: string
  status: string
}

export interface ScreenEvidenceRow {
  scrId: string
  refId: string
  source: string
  file: string
  viewport: string
  criteria: string
  status: string
}

export interface ScreenDetail {
  scrId: string
  name: string
  fields: Record<string, string>
  wireframe?: string
  stateText?: string
}

export interface ScreenSpecDocModel {
  title: string
  project?: string
  status?: string
  updatedAt?: string
  screens: ScreenListRow[]
  evidences: ScreenEvidenceRow[]
  details: ScreenDetail[]
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

function extractScreenDetails(content: string): ScreenDetail[] {
  const sections = [...content.matchAll(/^###\s+(?:\d+(?:\.\d+)?\s+)?(SCR-\d{3})\s+(.+)$/gm)]
  return sections.map((match, index) => {
    const start = match.index ?? 0
    const end = sections[index + 1]?.index ?? content.length
    const block = content.slice(start, end)
    const table = firstTable(extractTables(block), ['항목', '내용'])
    const fields = Object.fromEntries(
      (table?.rows ?? [])
        .map((row) => [getCell(row, ['항목']), getCell(row, ['내용'])])
        .filter(([key]) => key),
    )
    const wireframe = block.match(/텍스트 와이어프레임:\s*\n\n```text\n([\s\S]*?)\n```/)?.[1]?.trim()
    const stateText = block.match(/상태:\s*([^\n]+)/)?.[1]?.trim()
    return {
      scrId: match[1],
      name: match[2].trim(),
      fields,
      wireframe,
      stateText,
    }
  })
}

export function isScreenSpecDoc(doc: DocNode, content: string): boolean {
  const joinedSlug = doc.slug.join('/').toLowerCase()
  const name = doc.name.toLowerCase()
  return (
    joinedSlug.includes('02-design/screen') ||
    name.includes('screen-spec') ||
    content.includes('document_id: DOC-CORE-G2-003') ||
    content.includes('# 화면설계서')
  )
}

export function parseScreenSpecDoc(content: string): ScreenSpecDocModel {
  const tables = extractTables(content)
  const screenTable = firstTable(tables, ['SCR-ID', '화면명', '유형'])
  const evidenceTable = firstTable(tables, ['SCR-ID', '시안/와이어프레임 ID', '파일/URL'])

  return {
    title: extractMetadata(content, 'title_ko') ?? '화면설계서',
    project: extractMetadata(content, 'project'),
    status: extractMetadata(content, 'status'),
    updatedAt: extractMetadata(content, 'updated_at'),
    screens: (screenTable?.rows ?? [])
      .map((row) => ({
        scrId: getCell(row, ['SCR-ID']),
        name: getCell(row, ['화면명']),
        type: getCell(row, ['유형']),
        funcId: getCell(row, ['관련 FUNC']),
        pgmId: getCell(row, ['관련 PGM']),
        secId: getCell(row, ['관련 SEC']),
        status: getCell(row, ['상태']),
      }))
      .filter((row) => row.scrId.startsWith('SCR-') && Boolean(row.name || row.funcId || row.pgmId)),
    evidences: (evidenceTable?.rows ?? [])
      .map((row) => ({
        scrId: getCell(row, ['SCR-ID']),
        refId: getCell(row, ['시안/와이어프레임 ID']),
        source: getCell(row, ['출처']),
        file: getCell(row, ['파일/URL']),
        viewport: getCell(row, ['기준 Viewport']),
        criteria: getCell(row, ['비교 기준']),
        status: getCell(row, ['상태']),
      }))
      .filter((row) => row.scrId.startsWith('SCR-') && row.refId),
    details: extractScreenDetails(content),
  }
}
