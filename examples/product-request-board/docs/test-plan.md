# Request Board Test Plan

The following tests apply to the [sample contract](contracts.md). Input, expected outcome and method are definitions, not recorded passes. No production identity/retention or release approval is implied.

| ID | Input / action | Expected | Method | Status |
| --- | --- | --- | --- | --- |
| REG-001 | Reject '장비 필요' for '수량을 알려주세요', then resubmit '장비 2대 필요' | Same request ID, new submitted content, unchanged prior content/reason | API test_reg_001 and browser flow | Planned |
| REG-002 | Repeat rejection with another reviewer, resubmit, approve, restart app/read SQLite | Ordered, distinct snapshots survive each round and restart | API test_reg_002 and browser flow/reload | Planned |
| REG-003 | Reuse an old version or resubmit in submitted/approved state | 409; no content or history mutation | API test_reg_003 | Planned |
| REG-004 | Two reviewers decide concurrently; a commit occurs between reading the row and history | Exactly one decision/snapshot succeeds; each read uses a consistent snapshot | API test_reg_004, including WAL interleaving | Planned |
| REG-005 | Owner types but does not submit; another browser/reviewer reloads | Only original shared content is visible until resubmit | Browser two-session flow | Planned |
| SEC-REG-001 | Another requester lists/reads/resubmits, or a reviewer resubmits someone else's request | No unauthorized content/history returned or changed | API test_sec_reg_001 and browser access check | Planned |
| SEC-REG-002 | Review own request as reviewer, or review as requester | 403 with no mutation | API test_sec_reg_002 | Planned |
| SEC-REG-003 | Blank/oversize/extra fields, noninteger version, missing rejection reason, out-of-range request IDs | 422 with unchanged SQLite rows | API test_sec_reg_003 | Planned |
| SEC-REG-004 | Missing session, cross-origin write, untrusted Host, old session token, stale displayed actor | Denial without writes; test identity switching requires explicit demo mode | API test_sec_reg_004 and opt-in test | Planned |
| SEC-REG-005 | HTML-like content; second submission; delayed old-account response; another tab switches identity | Render plain text; select newly created request; discard prior identity's selected records and unsent editor | Browser checks on desktop/mobile | Planned |

Commands from the example root: `python -B -m unittest discover -s tests -p test_api.py -v`; `npm run test:e2e`; `python -B tests/probe_history.py`.

The negative probe copies only app/test source into a temporary directory and deliberately overwrites the preserved content there. The same preservation assertion must fail with an AssertionError, not import/environment error. The normal application and user databases remain unchanged.

Evidence: current command logs under `.local/`; official Playwright HTML/JSON report, screenshots and failure traces under `playwright-report/` and `test-results/`. These are local generated artifacts, not authored plans. Product-specific remote CI execution belongs to finish scope 4.
