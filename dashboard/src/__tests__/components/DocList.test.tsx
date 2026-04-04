/**
 * @file __tests__/components/DocList.test.tsx
 * @description DocList 컴포넌트 렌더링 테스트
 *
 * 커버 항목:
 * - data-testid="doc-list" 컨테이너 렌더링
 * - 빈 배열 → "산출물 문서가 없습니다." 메시지 표시
 * - requirements 카테고리 섹션 렌더링
 * - design 카테고리 섹션 렌더링
 * - 여러 카테고리가 혼합된 경우 각 섹션 그룹 분리
 * - 각 파일명이 doc-item에 표시됨
 * - data-testid="doc-category-{category}" 존재 확인
 *
 * @see docs/02-design/req-005-009-design.md §DocList
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import DocList from '@/components/DocList'
import { DocEntry } from '@/lib/types'

const mockDocs: DocEntry[] = [
  { name: 'REQUIREMENTS',   path: 'docs/01-requirements/REQUIREMENTS.md',   category: 'requirements' },
  { name: 'req-001-design', path: 'docs/02-design/req-001-design.md',        category: 'design' },
  { name: 'ui-design',      path: 'docs/02-design/ui-design.md',             category: 'design' },
  { name: 'TEST_PLAN',      path: 'docs/03-test-plan/TEST_PLAN.md',          category: 'test-plan' },
  { name: 'ux-review',      path: 'docs/04-review/ux-review.md',             category: 'review' },
]

describe('DocList', () => {
  it('data-testid="doc-list" 컨테이너를 렌더링한다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByTestId('doc-list')).toBeInTheDocument()
  })

  it('빈 배열 전달 시 "산출물 문서가 없습니다." 메시지를 표시한다', () => {
    render(<DocList docs={[]} />)
    expect(screen.getByText('산출물 문서가 없습니다.')).toBeInTheDocument()
  })

  it('requirements 카테고리 섹션을 렌더링한다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByTestId('doc-category-requirements')).toBeInTheDocument()
  })

  it('design 카테고리 섹션을 렌더링한다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByTestId('doc-category-design')).toBeInTheDocument()
  })

  it('test-plan 카테고리 섹션을 렌더링한다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByTestId('doc-category-test-plan')).toBeInTheDocument()
  })

  it('review 카테고리 섹션을 렌더링한다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByTestId('doc-category-review')).toBeInTheDocument()
  })

  it('REQUIREMENTS 파일명을 doc-item에 표시한다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByText('REQUIREMENTS')).toBeInTheDocument()
  })

  it('design 카테고리 파일들(req-001-design, ui-design)을 표시한다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByText('req-001-design')).toBeInTheDocument()
    expect(screen.getByText('ui-design')).toBeInTheDocument()
  })

  it('총 5개의 doc-item을 렌더링한다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getAllByTestId('doc-item')).toHaveLength(5)
  })

  it('other 카테고리 파일도 렌더링한다', () => {
    const otherDocs: DocEntry[] = [
      { name: 'NOTE', path: 'docs/NOTE.md', category: 'other' },
    ]
    render(<DocList docs={otherDocs} />)
    expect(screen.getByTestId('doc-category-other')).toBeInTheDocument()
    expect(screen.getByText('NOTE')).toBeInTheDocument()
  })

  it('카테고리에 해당하는 문서가 없으면 해당 섹션을 렌더링하지 않는다', () => {
    const reqOnly: DocEntry[] = [
      { name: 'REQUIREMENTS', path: 'docs/01-requirements/REQUIREMENTS.md', category: 'requirements' },
    ]
    render(<DocList docs={reqOnly} />)
    expect(screen.queryByTestId('doc-category-design')).not.toBeInTheDocument()
    expect(screen.queryByTestId('doc-category-review')).not.toBeInTheDocument()
  })
})
