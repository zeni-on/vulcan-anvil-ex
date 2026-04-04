/**
 * @file __tests__/components/EmptyState.test.tsx
 * @description EmptyState 컴포넌트 렌더링 테스트
 *
 * 커버 항목:
 * - 온보딩 안내 텍스트 렌더링
 * - 프로젝트 추가 CTA 버튼 렌더링
 * - 버튼 클릭 시 onAddProject 콜백 호출
 *
 * @see docs/02-design/ui-design.md §EmptyState
 */

import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import EmptyState from '@/components/EmptyState'

describe('EmptyState', () => {
  it('"등록된 프로젝트가 없습니다" 제목을 렌더링한다', () => {
    render(<EmptyState onAddProject={() => {}} />)
    expect(screen.getByText('등록된 프로젝트가 없습니다')).toBeInTheDocument()
  })

  it('온보딩 안내 설명 텍스트를 렌더링한다', () => {
    render(<EmptyState onAddProject={() => {}} />)
    expect(screen.getByText(/Vulcan 프로젝트를 추가하여/)).toBeInTheDocument()
  })

  it('"첫 번째 프로젝트 추가" 버튼을 렌더링한다', () => {
    render(<EmptyState onAddProject={() => {}} />)
    expect(screen.getByTestId('empty-state-add-button')).toBeInTheDocument()
  })

  it('추가 버튼 클릭 시 onAddProject 콜백을 호출한다', () => {
    const mockOnAddProject = jest.fn()
    render(<EmptyState onAddProject={mockOnAddProject} />)

    fireEvent.click(screen.getByTestId('empty-state-add-button'))

    expect(mockOnAddProject).toHaveBeenCalledTimes(1)
  })

  it('data-testid="empty-state" 속성을 가진 컨테이너를 렌더링한다', () => {
    render(<EmptyState onAddProject={() => {}} />)
    expect(screen.getByTestId('empty-state')).toBeInTheDocument()
  })

  it('min-h-[400px] 최소 높이 클래스를 적용한다', () => {
    render(<EmptyState onAddProject={() => {}} />)
    const container = screen.getByTestId('empty-state')
    expect(container.className).toContain('min-h-[400px]')
  })
})
