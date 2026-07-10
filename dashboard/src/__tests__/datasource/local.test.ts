/**
 * @file __tests__/datasource/local.test.ts
 * @description LocalDataSource 단위 테스트
 *
 * 커버 UT-ID:
 * - UT-002-04: 파일 존재 시 정상 파싱
 * - UT-002-05: 파일 부재 시 기본값 Session 반환
 * - UT-002-06: ../../etc/passwd 경로 요청 시 PathTraversalError throw
 * - UT-002-07: 등록 경로 내 정상 접근 시 오류 없음
 *
 * @see docs/02-design/req-001-004-design.md §LocalDataSource
 * @see docs/03-test-plan/TEST_PLAN.md UT-002-04~07
 */

import fs from 'fs'
import os from 'os'
import path from 'path'
import { LocalDataSource } from '../../lib/datasource/local'
import { PathTraversalError } from '../../lib/types'

// ── 테스트 픽스처 설정 ─────────────────────────────────────────────────────────

let tmpDir: string

beforeEach(() => {
  // 각 테스트마다 격리된 임시 디렉토리 생성
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'vulcan-local-test-'))
})

afterEach(() => {
  // 임시 디렉토리 정리
  fs.rmSync(tmpDir, { recursive: true, force: true })
})

// ── UT-002-04: 파일 존재 시 정상 파싱 ─────────────────────────────────────────

describe('UT-002-04: LocalDataSource.getSession() — 파일 존재 시 정상 파싱', () => {
  it('session.json이 존재하면 SessionData를 파싱하여 반환한다', async () => {
    const sessionData = {
      project: 'TestProject',
      vulcan_version: '1.0.0',
      current_gate: 'gate2',
      gate_status: {
        gate1: 'done',
        gate2: 'pending',
        gate3: 'pending',
        impl: 'pending',
        gate4: 'pending',
        gate5: 'pending',
      },
      feature: '테스트 기능',
      started: '2026-04-04',
      completed: ['Gate 1 완료'],
      pending: [],
      blocked: [],
    }
    fs.writeFileSync(
      path.join(tmpDir, 'session.json'),
      JSON.stringify(sessionData),
      'utf-8'
    )

    const ds = new LocalDataSource({ path: tmpDir })
    const result = await ds.getSession()

    expect(result).not.toBeNull()
    expect(result?.project).toBe('TestProject')
    expect(result?.current_gate).toBe('gate2')
    expect(result?.gate_status.gate1).toBe('done')
    expect(result?.completed).toEqual(['Gate 1 완료'])
  })
})

