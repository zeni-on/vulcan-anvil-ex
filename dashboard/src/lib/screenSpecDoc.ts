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
  tables: ScreenTable[]
}

export interface ScreenTable {
  title: string
  headers: string[]
  rows: string[][]
}

export interface ScreenSpecDocModel {
  title: string
  project?: string
  status?: string
  updatedAt?: string
  screens: ScreenListRow[]
  evidences: ScreenEvidenceRow[]
  details: ScreenDetail[]
  extraTables: ScreenTable[]
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

function toScreenTable(title: string, table: MarkdownTable): ScreenTable {
  return {
    title,
    headers: table.headers,
    rows: table.rows.map((row) => table.headers.map((header) => row[header] ?? '')),
  }
}

function extractTitledTables(content: string): ScreenTable[] {
  const lines = content.split(/\r?\n/)
  const tables: ScreenTable[] = []
  let currentHeading = '표'
  let index = 0

  while (index < lines.length) {
    const headingMatch = lines[index].match(/^#{2,6}\s+(.+?)\s*$/)
    if (headingMatch) currentHeading = headingMatch[1].trim()

    const line = lines[index]
    const next = lines[index + 1]
    if (line.trim().startsWith('|') && next && isDividerRow(next)) {
      const headers = splitTableRow(line)
      const rows: string[][] = []
      index += 2

      while (index < lines.length && lines[index].trim().startsWith('|')) {
        const cells = splitTableRow(lines[index])
        if (cells.length === headers.length) rows.push(cells)
        index += 1
      }

      tables.push({ title: currentHeading, headers, rows })
      continue
    }
    index += 1
  }

  return tables
}

function isMetadataTable(table: ScreenTable): boolean {
  return (
    hasHeaders({ headers: table.headers, rows: [] }, ['항목', '내용']) ||
    hasHeaders({ headers: table.headers, rows: [] }, ['SCR-ID', '화면명', '유형']) ||
    hasHeaders({ headers: table.headers, rows: [] }, ['SCR-ID', '시안/와이어프레임 ID', '파일/URL'])
  )
}

function tableKey(table: ScreenTable): string {
  return JSON.stringify([table.title, table.headers, table.rows])
}

function extractScreenDetails(content: string): ScreenDetail[] {
  const sections = [...content.matchAll(/^###\s+(?:\d+(?:\.\d+)?\s+)?(SCR-\d{3})\s+(.+)$/gm)]
  return sections.map((match, index) => {
    const start = match.index ?? 0
    const nextScreenStart = sections[index + 1]?.index ?? content.length
    const afterHeading = content.indexOf('\n', start)
    const searchStart = afterHeading >= 0 ? afterHeading + 1 : start + 1
    const nextTopLevelSection = content.slice(searchStart).search(/^##\s+/m)
    const nextTopLevelStart =
      nextTopLevelSection >= 0 ? searchStart + nextTopLevelSection : content.length
    const end = Math.min(nextScreenStart, nextTopLevelStart)
    const block = content.slice(start, end)
    const table = firstTable(extractTables(block), ['항목', '내용'])
    const fields = Object.fromEntries(
      (table?.rows ?? [])
        .map((row) => [getCell(row, ['항목']), getCell(row, ['내용'])])
        .filter(([key]) => key),
    )
    const wireframe = block.match(/텍스트 와이어프레임:\s*\n\n```text\n([\s\S]*?)\n```/)?.[1]?.trim()
    const stateText = block.match(/상태:\s*([^\n]+)/)?.[1]?.trim()
    const tables = extractTitledTables(block).filter((candidate) => !isMetadataTable(candidate))
    return {
      scrId: match[1],
      name: match[2].trim(),
      fields,
      wireframe,
      stateText,
      tables,
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
  const titledTables = extractTitledTables(content)
  const screenTable = firstTable(tables, ['SCR-ID', '화면명', '유형'])
  const evidenceTable = firstTable(tables, ['SCR-ID', '시안/와이어프레임 ID', '파일/URL'])
  const representedTitles = new Set(['화면 목록', '화면 시안 및 기준 증적'])
  const details = extractScreenDetails(content)
  const detailTableKeys = new Set(details.flatMap((detail) => detail.tables.map(tableKey)))

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
    details,
    extraTables: titledTables.filter((table) => {
      if (representedTitles.has(table.title)) return false
      if (table.title.includes('SCR-')) return false
      if (detailTableKeys.has(tableKey(table))) return false
      if (isMetadataTable(table)) return false
      return table.rows.length > 0
    }),
  }
}
