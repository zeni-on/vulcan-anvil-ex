import { isRequirementsDoc, parseRequirementsDoc } from '@/lib/requirementsDoc'
import { DocNode } from '@/lib/types'

const doc: DocNode = {
  name: 'DOC-CORE-G1-001_Requirements-Spec_v0.1',
  slug: ['docs', 'artifacts', '01-requirements', 'DOC-CORE-G1-001_Requirements-Spec_v0.1'],
  type: 'file',
}

const content = `# 요구사항정의서

\`\`\`yaml
---
document_id: DOC-CORE-G1-001
title_ko: 요구사항정의서
project: sample
status: Draft
updated_at: 2026-05-13
---
\`\`\`

## 3. 한눈에 보는 요구사항 요약

| 항목 | 내용 |
| --- | --- |
| 프로젝트 목표 | 로그인 TODO 앱 |
| 주요 사용자 | 일반 사용자 |

## 6. 기능 요구사항

| REQ-ID | 요구사항명 | 설명 | 우선순위 | 출처/외부 ID | 상태 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | 로그인 | 사용자는 로그인할 수 있다. | Must | 사용자 대화 | Draft |  |

## 8. 인수기준

| 상세 REQ-ID | 상세 요구사항명 | 설명 | 관련 AC-ID | 상태 |
| --- | --- | --- | --- | --- |
| REQ-001-01 | 로그인 성공 | 올바른 인증 정보로 로그인한다. | AC-001-01 | Draft |

| AC-ID | 관련 요구사항 | 인수기준 | 검증 방식 | 상태 |
| --- | --- | --- | --- | --- |
| AC-001-01 | REQ-001-01 | 로그인 상태가 생성된다. | 통합테스트 | Draft |

## 7. 비기능 요구사항

| NREQ-ID | 구분 | 요구사항명 | 설명 | 측정/검증 기준 | 참조 표준 | 우선순위 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NREQ-001 | 보안 | 접근통제 | 보호 기능은 인증 사용자만 접근한다. | 비로그인 접근 차단 | OWASP A01 | Must | Draft |

## 11. 보안 및 개인정보 고려사항

| SEC-ID | 관련 요구사항 | 보안 고려사항 | 참조 표준 | 적용 대상 | 검증 방향 |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | REQ-001 | 인증 우회 방지 | KISA SR2-1 | PGM- | IT- |
`

describe('requirementsDoc parser', () => {
  it('요구사항정의서 문서를 식별한다', () => {
    expect(isRequirementsDoc(doc, content)).toBe(true)
  })

  it('요구사항/AC/보안 표를 구조화한다', () => {
    const model = parseRequirementsDoc(content)

    expect(model.project).toBe('sample')
    expect(model.scopeSummary['프로젝트 목표']).toBe('로그인 TODO 앱')
    expect(model.functionalRequirements).toHaveLength(1)
    expect(model.functionalRequirements[0].id).toBe('REQ-001')
    expect(model.detailRequirements[0].id).toBe('REQ-001-01')
    expect(model.acceptanceCriteria[0].id).toBe('AC-001-01')
    expect(model.nonFunctionalRequirements[0].id).toBe('NREQ-001')
    expect(model.securityConsiderations[0].id).toBe('SEC-001')
  })
})
