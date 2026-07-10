/**
 * @file __tests__/e2e/stats-section.spec.ts
 * @description REQ-011 통계 섹션 E2E 테스트
 *
 * 커버 항목:
 * - TST-011-08: StatsCards 렌더링 및 현재 지표 카드 표시
 * - TST-011-09: CurrentGatePanel gate1 콘텐츠 렌더링
 * - TST-011-10: CurrentGatePanel impl 콘텐츠 렌더링 (진행률 바)
 * - TST-011-11: stats 없을 때 통계 섹션 미표시
 *
 * 전제 조건: 앱이 localhost:3001에서 실행 중이어야 함.
 */

import { test, expect } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'
import {
  E2E_SCREENSHOTS_DIR,
  E2E_SESSION_PATH,
  ensureE2EProject,
  removeE2EProject,
} from './fixture'

/** session.json을 읽어 원본 내용을 반환한다 */
function readSession(): object {
  return JSON.parse(fs.readFileSync(E2E_SESSION_PATH, 'utf-8'))
}

/** session.json을 덮어씌운다 */
function writeSession(data: object): void {
  fs.writeFileSync(E2E_SESSION_PATH, JSON.stringify(data, null, 2), 'utf-8')
}

let projectId: string

test.beforeAll(async ({ request }) => {
  projectId = await ensureE2EProject(request)
})

test.afterAll(async ({ request }) => {
  await removeE2EProject(request, projectId)
})

function detailUrl(): string {
  return `/projects/${projectId}`
}

// ── TST-011-08: StatsCards 렌더링 ───────────────────────────────────────────

test.describe('TST-011-08: StatsCards 렌더링 및 현재 지표 카드 표시', () => {
  let originalSession: object

  test.beforeAll(() => {
    originalSession = readSession()
  })

  test.afterAll(() => {
    writeSession(originalSession)
  })

  test('stats 포함된 프로젝트 상세 페이지에서 StatsCards가 렌더링된다', async ({ page }) => {
    // 현재 session.json에 stats가 있어야 함 (check-trace 실행 완료 상태)
    const session = readSession() as any
    if (!session.stats) {
      test.skip()
      return
    }

    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')

    // stats-cards 컨테이너 확인
    const statsCards = page.getByTestId('stats-cards')
    await expect(statsCards).toBeVisible()

    // 현재 Dashboard 계약의 지표 카드 13개 확인
    const statCards = page.getByTestId('stat-card')
    await expect(statCards).toHaveCount(13)

    // 스크린샷 캡처
    await page.screenshot({
      path: path.join(E2E_SCREENSHOTS_DIR, 'TST-011-08-StatsCards-렌더링.png'),
    })
  })

  test('요구사항 현황 섹션 헤더가 표시된다', async ({ page }) => {
    const session = readSession() as any
    if (!session.stats) { test.skip(); return }

    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')
    await expect(page.getByText('요구사항 현황')).toBeVisible()
  })

  test('테스트 현황 섹션 헤더가 표시된다', async ({ page }) => {
    const session = readSession() as any
    if (!session.stats) { test.skip(); return }

    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')
    await expect(page.getByText('테스트 현황')).toBeVisible()
  })

  test('레이아웃 순서: 통계 카드가 Gate 진행 현황 뒤에 있다', async ({ page }) => {
    const session = readSession() as any
    if (!session.stats) { test.skip(); return }

    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')

    const statsSection = page.getByTestId('stats-cards')
    const gateSection = page.getByTestId('gate-status-stepper')

    const statsBbox = await statsSection.boundingBox()
    const gateBbox = await gateSection.boundingBox()

    expect(statsBbox).not.toBeNull()
    expect(gateBbox).not.toBeNull()
    if (statsBbox && gateBbox) {
      expect(statsBbox.y).toBeGreaterThan(gateBbox.y)
    }
  })
})

// ── TST-011-09: CurrentGatePanel gate1 콘텐츠 ───────────────────────────────

test.describe('TST-011-09: CurrentGatePanel gate1 콘텐츠 렌더링', () => {
  let originalSession: object

  test.beforeAll(() => {
    originalSession = readSession()
    // current_gate를 gate1으로 변경
    const modified = { ...originalSession as any, current_gate: 'gate1' }
    writeSession(modified)
  })

  test.afterAll(() => {
    writeSession(originalSession)
  })

  test('gate1 콘텐츠 영역이 렌더링된다', async ({ page }) => {
    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')

    const gateContent = page.getByTestId('gate-content-gate1')
    await expect(gateContent).toBeVisible()

    await page.screenshot({
      path: path.join(E2E_SCREENSHOTS_DIR, 'TST-011-09-CurrentGatePanel-gate1.png'),
    })
  })

  test('REQ 그룹, 상세 요구사항, AC 정의 완료 행이 표시된다', async ({ page }) => {
    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')

    // gate-content-gate1 내부에서 검색 (stats-cards의 동일 텍스트와 충돌 방지)
    const gateContent = page.getByTestId('gate-content-gate1')
    await expect(gateContent.getByText('상위 요구사항')).toBeVisible()
    await expect(gateContent.getByText('상세 요구사항')).toBeVisible()
    await expect(gateContent.getByText('AC 정의 완료')).toBeVisible()
  })
})

// ── TST-011-10: CurrentGatePanel impl 콘텐츠 ────────────────────────────────

test.describe('TST-011-10: CurrentGatePanel impl 진행률 바', () => {
  let originalSession: object

  test.beforeAll(() => {
    originalSession = readSession()
    const modified = { ...originalSession as any, current_gate: 'impl' }
    writeSession(modified)
  })

  test.afterAll(() => {
    writeSession(originalSession)
  })

  test('구현 진행률 바(role=progressbar)가 렌더링된다', async ({ page }) => {
    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')

    const progressBar = page.getByRole('progressbar')
    await expect(progressBar).toBeVisible()

    await page.screenshot({
      path: path.join(E2E_SCREENSHOTS_DIR, 'TST-011-10-CurrentGatePanel-impl.png'),
    })
  })

  test('구현 진행률 텍스트가 표시된다', async ({ page }) => {
    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')

    await expect(page.getByText('요구사항 구현률')).toBeVisible()
  })
})

// ── TST-011-11: stats 없을 때 통계 섹션 미표시 ──────────────────────────────

test.describe('TST-011-11: stats 없을 때 통계 섹션 미표시', () => {
  let originalSession: object

  test.beforeAll(() => {
    originalSession = readSession()
    // stats 필드 제거
    const { stats: _removed, ...withoutStats } = originalSession as any
    writeSession(withoutStats)
  })

  test.afterAll(() => {
    writeSession(originalSession)
  })

  test('stats 없을 때 stats-section이 렌더링되지 않는다', async ({ page }) => {
    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('stats-section')).not.toBeVisible()

    await page.screenshot({
      path: path.join(E2E_SCREENSHOTS_DIR, 'TST-011-11-NoStats-미표시.png'),
    })
  })

  test('Gate 진행 현황 섹션은 정상 렌더링된다', async ({ page }) => {
    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')

    await expect(page.getByText('Gate 진행 현황')).toBeVisible()
  })

  test('산출물 문서 섹션은 정상 렌더링된다', async ({ page }) => {
    await page.goto(detailUrl())
    await page.waitForLoadState('networkidle')

    // exact: true로 섹션 레이블만 매칭 (커밋 메시지 중복 방지)
    await expect(page.getByText('산출물 문서', { exact: true })).toBeVisible()
  })
})
