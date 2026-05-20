# Roadmap

이 문서는 Vulcan-Anvil Ex의 현재 상태와 다음 초점을 정리합니다.

## 현재 상태

**Experimental - v0.2.2**

`0.2.2`는 Codex와 Claude 양쪽 런타임을 실제 프로젝트 생성과 Gate 진행에 사용할 수 있도록 확장한 `0.2.1` 흐름에 Gate 종료 승인, Run 입력/출력 계약, UI Implementation Contract, 상태별 UI 증적, 필수 검증 명령 기록 기준을 정렬한 패치 버전입니다.

포함된 주요 기능은 다음과 같습니다.

- Phase 0 + 5-Gate 진행 흐름
- Codex/GPT adapter
- Claude adapter
- Dashboard A2
- SW Architecture 산출물
- API 정의서 산출물
- DBML 기반 논리/물리 ERD 초안
- 보안가이드 산출물
- Spring Boot, Spring Security, React, Next.js, Vue.js, FastAPI 기술스택 베이스라인 초안
- 리팩토링의 DEBT/FIND/CR 분류와 문서 영향 판단 기준
- 변경관리/릴리즈 산출물
- Build Wave 운영 규칙
- Upgrade와 Dashboard 운영 흐름

아직 제품화된 안정 버전은 아니며, 실제 프로젝트 적용 결과에 따라 문서 체계와 CLI 명령은 계속 조정될 수 있습니다.

릴리즈별 변경사항은 `CHANGELOG.md`를 기준으로 확인합니다.

## 다음 초점

`0.2.2` 이후의 다음 초점은 다음입니다.

- 실제 SI형 다중 프로젝트 구조 검토
- Delivery Profile 도입: Audit/SI, Solution/Product, PoC, Lite 프로젝트별 문서 깊이와 Gate 강도 조절
- Solution Profile 정의: 감리 제출보다 제품 로드맵, 릴리즈, 아키텍처 결정, 품질 기준을 중심으로 한 절차 정리
- PoC/Lite Profile 정의: 빠른 검증을 위해 필수 ID, 핵심 요구사항, 최소 테스트, 짧은 Run 중심으로 운영
- 감리 제출용 DOCX/XLSX/HWPX 변환 흐름 설계
- Dashboard A2의 반응형 밀도와 검수 화면 개선
- Codex/Claude adapter의 실제 Run 결과 비교와 규칙 보강
- 독립 검수 기본 절차의 실제 프로젝트 적용 결과 확인과 review-import/watch 확장 여부 판단

## Delivery Profile 방향

Vulcan-Anvil Ex는 모든 프로젝트에 같은 무게의 절차를 강제하지 않는 방향으로 발전합니다.

| Profile | 목적 | 문서/Gate 강도 |
| --- | --- | --- |
| Audit/SI | 감리, 인수인계, 장기 유지보수 대응 | 가장 강함 |
| Solution/Product | 제품 로드맵, 릴리즈, 품질 기준 중심 | 중간 |
| PoC | 빠른 가능성 검증 | 낮음 |
| Lite | 소규모 내부 도구, 단기 자동화 | 가장 낮음 |

자세한 기준은 `docs/core/DELIVERY_PROFILES.md`를 따릅니다.

## 제출용 문서 전략

작업 중에는 Markdown 원천 문서를 나누어 관리합니다. 제출 시점에는 DOCX/XLSX/HWPX 템플릿과 생성 코드를 통해 필요한 내용을 합성하는 방향을 둡니다.

상세 전략은 `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md`를 기준으로 합니다.

## 세션 협업 모델

세션 간 실시간 통신은 Core 전제 조건이 아닙니다.

대신 다음 파일을 공유 상태로 사용합니다.

- `session.json`
- `docs/runs/`
- 증적 파일
- 백로그 문서
- Git 커밋

이상적인 세션 협업 모델은 `docs/reference/SESSION-COORDINATION-IDEAL.md`에 정리되어 있습니다. 실시간 브로드캐스트나 watcher는 향후 확장 옵션입니다.
