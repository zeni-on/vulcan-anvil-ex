# Backlog Phase와 증분 Gate — 설계 근거

> 본 문서는 Vulcan-Claude-Anvil v1.1 고도화(Backlog Phase 도입, 증분 Gate Rollback, Trivial 재정의)의 배경과 의사결정을 기록한다.
> 작성일: 2026-04-11 · 출처: IronBull 프로젝트 Backlog 운영 경험

## 1. 배경 — 왜 5-Gate만으로는 부족한가

Vulcan-Claude-Anvil의 5-Gate 프로세스(요구사항 → 설계 → 테스트계획 → 구현 → QA → 최종승인)는 **"한 번에 끝나는 프로젝트"**를 암묵적으로 전제한다. 그러나 실제 프로젝트는 Gate 5 이후에도 끝나지 않는다.

**IronBull 프로젝트에서 관찰된 현상**:

- 요구사항 60개 중 3개가 Gate 5 완료 시점까지 미구현 (Must 등급 NREQ 포함)
- Gate 4 QA가 페이지네이션을 "unwrap 동작만" 상태로 통과시킴 (기술 부채 축적)
- Python 3.12 `datetime.utcnow()` deprecation — 구현 중 발견된 기술 부채 20곳
- Could 등급 REQ-014(예약 브리핑) — MVP 범위 제외로 남겨둠

이는 프로세스 실패가 아니라 **소프트웨어 개발의 본질적 속성**이다. 소프트웨어는 "완성"되지 않고 "출시"될 뿐이다. Gate 5는 선을 긋지만, 선 너머의 작업이 0이 되는 것은 비현실적이다.

## 2. Backlog의 정체 — "TODO 리스트가 아닌 Gate 재진입 라우터"

IronBull은 Gate 5 이후 `docs/06-backlog/BACKLOG.md`를 즉석에서 도입했고, 실전 운영에서 Backlog가 단순한 TODO 리스트가 아니라 **"작업 크기에 맞는 최소 프로세스를 선택하는 라우터"** 역할을 한다는 것이 드러났다.

| 레벨 | 기준 (최초 정의) | 처리 경로 |
|------|-----------------|-----------|
| 🟢 Trivial | 격리된 수정, 1일 이내 | 바로 구현 |
| 🟡 Small | 단일 REQ 범위 | Gate 2 rollback |
| 🔴 Major | 새 기능, 아키텍처 영향 | Gate 1 rollback |

Triage Level이 곧 "어느 Gate로 돌아갈지"를 결정한다. 이것은 **규약을 탄력적으로 만드는 장치**이며, Anvil의 엄격함을 유지하면서 작은 작업에 큰 오버헤드를 부과하지 않는 방법이다.

## 3. Triage 운영에서 드러난 문제 3가지

IronBull의 9개 Backlog 항목을 재검증하는 과정에서 세 가지 구조적 문제가 드러났다.

### 3.1 "🟢 vs 🟡" 경계의 모호함

**문제**: BL-008(params_json 화이트리스트 스키마 검증)은 코딩 시간은 1시간이지만, 입력 거부 정책이 설계 문서에 반영되지 않으면 다음 리뷰에서 회귀할 수 있다. 최초 기준 "1일 이내"만 보면 🟢으로 분류되지만, 실제로는 🟡이 맞다.

**원인**: Trivial 기준이 **시간**으로 정의되어 있다. 시간은 실행 비용의 대리 지표일 뿐, 실제 리스크는 **"설계 문서에 반영할 결정을 포함하는가"**에서 온다.

**결론**: Trivial 기준을 **"어떤 문서(REQUIREMENTS, Design, Test-Plan, 보안 baseline)도 수정할 필요 없는가"**로 재정의한다. 시간은 부차적 힌트.

### 3.2 🔴의 "Gate 1 Rollback = 전체 재진행"은 현실과 안 맞음

**문제**: BL-001(Google Drive 동기화)을 🔴으로 처리하면 이론상 Gate 1~5 전부 재진행인데, 실제로는 NREQ-005/006만 영향을 받는다. 나머지 58개 REQ를 다시 Gate 4까지 돌리는 것은 낭비다.

