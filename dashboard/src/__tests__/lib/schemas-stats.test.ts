/**
 * @file __tests__/lib/schemas-stats.test.ts
 * @description SessionDataSchema stats 필드 Zod 검증 테스트
 *
 * 커버 항목:
 * - UT-011-09: stats 필드가 없는 session.json도 safeParse 통과
 * - UT-011-10: stats 필드가 있는 session.json도 safeParse 통과
 * - UT-011-11: stats 내 숫자 필드에 음수가 있으면 safeParse 실패
 *
 * @see docs/02-design/req-011-design.md §5
 */

import { SessionDataSchema } from '@/lib/schemas'

// ── 공통 픽스처 ──────────────────────────────────────────────────────────────

/** stats 없는 최소 유효 session.json */
const baseSession = {
  project: 'test-project',
  vulcan_version: '1.0.0',
  current_gate: 'gate1',
  gate_status: {
    gate1: 'in-progress',
    gate2: 'pending',
    gate3: 'pending',
    impl:  'pending',
    gate4: 'pending',
    gate5: 'pending',
  },
  started: '2026-04-04',
  completed: [],
  pending: [],
  blocked: [],
}

/** 유효한 stats 객체 */
const validStats = {
  requirements: {
    groups:      3,
    total:       15,
    implemented: 10,
    pending:     5,
    ac_defined:  12,
    ac_missing:  3,
  },
  tests: {
    total:   20,
    passed:  15,
    failed:  2,
    skipped: 1,
    pending: 2,
  },
  docs: {
    requirements: 1,
    design:       4,
    test_plan:    1,
    review:       2,
    total:        8,
  },
  updated_at: '2026-04-04',
}

// ── UT-011-09: stats 없는 session도 safeParse 통과 ────────────────────────────

describe('UT-011-09: stats 필드 없는 session.json', () => {
  it('stats 없어도 safeParse가 성공한다', () => {
    const result = SessionDataSchema.safeParse(baseSession)
    expect(result.success).toBe(true)
  })

  it('파싱 결과에 stats 필드가 undefined다', () => {
    const result = SessionDataSchema.safeParse(baseSession)
    if (!result.success) throw new Error('파싱 실패')
    expect(result.data.stats).toBeUndefined()
  })
})

// ── UT-011-10: stats 필드 있는 session.json도 safeParse 통과 ─────────────────

describe('UT-011-10: stats 필드 있는 session.json', () => {
  it('유효한 stats가 있을 때 safeParse가 성공한다', () => {
    const result = SessionDataSchema.safeParse({ ...baseSession, stats: validStats })
    expect(result.success).toBe(true)
  })

  it('파싱 결과의 stats 값이 입력과 일치한다', () => {
    const result = SessionDataSchema.safeParse({ ...baseSession, stats: validStats })
    if (!result.success) throw new Error('파싱 실패')
    expect(result.data.stats?.requirements.total).toBe(15)
    expect(result.data.stats?.tests.passed).toBe(15)
    expect(result.data.stats?.docs.total).toBe(8)
    expect(result.data.stats?.updated_at).toBe('2026-04-04')
  })
})

// ── UT-011-11: stats 내 음수 필드이면 safeParse 실패 ─────────────────────────

describe('UT-011-11: stats 내 음수 필드', () => {
  it('requirements.total 음수이면 safeParse가 실패한다', () => {
    const invalidStats = {
      ...validStats,
      requirements: { ...validStats.requirements, total: -1 },
    }
    const result = SessionDataSchema.safeParse({ ...baseSession, stats: invalidStats })
    expect(result.success).toBe(false)
  })

  it('tests.passed 음수이면 safeParse가 실패한다', () => {
    const invalidStats = {
      ...validStats,
      tests: { ...validStats.tests, passed: -5 },
    }
    const result = SessionDataSchema.safeParse({ ...baseSession, stats: invalidStats })
    expect(result.success).toBe(false)
  })

  it('docs.design 음수이면 safeParse가 실패한다', () => {
    const invalidStats = {
      ...validStats,
      docs: { ...validStats.docs, design: -2 },
    }
    const result = SessionDataSchema.safeParse({ ...baseSession, stats: invalidStats })
    expect(result.success).toBe(false)
  })

  it('requirements.ac_missing 음수이면 safeParse가 실패한다', () => {
    const invalidStats = {
      ...validStats,
      requirements: { ...validStats.requirements, ac_missing: -1 },
    }
    const result = SessionDataSchema.safeParse({ ...baseSession, stats: invalidStats })
    expect(result.success).toBe(false)
  })
})
