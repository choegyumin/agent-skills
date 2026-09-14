---
name: good-tests
description: Use whenever designing, writing, modifying, or reviewing tests; choosing what or where to test; creating or reviewing User Journey Tests; or making decisions about mocks and other test doubles. Keeps tests focused on observable behavior through public seams so they survive refactors. Do not use when only running existing tests or reporting their results.
---

# Good Tests

This skill is the reference for creating tests worth keeping: what a good test is, where tests go, and which anti-patterns to avoid.

## Required terminology

This skill uses the terms **User Journey Test** and **Focused Test**. User Journey Tests commonly appear as acceptance or E2E tests, but the terms are not synonymous. Before reading the following sections or references, or before designing, writing, modifying, or reviewing tests, read [terms.md](./terms.md) and understand the definitions precisely.

## Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. You can't test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?"

When the shape of that interface is itself in question, address the interface design before writing tests. Use the existing code and ADRs to identify the public interface and candidate seams, explain the trade-offs of each candidate, and agree on them with the user.

## Reference router

Route by the decision the work requires, not by the testing term the user happens to use. Read only the documents whose conditions apply. If several conditions overlap, read all applicable documents.

| Decision or task | Document to read |
| --- | --- |
| Design, write, modify, or review tests. | [tests.md](./tests.md) |
| Change a user journey, scenario, or story, or write, modify, or review a User Journey Test. | Also read [user-journey-tests.md](./user-journey-tests.md) |
| Choose, use, modify, or review a test double, or design an interface for one. | Also read [test-doubles.md](./test-doubles.md) |

When several conditions overlap, read only the required documents in this order: `tests.md` → `user-journey-tests.md` → `test-doubles.md`.