**AI 실행 관점의 심각성**: AI 에이전트에게 "60개 REQ 전체를 다시 검토하라"고 지시하면 컨텍스트 폭발로 품질이 급락한다. 반면 "NREQ-005/006만 보라"고 하면 훨씬 집중할 수 있다. 증분 Gate는 단순 효율 문제가 아니라 **AI 품질 문제**다.

**결론**: `vulcan.py rollback --gate gate1 --scope NREQ-005,NREQ-006` 형태로 영향받는 REQ-ID만 재진행할 수 있는 **증분 Gate Rollback**을 도입한다. check-trace도 scope 모드를 지원해야 한다.

### 3.3 Backlog 항목의 중복/종속 관계

**문제**: BL-002(동기화 상태 확인)가 BL-001의 "선행 필요" 하위 작업으로 분리되어 있었다. 그러나 BL-001을 🔴으로 돌리면 요구사항 단계에서 NREQ-005-02도 함께 설계되므로, BL-002는 독립 항목이 아니라 **BL-001의 AC**여야 한다.

**원인**: "Backlog 항목 = PR 단위"로 착각. Backlog 항목은 "Gate 재진입 단위"여야 한다.

**결론**: 종속 관계가 있는 항목은 상위 항목에 흡수하고 Rejected 처리. PROCESS.md에 "중복/흡수 규칙" 섹션 추가.

## 4. Backlog 안전장치 — "Gate 4 타협 방지"

Backlog가 **"Gate 4에서 타협하는 핑계"**가 될 위험이 있다. IronBull의 BL-003(페이지네이션 unwrap 통과)이 대표 사례다. 이것이 반복되면 Gate 4는 "진짜 검증"이 아니라 "다음 배치로 미루는 의식"이 된다.

**규칙**:
- Gate 4에서 Blocker/Major 이슈는 **Backlog로 이월 불가**. 반드시 현 Gate 내에서 해결.
- Minor 이슈만 Backlog 이월 허용.
- P0/P1은 다음 배치에서 **반드시** 처리 (무기한 보류 금지).

## 5. 고도화 결정 사항 요약

| # | 항목 | 변경 |
|---|------|------|
| 1 | Backlog Phase 승격 | `templates/docs/06-backlog/` 추가, vulcan.py에 `backlog` CRUD 명령 도입 |
| 2 | 증분 Gate Rollback | `rollback --scope REQ-ID,...` 옵션, session.json scoped 상태, check-trace scope 모드 |
| 3 | Trivial 기준 재정의 | "1일 이내" → "문서 수정 불필요"; qa/pm 에이전트 프롬프트 반영 |

## 6. AI 실행 관점의 일반화된 교훈

실제 실행의 90%가 AI인 환경에서 Vulcan-Anvil이 해결해야 하는 본질적 문제는 세 가지다.

1. **컨텍스트 망각** — 긴 프로젝트에서 초기 결정을 잊는다 → Gate 문서가 외부 기억장치
2. **국소 최적화 편향** — 당장의 파일만 보고 전체 일관성을 깬다 → TRACEABILITY가 일관성 체크
3. **확신 편향** — 틀린 방향도 자신있게 밀어붙인다 → Gate 승인이 강제 중단점

Backlog와 증분 Gate는 여기에 네 번째를 추가한다.

4. **"완성" 환각** — AI는 "진짜 완성"과 "타협한 완성"을 스스로 구분하지 못한다 → Backlog가 타협을 명시적으로 기록하게 강제

이것이 없으면 AI가 "다 끝났어요"라고 말하고 넘어가고, 그 타협이 증발한다. Backlog Phase는 이 망각을 막는 안전장치다.

## 7. 적용 범위

본 문서의 결정은 Vulcan-Claude-Anvil **v1.1부터** 적용된다. IronBull과 같은 기존 프로젝트는 이미 `docs/06-backlog/`를 수동으로 운영 중이므로, v1.1 템플릿으로 마이그레이션할 때 기존 BACKLOG.md를 새 규약에 맞게 재분류해야 한다 (특히 Trivial 기준 변경).
