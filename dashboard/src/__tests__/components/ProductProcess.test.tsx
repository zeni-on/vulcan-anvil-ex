import React from 'react'
import { render, screen, within } from '@testing-library/react'
import '@testing-library/jest-dom'
import GateStatusStepper from '../../components/GateStatusStepper'
import GateProgressChart from '../../components/GateProgressChart'
import GateProgress from '../../components/GateProgress'
import CurrentGatePanel from '../../components/CurrentGatePanel'
import LayoutA2 from '../../components/LayoutA2'
import { PRODUCT_STATES, productSession } from '../fixtures/productSession'
import { BASE_SESSION } from '../e2e/fixture'

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
