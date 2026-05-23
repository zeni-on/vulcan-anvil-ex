# Implementation Scaffold Skill

## 목적

Impl 진입 직후 feature 구현 전에 빌드 가능한 계약 skeleton을 만든다.

이 skill은 업무 로직 구현이 아니라 Program Design의 `PGM/IF/MTH/DTO/Entity/Component` 계약을 실제 파일, class/interface, public method signature, 테스트 골격으로 고정하는 작업이다.

## 입력

- 현재 scaffold Run
- `target_contracts.interface_contract`
- `target_contracts.contract_skeleton`
- 프로그램 설계서
- 개발표준정의서
- Gate 3 테스트케이스

## 절차

1. `AGENTS.md`, `session.json`, 현재 Run 문서를 먼저 읽는다.
2. `target_contracts.interface_contract`의 public signature, DTO/schema, error contract를 확인한다.
3. `target_contracts.contract_skeleton.files`에 지정된 파일만 생성하거나 보강한다.
4. 신규 개발이면 폴더, 빌드 설정, app entrypoint, public class/interface/method, DTO/schema, 테스트 파일 skeleton을 만든다.
5. 고도화이면 기존 코드와 Program Design의 계약을 매핑하고, 누락 skeleton만 보강한다.
6. 업무 로직은 완성하지 않는다. method body는 `TODO`, `NotImplemented`, 최소 wiring, 빈 adapter처럼 빌드가 깨지지 않는 수준으로 둔다.
7. contract skeleton smoke 명령 또는 Run의 `verification.commands`를 가능한 범위에서 실행한다.
8. 다음 Build Wave가 채워야 할 method, 테스트, 남은 ISSUE/CR 후보를 Run 결과에 남긴다.

## 금지

- 업무 기능 로직 완성
- 전체 E2E 또는 Gate 4 QA Pass 선언
- `session.json`, Gate 상태, wave-complete, sync-session 직접 변경
- `scope.writable` 밖 파일 수정
- Program Design에 없는 class, method, schema 임의 생성

## 완료 조건

- Program Design의 public signature가 실제 skeleton 파일에 존재한다.
- 신규/고도화 모드와 생략 사유가 Run에 기록되어 있다.
- compile/import/build smoke가 통과했거나 Not Run 사유가 명확하다.
- 다음 Build Wave가 구현할 계약 단위가 식별되어 있다.
