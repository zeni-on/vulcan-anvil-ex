# Status Filter Test Plan

Definitions for the [extension](status-filter.md) and regression of the [existing contract](contracts.md). Planned is a definition status, not an execution result.

| ID | Input / action | Expected | Method | Status |
| --- | --- | --- | --- | --- |
| REG-006 | List each status, omit status, reject/resubmit, restart the app on the same database | Correct subsets and ordering; old content/reason/history unchanged; resubmission moves the request between subsets | API filter tests, browser @status-filter, ci/iteration_assertions.py extension | Planned |
| SEC-REG-006 | Filter as owner/other requester/reviewer; supply empty/unknown status | Existing authorization retained; invalid input returns 422 without changing rows/history | API filter tests and iteration assertions | Planned |

The repeatable process rehearsal is `npm run test:iteration`. It creates only a disposable project and uses actual CLI transitions and API/SQLite assertions. Its explicit fixture decisions simulate a trusted owner; they do not prove that a real user accepted this feature. Screen assertions run separately through `npm run test:e2e` and the required CI inventory.
