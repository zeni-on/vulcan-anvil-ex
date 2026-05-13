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

  it('세로형 QA Finding 개요와 EV-UI 증적 매칭을 읽는다', () => {
    const model = parseQaDoc(`# QA 발견사항

\`\`\`yaml
---
document_id: DOC-QA-G4-001
title_ko: QA 발견사항
project: sample-anvil-ex3
status: Review Requested
updated_at: 2026-05-13
---
\`\`\`

## 1. 발견사항 개요

| 항목 | 내용 |
| --- | --- |
| FIND-ID | 해당없음 |
| 제목 | Gate 4 QA 현재 발견사항 없음 |
| 심각도 | Blocker / Major / Minor / Trivial |
| 상태 | Closed |
| CR 필요 여부 | No |

## 2. 관련 추적 ID

| 구분 | 관련 ID |
| --- | --- |
| 테스트 | UI-001~UI-005 |
| 증적 | EV-UI-001, EV-UI-002 |

## 4. 화면 증적

| 증적 ID | 관련 UI | 파일 | 설명 |
| --- | --- | --- | --- |
| EV-UI-001 | UI-001 | docs/artifacts/04-review/evidence/ui/UI-001_login.png | 로그인 화면 |
| EV-UI-002 | UI-002 | docs/artifacts/04-review/evidence/ui/UI-002_map.png | 지도 화면 |

판정:

\`\`\`text
현재 Open FIND 없음.
\`\`\`
`)

    expect(model.documentKind).toBe('finding')
    expect(model.findings[0].id).toBe('해당없음')
    expect(model.findings[0].status).toBe('Closed')
    expect(model.evidences).toHaveLength(2)
    expect(model.evidences[0].id).toBe('EV-UI-001')
    expect(model.judgement).toContain('Open FIND 없음')
  })

  it('Gate 4 테스트 결과서의 REQ 요약과 화면 증적 표를 읽는다', () => {
    const model = parseQaDoc(`# Gate 4 QA 테스트 결과서

\`\`\`yaml
---
document_id: DOC-QA-G4-002
title: QA Test Result
title_ko: QA 테스트 결과서
project: sample-anvil-ex3
status: Review Requested
updated_at: 2026-05-13
---
\`\`\`

## 2. 요구사항 검증 요약

| REQ-ID | 검증 항목 | 관련 테스트 | 결과 | 증적 |
| --- | --- | --- | --- | --- |
| REQ-001-01 | 로그인 성공/실패 | UT-001, IT-001, UI-001 | Pass | UI-001_login.png |

## 4. 화면 증적

| 증적 ID | 관련 UI | 파일 | 설명 |
| --- | --- | --- | --- |
| EV-UI-001 | UI-001 | docs/artifacts/04-review/evidence/ui/UI-001_login.png | 로그인 화면 |
`)

    expect(model.documentKind).toBe('result')
    expect(model.results[0].id).toBe('REQ-001-01')
    expect(model.results[0].target).toBe('REQ-001-01')
    expect(model.results[0].result).toBe('Pass')
    expect(model.evidences.some((evidence) =>
      evidence.path === 'docs/artifacts/04-review/evidence/ui/UI-001_login.png',
    )).toBe(true)
    expect(model.evidences.every((evidence) => evidence.path.includes('docs/artifacts/04-review/evidence/ui/'))).toBe(true)
  })
})
