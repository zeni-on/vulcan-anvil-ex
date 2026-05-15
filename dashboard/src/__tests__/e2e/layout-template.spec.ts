/**
 * @file e2e/layout-template.spec.ts
 * @description REQ-012 레이아웃 템플릿 시스템 E2E / Security 테스트
 *
 * TST-012-01: 템플릿 A 기본 렌더링 (E2E)
 * TST-012-02: 템플릿 A2 렌더링 (E2E)
 * TST-012-02B: 템플릿 B 렌더링 (E2E)
 * TST-012-03: 토글 버튼으로 즉시 전환 (E2E)
 * TST-012-04: localStorage 영속성 — 새로고침 후 복원 (E2E)
 * TST-012-05: localStorage 유효하지 않은 값 폴백 (Integration via E2E)
 * TST-SEC-012-01: localStorage 값 주입 차단 (Security)
 */

import { test, expect } from '@playwright/test'
import path from 'path'

const PROJECT_ID = 'local-julyi-Documents-workspace-antigravity-Vulcan-Dev-kweVml'
const PROJECT_URL = `/projects/${PROJECT_ID}`
const SCREENSHOTS_DIR = path.resolve(__dirname, '../../../../docs/04-review/screenshots')

const STORAGE_KEY = 'vulcan-dashboard-layout'

