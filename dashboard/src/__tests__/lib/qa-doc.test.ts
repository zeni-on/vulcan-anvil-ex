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
    expect(model.findings).toHaveLength(0)
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
| REQ-001-02 | 비로그인 보호 | UT-002, IT-002, UI-005 | Pass | UI-001_login.png |
| REQ-001-03 | 빌드 검증 | QA-CMD-005 | Pass | QA-CMD-005_build.log |

## 4. 화면 증적

| 증적 ID | 관련 UI | 파일 | 설명 |
| --- | --- | --- | --- |
| EV-UI-001 | UI-001 | docs/artifacts/04-review/evidence/ui/UI-001_login.png | 로그인 화면 |

## 5. 실행 로그

| 증적 ID | 관련 UI | 파일 | 설명 |
| --- | --- | --- | --- |
| QA-CMD-005 | QA-CMD-005 | docs/artifacts/04-review/evidence/logs/QA-CMD-005_build.log | frontend build log |
`)

    expect(model.documentKind).toBe('result')
    expect(model.results[0].id).toBe('REQ-001-01')
    expect(model.results[0].kind).toBe('requirement')
    expect(model.results[0].target).toBe('UT-001, IT-001, UI-001')
    expect(model.results[0].method).toBe('로그인 성공/실패')
    expect(model.results[0].result).toBe('Pass')
    expect(model.evidences.some((evidence) =>
      evidence.path === 'docs/artifacts/04-review/evidence/ui/UI-001_login.png',
    )).toBe(true)
    expect(model.evidences).toHaveLength(2)
    expect(model.evidences.some((evidence) =>
      evidence.path === 'docs/artifacts/04-review/evidence/logs/QA-CMD-005_build.log' &&
      evidence.kind === 'log',
    )).toBe(true)
    expect(model.evidences.some((evidence) =>
      evidence.path.includes('docs/artifacts/04-review/evidence/ui/') &&
      evidence.kind === 'image',
    )).toBe(true)
  })

  it('마크다운 링크와 QA 문서 기준 상대 증적 경로를 프로젝트 기준 경로로 정규화한다', () => {
    const model = parseQaDoc(`# Gate 4 QA 테스트 결과서

\`\`\`yaml
---
document_id: DOC-QA-G4-002
title_ko: QA 테스트 결과서
---
\`\`\`

## 2. 요구사항 검증 요약

| REQ-ID | 검증 항목 | 관련 테스트 | 결과 | 증적 |
| --- | --- | --- | --- | --- |
| REQ-001 | 회원가입 | UI-002-01 | Pass | [회원가입 기본](evidence/ui/UI-002-01_signup_default_desktop.png) |

## 4. 화면 증적

| 증적 ID | 관련 UI | 관련 SCR | 상태/시나리오 | 기대 화면 | 실제 확인 | 파일 | 결과 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-UI-002-01 | UI-002-01 | SCR-002 | 회원가입 기본 | 폼 표시 | 확인 | [UI-002-01_signup_default_desktop.png](evidence/ui/UI-002-01_signup_default_desktop.png) | Pass |

## 3. 실행 검증

| 검증 ID | 목적 | 실행 위치(cwd) | 명령/방법 | OS | 필수 여부 | 성공 기준 | Exit Code | 결과 | 로그/증적 | 요약 | 관련 Run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA-CMD-005 | Playwright UI/E2E | frontend | npm run test:e2e | Windows | 필수 | exit code 0 | 0 | Pass | [last-run](evidence/ui/playwright-output/.last-run.json), [HTML report](evidence/ui/playwright-report/index.html) | 통과 | RUN-016 |
`)

    expect(model.evidences.some((evidence) =>
      evidence.path === 'docs/artifacts/04-review/evidence/ui/UI-002-01_signup_default_desktop.png' &&
      evidence.kind === 'image',
    )).toBe(true)
    expect(model.evidences.some((evidence) =>
      evidence.path === 'docs/artifacts/04-review/evidence/ui/playwright-output/.last-run.json' &&
      evidence.kind === 'log',
    )).toBe(true)
    expect(model.evidences.some((evidence) =>
      evidence.path === 'docs/artifacts/04-review/evidence/ui/playwright-report/index.html' &&
      evidence.kind === 'log',
    )).toBe(true)
  })
})
