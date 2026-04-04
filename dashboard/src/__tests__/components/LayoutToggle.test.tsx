/**
 * @file __tests__/components/LayoutToggle.test.tsx
 * @description LayoutToggle 컴포넌트 단위 테스트
 *
 * 커버 항목:
 * - UT-012-07: template='A'일 때 Columns 아이콘(data-testid="icon-columns") 렌더링
 * - UT-012-08: template='B'일 때 LayoutGrid 아이콘(data-testid="icon-layout-grid") 렌더링
 * - UT-012-09: 버튼 클릭 시 onToggle 콜백 호출됨
 *
 * @see docs/02-design/req-012-design.md §LayoutToggle
 */

import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import LayoutToggle from '@/components/LayoutToggle'

// ── UT-012-07 ─────────────────────────────────────────────────────────────────

describe('UT-012-07: template=A일 때 Columns 아이콘 렌더링', () => {
  it('template이 A이면 data-testid="icon-columns" 아이콘이 렌더링된다', () => {
    render(<LayoutToggle template="A" onToggle={() => {}} />)
    expect(screen.getByTestId('icon-columns')).toBeInTheDocument()
  })

  it('template이 A이면 data-testid="icon-layout-grid" 아이콘이 렌더링되지 않는다', () => {
    render(<LayoutToggle template="A" onToggle={() => {}} />)
    expect(screen.queryByTestId('icon-layout-grid')).not.toBeInTheDocument()
  })

  it('template이 A이면 "템플릿 A" 텍스트가 포함된다', () => {
    render(<LayoutToggle template="A" onToggle={() => {}} />)
    expect(screen.getByText('템플릿 A')).toBeInTheDocument()
  })
})

// ── UT-012-08 ─────────────────────────────────────────────────────────────────

describe('UT-012-08: template=B일 때 LayoutGrid 아이콘 렌더링', () => {
  it('template이 B이면 data-testid="icon-layout-grid" 아이콘이 렌더링된다', () => {
    render(<LayoutToggle template="B" onToggle={() => {}} />)
    expect(screen.getByTestId('icon-layout-grid')).toBeInTheDocument()
  })

  it('template이 B이면 data-testid="icon-columns" 아이콘이 렌더링되지 않는다', () => {
    render(<LayoutToggle template="B" onToggle={() => {}} />)
    expect(screen.queryByTestId('icon-columns')).not.toBeInTheDocument()
  })

  it('template이 B이면 "템플릿 B" 텍스트가 포함된다', () => {
    render(<LayoutToggle template="B" onToggle={() => {}} />)
    expect(screen.getByText('템플릿 B')).toBeInTheDocument()
  })
})

// ── UT-012-09 ─────────────────────────────────────────────────────────────────

describe('UT-012-09: 버튼 클릭 시 onToggle 콜백 호출', () => {
  it('버튼을 클릭하면 onToggle 콜백이 1회 호출된다', () => {
    const onToggle = jest.fn()
    render(<LayoutToggle template="A" onToggle={onToggle} />)

    fireEvent.click(screen.getByTestId('layout-toggle'))

    expect(onToggle).toHaveBeenCalledTimes(1)
  })

  it('template=B 상태에서도 버튼 클릭 시 onToggle 콜백이 호출된다', () => {
    const onToggle = jest.fn()
    render(<LayoutToggle template="B" onToggle={onToggle} />)

    fireEvent.click(screen.getByTestId('layout-toggle'))

    expect(onToggle).toHaveBeenCalledTimes(1)
  })

  it('버튼에 aria-label="레이아웃 전환" 속성이 있다', () => {
    render(<LayoutToggle template="A" onToggle={() => {}} />)
    expect(screen.getByRole('button', { name: '레이아웃 전환' })).toBeInTheDocument()
  })
})
