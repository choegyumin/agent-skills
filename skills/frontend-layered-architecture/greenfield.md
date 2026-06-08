# Greenfield Project Frontend Architecture Flow

Use this file when there is no existing frontend directory/layer structure and the user has not specified one.

This file only chooses the next workflow step. Do not use it to ask design questions, propose structure, explain dependencies, or write documentation.

Before responding to the user, read the isolation rules, choose the first matching step, then follow only that step.

## Read Before Routing: Step Isolation Rules

This file is a router, not a table of contents.

- Choose the first matching step only.
- Read exactly one routed step file per response.
- Do not read files mentioned in later routing entries.
- Do not continue to another step unless the user explicitly asks to continue.
- Do not ask user-facing design questions from this file.
- If required design decisions are incomplete, read `greenfield-ask.md` before asking anything.
- If the top-level structure and dependency direction are not approved, read `greenfield-propose.md` before proposing anything.
- Do not create files, change settings, or write documentation before the user approves that action. A target document alone is not approval to write or update it.
- In existing codebases, ignore this flow unless the user explicitly asks to use it.
- Do not use this flow as a best-practice reference for existing project judgments.

## Step Routing

Handle only the first matching step. Do not answer directly from this routing list.

Required design decisions are OpenAPI Code Generation and Data Access Entry Points.

1. If required design decisions are incomplete, read [`greenfield-ask.md`](./greenfield-ask.md).
2. If required design decisions are complete but the top-level structure and dependency direction are not approved, read [`greenfield-propose.md`](./greenfield-propose.md).
3. If the top-level structure and dependency direction are approved but follow-up conventions are incomplete, read [`greenfield-ask.md`](./greenfield-ask.md).
4. If the structure, dependency direction, and follow-up conventions are approved, ask where to record the selected rules unless the user already gave a target document.
5. If documentation writing is approved, read [`writing-docs.md`](./writing-docs.md) before writing or updating any project document.
6. If architecture rule enforcement is requested or approved, read [`enforcing-rules.md`](./enforcing-rules.md).
