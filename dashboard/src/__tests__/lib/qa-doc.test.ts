import { isQaDoc, parseQaDoc } from '@/lib/qaDoc'
import { DocNode } from '@/lib/types'

const doc: DocNode = {
  name: 'DOC-QA-G4-001_QA-Finding_v0.1',
  slug: ['docs', 'artifacts', '04-review', 'DOC-QA-G4-001_QA-Finding_v0.1'],
  type: 'file',
}

const content = `# QA 발견사항

\`\`\`yaml
---
document_id: DOC-QA-G4-001
title_ko: QA 발견사항
project: sample
status: CompletedWithIssues
updated_at: 2026-05-13
---
\`\`\`

| FIND-ID | 제목 | 심각도 | 상태 | CR 필요 여부 | 관련 ID |
| --- | --- | --- | --- | --- | --- |
| FIND-001 | 버튼 오류 | Minor | Fixed | No | REQ-001, UI-004 |

| UI-ID | 설명 | 캡처 경로 |
| --- | --- | --- |
| UI-001 | 회원가입 화면 | \`docs/artifacts/04-review/evidence/ui/UI-001_signup.png\` |
| UI-004-A | 수정 화면 | \`docs/artifacts/04-review/evidence/ui/UI-004_edit.png\` |

판정:

\`\`\`text
FIND-001은 기존 설계 범위 안에서 수정 완료.
\`\`\`
`

describe('qaDoc parser', () => {
  it('QA 문서를 식별한다', () => {
    expect(isQaDoc(doc, content)).toBe(true)
  })

  it('발견사항, 이미지 증적, 판정을 구조화한다', () => {
    const model = parseQaDoc(content)

    expect(model.documentKind).toBe('finding')
    expect(model.project).toBe('sample')
    expect(model.findings[0].id).toBe('FIND-001')
    expect(model.evidences).toHaveLength(1)
    expect(model.evidences[0].path).toBe('docs/artifacts/04-review/evidence/ui/UI-004_edit.png')
    expect(model.judgement).toContain('수정 완료')
  })
})
