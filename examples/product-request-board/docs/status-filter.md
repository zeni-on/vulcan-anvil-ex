# Status Filter: Sample Extension

This is a technical extension selected for the Product iteration rehearsal, not a newly approved PMTool or production requirement. The existing resubmission/security contract remains in `contracts.md`; its definitions are not copied or rewritten here.

| ID | Definition |
| --- | --- |
| SCN-002 | Find an authorized request by its current status, then continue the existing review/resubmission flow. |
| REQ-003 | Allow optional submitted/rejected/approved filtering without changing ownership, visibility, stored content, or decision history. Omission means all authorized requests. |
| AC-004 | A rejected request appears in rejected results, moves to submitted results after resubmission, and retains the previous content/rejection reason. |
| AC-005 | Filtering never reveals another owner's requests to a requester. Reviewers keep their existing visibility. Invalid status returns the existing 422 INVALID_INPUT response. |
| AC-006 | Existing requests and immutable decision snapshots remain readable after restarting the application with the same SQLite file. No schema migration is required by this extension. |

## Interface

`GET /api/requests?status=submitted|rejected|approved` keeps the existing response shape and descending ID order. The optional query selects a subset of the authorized list; it is not an authorization parameter. Unknown or empty status is invalid. No status is persisted by this read operation.

The browser provides an All/submitted/rejected/approved selector. Excluded selected details are cleared, empty results are supported, and account changes cannot leave another actor's records or unsent editor visible. The list must reflect resubmission/decision changes under the active filter.

This adds no deletion, notification, new role, authentication provider, or publication permission.
