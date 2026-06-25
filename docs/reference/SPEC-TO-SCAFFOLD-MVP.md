# Spec-to-Scaffold MVP

> Status: draft v0.1  
> Purpose: define the first safe step from Gate 2 Program Design contracts to implementation scaffold planning.

## 1. Goal

Spec-to-Scaffold should reduce the gap between Program Design and Build Wave handoff.

The MVP does not generate code. It reads the approved or draft Program Design and produces a dry-run scaffold plan that an Orchestrator can review before creating `BW-000 implementation-scaffold` or a scoped Build Wave Run.

## 2. Current Command

```powershell
python vulcan.py scaffold-plan --json
python vulcan.py scaffold-plan --program-design docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Design_v0.1.md
```

The command reads:

- Interface Contract
- Public Method Contract
- DTO / Entity / Data Contract
- Contract Skeleton candidate table

It returns:

- candidate files
- `create` or `verify` action
- linked contract IDs
- public signatures or public contract text
- smoke command hints
- extracted interface, method, DTO, and skeleton records

## 3. Boundaries

`scaffold-plan` is dry-run only.

It does not:

- create files
- modify Program Design
- mark requirements as Implemented
- run tests
- approve a Gate
- replace `run-preflight`, `run-check`, or `check-contract`

If the plan is acceptable, the Orchestrator creates or updates an implementation-scaffold/Build Wave Run and delegates the actual skeleton creation to a worker, subagent, thread, or native branch agent.

## 4. Intended Flow

```text
Gate 2 Program Design
  -> python vulcan.py scaffold-plan --json
  -> Orchestrator reviews create/verify candidates
  -> BW-000 implementation-scaffold or scoped Build Wave Run
  -> worker creates/aligns skeleton
  -> Orchestrator reruns smoke/check-contract/run-check
```

## 5. Why Dry-run First

Automatic code generation can invert the source of truth: implementation starts to define design.

The first useful step is therefore not code creation, but surfacing a concrete, reviewable plan:

- Which files are implied by the design?
- Which public contracts should exist?
- Which DTO/schema/data contracts are known?
- Which skeleton paths already exist?
- Which smoke commands are suggested?

This keeps Gate 2 as the design authority while still reducing manual Run drafting cost.

## 6. Next Candidates

Future work can add:

- `scaffold-generate --dry-run` that shows exact file diffs without writing them
- language-specific skeleton renderers for Python, Java, TypeScript
- conflict detection between skeleton candidates and existing code
- Dashboard view for scaffold plan review
- integration with `execute --dry-run --json`

Actual file generation should remain behind explicit Orchestrator review and user-approved implementation scope.
