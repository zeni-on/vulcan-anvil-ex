import { isScreenSpecDoc, parseScreenSpecDoc } from '@/lib/screenSpecDoc'
import { DocNode } from '@/lib/types'

const doc: DocNode = {
  name: 'DOC-CORE-G2-003_Screen-Spec_v0.1',
  slug: ['docs', 'artifacts', '02-design', 'screen', 'DOC-CORE-G2-003_Screen-Spec_v0.1'],
  type: 'file',
}

const content = `# 화면설계서

\`\`\`yaml
---
document_id: DOC-CORE-G2-003
title_ko: 화면설계서
project: sample
status: Draft
updated_at: 2026-05-13
---
\`\`\`

## 2. 화면 목록

| SCR-ID | 화면명 | 유형 | 관련 FUNC | 관련 PGM | 관련 SEC | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| SCR-001 | 로그인 | Page | FUNC-001 | PGM-001 | SEC-001 | Draft |

## 3. 화면 시안 및 기준 증적

| SCR-ID | 시안/와이어프레임 ID | 출처 | 파일/URL | 기준 Viewport | 비교 기준 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| SCR-001 | UIREF-001 | 문서 내 텍스트 와이어프레임 | 본 문서 4.1 | Desktop 1280x720 | 폼 배치 | Draft |

## 4. 화면 상세

### 4.1 SCR-001 로그인

| 항목 | 내용 |
| --- | --- |
| 관련 요구사항 | REQ-001-01 |
| 관련 인수기준 | AC-001-01 |
| 접근 권한 | 비회원 |
| 화면 구조 | 이메일, 비밀번호, 로그인 버튼 |

텍스트 와이어프레임:

\`\`\`text
[Login]
[Email____]
[Password_]
\`\`\`

상태: 기본 상태, 오류 상태를 가진다.

#### 4.2 화면 구성

| 영역 | 구성요소 | 설명 | 표시 조건 |
| --- | --- | --- | --- |
| 인증 폼 | 이메일, 비밀번호 | 로그인 정보 입력 | 기본 |

## 5. UI 테스트 및 증적 기준

| UI-ID | 대상 SCR | 사용자 흐름 | 기준 시안 | Viewport | 캡처 경로 | 비교 기준 | 관련 AC/SEC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UI-001 | SCR-001 | 로그인 | UIREF-001 | Desktop 1280x720 | docs/artifacts/04-review/evidence/ui/UI-001.png | 폼 배치 | AC-001-01 |
`

describe('screenSpecDoc parser', () => {
  it('화면설계서 문서를 식별한다', () => {
    expect(isScreenSpecDoc(doc, content)).toBe(true)
  })

  it('화면 목록과 텍스트 와이어프레임을 구조화한다', () => {
    const model = parseScreenSpecDoc(content)

    expect(model.project).toBe('sample')
    expect(model.screens).toHaveLength(1)
    expect(model.evidences[0].refId).toBe('UIREF-001')
    expect(model.details[0].scrId).toBe('SCR-001')
    expect(model.details[0].wireframe).toContain('[Email____]')
    expect(model.details[0].stateText).toContain('오류 상태')
    expect(model.details[0].tables[0].title).toBe('4.2 화면 구성')
    expect(model.details[0].tables[0].rows[0]).toContain('인증 폼')
    expect(model.extraTables[0].title).toBe('5. UI 테스트 및 증적 기준')
  })
})
