/**
 * @file schemas.ts
 * @description Zod 런타임 검증 스키마 정의
 *
 * 역할:
 * - projects.json, session.json 파싱 시 스키마 검증
 * - 스키마 오류 항목은 제외하고 정상 항목만 반환 (REQ-009-06)
 *
 * @see docs/02-design/req-data-design.md §4-2
 */

import { z } from 'zod'

// ── Project 스키마 ────────────────────────────────────────────────────────────

export const GitHubProjectSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  type: z.literal('github'),
  repo: z.string().regex(/^[^/]+\/[^/]+$/, 'owner/repo 형식이어야 합니다'),
  branch: z.string().min(1),
  addedAt: z.string().datetime(),
})

export const LocalProjectSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  type: z.literal('local'),
  path: z.string().min(1),
  addedAt: z.string().datetime(),
})

/**
 * Project discriminated union 스키마.
 * type 필드 기준으로 GitHubProject 또는 LocalProject 중 하나를 선택한다.
 */
export const ProjectSchema = z.discriminatedUnion('type', [
  GitHubProjectSchema,
  LocalProjectSchema,
])

/**
 * projects.json 전체 배열 스키마.
 * 개별 항목 파싱 실패 시 해당 항목을 제외하는 폴백 처리를 위해
 * readProjects()에서 ProjectSchema.safeParse()를 항목별로 호출한다.
 */
export const ProjectsListSchema = z.array(ProjectSchema)

// ── Session 스키마 ────────────────────────────────────────────────────────────

export const GateStatusSchema = z.enum(['done', 'in-progress', 'pending', 'awaiting-approval', 'blocked'])

export const GateKeySchema = z.enum(['phase0', 'gate1', 'gate2', 'gate3', 'impl', 'gate4', 'gate5', 'completed'])

// ── Stats 스키마 (REQ-011-02) ─────────────────────────────────────────────────

/**
 * RequirementsStats Zod 스키마.
 * 모든 수치는 음수 불허 정수다.
 */
export const RequirementsStatsSchema = z.object({
  groups:       z.number().int().min(0),
  total:        z.number().int().min(0),
  implemented:  z.number().int().min(0),
  pending:      z.number().int().min(0),
  ac_defined:   z.number().int().min(0),
  ac_missing:   z.number().int().min(0),
})

/** TestStats Zod 스키마. 모든 수치는 음수 불허 정수다. */
export const TestStatsSchema = z.object({
  total:   z.number().int().min(0),
  passed:  z.number().int().min(0),
  failed:  z.number().int().min(0),
  skipped: z.number().int().min(0),
  pending: z.number().int().min(0),
})

/** DocsStats Zod 스키마. 모든 수치는 음수 불허 정수다. */
export const DocsStatsSchema = z.object({
  discovery:    z.number().int().min(0).optional(),
  requirements: z.number().int().min(0),
  design:       z.number().int().min(0),
  test_plan:    z.number().int().min(0),
  review:       z.number().int().min(0),
  release:      z.number().int().min(0).optional(),
  backlog:      z.number().int().min(0).optional(),
  runs:         z.number().int().min(0).optional(),
  total:        z.number().int().min(0),
})

export const BacklogStatsSchema = z.object({
  active:   z.number().int().min(0),
  done:     z.number().int().min(0),
  rejected: z.number().int().min(0),
  by_type: z.object({
    idea:  z.number().int().min(0),
    find:  z.number().int().min(0),
    cr:    z.number().int().min(0),
    issue: z.number().int().min(0),
    debt:  z.number().int().min(0),
  }).optional(),
  by_level: z.object({
    trivial: z.number().int().min(0),
    small:   z.number().int().min(0),
    major:   z.number().int().min(0),
  }),
  by_priority: z.object({
    p0: z.number().int().min(0),
    p1: z.number().int().min(0),
    p2: z.number().int().min(0),
    p3: z.number().int().min(0),
  }),
})

