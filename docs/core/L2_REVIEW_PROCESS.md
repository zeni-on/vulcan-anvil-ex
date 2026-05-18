# L2 Review Process

> 상태: v0.1
> 목적: 작성 세션과 분리된 독립 리뷰를 Gate 종료 검수에 붙이는 실험 절차를 정의한다.

## 1. 개념

L2 Review는 같은 런타임이라도 작성 세션과 리뷰 세션을 분리해 산출물을 다시 검수하는 절차다.

| 수준 | 의미 | 예 |
| --- | --- | --- |
| L1 | 같은 세션의 자기 점검 | 메인 Orchestrator가 직접 리뷰 |
| L2 | 별도 세션 또는 별도 worktree의 독립 리뷰 | Codex가 작성한 산출물을 새 Codex 세션이 검토 |
| L3 | 다른 런타임 교차 리뷰 | Codex 산출물을 Claude가 검토, 또는 반대 |

L2 리뷰어는 수정자가 아니라 검수자다. 결과는 `PASS`, `FIND`, `CR`, `ISSUE` 후보로 남기고, Orchestrator가 본선 산출물 반영 여부를 다시 판단한다.

## 2. 기본 원칙

- L2 Review는 실험 기능이며 Gate 완료를 항상 막는 필수 절차는 아니다.
- 우선 적용 Gate는 `gate2`, `gate4`다.
- 리뷰 요청과 결과는 `docs/reviews/`에 파일로 남긴다.
- 리뷰 Run은 `docs/runs/`에 별도로 남긴다.
- 가능하면 별도 worktree를 사용해 작성 맥락과 파일 변경을 분리한다.
- L2 리뷰 결과는 자동 승인하지 않는다. Orchestrator가 재검토한 뒤 `FIND`, `CR`, `ISSUE`, 승인 후보로 분류한다.

## 3. 설정

프로젝트 루트의 `vulcan.config.json`에서 L2 Review 기본값을 둔다.

```json
{
  "review": {
    "l2_enabled": false,
    "l2_runner": "codex",
    "l2_triggers": ["gate2", "gate4"],
    "l2_worktree": true,
    "l2_readonly": true
  }
}
```

`l2_enabled`가 `false`여도 사용자가 명시적으로 `vulcan.py l2-review`를 실행하면 요청을 만들 수 있다.

## 4. 생성 명령

```bash
python vulcan.py l2-review \
  --gate gate2 \
  --title "Gate 2 설계 독립 검수" \
  --from-run RUN-003 \
  --related-ids REQ-001,FUNC-001,SCR-001
```

기본 동작:

- `docs/reviews/RV-NNN_*_request.md` 생성
- `docs/reviews/RV-NNN_*_result.md` 생성
- `docs/runs/RUN-NNN_l2-review-*_v0.1.md` 생성
- `vulcan.config.json.review.l2_worktree`가 `true`이면 detached worktree 생성

## 5. 리뷰어의 작업

리뷰어는 request 파일을 읽고 result 파일만 작성한다.

### 금지

- 본선 산출물을 직접 수정하지 않는다.
- 작성자의 의도를 추측해 누락을 통과시키지 않는다.
- 실행하지 않은 테스트를 Pass로 기록하지 않는다.
- 대화상 승인 없이 `User Approved`로 기록하지 않는다.

### 필수

- `PASS`, `FIND`, `CR`, `ISSUE` 중 하나로 판정한다.
- `FIND`는 승인된 범위 안의 결함으로 남긴다.
- 기준선 변경이 필요하면 `CR`로 남긴다.
- 추가 판단이 필요하면 `ISSUE`로 남긴다.
- 검증 명령을 실행했으면 cwd, 명령, exit code, 성공 기준, 로그/증적 경로를 기록한다.

## 6. Gate별 중점

### Gate 2

- Gate 2 설계 순서가 지켜졌는지 확인한다.
- SW Architecture가 상세 설계와 함께 Baseline 후보로 보강되었는지 확인한다.
- REQ/AC가 FUNC, SCR, PGM, API, DB, SEC, DEV 기준으로 전개되었는지 확인한다.
- UIREF/prototype이 있으면 UI Implementation Contract와 상태별 UI 증적 기준이 있는지 확인한다.
- Gate 3 테스트 설계로 넘길 검증 후보와 미해결 질문이 분리되었는지 확인한다.

### Gate 4

- 테스트 결과서가 개발표준과 테스트케이스의 필수 명령을 모두 기록했는지 확인한다.
- 각 검증 결과에 cwd, 명령, exit code, 성공 기준, 로그/증적 경로가 있는지 확인한다.
- UI 증적이 상태/시나리오별 UI-ID와 1:1로 연결되었는지 확인한다.
- 기준 UIREF와 구현 screenshot 차이가 `Pass`, `FIND`, `CR`로 판정되었는지 확인한다.
- 미실행 검증이나 기대 화면과 다른 캡처가 Pass로 기록되지 않았는지 확인한다.

## 7. Worktree 정리

L2 worktree는 결과 수집 후 사람이 확인하고 삭제한다.

```bash
git worktree remove <worktree-path>
```

삭제 전 result 파일이 본선 `docs/reviews/`에도 반영되어 있는지 확인한다.
