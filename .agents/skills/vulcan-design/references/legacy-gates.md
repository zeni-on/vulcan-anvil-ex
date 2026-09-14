# Legacy design workflow

Use only for an unmarked project's existing Gate lifecycle.
Product iterative projects use Core CLI section 4.1 from SKILL.md instead.
Project-root paths below remain relative to the project, not this reference file.

## Inputs

1. Read `AGENTS.md` and selected `session.json` state. Product uses the assigned design scope under `PRODUCT_PROFILE_BASELINE.md` section 7; read the current Gate 2 Run only when one is used. Other profiles retain their Run requirements.
2. Read Gate 1 requirements, acceptance criteria, and open decisions.
3. Run `python vulcan.py status` when current Gate, profile, branch, or next action is unclear.
4. Confirm the delivery profile with `python vulcan.py profile-status` only when profile detail is needed beyond `status`.
5. Apply profile-specific design depth from `docs/core/DELIVERY_PROFILES.md`.
   For Product, use `docs/core/PRODUCT_DOCUMENT_WRITING.md` for owned source paths and optional templates. Keep detailed contracts in one source and link from the ledger, without auto-relocating approved documents.
6. Prefer `docs/core/GATE2_DESIGN_SEQUENCE.md` when the design order is unclear.

## Workflow

1. Fix design scope before writing detailed design.
2. Draft or update architecture first as the design map.
3. Keep Program Design as the contract source for class/interface/public method/DTO boundaries.
4. Convert UI baseline/prototype assets into explicit UI implementation contracts.
5. Keep API, DB, security, screen, and development-standard decisions consistent.
6. Update traceability candidates through `trace-context` or `--trace-seed` when possible.

## Verification

- Run `python vulcan.py run-check <run-file>` for changed Run documents.
- Run `python vulcan.py check-trace` when traceability was changed.
- Run `python vulcan.py check-contract` only when implementation code exists.

## Stop Conditions

Stop and ask when requirements, architecture, security, data, or UI baseline inputs conflict, or when the design would require a CR.