test.describe('REQ-012: 레이아웃 템플릿 시스템 E2E 테스트', () => {

  /**
   * TST-012-01: localStorage에 레이아웃 설정이 없는 상태에서 프로젝트 상세 페이지 접속
   * 기대: 템플릿 A (3컬럼) 레이아웃이 기본으로 렌더링됨
   */
  test('TST-012-01: localStorage 없을 때 템플릿 A(3컬럼) 기본 렌더링', async ({ page }) => {
    // localStorage 클리어 후 접속
    await page.goto(PROJECT_URL)
    await page.evaluate(() => localStorage.removeItem('vulcan-dashboard-layout'))
    await page.reload()

    // data-testid="layout-a"가 렌더링되어야 함
    await page.waitForSelector('[data-testid="layout-a"]', { timeout: 10000 })
    await expect(page.locator('[data-testid="layout-a"]')).toBeVisible()

    // layout-b는 렌더링되지 않아야 함
    await expect(page.locator('[data-testid="layout-b"]')).not.toBeVisible()

    // 3컬럼 구조 확인: docs / center / commits 컨테이너
    await expect(page.locator('[data-testid="layout-a-docs"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-a-center"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-a-commits"]')).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-012-01-templateA-기본렌더링.png') })
  })

  /**
   * TST-012-02: localStorage에 "vulcan-dashboard-layout": "A2"가 설정된 상태에서 접속
   * 기대: 템플릿 A2 레이아웃이 렌더링됨
   */
  test('TST-012-02: localStorage에 A2가 설정된 상태에서 템플릿 A2 렌더링', async ({ page }) => {
    await page.goto(PROJECT_URL)
    await page.evaluate((key) => localStorage.setItem(key, 'A2'), STORAGE_KEY)
    await page.reload()

    await page.waitForSelector('[data-testid="layout-a2"]', { timeout: 10000 })
    await expect(page.locator('[data-testid="layout-a2"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-a"]')).not.toBeVisible()
    await expect(page.locator('[data-testid="layout-b"]')).not.toBeVisible()

    await expect(page.locator('[data-testid="layout-a2-docs"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-a2-center"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-a2-side"]')).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-012-02-templateA2-렌더링.png') })
  })

  /**
   * TST-012-02B: localStorage에 "vulcan-dashboard-layout": "B"가 설정된 상태에서 접속
   * 기대: 템플릿 B (상단 stats + 하단 2컬럼) 레이아웃이 렌더링됨
   */
  test('TST-012-02B: localStorage에 B가 설정된 상태에서 템플릿 B 렌더링', async ({ page }) => {
    await page.goto(PROJECT_URL)
    // localStorage에 B 설정 후 새로고침
    await page.evaluate((key) => localStorage.setItem(key, 'B'), STORAGE_KEY)
    await page.reload()

    // data-testid="layout-b"가 렌더링되어야 함
    await page.waitForSelector('[data-testid="layout-b"]', { timeout: 10000 })
    await expect(page.locator('[data-testid="layout-b"]')).toBeVisible()

    // layout-a는 렌더링되지 않아야 함
    await expect(page.locator('[data-testid="layout-a"]')).not.toBeVisible()

    // 상단 stats + 하단 좌/우 컨테이너 확인
    await expect(page.locator('[data-testid="layout-b-left"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-b-commits"]')).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-012-02-templateB-렌더링.png') })
  })

  /**
   * TST-012-03: 프로젝트 상세 페이지에서 우측 상단 레이아웃 토글 버튼 클릭
   * 기대: 페이지 새로고침 없이 레이아웃이 A → A2 → B → A로 즉시 전환됨
   */
  test('TST-012-03: 토글 버튼 클릭 시 레이아웃 즉시 전환 (페이지 리로드 없음)', async ({ page }) => {
    // localStorage 초기화 후 A 상태로 시작
    await page.goto(PROJECT_URL)
    await page.evaluate((key) => localStorage.removeItem(key), STORAGE_KEY)
    await page.reload()

    await page.waitForSelector('[data-testid="layout-a"]', { timeout: 10000 })

    // 토글 버튼 확인 — Columns 아이콘 (A 상태)
    const toggleBtn = page.locator('[data-testid="layout-toggle"]')
    await expect(toggleBtn).toBeVisible()
    await expect(page.locator('[data-testid="icon-columns"]')).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-012-03-토글버튼-A상태.png') })

    // 클릭 — A → A2 전환
    await toggleBtn.click()

    // 페이지 URL이 변경되지 않아야 함 (SPA 전환)
    await expect(page).toHaveURL(new RegExp(PROJECT_ID))

    // layout-a2 렌더링 확인
    await expect(page.locator('[data-testid="layout-a2"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-a"]')).not.toBeVisible()

    // 아이콘이 PanelLeft로 전환됨
    await expect(page.locator('[data-testid="icon-panel-left"]')).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-012-03-토글버튼-A2전환후.png') })

    // A2 → B 전환
    await toggleBtn.click()
    await expect(page.locator('[data-testid="layout-b"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-a2"]')).not.toBeVisible()

    // 아이콘이 LayoutGrid로 전환됨
    await expect(page.locator('[data-testid="icon-layout-grid"]')).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-012-03-토글버튼-B전환후.png') })

    // B → A 재전환
    await toggleBtn.click()
    await expect(page.locator('[data-testid="layout-a"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-b"]')).not.toBeVisible()
    await expect(page.locator('[data-testid="icon-columns"]')).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-012-03-토글버튼-A재전환.png') })
  })

  /**
   * TST-012-04: 템플릿 B로 전환 후 페이지 새로고침
   * 기대: 새로고침 후 localStorage 저장값이 복원되어 템플릿 B 레이아웃이 자동으로 적용됨
   */
  test('TST-012-04: 템플릿 B 전환 후 새로고침 시 B 유지 (localStorage 영속성)', async ({ page }) => {
    await page.goto(PROJECT_URL)
    await page.evaluate((key) => localStorage.removeItem(key), STORAGE_KEY)
    await page.reload()

    await page.waitForSelector('[data-testid="layout-a"]', { timeout: 10000 })

    // A → A2 → B 전환
    await page.locator('[data-testid="layout-toggle"]').click()
    await expect(page.locator('[data-testid="layout-a2"]')).toBeVisible()
    await page.locator('[data-testid="layout-toggle"]').click()
    await expect(page.locator('[data-testid="layout-b"]')).toBeVisible()

    // localStorage 저장값 확인
    const storedValue = await page.evaluate((key) => localStorage.getItem(key), STORAGE_KEY)
    expect(storedValue).toBe('B')

    // 새로고침
    await page.reload()
    await page.waitForSelector('[data-testid="layout-b"]', { timeout: 10000 })

    // B가 복원되어야 함
    await expect(page.locator('[data-testid="layout-b"]')).toBeVisible()
    await expect(page.locator('[data-testid="layout-a"]')).not.toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-012-04-새로고침후B유지.png') })
  })

  /**
   * TST-012-05: localStorage에 유효하지 않은 값 저장 후 접속
   * 기대: useLayoutTemplate 초기화 시 'A'로 폴백
   */
  test('TST-012-05: localStorage 유효하지 않은 값("C", "undefined", "") → A 폴백', async ({ page }) => {
    const invalidValues = ['C', 'undefined', '']

    for (const invalidVal of invalidValues) {
      await page.goto(PROJECT_URL)
      await page.evaluate(
        ({ key, val }) => localStorage.setItem(key, val),
        { key: STORAGE_KEY, val: invalidVal }
      )
      await page.reload()

      await page.waitForSelector('[data-testid="layout-a"]', { timeout: 10000 })

      // A로 폴백되어야 함
      await expect(page.locator('[data-testid="layout-a"]')).toBeVisible()
      await expect(page.locator('[data-testid="layout-b"]')).not.toBeVisible()
    }

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-012-05-유효하지않은값-폴백.png') })
  })

  /**
   * TST-SEC-012-01: localStorage 값 주입 시도
   * 기대: 'C', '<script>alert(1)</script>', '../etc/passwd' 등 임의 값 → A로 강제 폴백
   */
  test('TST-SEC-012-01: localStorage 악의적 값 주입 시도 → A 폴백 (SEC-012-01)', async ({ page }) => {
    const maliciousValues = [
      'C',
      '<script>alert(1)</script>',
      '../etc/passwd',
      'javascript:void(0)',
      '{"template":"B"}',
    ]

    for (const malVal of maliciousValues) {
      await page.goto(PROJECT_URL)
      await page.evaluate(
        ({ key, val }) => localStorage.setItem(key, val),
        { key: STORAGE_KEY, val: malVal }
      )
      await page.reload()

      await page.waitForSelector('[data-testid="layout-a"]', { timeout: 10000 })

      // 임의 값이 레이아웃 로직에 영향을 주지 않고 A로 폴백되어야 함
      await expect(page.locator('[data-testid="layout-a"]')).toBeVisible()
      await expect(page.locator('[data-testid="layout-b"]')).not.toBeVisible()
    }

    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'TST-SEC-012-01-주입차단-A폴백.png') })
  })
})
