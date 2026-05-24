import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import DocDrawer from '@/components/DocDrawer'
import { useDocContent } from '@/hooks/useDocContent'
import { DocNode } from '@/lib/types'

jest.mock('react-markdown', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

jest.mock('remark-gfm', () => ({
  __esModule: true,
  default: jest.fn(),
}))

jest.mock('rehype-sanitize', () => ({
  __esModule: true,
  default: jest.fn(),
  defaultSchema: { attributes: { code: [] } },
}))

jest.mock('@/components/MermaidBlock', () => ({
  __esModule: true,
  default: () => <div data-testid="mermaid-block" />,
}))

jest.mock('@/hooks/useDocContent', () => ({
  useDocContent: jest.fn(),
}))

const mockUseDocContent = useDocContent as jest.MockedFunction<typeof useDocContent>

const qaDoc: DocNode = {
  name: 'DOC-QA-G4-002_Test-Result_v0.1',
  path: 'docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md',
  slug: ['docs', 'artifacts', '04-review', 'DOC-QA-G4-002_Test-Result_v0.1.md'],
  children: [],
}

describe('DocDrawer', () => {
  beforeEach(() => {
    mockUseDocContent.mockReset()
  })

  it('QA 결과 문서를 요약 뷰가 아니라 전체 Markdown 문서로 렌더링한다', () => {
    mockUseDocContent.mockReturnValue({
      content: `---
document_id: DOC-QA-G4-002
title_ko: 테스트 결과서
project: sample-ex-0524-1
status: Draft
updated_at: 2026-05-24
---

## 3. 실행 검증

| 검증 ID | 명령/방법 | 결과 | 요약 | 로그/증적 |
| --- | --- | --- | --- | --- |
| QA-CMD-006 | npx playwright test | Pass | 화면 검증 통과 | [회원가입 기본](evidence/ui/UI-002-01_signup_default_desktop.png) |
| QA-CMD-007 | backend server log | Pass | 로그 확인 | docs/artifacts/04-review/evidence/ui/gate4-backend.out.log |

## 4. 화면 증적

| 증적 ID | 관련 UI | 관련 SCR | 상태/시나리오 | 기대 화면 | 실제 확인 | 파일 | 결과 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UI-002-01 | UI-002 | SCR-001 | 회원가입 기본 | 회원가입 폼 | 확인 | [회원가입 기본](evidence/ui/UI-002-01_signup_default_desktop.png) | Pass |
`,
      isLoading: false,
      error: undefined,
    })

    render(<DocDrawer projectId="sample-project" doc={qaDoc} onClose={jest.fn()} />)

    expect(screen.getByText(/## 3\. 실행 검증/)).toBeInTheDocument()
    expect(screen.getByText(/## 4\. 화면 증적/)).toBeInTheDocument()
    expect(screen.getByText(/\[회원가입 기본]\(evidence\/ui\/UI-002-01_signup_default_desktop\.png\)/)).toBeInTheDocument()
    expect(document.body.textContent).toContain(
      '[docs/artifacts/04-review/evidence/ui/gate4-backend.out.log](docs/artifacts/04-review/evidence/ui/gate4-backend.out.log)',
    )
  })
})