export const ImplementationStatsSchema = z.object({
  requirements: z.object({
    total:        z.number().int().min(0),
    implemented:  z.number().int().min(0),
    pending:      z.number().int().min(0),
    completed_ids: z.array(z.string()),
  }),
  waves: z.object({
    total:     z.number().int().min(0),
    completed: z.number().int().min(0),
    current:   z.string().optional(),
    items: z.array(z.object({
      id:          z.string().min(1),
      status:      z.string().min(1),
      run:         z.string().optional(),
      related_ids: z.array(z.string()).optional(),
    })),
  }),
})

// ── vulcan.config.json runtime 스키마 ────────────────────────────────────────

export const RuntimeRunnerSchema = z.object({
  name: z.string().min(1),
  model: z.string().optional(),
  effort: z.string().optional(),
  reasoning_effort: z.string().optional(),
  sandbox: z.string().optional(),
  version: z.string().optional(),
})

export const RuntimeActivitySchema = z.object({
  target_type: z.enum(['review', 'run']).optional(),
  target_id: z.string().min(1),
  review_id: z.string().optional(),
  run_id: z.string().optional(),
  run_file: z.string().optional(),
  inferred_role: z.string().optional(),
  status: z.string().min(1),
  runner: z.string().min(1),
  model: z.string().optional(),
  reasoning_effort: z.string().optional(),
  model_source: z.string().optional(),
  sandbox: z.string().optional(),
  exec_dir: z.string().optional(),
  worktree_path: z.string().nullable().optional(),
  branch: z.string().nullable().optional(),
  started_at: z.string().optional(),
  deadline_at: z.string().optional(),
  completed_at: z.string().optional(),
  duration_seconds: z.number().optional(),
  timeout_seconds: z.number().optional(),
  hard_timeout_seconds: z.number().optional(),
  extension_seconds: z.number().optional(),
  max_extensions: z.number().optional(),
  timed_out: z.boolean().optional(),
  timeout_reason: z.string().optional(),
  timeout_policy: z.object({
    watchdog_enabled: z.boolean().optional(),
    progress_probe_seconds: z.number().optional(),
    no_progress_timeout_seconds: z.number().optional(),
    min_runtime_seconds: z.number().optional(),
    hard_timeout_seconds: z.number().optional(),
    extension_seconds: z.number().optional(),
    max_extensions: z.number().optional(),
    extensions_used: z.number().optional(),
    watchdog_state: z.string().optional(),
    last_probe_at: z.string().optional(),
    last_progress_at: z.string().optional(),
    last_progress_age_seconds: z.number().optional(),
    last_progress_reasons: z.array(z.string()).optional(),
    quiet_probe_count: z.number().optional(),
    timeout_reason: z.string().optional(),
  }).optional(),
  watchdog: z.object({
    enabled: z.boolean().optional(),
    state: z.string().optional(),
    last_probe_at: z.string().optional(),
    last_progress_at: z.string().optional(),
    last_progress_age_seconds: z.number().optional(),
    last_progress_reasons: z.array(z.string()).optional(),
    quiet_probe_count: z.number().optional(),
    progress_probe_seconds: z.number().optional(),
    no_progress_timeout_seconds: z.number().optional(),
    min_runtime_seconds: z.number().optional(),
  }).optional(),
  exit_code: z.number().optional(),
  result_file_changed: z.boolean().optional(),
  run_file_changed: z.boolean().optional(),
  changed_files: z.array(z.string()).optional(),
  phase: z.string().optional(),
  current_task: z.string().optional(),
  current_message: z.string().optional(),
  last_update: z.string().optional(),
  status_file: z.string().optional(),
  status_stale: z.boolean().optional(),
  last_update_age_seconds: z.number().optional(),
  resume_supported: z.boolean().optional(),
  thread_id: z.string().optional(),
  session_id: z.string().optional(),
  resume_hint: z.string().optional(),
  log: z.string().optional(),
  stderr_log: z.string().optional(),
  last_message: z.string().optional(),
  summary: z.string().optional(),
  transcript: z.string().optional(),
  transcript_response_detected: z.boolean().optional(),
  result_file: z.string().optional(),
  events: z.array(z.object({
    at: z.string().optional(),
    phase: z.string().optional(),
    status: z.string().optional(),
    message: z.string().optional(),
  })).default([]),
})

