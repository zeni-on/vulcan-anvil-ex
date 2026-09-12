import React from 'react'
import { render, screen, within } from '@testing-library/react'
import '@testing-library/jest-dom'
import GateStatusStepper from '../../components/GateStatusStepper'
import GateProgressChart from '../../components/GateProgressChart'
import GateProgress from '../../components/GateProgress'
import CurrentGatePanel from '../../components/CurrentGatePanel'
import LayoutA2 from '../../components/LayoutA2'
import { PRODUCT_STATES, productSession, newProductSession } from '../fixtures/productSession'
import { BASE_SESSION } from '../e2e/fixture'
import ProductProcessPanel from '../../components/ProductProcessPanel'

test('new Product scope is intelligible and read-only without authority claims', () => {
  render(<ProductProcessPanel session={newProductSession()} />)
  expect(screen.getByRole('heading', { name: '기획·설계' })).toBeVisible()
  expect(screen.getByText('docs/product/PRODUCT_BRIEF.md')).toBeVisible()
  expect(screen.getByText('아직 관련 ID, 계약, 테스트, 필수 검사가 등록되지 않았습니다.')).toBeVisible()
  expect(screen.getByText('Product · 읽기 전용 · 저장된 상태 · 증적 미검증')).toBeVisible()
  expect(screen.getByText('저장된 단계 완료: 0 / 3')).toBeVisible()
  expect(screen.getAllByText('대기')).toHaveLength(2)
  expect(screen.queryByRole('button')).not.toBeInTheDocument()
  expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
  expect(screen.queryByText(/실험|인수 완료|최종 승인/)).not.toBeInTheDocument()
})

test.each(['related_ids', 'contracts', 'tests', 'required_checks'] as const)('populated %s is not described as empty scope', key => {
  const session = newProductSession()
  if (key === 'contracts' || key === 'tests') session.current_work.scope[key] = [{ ref: 'docs/check.md', revision: 'r1' }]
  else session.current_work.scope[key] = ['CHECK-001']
  render(<ProductProcessPanel session={session} />)
  expect(screen.queryByText(/아직 관련 ID/)).not.toBeInTheDocument()
})

test.each(PRODUCT_STATES)('A2 displays minimal %s without stats or old gate summaries', state => {
  render(<LayoutA2 projectId="pilot" session={productSession(state)} sessionLoading={false} sessionError={null} docs={[]} docsLoading={false} docsError={null} commits={[]} commitsLoading={false} commitsError={null} onDocSelect={() => {}} />)
  const panel = screen.getByTestId('product-process-panel')
  expect(within(panel).getAllByRole('listitem')).toHaveLength(3)
  expect(within(panel).getByText('docs/work.md#request')).toBeVisible()
  expect(within(panel).getByText('REQ-001, SEC-001')).toBeVisible()
  expect(within(panel).getByText('릴리즈 별도 승인 필요')).toBeVisible()
  expect(screen.queryByText(/Gate 5|최종 승인|Build Wave/)).not.toBeInTheDocument()
  if (state === 'completed') expect(within(panel).getByRole('heading', { name: '이번 범위 인수 완료' })).toBeVisible()
})

test.each([GateStatusStepper, GateProgressChart, GateProgress])('%p routes pilot to persisted stages', Component => {
  render(<Component session={productSession('completed')} />)
  expect(screen.getByRole('heading', { name: '이번 범위 인수 완료' })).toBeVisible()
  expect(screen.getAllByRole('listitem')).toHaveLength(3)
})

test('CurrentGate does not interpret pilot impl as legacy implementation', () => {
  render(<CurrentGatePanel session={productSession('impl')} stats={BASE_SESSION.stats} docs={[]} />)
  expect(screen.getByTestId('product-process-panel')).toBeVisible()
  expect(screen.queryByTestId('gate-content-impl')).not.toBeInTheDocument()
})
