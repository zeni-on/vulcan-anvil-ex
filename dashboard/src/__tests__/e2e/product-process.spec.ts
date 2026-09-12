import fs from 'node:fs'
import path from 'node:path'
import { test, expect } from '@playwright/test'
import { PRODUCT_STATES, productSession, newProductSession, invalidProductSessions } from '../fixtures/productSession'
import { BASE_SESSION } from './fixture'

let root: string
let id: string
test.beforeAll(async ({ request }) => {
  fs.mkdirSync(path.resolve('test-results'), { recursive: true })
  root = fs.mkdtempSync(path.resolve('test-results/product-e2e-'))
  fs.writeFileSync(path.join(root, 'session.json'), JSON.stringify(productSession()))
  const response = await request.post('/api/projects', { data: { type: 'local', path: root } })
  expect(response.ok()).toBeTruthy()
  id = (await response.json()).project.id
})
test.afterAll(async ({ request }) => {
  if (id) await request.delete(`/api/projects/${id}`)
  if (root) fs.rmSync(root, { recursive: true, force: true })
})

for (const width of [390, 1440]) {
  test(`new Product init empty scope at ${width}px`, async ({ page, request }) => {
    const session = newProductSession()
    const serialized = JSON.stringify(session)
    fs.writeFileSync(path.join(root, 'session.json'), serialized)
    expect((await (await request.get(`/api/projects/${id}/session`)).json()).session).toEqual(session)
    await page.setViewportSize({ width, height: 1000 })
    await page.addInitScript(() => localStorage.setItem('vulcan-dashboard-layout', 'A2'))
    await page.goto(`/projects/${id}`)
    const panel = page.getByTestId('product-process-panel')
    await expect(page.getByRole('heading', { name: 'Product', exact: true })).toBeVisible()
    await expect(panel.getByRole('heading', { name: '기획·설계' })).toBeVisible()
    await expect(panel.getByText('docs/product/PRODUCT_BRIEF.md')).toBeVisible()
    await expect(panel.getByText('아직 관련 ID, 계약, 테스트, 필수 검사가 등록되지 않았습니다.')).toBeVisible()
    await expect(panel.getByText('Product · 읽기 전용 · 저장된 상태 · 증적 미검증')).toBeVisible()
    await expect(panel.getByText('저장된 단계 완료: 0 / 3')).toBeVisible()
    await expect(panel.getByText('대기', { exact: true })).toHaveCount(2)
    await expect(panel.getByRole('button')).toHaveCount(0)
    await expect(page.getByText(/Product 실험|Gate 5|최종 승인|이번 범위 인수 완료/)).toHaveCount(0)
    expect(await panel.evaluate(el => el.scrollWidth <= el.clientWidth)).toBeTruthy()
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()
    await page.screenshot({ path: test.info().outputPath(`new-product-${width}.png`), fullPage: true })
    expect(fs.readFileSync(path.join(root, 'session.json'), 'utf8')).toBe(serialized)
  })

  for (const state of PRODUCT_STATES) {
    test(`${state} persisted minimal session at ${width}px`, async ({ page, request }) => {
      const serialized = JSON.stringify(productSession(state))
      fs.writeFileSync(path.join(root, 'session.json'), serialized)
      const response = await request.get(`/api/projects/${id}/session`)
      expect((await response.json()).session).toEqual(productSession(state))
      await page.setViewportSize({ width, height: 1000 })
      await page.addInitScript(() => localStorage.setItem('vulcan-dashboard-layout', 'A2'))
      await Promise.all([
        page.waitForResponse(response => response.url().endsWith(`/api/projects/${id}/session`) && response.status() === 200),
        page.goto(`/projects/${id}`),
      ])
      const panel = page.getByTestId('product-process-panel')
      await expect(panel).toBeVisible()
      await expect(panel.getByRole('listitem')).toHaveCount(3)
      await expect(panel.getByText('docs/work.md#request')).toBeVisible()
      await expect(panel.getByText('릴리즈 별도 승인 필요')).toBeVisible()
      await expect(page.getByText(/Gate 5|최종 승인|Build Wave/)).toHaveCount(0)
      if (state === 'completed') await expect(panel.getByRole('heading', { name: '이번 범위 인수 완료' })).toBeVisible()
      expect(await panel.evaluate(el => el.scrollWidth <= el.clientWidth)).toBeTruthy()
      if (width < 1280) {
        const center = page.getByTestId('layout-a2-center')
        expect(await center.evaluate(el => el.scrollHeight <= el.clientHeight)).toBeTruthy()
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()
      }
      await page.screenshot({ path: test.info().outputPath(`${state}-${width}.png`), fullPage: true })
      expect(fs.readFileSync(path.join(root, 'session.json'), 'utf8')).toBe(serialized)
    })
  }
}

for (const template of ['A', 'B']) {
  test(`mobile ${template} keeps the scoped panel unclipped`, async ({ page }) => {
    fs.writeFileSync(path.join(root, 'session.json'), JSON.stringify(productSession('completed')))
    await page.setViewportSize({ width: 390, height: 1000 })
    await page.addInitScript(value => localStorage.setItem('vulcan-dashboard-layout', value), template)
    await Promise.all([
      page.waitForResponse(response => response.url().endsWith(`/api/projects/${id}/session`) && response.status() === 200),
      page.goto(`/projects/${id}`),
    ])
    const panel = page.getByTestId('product-process-panel')
    await expect(panel).toBeVisible()
    await expect(panel.getByText('REQ-001, SEC-001')).toBeVisible()
    const container = page.getByTestId(template === 'A' ? 'layout-a-center' : 'layout-b-left')
    expect(await container.evaluate(el => el.scrollHeight <= el.clientHeight)).toBeTruthy()
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()
  })
}

for (const profile of ['product', 'audit', 'poc']) {
  test(`unmarked ${profile} retains legacy Dashboard`, async ({ page, request }) => {
    const session = { ...BASE_SESSION, profile }
    fs.writeFileSync(path.join(root, 'session.json'), JSON.stringify(session))
    expect((await (await request.get(`/api/projects/${id}/session`)).json()).session).toEqual(session)
    await page.addInitScript(() => localStorage.setItem('vulcan-dashboard-layout', 'A2'))
    await page.goto(`/projects/${id}`)
    await expect(page.getByTestId('gate-status-stepper')).toBeVisible()
    await expect(page.getByTestId('product-process-panel')).toHaveCount(0)
  })
}

for (const [label, value] of invalidProductSessions()) {
  test(`rejects ${label} without legacy fallback`, async ({ page, request }) => {
    fs.writeFileSync(path.join(root, 'session.json'), JSON.stringify(value))
    expect((await request.get(`/api/projects/${id}/session`)).status()).toBe(503)
    await Promise.all([
      page.waitForResponse(response => response.url().endsWith(`/api/projects/${id}/session`) && response.status() === 503),
      page.goto(`/projects/${id}`),
    ])
    await expect(page.getByText('Gate 상태를 불러오지 못했습니다.')).toBeVisible()
    await expect(page.getByTestId('gate-status-stepper')).toHaveCount(0)
    await expect(page.getByTestId('product-process-panel')).toHaveCount(0)
    const projects = await (await request.get('/api/projects')).json()
    expect(projects.projects.some((project: { id: string }) => project.id === id)).toBeTruthy()
  })
}
