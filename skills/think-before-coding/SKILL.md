---
name: think-before-coding
description: Guardrails for writing, modifying, reviewing, or refactoring code. Use whenever a task involves code to clarify ambiguous requirements before implementation, avoid over-engineering and speculative abstractions, and keep changes minimal and scoped.
---

# Think Before Coding

Use these principles to guide every implementation decision:

- **KISS (Keep It Simple, Stupid)**
- **YAGNI (You Aren't Gonna Need It)**
- **AHA (Avoid Hasty Abstractions)** — Don't force DRY (Don't Repeat Yourself); prefer duplication over the wrong abstraction.

## 1. Don't assume. Ask before implementing.

- If material requirements are unclear or have multiple consequential interpretations, ask. Don't assume silently.
- If a simpler approach exists, say so. Push back when warranted.

## 2. Write the minimum complete code that solves the problem. Nothing speculative.

- **A minimal solution is not a band-aid solution.** Unless the user's intent or instructions require otherwise, default to a minimal solution.
- No features beyond what was asked.
- Prefer direct code for single-use logic. Abstract only when it clearly improves readability or isolates a boundary.
- No flexibility or configurability for hypothetical future needs.
- No defensive code for states ruled out by enforced invariants.
- If the solution grows out of proportion to the problem, step back and simplify.
- In urgent situations, you may propose a band-aid solution; disclose what it masks, hides, or leaves unresolved, and get explicit approval before implementation.

Use the first option that applies:

1. Does this need to exist at all? If the need is speculative, skip it.
2. Does the codebase already have a helper, type, or pattern for it? Reuse it. Look before you write.
3. Does an already-installed dependency or native platform feature solve it cleanly? Follow established project conventions; otherwise choose the simpler, more direct option.
4. Otherwise, write the smallest direct, readable implementation that works. Don't add a dependency for a few clear lines.

Before proceeding, reconsider any unapproved band-aid that masks symptoms or hides the problem, and repeat the sequence.

## 3. Touch only what you must. Clean up only your own mess.

- Don't refactor, reformat, or clean up unrelated code.
- Match existing style, even if you'd do it differently.
- Remove code made unused by your changes. Leave pre-existing dead code alone unless asked, and mention it in the final report.
- Every changed line should serve the request or be necessary to keep the change correct.
