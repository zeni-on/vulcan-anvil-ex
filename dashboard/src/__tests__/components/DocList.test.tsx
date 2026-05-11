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
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import DocList from '@/components/DocList'
import { DocEntry } from '@/lib/types'

const mockDocs: DocEntry[] = [
  { name: 'REQUIREMENTS', path: 'docs/artifacts/01-requirements/REQUIREMENTS.md', category: 'requirements' },
  { name: 'function-spec', path: 'docs/artifacts/02-design/function/function-spec.md', category: 'design' },
  { name: 'screen-spec', path: 'docs/artifacts/02-design/screen/screen-spec.md', category: 'design' },
  { name: 'TEST_PLAN', path: 'docs/artifacts/03-test/TEST_PLAN.md', category: 'test-plan' },
  { name: 'ux-review', path: 'docs/artifacts/04-review/ux-review.md', category: 'review' },
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

  it('design 카테고리 파일을 하위 폴더별로 표시한다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByTestId('doc-subfolder-function')).toBeInTheDocument()
    expect(screen.getByTestId('doc-subfolder-screen')).toBeInTheDocument()
    expect(screen.getByText('function-spec')).toBeInTheDocument()
    expect(screen.getByText('screen-spec')).toBeInTheDocument()
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
    fireEvent.click(screen.getByTestId('doc-category-toggle-other'))
    expect(screen.getByText('NOTE')).toBeInTheDocument()
  })

  it('산출물과 운영/템플릿 문서를 별도 섹션으로 분리한다', () => {
    const mixedDocs: DocEntry[] = [
      ...mockDocs,
      { name: 'FUNCTION_SPEC_TEMPLATE', path: 'docs/templates/FUNCTION_SPEC_TEMPLATE.md', category: 'templates' },
      { name: 'GATE_PROMPTS', path: 'docs/adapters/codex-gpt/GATE_PROMPTS.md', category: 'agent' },
    ]
    render(<DocList docs={mixedDocs} />)

    expect(screen.getByTestId('doc-section-프로젝트 산출물')).toBeInTheDocument()
    expect(screen.getByTestId('doc-section-운영/템플릿')).toBeInTheDocument()
    expect(screen.getByText('REQUIREMENTS')).toBeInTheDocument()
    expect(screen.queryByText('FUNCTION_SPEC_TEMPLATE')).not.toBeInTheDocument()

    fireEvent.click(screen.getByTestId('doc-category-toggle-templates'))
    expect(screen.getByText('FUNCTION_SPEC_TEMPLATE')).toBeInTheDocument()
  })

  it('프로젝트 산출물은 문서가 없는 카테고리도 폴더 구조로 렌더링한다', () => {
    const reqOnly: DocEntry[] = [
      { name: 'REQUIREMENTS', path: 'docs/artifacts/01-requirements/REQUIREMENTS.md', category: 'requirements' },
    ]
    render(<DocList docs={reqOnly} />)
    expect(screen.getByTestId('doc-category-design')).toBeInTheDocument()
    expect(screen.getByTestId('doc-category-review')).toBeInTheDocument()
    expect(screen.getByTestId('doc-category-toggle-design')).toHaveTextContent('(0)')
    expect(screen.getByTestId('doc-category-toggle-review')).toHaveTextContent('(0)')
  })

  it('카테고리 토글 버튼이 렌더링된다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByTestId('doc-category-toggle-requirements')).toBeInTheDocument()
    expect(screen.getByTestId('doc-category-toggle-design')).toBeInTheDocument()
  })

  it('카테고리 토글 버튼 클릭 시 문서 목록이 접힌다', () => {
    render(<DocList docs={mockDocs} />)
    expect(screen.getByText('REQUIREMENTS')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('doc-category-toggle-requirements'))
    expect(screen.queryByText('REQUIREMENTS')).not.toBeInTheDocument()
  })

  it('카테고리 토글 버튼 두 번 클릭 시 문서 목록이 다시 펼쳐진다', () => {
    render(<DocList docs={mockDocs} />)
    const toggle = screen.getByTestId('doc-category-toggle-requirements')
    fireEvent.click(toggle)
    expect(screen.queryByText('REQUIREMENTS')).not.toBeInTheDocument()
    fireEvent.click(toggle)
    expect(screen.getByText('REQUIREMENTS')).toBeInTheDocument()
  })

  it('카테고리 토글 버튼에 aria-expanded 속성이 설정된다', () => {
    render(<DocList docs={mockDocs} />)
    const toggle = screen.getByTestId('doc-category-toggle-requirements')
    expect(toggle).toHaveAttribute('aria-expanded', 'true')
    fireEvent.click(toggle)
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
  })
})
