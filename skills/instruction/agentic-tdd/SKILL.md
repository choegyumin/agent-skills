---
name: agentic-tdd
description: Use whenever implementing changes with TDD, BDD, ATDD, or related test-first workflows. Guides refactoring timing and the final test-cleanup pass.
---

# Agentic TDD: Red, Green, Refactor, Tidy

Read "red-green-refactor" as "red-green-red-…-green-refactor-tidy".

- **Red before green.** Write and run the failing test first. Confirm that it fails for the expected reason because the intended behavior does not exist yet. If it already passes, check whether the behavior already exists and whether the chosen seam, inputs, preconditions, and expected result are correct.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle. Move to the next slice only after the test passes. Do not anticipate future tests or add speculative features.
- **Refactor after implementation.** Complete the intended change through repeated red-green cycles, then refactor during review if needed. A passing test is not a reason to mechanically refactor after every green.
- **Tidy by default.** After implementation and any needed refactoring, reassess the tests and improve, merge, or remove them according to their ongoing value. A test useful for reaching green is not automatically worth keeping. AI-written tests often include mechanical checks of the immediate change, so even passing tests almost always need a deliberate cleanup pass. Do not force changes when no cleanup is warranted.