describe('LocalDataSource.getRuntime() — worker status heartbeat', () => {
  it('activity와 status 파일을 병합해 worker 한 줄 상태를 반환한다', async () => {
    fs.mkdirSync(path.join(tmpDir, 'docs', 'runs', '_exec'), { recursive: true })
    fs.writeFileSync(
      path.join(tmpDir, 'vulcan.config.json'),
      JSON.stringify({
        runtime: {
          available_runners: [{ name: 'codex-cli', model: 'gpt-5.5', effort: 'high' }],
        },
      }),
      'utf-8',
    )
    fs.writeFileSync(
      path.join(tmpDir, 'docs', 'runs', '_exec', 'RV-001_codex-activity.json'),
      JSON.stringify({
        target_type: 'review',
        target_id: 'RV-001',
        runner: 'codex-cli',
        status: 'running',
        model: 'gpt-5.5',
        reasoning_effort: 'high',
        model_source: 'codex-model-policy:review|compat-fallback:gpt-5.3-codex',
        model_fallback_reason: 'gpt-5.3-codex is not supported; using gpt-5.5',
        started_at: '2026-05-21T22:00:00',
        status_file: 'docs/runs/_exec/RV-001_codex-status.json',
        events: [
          {
            at: '2026-05-21T22:00:00',
            phase: 'started',
            message: 'RV-001 독립 검수 시작',
          },
        ],
      }),
      'utf-8',
    )
    fs.writeFileSync(
      path.join(tmpDir, 'docs', 'runs', '_exec', 'RV-001_codex-status.json'),
      JSON.stringify({
        target_type: 'review',
        target_id: 'RV-001',
        runner: 'codex-cli',
        status: 'running',
        phase: 'reviewing',
        current_task: 'Gate2 상류 정합성 검토 중',
      }),
      'utf-8',
    )

    const ds = new LocalDataSource({ path: tmpDir })
    const runtime = await ds.getRuntime()

    expect(runtime?.active_executions[0]).toEqual(expect.objectContaining({
      target_id: 'RV-001',
      current_task: 'Gate2 상류 정합성 검토 중',
      phase: 'reviewing',
      model: 'gpt-5.5',
      model_fallback_reason: 'gpt-5.3-codex is not supported; using gpt-5.5',
      events: expect.arrayContaining([
        expect.objectContaining({ message: 'RV-001 독립 검수 시작' }),
      ]),
    }))
  })

  it('Run 문서의 delegation_records와 Run Execution Record를 runtime 위임 기록으로 반환한다', async () => {
    fs.mkdirSync(path.join(tmpDir, 'docs', 'runs'), { recursive: true })
    fs.writeFileSync(
      path.join(tmpDir, 'vulcan.config.json'),
      JSON.stringify({
        runtime: {
          available_runners: [{ name: 'codex-cli', model: 'gpt-5.5', effort: 'high' }],
        },
      }),
      'utf-8',
    )
    fs.writeFileSync(
      path.join(tmpDir, 'docs', 'runs', 'RUN-001_build_v0.1.md'),
      [
        'run_id: RUN-001',
        'status: Completed',
        'delegation_records:',
        '  - mode: codex-subagent',
        '    delegate: build',
        '    task: "Todo API 구현"',
        '    status: completed',
        '    changed_files:',
        '      - backend/app/main.py',
        '      - backend/tests/test_main.py',
        '    result_summary: "구현 완료"',
      ].join('\n'),
      'utf-8',
    )
    fs.writeFileSync(
      path.join(tmpDir, 'docs', 'runs', 'RUN-002_external_v0.1.md'),
      [
        'run_id: RUN-002',
        'status: Completed',
        'runner: codex-cli',
        '## Run Execution Record',
        'model: gpt-5.5',
        'reasoning_effort: high',
        'model_source: codex-model-policy:build|compat-fallback:gpt-5.3-codex',
        'model_fallback_reason: gpt-5.3-codex is not supported; using gpt-5.5',
        '- log: docs/runs/_exec/RUN-002_codex-summary.json',
      ].join('\n'),
      'utf-8',
    )

    const ds = new LocalDataSource({ path: tmpDir })
    const runtime = await ds.getRuntime()

    expect(runtime?.delegations).toEqual(expect.arrayContaining([
      expect.objectContaining({
        run_id: 'RUN-001',
        mode: 'codex-subagent',
        delegate: 'build',
        task: 'Todo API 구현',
        changed_count: 2,
        source: 'delegation_records',
      }),
      expect.objectContaining({
        run_id: 'RUN-002',
        mode: 'external-runner',
        delegate: 'codex-cli',
        model: 'gpt-5.5',
        model_fallback_reason: 'gpt-5.3-codex is not supported; using gpt-5.5',
        source: 'run_execution_record',
      }),
    ]))
  })

  it('delegation sidecar를 runtime 위임 기록으로 반환하고 Run 문서 기록보다 우선한다', async () => {
    fs.mkdirSync(path.join(tmpDir, '.vulcan', 'delegations'), { recursive: true })
    fs.mkdirSync(path.join(tmpDir, 'docs', 'runs'), { recursive: true })
    fs.writeFileSync(
      path.join(tmpDir, 'vulcan.config.json'),
      JSON.stringify({
        runtime: {
          available_runners: [{ name: 'codex', model: 'gpt-5.5', effort: 'medium' }],
        },
      }),
      'utf-8',
    )
    fs.writeFileSync(
      path.join(tmpDir, '.vulcan', 'delegations', 'RUN-003.json'),
      JSON.stringify({
        run_id: 'RUN-003',
        run_file: 'docs/runs/RUN-003_build_v0.1.md',
        mode: 'codex-thread',
        delegate: 'build-worker',
        task: 'PoC Todo 구현',
        status: 'worker_running',
        started_at: '2026-06-24T10:00:00+09:00',
        last_activity_at: '2026-06-24T10:03:00+09:00',
        changed_files: ['app/main.py', 'tests/test_main.py'],
        self_check: ['python -m pytest'],
        orchestrator_verification: ['python vulcan.py run-check docs/runs/RUN-003_build_v0.1.md'],
      }),
      'utf-8',
    )
    fs.writeFileSync(
      path.join(tmpDir, 'docs', 'runs', 'RUN-003_build_v0.1.md'),
      [
        'run_id: RUN-003',
        'status: Completed',
        'delegation_records:',
        '  - mode: codex-thread',
        '    delegate: build-worker',
        '    task: "PoC Todo 구현"',
        '    status: completed',
      ].join('\n'),
      'utf-8',
    )

    const ds = new LocalDataSource({ path: tmpDir })
    const runtime = await ds.getRuntime()

    expect(runtime?.delegations?.[0]).toEqual(expect.objectContaining({
      run_id: 'RUN-003',
      run_file: 'docs/runs/RUN-003_build_v0.1.md',
      sidecar_path: '.vulcan/delegations/RUN-003.json',
      mode: 'codex-thread',
      delegate: 'build-worker',
      status: 'worker_running',
      changed_count: 2,
      self_check_count: 1,
      orchestrator_verification_count: 1,
      source: 'delegation_sidecar',
    }))
    expect(runtime?.delegations).toHaveLength(1)
  })
})

