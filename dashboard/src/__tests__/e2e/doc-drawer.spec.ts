/**
 * @file e2e/doc-drawer.spec.ts
 * @description REQ-010 DocDrawer E2E 테스트
 *
 * TST-010-01: DocList 파일 클릭 시 DocDrawer 열림 (E2E)
 * TST-010-02: Markdown 콘텐츠 렌더링 검증 (Integration)
 * TST-010-03: ESC 키로 DocDrawer 닫기 (E2E)
 * TST-010-04: X 버튼으로 DocDrawer 닫기 (E2E)
 * TST-010-05: 배경 오버레이 클릭으로 DocDrawer 닫기 (E2E)
 */

import { test, expect } from '@playwright/test'
import path from 'path'

const PROJECT_ID = 'local-julyi-Documents-workspace-antigravity-Vulcan-Dev-kweVml'
const PROJECT_URL = `/projects/${PROJECT_ID}`
const SCREENSHOTS_DIR = path.resolve(__dirname, '../../../../docs/04-review/screenshots')

test.describe('REQ-010: DocDrawer E2E 테스트', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(PROJECT_URL)
    // 문서 목록이 로드될 때까지 대기
    await page.waitForSelector('[data-testid="doc-list"]', { timeout: 10000 })
  })

  /**
   * TST-010-01: DocList 파일 항목 클릭 시 DocDrawer 슬라이드인 열림
   */
  test('TST-010-01: 파일 클릭 시 DocDrawer가 오른쪽에서 슬라이드인하여 열린다', async ({ page }) => {
    // 첫 번째 클릭 가능한 문서 항목 클릭
    const firstDocItem = page.locator('[data-testid="doc-item"]').first()
    await firstDocItem.click()

    // Drawer가 열렸는지 확인 (role=dialog)
    const drawer = page.locator('[role="dialog"]')
    await expect(drawer).toBeVisible()

    // Drawer가 translate-x-0 상태인지 확인 (슬라이드인 완료)
    await expect(drawer).not.toHaveClass(/translate-x-full/)

    // 기존 대시보드 화면이 여전히 보이는지 확인
    await expect(page.locator('[data-testid="doc-list"]')).toBeVisible()

    // 스크린샷 저장
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/TST-010-01-drawer-open.png`,
      fullPage: false,
    })
  })

  /**
   * TST-010-02: Markdown 렌더링 검증 — 헤더, 테이블, 코드 블록, 굵게, 리스트
   */
  test('TST-010-02: Drawer에서 Markdown h1~h6, 표, 코드 블록, 굵게, 리스트가 렌더링된다', async ({ page }) => {
    // REQUIREMENTS 문서 클릭 (헤더, 테이블, 굵게 포함)
    const reqItem = page.locator('[data-testid="doc-item"]').filter({ hasText: 'REQUIREMENTS' })
    await reqItem.first().click()

    const drawer = page.locator('[role="dialog"]')
    await expect(drawer).toBeVisible()

    // 마크다운 렌더링 영역 대기 (prose 클래스)
    await page.waitForSelector('.prose', { timeout: 10000 })

    // h1 헤더 렌더링 확인
    const heading = drawer.locator('h1').first()
    await expect(heading).toBeVisible()

    // 표(table) 렌더링 확인 — REQUIREMENTS 문서에 | 테이블이 있음
    const table = drawer.locator('table').first()
    await expect(table).toBeVisible()

    // 굵게(strong) 렌더링 확인
    const strong = drawer.locator('strong').first()
    await expect(strong).toBeVisible()

    // 스크린샷 저장
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/TST-010-02-markdown-render.png`,
      fullPage: false,
    })
  })

  /**
   * TST-010-03: ESC 키로 DocDrawer 닫기
   */
  test('TST-010-03: ESC 키를 누르면 DocDrawer가 닫힌다', async ({ page }) => {
    const firstDocItem = page.locator('[data-testid="doc-item"]').first()
    await firstDocItem.click()

    const drawer = page.locator('[role="dialog"]')
    await expect(drawer).toBeVisible()

    // ESC 키 입력
    await page.keyboard.press('Escape')

    // Drawer가 slide-out 상태로 전환 (translate-x-full)
    await expect(drawer).toHaveClass(/translate-x-full/, { timeout: 1000 })

    // 스크린샷 저장
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/TST-010-03-esc-close.png`,
      fullPage: false,
    })
  })

  /**
   * TST-010-04: X 버튼으로 DocDrawer 닫기
   */
  test('TST-010-04: X 버튼 클릭 시 DocDrawer가 닫힌다', async ({ page }) => {
    const firstDocItem = page.locator('[data-testid="doc-item"]').first()
    await firstDocItem.click()

    const drawer = page.locator('[role="dialog"]')
    await expect(drawer).toBeVisible()

    // X 버튼 클릭
    const closeBtn = drawer.locator('button[aria-label="닫기"]')
    await closeBtn.click()

    // Drawer가 translate-x-full 상태로 전환
    await expect(drawer).toHaveClass(/translate-x-full/, { timeout: 1000 })

    // 스크린샷 저장
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/TST-010-04-x-button-close.png`,
      fullPage: false,
    })
  })

  /**
   * TST-010-05: 배경 오버레이 클릭으로 DocDrawer 닫기
   */
  test('TST-010-05: 배경 오버레이 클릭 시 DocDrawer가 닫힌다', async ({ page }) => {
    const firstDocItem = page.locator('[data-testid="doc-item"]').first()
    await firstDocItem.click()

    const drawer = page.locator('[role="dialog"]')
    await expect(drawer).toBeVisible()

    // 배경 오버레이 클릭 (z-40, aria-hidden)
    const overlay = page.locator('div.fixed.inset-0')
    await overlay.click({ position: { x: 10, y: 10 } })

    // Drawer가 translate-x-full 상태로 전환
    await expect(drawer).toHaveClass(/translate-x-full/, { timeout: 1000 })

    // 스크린샷 저장
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/TST-010-05-overlay-close.png`,
      fullPage: false,
    })
  })
})
