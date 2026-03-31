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