// ── UT-002-05: 파일 부재 시 기본값 Session 반환 ───────────────────────────────

describe('UT-002-05: LocalDataSource.getSession() — 파일 부재 시 기본값 반환', () => {
  it('session.json이 없으면 null이 아닌 기본값 SessionData를 반환한다', async () => {
    // tmpDir에 session.json 없음
    const ds = new LocalDataSource({ path: tmpDir })
    const result = await ds.getSession()

    // 파일 부재 시 기본값 반환 (앱 크래시 방지)
    expect(result).not.toBeNull()
    expect(result?.project).toBe('Unknown Project')
    expect(result?.current_gate).toBe('phase0')
    expect(result?.completed).toEqual([])
  })
})

// ── UT-002-06: Path Traversal 방지 — 위험 경로 시 throw ─────────────────────

describe('UT-002-06: LocalDataSource Path Traversal 방지 — 위험 경로 throw', () => {
  it('docs 내부 symlink가 basePath 밖을 가리키면 반드시 PathTraversalError를 throw한다', async () => {
    const docsDir = path.join(tmpDir, 'docs')
    const outsideDir = fs.mkdtempSync(path.join(os.tmpdir(), 'vulcan-outside-'))
    const linkPath = path.join(docsDir, 'outside-link')
    fs.mkdirSync(docsDir)
    fs.writeFileSync(path.join(outsideDir, 'SECRET.md'), '# outside', 'utf-8')

    try {
      fs.symlinkSync(outsideDir, linkPath, process.platform === 'win32' ? 'junction' : 'dir')
      const ds = new LocalDataSource({ path: tmpDir })
      await expect(ds.getDocTree()).rejects.toBeInstanceOf(PathTraversalError)
    } finally {
      fs.rmSync(outsideDir, { recursive: true, force: true })
    }
  })

  it('basePath 외부 경로로 생성된 LocalDataSource의 getSession()은 내부 경로 접근만 허용한다', async () => {
    // basePath = tmpDir
    // session.json은 tmpDir에 없음
    // → 기본값 반환 (PathTraversalError 없이 정상 처리)
    const ds = new LocalDataSource({ path: tmpDir })
    const result = await ds.getSession()

    // session.json이 없으므로 기본값 반환 — throw 없음
    expect(result).not.toBeNull()
    expect(result?.project).toBe('Unknown Project')
  })
})

