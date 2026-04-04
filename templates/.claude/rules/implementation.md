---
paths:
  - "src/**"
---

# 구현 규칙

## 병렬 실행 전략

1. **의존성 분석** — REQ 그룹 간 의존 관계 파악
2. **Wave 구성** — 복잡도/의존성으로 Wave를 나눔 (경량은 묶고, 복잡은 단독)
3. **에이전트 투입** — 각 Wave마다 frontend-dev + backend-dev 병렬 투입
4. **Wave 완료 확인** — 코드/단위 테스트 정상 확인 후 다음 Wave

## 병렬 실행 조건

- 두 REQ 그룹이 동일 DB 테이블을 변경하지 않을 것
- 두 REQ 그룹 간 API 호출 의존이 없을 것
- 공유 컴포넌트/모듈이 충돌하지 않을 것

## 팀원 간 소통

- frontend-dev ↔ backend-dev: API 스펙, 응답 형식 소통
- 구현 완료 → ux-reviewer 투입 (스크린샷 기반 UI 검수)
- ux-reviewer 🔴 → frontend-dev 수정 → 재검수 (최대 2회)
- ux-reviewer 통과 → qa에게 구현 완료 + UX 리뷰 결과 전달
