---
name: engineering-cost-review
description: Use when reviewing a blueprint (PRD, spec, implementation plan, design/architecture doc, or product scope and technical decisions from the current session) right after it is written or before implementation, to check whether its implementation cost is economical and rational. Not for reviewing already-implemented code.
---

# Engineering Cost Review

- Don't implement requirements verbatim, with no critique.
- If the simplest approach satisfies the requirement, **recommend** it.
- If the simplest approach serves the goal but conflicts with the requirement, **propose** changing the requirement.
- If the requirement's scope and cost are so large they crowd out the purpose, **question** whether the scope is appropriate.
- This is not selfishness that sacrifices UX for DX — it must be a rational choice made with the user's goal and the product's future in mind.
- The user holds decision authority. Present your findings as _recommendations in a report_; make any actual change or execution only after the user confirms.

## Why this skill exists

The most common and costly mistake when using AI to settle a blueprint (spec, implementation plan, etc.) is **believing requirements must be implemented verbatim**. The user assumes "drop this feature and the implementation gets simpler too." But the reverse is often true — cutting it adds **workaround code**, and the next iteration rebuilds it anyway, producing **double work**. The paradox of reducing requirements yet increasing implementation.

This mistake persists because the user reasons about cost from _general intuition_, and intuition is wrong when it doesn't know what the current or intended stack provides. So this skill's job is to ask, for each decision in the blueprint, **"Does this decision minimize implementation cost _in this stack_?"** and propose a cheaper path when one exists. The **final judgment of whether a proposal is "reasonable" stays with the user** — they know timeline, risk, and business context more accurately.

## What this skill does / doesn't do

**Does:**

- Flag decisions in the blueprint that needlessly inflate implementation cost, judged against the stack in use or under consideration.

**Doesn't (single-lens principle):**

- Does not co-author requirements or decisions through interview — that's what to do _after the report_. This skill doesn't make decisions; it finds needless implementation cost in an already-written blueprint and produces _a report of recommendations_.
- Does not comment on spec hygiene (ambiguous terms, missing content, formatting). It hunts only _needless implementation cost_.
- Does not review already-implemented code — evaluating what's built can't undo spent cost. It looks only at _pre-implementation decisions_.
- Does not ask "is it simpler?" in the abstract. It asks only "is this approach cheaper _in this stack_?"

## Core lens

One question per decision:

> **Does this decision actually minimize implementation cost _in this stack_?**

"_In this stack_" is the point — not a general rule, but how cost is actually measured in the real technology, framework, dependencies, and config.

## Review procedure

1. **Extract decisions.** Pull concrete decisions out of the blueprint. "Out of scope" declarations are decisions too. If something is too vague to classify, report it as "undecidable" rather than skipping.