export const RuntimeWorktreeSchema = z.object({
  id: z.string().min(1),
  path: z.string().min(1),
  branch: z.string().nullable().optional(),
  runner: z.string().nullable().optional(),
  target_id: z.string().nullable().optional(),
  target_type: z.enum(['review', 'run']).nullable().optional(),
  status: z.string().min(1),
  exists: z.boolean(),
  changed_files: z.array(z.string()).default([]),
  changed_count: z.number().nonnegative(),
  activity_status: z.string().nullable().optional(),
  deadline_at: z.string().nullable().optional(),
  stale: z.boolean().optional(),
})

export const WorkflowPolicySchema = z.object({
  branch_mode: z.string().optional(),
  main_branch: z.string().optional(),
  integration_branch: z.string().optional(),
  impl_uses_integration_branch: z.boolean().optional(),
  qa_worktree_enabled: z.boolean().optional(),
  qa_stage_mode: z.string().optional(),
  release_merge_to: z.string().optional(),
  enforce_branch_guard: z.boolean().optional(),
}).passthrough()

export const ProjectRuntimeSchema = z.object({
  primary: z.string().nullable().optional(),
  current_branch: z.string().nullable().optional(),
  workflow: WorkflowPolicySchema.nullable().optional(),
  available_runners: z.array(RuntimeRunnerSchema).default([]),
  active_executions: z.array(RuntimeActivitySchema).default([]),
  worktrees: z.array(RuntimeWorktreeSchema).default([]),
}).transform((runtime) => {
  const names = runtime.available_runners.map((runner) => runner.name)
  const hasRunner = names.length > 0
  const families = new Set(
    names.map((name) => {
      if (name === 'codex-cli' || name === 'codex') return 'codex'
      if (name === 'claude-cli' || name === 'claude') return 'claude'
      if (name === 'antigravity-cli' || name === 'antigravity' || name === 'agy') return 'gemini'
      return name
    })
  )

  return {
    ...runtime,
    capabilities: {
      same_runner_independent_review: hasRunner,
      cross_model_validation: families.size >= 2,
      parallel_cross_runner_work: families.size >= 2,
    },
  }
})

export const VulcanConfigSchema = z.object({
  runtime: ProjectRuntimeSchema.optional(),
  workflow: WorkflowPolicySchema.optional(),
})

/** ProjectStats Zod 스키마. updated_at은 YYYY-MM-DD 형식을 검증한다. */
export const ProjectStatsSchema = z.object({
  requirements: RequirementsStatsSchema,
  implementation: ImplementationStatsSchema.optional(),
  tests:        TestStatsSchema,
  docs:         DocsStatsSchema,
  backlog:      BacklogStatsSchema.optional(),
  updated_at:   z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
})

export const SessionDataSchema = z.object({
  project: z.string().min(1),
  vulcan_src: z.string().optional(),
  vulcan_version: z.string().min(1),
  current_gate: GateKeySchema,
  gate_status: z.object({
    gate1: GateStatusSchema,
    gate2: GateStatusSchema,
    gate3: GateStatusSchema,
    impl: GateStatusSchema,
    gate4: GateStatusSchema,
    gate5: GateStatusSchema,
  }),
  feature: z.string().optional(),
  started: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'YYYY-MM-DD 형식이어야 합니다'),
  completed: z.array(z.string()),
  pending: z.array(z.string()),
  blocked: z.array(z.string()),
  branch_state: z.object({
    main_branch: z.string().optional(),
    integration_branch: z.string().optional(),
    current_role: z.string().optional(),
    current_branch: z.string().optional(),
    started_at: z.string().optional(),
    stage: z.string().optional(),
  }).optional(),
  /** check-trace 실행 시 계산된 프로젝트 통계. stats 없는 session.json도 유효하다. */
  stats: ProjectStatsSchema.optional(),
})

// ── 추론 타입 내보내기 ─────────────────────────────────────────────────────────

export type SessionDataFromSchema = z.infer<typeof SessionDataSchema>
export type ProjectRuntimeFromSchema = z.infer<typeof ProjectRuntimeSchema>
export type ProjectFromSchema = z.infer<typeof ProjectSchema>
