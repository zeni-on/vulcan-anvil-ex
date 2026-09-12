# Request Board: Sample Contract

User approved the following local-sample policy on 2026-09-12. This is not a production authentication, retention, or deployment policy. Earlier candidate writing examples remain unchanged.

## Business Flow

| ID | Definition |
| --- | --- |
| SCN-001 | Submit, reject with a reason, amend the same request, resubmit, and review again. |
| REQ-001 | Only the owner can resubmit a rejected request. Resubmission becomes reviewable atomically; unsent edits remain in the browser only. |
| REQ-002 | Preserve each decision's submitted content, rejection reason, reviewer, and round. Repeated rejection adds history without rewriting an older snapshot. No automatic deletion in this local sample. |
| AC-001 | After '장비 필요' is rejected for '수량을 알려주세요', resubmit '장비 2대 필요' under the same request ID. Its state is submitted. |
| AC-002 | The old content and reason remain distinct from the latest content after resubmission, a second rejection, page reload, and application restart. |
| AC-003 | A reviewer cannot observe an owner's unsent textarea changes. Submission changes the shared current content. |

## Security And Concurrency

| ID | Definition |
| --- | --- |
| SEC-001 | Owners see their own requests/history; reviewers see requests/history. Other requesters cannot list or read another owner's records. Only reviewers may decide, never on their own request. |
| SEC-002 | The server derives the actor from a session, not body fields. Missing sessions, cross-origin writes, malformed input, invalid states, and stale versions must not change data/history. |

This loopback-only demonstration uses an explicitly enabled test identity selector (Alice/민수, Bob/지수, Carol/영희 reviewer, Dana/준호 reviewer). The selector is not real authentication: anyone at the local demo can select a test identity. Never expose it to a network or use customer data. Deployment/real identity-provider security is out of scope, not satisfied by these tests.

## API And Data

- `GET /api/demo/users`: fixed test identities; `POST /api/demo/session {userId}`: switch test identity using an HttpOnly, SameSite=Strict session cookie; `GET /api/me`: current identity.
- `GET /api/requests`: authorized list; `POST /api/requests {content}`: create a submitted request; `GET /api/requests/{id}`: authorized detail and history.
- `POST /api/requests/{id}/decision {decision,reason,version}`: approve/reject a submitted request; rejection requires a nonblank reason.
- `POST /api/requests/{id}/resubmit {content,version}`: owner submits amended content of a rejected request.
- Response detail: `{id,owner:{id,name,role},content,status,reason,version,history:[{round,content,decision,reason,reviewer:{id,name,role},decidedAt}]}`. List response `{requests:[...]}`; identity response `{user:...}`; errors `{error:{code,message}}`.
- Status values: submitted, rejected, approved. Content/reason length 1..4000 (approval reason may be empty); version is a positive strict integer. Unknown body fields are rejected. State/version checks and changes share one SQLite transaction.
- SQLite owns requests and immutable decision snapshots. Each decision increments its round and version; resubmission increments version without overwriting snapshots. Approved requests cannot be amended in this sample.
- Same-origin JSON writes are required. Unauthorized detail returns 404; missing identity 401; forbidden action 403; stale/invalid state 409; invalid input 422. Display content as text, never HTML.
- Request IDs are positive signed SQLite integers (1..9223372036854775807). Reads use one transaction for the current row and decision history.
- Browser tabs share the demo cookie. Identity changes notify other tabs to reload the actor and clear unsent drafts. The browser sends `X-Demo-User`; a mismatch with the server session returns `IDENTITY_CHANGED` (409), without writing. This is a stale-UI guard, not authentication or permission to impersonate a user.

Technical transaction/version handling prevents duplicate decisions and lost updates; it does not add an unapproved business role. No draft storage, deletion, notifications, assigned-reviewer workflow, or real release is introduced.