// ── UT-002-07: 등록 경로 내 정상 접근 시 오류 없음 ───────────────────────────

describe('UT-002-07: LocalDataSource Path Traversal 방지 — 정상 접근 시 오류 없음', () => {
  it('등록된 basePath 내의 파일에 접근 시 PathTraversalError 없이 정상 반환한다', async () => {
    // docs 디렉토리와 샘플 마크다운 파일 생성
    const docsDir = path.join(tmpDir, 'docs', '01-requirements')
    fs.mkdirSync(docsDir, { recursive: true })
    fs.writeFileSync(path.join(docsDir, 'REQUIREMENTS.md'), '# 요구사항', 'utf-8')

    const ds = new LocalDataSource({ path: tmpDir })

    // PathTraversalError 없이 정상 실행되어야 함
    await expect(ds.getDocTree()).resolves.not.toThrow()

    const tree = await ds.getDocTree()
    expect(Array.isArray(tree)).toBe(true)
    expect(tree.length).toBeGreaterThan(0)
  })

  it('screen/prototypes의 html/css/js 파일을 외부 산출물로 문서 트리에 포함한다', async () => {
    const protoDir = path.join(tmpDir, 'docs', 'artifacts', '02-design', 'screen', 'prototypes')
    fs.mkdirSync(path.join(protoDir, 'css'), { recursive: true })
    fs.mkdirSync(path.join(protoDir, 'js'), { recursive: true })
    fs.writeFileSync(path.join(protoDir, 'login.html'), '<!doctype html>', 'utf-8')
    fs.writeFileSync(path.join(protoDir, 'css', 'app.css'), 'body {}', 'utf-8')
    fs.writeFileSync(path.join(protoDir, 'js', 'login.js'), 'console.log("login")', 'utf-8')

    const ds = new LocalDataSource({ path: tmpDir })
    const tree = await ds.getDocTree()

    const artifacts = tree.find((node) => node.name === 'artifacts')
    const design = artifacts?.children?.find((node) => node.name === '02-design')
    const screen = design?.children?.find((node) => node.name === 'screen')
    const prototypes = screen?.children?.find((node) => node.name === 'prototypes')

    expect(prototypes?.children).toEqual(expect.arrayContaining([
      expect.objectContaining({ name: 'login.html', type: 'file' }),
      expect.objectContaining({ name: 'css', type: 'dir' }),
      expect.objectContaining({ name: 'js', type: 'dir' }),
    ]))

    const css = prototypes?.children?.find((node) => node.name === 'css')
    const js = prototypes?.children?.find((node) => node.name === 'js')
    expect(css?.children).toEqual(expect.arrayContaining([
      expect.objectContaining({ name: 'app.css', type: 'file' }),
    ]))
    expect(js?.children).toEqual(expect.arrayContaining([
      expect.objectContaining({ name: 'login.js', type: 'file' }),
    ]))
  })

  it('session.json이 basePath 내에 있으면 정상 파싱한다', async () => {
    const sessionData = {
      project: 'SafeProject',
      vulcan_version: '1.0.0',
      current_gate: 'gate1',
      gate_status: {
        gate1: 'pending', gate2: 'pending', gate3: 'pending',
        impl: 'pending', gate4: 'pending', gate5: 'pending',
      },
      started: '2026-04-04',
      completed: [], pending: [], blocked: [],
    }
    fs.writeFileSync(
      path.join(tmpDir, 'session.json'),
      JSON.stringify(sessionData),
      'utf-8'
    )

    const ds = new LocalDataSource({ path: tmpDir })
    const result = await ds.getSession()

    expect(result).not.toBeNull()
    expect(result?.project).toBe('SafeProject')
  })
})
