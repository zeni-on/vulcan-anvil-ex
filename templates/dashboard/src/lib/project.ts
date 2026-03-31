import fs from 'fs'
import path from 'path'

// dashboard/의 부모 디렉토리 = 프로젝트 루트
export const PROJECT_ROOT = path.join(process.cwd(), '..')

export interface Session {
  project: string
  vulcan_version?: string
  current_gate: string
  gate_status: Record<string, 'pending' | 'done'>
  feature: string
  started: string
  completed: string[]
  pending: string[]
  blocked: string[]
}

export interface DocNode {
  name: string
  slug: string[]
  type: 'file' | 'dir'
  children?: DocNode[]
}

export function readSession(): Session {
  const p = path.join(PROJECT_ROOT, 'session.json')
  try {
    return JSON.parse(fs.readFileSync(p, 'utf-8'))
  } catch {
    return {
      project: 'Unknown Project',
      current_gate: 'gate1',
      gate_status: {
        gate1: 'pending',
        gate2: 'pending',
        gate3: 'pending',
        gate4: 'pending',
        gate5: 'pending',
      },
      feature: '',
      started: '',
      completed: [],
      pending: [],
      blocked: [],
    }
  }
}

export function buildDocTree(dir: string, slugPrefix: string[] = []): DocNode[] {
  if (!fs.existsSync(dir)) return []

  return fs
    .readdirSync(dir)
    .filter(f => !f.startsWith('.') && !f.endsWith('.gitkeep'))
    .sort()
    .map(f => {
      const fullPath = path.join(dir, f)
      const slug = [...slugPrefix, f]
      const stat = fs.statSync(fullPath)

      if (stat.isDirectory()) {
        const children = buildDocTree(fullPath, slug)
        if (children.length === 0) return null
        return { name: f, slug, type: 'dir' as const, children }
      }

      if (!f.endsWith('.md')) return null
      return { name: f.replace('.md', ''), slug, type: 'file' as const }
    })
    .filter(Boolean) as DocNode[]
}

export function readDoc(slug: string[]): string | null {
  const p = path.join(PROJECT_ROOT, 'docs', ...slug)
  if (!fs.existsSync(p)) return null
  return fs.readFileSync(p, 'utf-8')
}

// ── 통계 파싱 ───────────────────────────────────────────────────────────────

export interface RequirementsStats {
  groups: number        // REQ-NNN 그룹 수
  total: number         // REQ-NNN-NN 상세 요구사항 수
  acDefined: number     // AC-NNN-NN 정의된 수
  missing: string[]     // AC 미정의 REQ-ID 목록
}

export interface TestStats {
  total: number         // TST-ID 전체 수
  passed: number        // ✅ Pass 수
  failed: number        // ❌ Fail 수
  skipped: number       // ⏭ Skip 수
}

export function parseRequirementsStats(): RequirementsStats {
  const p = path.join(PROJECT_ROOT, 'docs', 'requirements', 'REQUIREMENTS.md')
  if (!fs.existsSync(p)) return { groups: 0, total: 0, acDefined: 0, missing: [] }

  const content = fs.readFileSync(p, 'utf-8')

  const detailReqs = [...new Set(content.match(/\bREQ-\d{3}-\d{2}\b/g) ?? [])]
  const allReqs    = [...new Set(content.match(/\bREQ-\d{3}\b/g) ?? [])]
  const groups     = allReqs.filter(r => !/REQ-\d{3}-\d{2}/.test(r))
  const acDefined  = [...new Set(content.match(/\bAC-\d{3}-\d{2}\b/g) ?? [])]

  // AC가 없는 REQ-NNN-NN 찾기
  const missing = detailReqs.filter(req => {
    const acId = req.replace('REQ-', 'AC-')
    return !acDefined.includes(acId)
  })

  return {
    groups: groups.length,
    total: detailReqs.length,
    acDefined: acDefined.length,
    missing,
  }
}

export function parseTestStats(): TestStats {
  const p = path.join(PROJECT_ROOT, 'docs', 'test-plan', 'TEST_PLAN.md')
  if (!fs.existsSync(p)) return { total: 0, passed: 0, failed: 0, skipped: 0 }

  const content = fs.readFileSync(p, 'utf-8')

  const tstIds = [...new Set(content.match(/\bTST-\d{3}-\d{2}\b/g) ?? [])]

  // 테이블 행에서 Pass/Fail/Skip 마커 파싱
  // 예: | TST-001-01 | ... | ✅ Pass | 또는 | Pass |
  const passCount   = (content.match(/✅\s*Pass/gi) ?? []).length
  const failCount   = (content.match(/❌\s*Fail/gi) ?? []).length
  const skipCount   = (content.match(/⏭\s*Skip|⚠️\s*Skip/gi) ?? []).length

  return {
    total: tstIds.length,
    passed: passCount,
    failed: failCount,
    skipped: skipCount,
  }
}