2. **Verify the stack (read, don't reason).** Before judging a decision's cost, read the real stack — lockfile, config, existing patterns in the codebase, framework defaults. Use current official docs and Context7 if needed. Asserting cost from general knowledge alone repeats the exact mistake this skill catches. The installed stack is the premise — do not question it.

3. **Three questions per decision.** For each:
   - (a) Does this cut/choice _actually_ simplify implementation in this stack, or complicate it?
   - (b) Will the cut feature come back later? If so, today's "simple" path becomes double work. Whether to absorb double work for speed is the user's call, so the AI reports the double-work fact.
   - (c) Does the stack provide this by default / for free? (Then not using it is a loss.)

4. **Don't flag without evidence.** Every flag must cite _what in the stack_ (a feature, default, dependency, or config) overturns the assumed cost. A cost claim without a citation is just another assumption.

5. **Flag, pass, or undecidable.** Mismatch → flag. Fully verified with no mismatch → pass. Can't verify (missing artifact, unverifiable stack or version, no evidence either way) → undecidable — do not force a pass by assuming the optimistic case.

## Flag categories

Problems usually overlap, so a case often matches more than one. If several apply, assign only the highest-priority one from the list below. Lower number = higher priority (1 is top).

1. **`Unjustified Dependency`:** The blueprint proposes adopting a NEW technology — a dependency, framework, data store, or service being added to the stack (not something already installed) — but no requirement anchors or justifies the adoption. Flag it for the user to ground or reconsider: this marks the choice as unconfirmed, not as wrong.
2. **`Irony of Cutting Scope`:** A feature was cut, yet implementation grows.
3. **`Reinvent the Wheel`:** Building anew something the stack provides by default, or that already exists in the codebase.
4. **`Cost Underestimation`:** Assumed simple, but actually _materially_ harder — including architectural over-build (e.g. microservices or event-driven design chosen where a simpler structure suffices). Only a material cost gap qualifies; a genuinely cheap task that merely has a minor edge case to handle is not this flag.

## Examples

**Flagged 1 — A new technology with no requirement behind it**

- Requirement: "A small internal tool to look up customer orders by ID."
- Decision: Adopt a GraphQL API.
- Assumed cost: GraphQL is a modern, flexible choice for the tool's data access.
- Actual cost: The requirement is a single lookup-by-ID — one endpoint. No requirement calls for GraphQL's flexible querying, schema federation, or multiple consumers. With nothing anchoring the adoption, its cost-minimization cannot be verified.
- Verdict: Not a verdict that GraphQL is wrong — only that it is unconfirmed. Ground it (state the requirement that needs it) or reconsider. The user decides.

**Flagged 2 — Building the admin screen by hand**

- Requirement: "Need a member-management screen. Use a CMS, but only show a list. Filters/sorting are out of scope — fast validation comes first."
- Decision: "The CMS we'd use ships filters/sorting by default and they can't be disabled. So we build just that screen by hand."
- Assumed cost: "We have to hide filters/sorting, and a simple list is cheap to build ourselves."
- Actual cost: The CMS provides every feature from a single resource definition. Filters/sorting are merely low-priority — their presence doesn't harm the requirement. Cutting saves no work, and honoring the cut only adds needless code; when priority returns, it gets rebuilt by tearing the custom screen out.
- Verdict: No need to cut. Show the CMS's built-in filters/sorting from the start.

**Flagged 3 — Building search by hand**

- Requirement: "Need product search. Build it like the search that already exists in the product, but typo-correction/autocomplete need a rules decision, so they're out of scope — match only the exact word typed."
- Decision: "Instead of the search OSS already in the stack (typo-correction, autocomplete, ranking, indexing), build a LIKE search ourselves."
- Assumed cost: "We have to strip typo-correction/autocomplete, and exact matching is cheap to build ourselves."
- Actual cost: The OSS matches exact words too, so using it as-is satisfies the requirement. Cutting saves no work; honoring it only adds needless code.
- Verdict: Adopt the OSS's typo-correction/autocomplete rules, temporarily or permanently.

**Not flagged — Building a diary-app MVP (core guardrail)**

- Requirement: "A new diary app with differentiated UX. Recruited testers mostly use a single mobile device and already write at planned times. Remove features unneeded for demand validation."
- Decision: "Drop multi-device sync — single-device local storage. No push notifications."
- Assumed cost: "Given the testers' usage pattern, these aren't needed for the MVP, and nothing in the stack or codebase already provides or implements them."
- Core guardrail: Distinguish "something to build later" from "building more now in order to rebuild it later." Deferring is healthy. Flag only the case where you build extra now and tear it out again later.

## Output format

Post the review as a message — do not write it to a file. Write everything in the user's language, except `CATEGORY` names, which stay verbatim in English.

If there are flags:

```md
## [`CATEGORY`] — Flag 1

- Requirement: (the user's requirement, from the blueprint or current session)
- Decision: (the implementation approach decided in the blueprint or current session)
- Assumed cost: (the cost the decision implicitly presupposes)
- Actual cost: (the real cost in this stack, with evidence and source)
- Verdict: (the more economical/rational alternative; what to reconsider)

## [`CATEGORY`] — Flag 2

...
```

If a decision cannot be judged — the relevant artifact is missing (e.g. a file needed to verify the claim), the stack or version is unverifiable, or there is no explicit evidence either way — list it as undecidable. Undecidable is neither a flag nor a pass; do not force it into either.

```md
## Undecidable

- Decision: ...
- Missing evidence: ...
```

If there are no flags and nothing undecidable, say so plainly:

```md
No cost mismatch. (Decisions reviewed: N, stack: ...)
```

Don't manufacture flags. Most blueprints are healthy.

## Input

- If a path is given, read that file.
- Otherwise synthesize from the decisions in the current conversation, or from recent spec/plan artifacts.
- If the decisions aren't concrete enough to extract anything → review is not possible; say so and stop.
