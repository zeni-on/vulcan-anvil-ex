/**
 * @file types.ts
 * @description 프로젝트 전역 TypeScript 타입 정의
 *
 * 역할:
 * - Project discriminated union (GitHubProject | LocalProject)
 * - DataSource 인터페이스 (REQ-002-01)
 * - SessionData, CommitEntry, DocNode 공통 타입
 *
 * @see docs/02-design/req-data-design.md §2
 * @see docs/02-design/req-001-004-design.md §DataSource 인터페이스
 */

// ── Gate 관련 타입 ─────────────────────────────────────────────────────────────

/**
 * Gate 진행 키.
 * 'completed'는 Gate 5 완료 후 vulcan.py가 current_gate에만 기록하는 최종 상태다.
 * gate_status Record의 키로는 사용하지 않는다.
 */
export type GateKey = 'gate1' | 'gate2' | 'gate3' | 'impl' | 'gate4' | 'gate5' | 'completed'

/** gate_status Record에서 사용하는 키 — 'completed'는 current_gate 전용이므로 제외 */
export type GateStatusKey = Exclude<GateKey, 'completed'>

/** Gate 단위 상태 값 */
export type GateStatus = 'done' | 'in-progress' | 'pending' | 'blocked'

// ── projects.json 타입 ────────────────────────────────────────────────────────

/** GitHub 모드 프로젝트 */
export interface GitHubProject {
  id: string
  name: string
  type: 'github'
  repo: string    // "owner/repo" 형식
  branch: string
  addedAt: string // ISO 8601
}

/** 로컬 모드 프로젝트 */
export interface LocalProject {
  id: string
  name: string
  type: 'local'
  path: string    // 절대 경로
  addedAt: string // ISO 8601
}

/**
 * projects.json 항목 타입 (discriminated union).
 * type 필드로 GitHub/로컬 모드를 구분한다.
 */
export type Project = GitHubProject | LocalProject

export type ProjectList = Project[]

// ── session.json stats 타입 (REQ-011-02) ──────────────────────────────────────

/**
 * session.json stats.requirements 섹션 타입.
 * check-trace 실행 시 계산된 요구사항 현황을 담는다.
 */
export interface RequirementsStats {
  groups: number
  total: number
  implemented: number
  pending: number
  ac_defined: number
  ac_missing: number
}

/**
 * session.json stats.tests 섹션 타입.
 * TEST_PLAN.md의 TST-ID 상태를 집계한 값을 담는다.
 */
export interface TestStats {
  total: number
  passed: number
  failed: number
  skipped: number
  pending: number
}

/**
 * session.json stats.docs 섹션 타입.
 * docs/ 하위 각 카테고리 디렉토리의 .md 파일 수를 담는다.
 */
export interface DocsStats {
  requirements: number
  design: number
  test_plan: number
  review: number
  total: number
}

export interface BacklogStats {
  active:    number
  done:      number
  rejected:  number
  by_level: {
    trivial: number
    small:   number
    major:   number
  }
  by_priority: {
    p0: number
    p1: number
    p2: number
    p3: number
  }
}

/**
 * session.json stats 필드 전체 타입.
 * check-trace 실행 시 한 번 계산되어 session.json에 기록된다.
 */
export interface ProjectStats {
  requirements: RequirementsStats
  tests: TestStats
  docs: DocsStats
  backlog?: BacklogStats
  updated_at: string  // "YYYY-MM-DD"
}

// ── session.json 타입 ─────────────────────────────────────────────────────────

/** session.json 전체 구조 */
export interface SessionData {
  project: string
  vulcan_src?: string
  vulcan_version: string
  current_gate: GateKey
  gate_status: Record<GateStatusKey, GateStatus>
  feature?: string
  started: string      // "YYYY-MM-DD"
  completed: string[]
  pending: string[]
  blocked: string[]
  /** check-trace 실행 시 계산된 프로젝트 통계 (REQ-011-02). 없을 수 있으므로 optional. */
  stats?: ProjectStats
}

// ── DataSource 공통 반환 타입 ──────────────────────────────────────────────────

/** Git 커밋 항목 */
export interface CommitEntry {
  sha: string
  message: string
  author: string
  date: string // ISO 8601
}

