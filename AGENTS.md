# Codex Agent Guide

> Purpose: This is the Codex/GPT runtime entry point for Vulcan-Anvil Ex projects.

## 1. Role

You are a Codex/GPT agent working inside a Vulcan-Anvil Ex project.

Use this file as the runtime entry document. Do not treat Claude-specific files as your primary instructions.

## 2. Instruction Hierarchy

Follow instructions in this order:

1. User request and current conversation context
2. This `AGENTS.md`
3. `docs/core/`
4. `docs/adapters/codex-gpt/`
5. Relevant project artifacts under `docs/`
6. Existing codebase conventions

Claude runtime files such as `.claude/CLAUDE.md`, `.claude/agents/`, and `.claude/skills/` may exist in the same repository, but they are not the Codex runtime contract. Use them only as reference material when the user explicitly asks or when adapter comparison is needed.

## 3. Required Core Documents

Before starting a non-trivial Run, read the relevant parts of:

- `docs/core/ID_SYSTEM.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/DOCUMENT_METADATA.md`
- `docs/core/REFERENCE_STANDARDS.md`
- `docs/core/DATA_STANDARD_RULES.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/CHANGE_CONTROL_PROCESS.md`

For Codex/GPT-specific execution, also read:

- `docs/adapters/codex-gpt/README.md`
- `docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/GATE_PROMPTS.md`
- `docs/adapters/codex-gpt/LIMITATIONS.md`

## 4. Run Rules

- Work in small, explicit Runs.
- Link every meaningful change to relevant IDs such as `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `UI`, `FIND`, or `CR`.
- If a QA issue is inside the approved design scope, record it as `FIND` and handle it through the G4 QA Fix Loop.
- If the issue changes requirements, acceptance criteria, architecture, security baseline, data design, or release scope, escalate it to `CR`.
- Do not report tests as passed unless they were actually run.
- Keep implementation, tests, evidence, and traceability updates connected.

## 5. Reference Document Boundaries

- `docs/seed-docs/` contains public standards injected into the project. Treat these as read-only references.
- `docs/ref-docs/` may contain sensitive project reference documents. Do not commit files under this directory.
- If sensitive reference material is needed, summarize only the necessary derived rule or decision in project artifacts.

## 6. Output

At the end of a Run, provide a concise completion report and, when appropriate, create or update a Run record under:

```text
docs/runs/
```

Use the structure defined in:

```text
docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md
```

