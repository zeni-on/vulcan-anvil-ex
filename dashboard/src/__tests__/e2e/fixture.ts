import fs from 'node:fs'
import path from 'node:path'
import type { APIRequestContext } from '@playwright/test'

interface RegisteredProject {
  id: string
  type: 'local' | 'github'
  path?: string
}

export const E2E_PROJECT_ROOT = path.resolve(process.cwd(), '..', '.vulcan', 'dashboard-e2e-fixture')
export const E2E_SCREENSHOTS_DIR = path.join(E2E_PROJECT_ROOT, 'docs', 'evidence', 'screenshots')
export const E2E_SESSION_PATH = path.join(E2E_PROJECT_ROOT, 'session.json')

export const BASE_SESSION = {
  project: 'Vulcan Dashboard E2E Fixture',
  feature: 'Repository-contained E2E fixture',
  profile: 'product',
  vulcan_version: '0.4.9',
  current_gate: 'gate1',
  gate_status: {
    gate1: 'pending', gate2: 'pending', gate3: 'pending',
    impl: 'pending', gate4: 'pending', gate5: 'pending',
  },
  started: '2026-07-10',
  completed: [],
  pending: [],
  blocked: [],
  stats: {
    requirements: {
      groups: 3, total: 15, implemented: 10, pending: 5, ac_defined: 12, ac_missing: 3,
    },
    tests: { total: 20, passed: 15, failed: 2, skipped: 1, pending: 2 },
    docs: { requirements: 1, design: 1, test_plan: 1, review: 0, total: 3 },
    updated_at: '2026-07-10',
  },
}

function normalized(value: string): string {
  return path.resolve(value).toLowerCase()
}

export function writeFixtureSession(session: object = BASE_SESSION): void {
  fs.mkdirSync(E2E_PROJECT_ROOT, { recursive: true })
  fs.writeFileSync(E2E_SESSION_PATH, JSON.stringify(session, null, 2), 'utf-8')
}

export function prepareE2EFixture(): void {
  fs.rmSync(E2E_PROJECT_ROOT, { recursive: true, force: true })
  fs.mkdirSync(path.join(E2E_PROJECT_ROOT, 'docs', 'artifacts', '01-requirements'), { recursive: true })
  fs.mkdirSync(path.join(E2E_PROJECT_ROOT, 'docs', 'artifacts', '02-design'), { recursive: true })
  fs.mkdirSync(E2E_SCREENSHOTS_DIR, { recursive: true })
  writeFixtureSession()
  fs.writeFileSync(
    path.join(E2E_PROJECT_ROOT, 'docs', 'artifacts', '01-requirements', 'REQUIREMENTS.md'),
    '# Requirements\n\n**Fixture contract**\n\n| ID | Requirement |\n| --- | --- |\n| REQ-001-01 | Render the dashboard fixture |\n',
    'utf-8',
  )
  fs.writeFileSync(
    path.join(E2E_PROJECT_ROOT, 'docs', 'artifacts', '02-design', 'DESIGN.md'),
    '# Design\n\nRepository-contained test data.\n',
    'utf-8',
  )
}

export async function ensureE2EProject(request: APIRequestContext): Promise<string> {
  prepareE2EFixture()
  const listResponse = await request.get('/api/projects')
  const list = (await listResponse.json()) as { projects?: RegisteredProject[] }
  const existing = list.projects?.find(
    (project) => project.type === 'local' && project.path && normalized(project.path) === normalized(E2E_PROJECT_ROOT),
  )
  if (existing) return existing.id

  const createResponse = await request.post('/api/projects', {
    data: { type: 'local', path: E2E_PROJECT_ROOT },
  })
  if (!createResponse.ok()) {
    throw new Error(`Failed to register E2E fixture: ${createResponse.status()} ${await createResponse.text()}`)
  }
  const created = (await createResponse.json()) as { project: RegisteredProject }
  return created.project.id
}

export async function removeE2EProject(request: APIRequestContext, projectId: string): Promise<void> {
  await request.delete(`/api/projects/${projectId}`)
  fs.rmSync(E2E_PROJECT_ROOT, { recursive: true, force: true })
}