/**
 * 문서 트리 노드.
 * 기존 src/lib/project.ts의 DocNode와 호환되는 구조를 유지한다.
 */
export interface DocNode {
  name: string
  slug: string[]
  type: 'file' | 'dir'
  children?: DocNode[]
}

// ── DataSource 인터페이스 (REQ-002-01) ────────────────────────────────────────

/**
 * DataSource 인터페이스.
 *
 * GitHub 모드와 로컬 모드의 공통 계약이다.
 * UI 컴포넌트는 이 인터페이스만 의존하며 구현체 타입을 알 필요가 없다 (REQ-002-04).
 */
export interface DataSource {
  getSession(): Promise<SessionData | null>
  getDocTree(): Promise<DocNode[]>
  getCommits(limit: number): Promise<CommitEntry[]>
  /** docs/ 하위 .md 파일 내용을 raw 텍스트로 반환. 파일 미존재 시 ENOENT/DataSourceError throw. (REQ-010-01) */
  readDocFile(relPath: string): Promise<string>
}

// ── API 응답 타입 ──────────────────────────────────────────────────────────────

/**
 * GET /api/projects/[id]/data 응답 타입.
 * Promise.allSettled로 병렬 패치한 결과를 조합한다.
 */
export interface ProjectData {
  session: SessionData | null
  docs: DocNode[]
  commits: CommitEntry[]
  fetchedAt: string // ISO 8601 — SWR 캐시 무효화 확인용
}

/**
 * 산출물 문서 항목 (REQ-005-02).
 * DocNode의 평면 표현으로, DocList 컴포넌트가 카테고리별로 그룹화한다.
 * path는 항상 상대 경로 — 절대 경로를 클라이언트에 노출하지 않는다 (SEC-002-04).
 */
export interface DocEntry {
  name: string
  path: string    // 상대 경로 (프로젝트 루트 기준)
  category: 'discovery' | 'requirements' | 'design' | 'test-plan' | 'review' | 'other'
  /**
   * 파일 종류:
   *  - 'markdown' (기본): dashboard 내 Drawer에서 렌더
   *  - 'external': OS 기본 앱으로 열어야 하는 파일 (xlsx/pptx/pdf/hwp 등)
   * 미지정 시 'markdown'으로 간주한다 (기존 호출자 호환).
   */
  kind?: 'markdown' | 'external'
  /** 확장자(소문자, 점 없음). 'external' 유형일 때 아이콘 선택에 사용. */
  ext?: string
}

/** 외부 앱으로 열 수 있는 산출물 파일 확장자 (소문자, 점 없음) */
export const EXTERNAL_DOC_EXTENSIONS = [
  'pdf',
  'xlsx',
  'xls',
  'pptx',
  'ppt',
  'docx',
  'doc',
  'hwp',
  'hwpx',
] as const

export type ExternalDocExt = (typeof EXTERNAL_DOC_EXTENSIONS)[number]

export function isExternalDocExt(ext: string): ext is ExternalDocExt {
  return (EXTERNAL_DOC_EXTENSIONS as readonly string[]).includes(ext.toLowerCase())
}

/** GET /api/projects/[id]/session 응답 타입 */
export interface SessionApiResponse {
  session: SessionData | null
  fetchedAt: string
}

/** GET /api/projects/[id]/docs 응답 타입 */
export interface DocsApiResponse {
  docs: DocEntry[]
  fetchedAt: string
  /** 프로젝트 타입 — UI에서 '폴더 열기' 버튼 노출 여부 결정에 사용 */
  projectType: 'local' | 'github'
}

/** GET /api/projects/[id]/commits 응답 타입 */
export interface CommitsApiResponse {
  commits: CommitEntry[]
  fetchedAt: string
}

/** DataSource 계층에서 발생하는 공통 에러 */
export class DataSourceError extends Error {
  constructor(
    message: string,
    public readonly cause?: unknown,
  ) {
    super(message)
    this.name = 'DataSourceError'
  }
}

/** Path Traversal 감지 시 throw하는 에러 (SEC-001-02, REQ-009-03) */
export class PathTraversalError extends Error {
  constructor(attemptedPath: string) {
    super(`Path traversal attempt detected: ${attemptedPath}`)
    this.name = 'PathTraversalError'
  }
}
