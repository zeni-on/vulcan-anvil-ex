import {
  countTraceabilityGaps,
  isTraceabilityDoc,
  parseTraceabilityDoc,
} from '@/lib/traceabilityDoc'
import { DocNode } from '@/lib/types'

const doc: DocNode = {
  name: 'DOC-CORE-G4-001_Traceability-Matrix_v0.1',
  slug: ['docs', 'artifacts', '02-traceability', 'DOC-CORE-G4-001_Traceability-Matrix_v0.1'],
  type: 'file',
}

const content = `# 요구사항추적표

\`\`\`yaml
---
document_id: DOC-CORE-G4-001
title_ko: 요구사항추적표
project: sample
status: Draft
updated_at: 2026-05-13
---
\`\`\`

## 4. 요구사항 추적 매트릭스

| REQ-ID | NREQ-ID | AC-ID | FUNC-ID | SCR-ID | PGM-ID | DB-ID | IF-ID | SEC-ID | 참조 표준 | UT-ID | IT-ID | PT-ID | 상태 | 증적 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-001-01 | NREQ-001 | AC-001-01 | FUNC-001 | SCR-001 | PGM-001 | DB-001 | 해당없음 | SEC-001 | OWASP A01 | UT-001 | IT-001 | 해당없음 | Verified | TEST-RESULT | 정상 흐름 |
| REQ-002-01 | NREQ-001 | AC-002-01 | 미정 | SCR-002 | PGM-002 | DB-001 | 해당없음 | SEC-001 | OWASP A01 | 해당없음 | 해당없음 | 해당없음 | Draft | 미정 | 설계 보강 필요 |

## 5. 요구사항별 검증 요약

| REQ-ID | 요구사항명 | 인수기준 수 | 설계 연결 | 테스트 연결 | 검증 상태 | 미해결 사항 |
| --- | --- | ---: | --- | --- | --- | --- |
| REQ-001 | 로그인 | 1 | 완료 | 완료 | Verified | 없음 |

## 6. 보안항목 추적

| SEC-ID | 보안항목 | 관련 REQ/NREQ | 참조 표준 | 적용 대상 | 검증 테스트 | 증적 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-001 | 접근통제 | REQ-001 | OWASP A01 | PGM-001 | IT-001 | TEST-RESULT | Verified |

## 9. 추적성 결함 목록

| 결함 ID | 결함 유형 | 관련 ID | 설명 | 조치 담당 | 상태 |
| --- | --- | --- | --- | --- | --- |
| ISSUE-001 | 설계 연결 누락 | REQ-002-01 | FUNC 미정 | design | Open |
`

describe('traceabilityDoc parser', () => {
  it('요구사항추적표 문서를 식별한다', () => {
    expect(isTraceabilityDoc(doc, content)).toBe(true)
  })

  it('추적 매트릭스와 결함 목록을 구조화한다', () => {
    const model = parseTraceabilityDoc(content)

    expect(model.project).toBe('sample')
    expect(model.rows).toHaveLength(2)
    expect(model.rows[0].reqId).toBe('REQ-001-01')
    expect(model.summaries[0].verification).toBe('Verified')
    expect(model.securityRows[0].secId).toBe('SEC-001')
    expect(model.issues[0].status).toBe('Open')
  })

  it('추적 누락 수를 계산한다', () => {
    const model = parseTraceabilityDoc(content)
    expect(countTraceabilityGaps(model.rows)).toEqual({
      ac: 0,
      design: 1,
      test: 1,
      evidence: 1,
    })
  })
})
