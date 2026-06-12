## Review Sections (11 sections, after scope and mode are agreed)

**Anti-skip rule:** Never condense, abbreviate, or skip any review section (1-11) regardless of plan type (strategy, spec, code, infra). Every section in this skill exists for a reason. "This is a strategy doc so implementation sections don't apply" is always wrong — implementation details are where strategy breaks down. If a section genuinely has zero findings, say "No issues found" and move on — but you must evaluate it.

**Anti-shortcut clause:** The plan file is the OUTPUT of the interactive review, not a substitute for it. Writing every finding into one plan write and calling plan finalization without firing structured choice prompt is the precise failure mode of the May 2026 transcript bug — the model explored, found issues, and dumped them into a deliverable rather than walking the user through them. If you have ANY non-trivial finding in any review section, the path from finding to plan finalization goes THROUGH structured choice prompt. Zero findings in every section is the only path to plan finalization that bypasses structured choice prompt. If you find yourself wanting to write a plan with findings before asking, stop and ask with a structured choice prompt now — that's the bug, recognize it.

### Section 1: Architecture Review
Evaluate and diagram:
* Overall system design and component boundaries. Draw the dependency graph.
* Data flow — all four paths. For every new data flow, ASCII diagram the:
    * Happy path (data flows correctly)
    * Nil path (input is nil/missing — what happens?)
    * Empty path (input is present but empty/zero-length — what happens?)
    * Error path (upstream call fails — what happens?)
* State machines. ASCII diagram for every new stateful object. Include impossible/invalid transitions and what prevents them.
* Coupling concerns. Which components are now coupled that weren't before? Is that coupling justified? Draw the before/after dependency graph.
* Scaling characteristics. What breaks first under 10x load? Under 100x?
* Single points of failure. Map them.
* Security architecture. Auth boundaries, data access patterns, API surfaces. For each new endpoint or data mutation: who can call it, what do they get, what can they change?
* Production failure scenarios. For each new integration point, describe one realistic production failure (timeout, cascade, data corruption, auth failure) and whether the plan accounts for it.
* Rollback posture. If this ships and immediately breaks, what's the rollback procedure? Git revert? Feature flag? DB migration rollback? How long?

**EXPANSION and SELECTIVE EXPANSION additions:**
* What would make this architecture beautiful? Not just correct — elegant. Is there a design that would make a new engineer joining in 6 months say "oh, that's clever and obvious at the same time"?
* What infrastructure would make this feature a platform that other features can build on?

**SELECTIVE EXPANSION:** If any accepted cherry-picks from Step 0D affect the architecture, evaluate their architectural fit here. Flag any that create coupling concerns or don't integrate cleanly — this is a chance to revisit the decision with new information.

Required ASCII diagram: full system architecture showing new components and their relationships to existing ones.
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 2: Error & Rescue Map
This is the section that catches silent failures. It is not optional.
For every new method, service, or codepath that can fail, fill in this table:
```
  METHOD/CODEPATH          | WHAT CAN GO WRONG           | EXCEPTION CLASS
  -------------------------|-----------------------------|-----------------
  ExampleService#call      | API timeout                 | TimeoutError
                           | API returns 429             | RateLimitError
                           | API returns malformed JSON  | JSONParseError
                           | DB connection pool exhausted| ConnectionPoolExhausted
                           | Record not found            | RecordNotFound
  -------------------------|-----------------------------|-----------------

  EXCEPTION CLASS              | RESCUED?  | RESCUE ACTION          | USER SEES
  -----------------------------|-----------|------------------------|------------------
  TimeoutError                 | Y         | Retry 2x, then raise   | "Service temporarily unavailable"
  RateLimitError               | Y         | Backoff + retry         | Nothing (transparent)
  JSONParseError               | N ← GAP   | —                      | 500 error ← BAD
  ConnectionPoolExhausted      | N ← GAP   | —                      | 500 error ← BAD
  RecordNotFound               | Y         | Return nil, log warning | "Not found" message
```
Rules for this section:
* Catch-all error handling (`rescue StandardError`, `catch (Exception e)`, `except Exception`) is ALWAYS a smell. Name the specific exceptions.
* Catching an error with only a generic log message is insufficient. Log the full context: what was being attempted, with what arguments, for what user/request.
* Every rescued error must either: retry with backoff, degrade gracefully with a user-visible message, or re-raise with added context. "Swallow and continue" is almost never acceptable.
* For each GAP (unrescued error that should be rescued): specify the rescue action and what the user should see.
* For LLM/AI service calls specifically: what happens when the response is malformed? When it's empty? When it hallucinates invalid JSON? When the model returns a refusal? Each of these is a distinct failure mode.
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 3: Security & Threat Model
Security is not a sub-bullet of architecture. It gets its own section.
Evaluate:
* Attack surface expansion. What new attack vectors does this plan introduce? New endpoints, new params, new file paths, new background jobs?
* Input validation. For every new user input: is it validated, sanitized, and rejected loudly on failure? What happens with: nil, empty string, string when integer expected, string exceeding max length, unicode edge cases, HTML/script injection attempts?
* Authorization. For every new data access: is it scoped to the right user/role? Is there a direct object reference vulnerability? Can user A access user B's data by manipulating IDs?
* Secrets and credentials. New secrets? In env vars, not hardcoded? Rotatable?
* Dependency risk. New gems/npm packages? Security track record?
* Data classification. PII, payment data, credentials? Handling consistent with existing patterns?
* Injection vectors. SQL, command, template, LLM prompt injection — check all.
* Audit logging. For sensitive operations: is there an audit trail?

For each finding: threat, likelihood (High/Med/Low), impact (High/Med/Low), and whether the plan mitigates it.
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 4: Data Flow & Interaction Edge Cases
This section traces data through the system and interactions through the UI with adversarial thoroughness.

**Data Flow Tracing:** For every new data flow, produce an ASCII diagram showing:
```
  INPUT ──▶ VALIDATION ──▶ TRANSFORM ──▶ PERSIST ──▶ OUTPUT
    │            │              │            │           │
    ▼            ▼              ▼            ▼           ▼
  [nil?]    [invalid?]    [exception?]  [conflict?]  [stale?]
  [empty?]  [too long?]   [timeout?]    [dup key?]   [partial?]
  [wrong    [wrong type?] [OOM?]        [locked?]    [encoding?]
   type?]
```
For each node: what happens on each shadow path? Is it tested?

**Interaction Edge Cases:** For every new user-visible interaction, evaluate:
```
  INTERACTION          | EDGE CASE              | HANDLED? | HOW?
  ---------------------|------------------------|----------|--------
  Form submission      | Double-click submit    | ?        |
                       | Submit with stale CSRF | ?        |
                       | Submit during deploy   | ?        |
  Async operation      | User navigates away    | ?        |
                       | Operation times out    | ?        |
                       | Retry while in-flight  | ?        |
  List/table view      | Zero results           | ?        |
                       | 10,000 results         | ?        |
                       | Results change mid-page| ?        |
  Background job       | Job fails after 3 of   | ?        |
                       | 10 items processed     |          |
                       | Job runs twice (dup)   | ?        |
                       | Queue backs up 2 hours | ?        |
```
Flag any unhandled edge case as a gap. For each gap, specify the fix.
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 5: Code Quality Review
Evaluate:
* Code organization and module structure. Does new code fit existing patterns? If it deviates, is there a reason?
* DRY violations. Be aggressive. If the same logic exists elsewhere, flag it and reference the file and line.
* Naming quality. Are new classes, methods, and variables named for what they do, not how they do it?
* Error handling patterns. (Cross-reference with Section 2 — this section reviews the patterns; Section 2 maps the specifics.)
* Missing edge cases. List explicitly: "What happens when X is nil?" "When the API returns 429?" etc.
* Over-engineering check. Any new abstraction solving a problem that doesn't exist yet?
* Under-engineering check. Anything fragile, assuming happy path only, or missing obvious defensive checks?
* Cyclomatic complexity. Flag any new method that branches more than 5 times. Propose a refactor.
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 6: Test Review
Make a complete diagram of every new thing this plan introduces:
```
  NEW UX FLOWS:
    [list each new user-visible interaction]

  NEW DATA FLOWS:
    [list each new path data takes through the system]

  NEW CODEPATHS:
    [list each new branch, condition, or execution path]

  NEW BACKGROUND JOBS / ASYNC WORK:
    [list each]

  NEW INTEGRATIONS / EXTERNAL CALLS:
    [list each]

  NEW ERROR/RESCUE PATHS:
    [list each — cross-reference Section 2]
```
For each item in the diagram:
* What type of test covers it? (Unit / Integration / System / E2E)
* Does a test for it exist in the plan? If not, write the test spec header.
* What is the happy path test?
* What is the failure path test? (Be specific — which failure?)
* What is the edge case test? (nil, empty, boundary values, concurrent access)

Test ambition check (all modes): For each new feature, answer:
* What's the test that would make you confident shipping at 2am on a Friday?
* What's the test a hostile QA engineer would write to break this?
* What's the chaos test?

Test pyramid check: Many unit, fewer integration, few E2E? Or inverted?
Flakiness risk: Flag any test depending on time, randomness, external services, or ordering.
Load/stress test requirements: For any new codepath called frequently or processing significant data.

For LLM/prompt changes: Check CLAUDE.md for the "Prompt/LLM changes" file patterns. If this plan touches ANY of those patterns, state which eval suites must be run, which cases should be added, and what baselines to compare against.
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 7: Performance Review
Evaluate:
* N+1 queries. For every new ActiveRecord association traversal: is there an includes/preload?
* Memory usage. For every new data structure: what's the maximum size in production?
* Database indexes. For every new query: is there an index?
* Caching opportunities. For every expensive computation or external call: should it be cached?
* Background job sizing. For every new job: worst-case payload, runtime, retry behavior?
* Slow paths. Top 3 slowest new codepaths and estimated p99 latency.
* Connection pool pressure. New DB connections, Redis connections, HTTP connections?
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 8: Observability & Debuggability Review
New systems break. This section ensures you can see why.
Evaluate:
* Logging. For every new codepath: structured log lines at entry, exit, and each significant branch?
* Metrics. For every new feature: what metric tells you it's working? What tells you it's broken?
* Tracing. For new cross-service or cross-job flows: trace IDs propagated?
* Alerting. What new alerts should exist?
* Dashboards. What new dashboard panels do you want on day 1?
* Debuggability. If a bug is reported 3 weeks post-ship, can you reconstruct what happened from logs alone?
* Admin tooling. New operational tasks that need admin UI or rake tasks?
* Runbooks. For each new failure mode: what's the operational response?

**EXPANSION and SELECTIVE EXPANSION addition:**
* What observability would make this feature a joy to operate? (For SELECTIVE EXPANSION, include observability for any accepted cherry-picks.)
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 9: Deployment & Rollout Review
Evaluate:
* Migration safety. For every new DB migration: backward-compatible? Zero-downtime? Table locks?
* Feature flags. Should any part be behind a feature flag?
* Rollout order. Correct sequence: migrate first, deploy second?
* Rollback plan. Explicit step-by-step.
* Deploy-time risk window. Old code and new code running simultaneously — what breaks?
* Environment parity. Tested in staging?
* Post-deploy verification checklist. First 5 minutes? First hour?
* Smoke tests. What automated checks should run immediately post-deploy?

**EXPANSION and SELECTIVE EXPANSION addition:**
* What deploy infrastructure would make shipping this feature routine? (For SELECTIVE EXPANSION, assess whether accepted cherry-picks change the deployment risk profile.)
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 10: Long-Term Trajectory Review
Evaluate:
* Technical debt introduced. Code debt, operational debt, testing debt, documentation debt.
* Path dependency. Does this make future changes harder?
* Knowledge concentration. Documentation sufficient for a new engineer?
* Reversibility. Rate 1-5: 1 = one-way door, 5 = easily reversible.
* Ecosystem fit. Aligns with Rails/JS ecosystem direction?
* The 1-year question. Read this plan as a new engineer in 12 months — obvious?

**EXPANSION and SELECTIVE EXPANSION additions:**
* What comes after this ships? Phase 2? Phase 3? Does the architecture support that trajectory?
* Platform potential. Does this create capabilities other features can leverage?
* (SELECTIVE EXPANSION only) Retrospective: Were the right cherry-picks accepted? Did any rejected expansions turn out to be load-bearing for the accepted ones?
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

### Section 11: Design & UX Review (skip if no UI scope detected)
The CEO calling in the designer. Not a pixel-level audit — that's /plan-design-review and /design-review. This is ensuring the plan has design intentionality.

Evaluate:
* Information architecture — what does the user see first, second, third?
* Interaction state coverage map:
  FEATURE | LOADING | EMPTY | ERROR | SUCCESS | PARTIAL
* User journey coherence — storyboard the emotional arc
* AI slop risk — does the plan describe generic UI patterns?
* DESIGN.md alignment — does the plan match the stated design system?
* Responsive intention — is mobile mentioned or afterthought?
* Accessibility basics — keyboard nav, screen readers, contrast, touch targets

**EXPANSION and SELECTIVE EXPANSION additions:**
* What would make this UI feel *inevitable*?
* What 30-minute UI touches would make users think "oh nice, they thought of that"?

Required ASCII diagram: user flow showing screens/states and transitions.

If this plan has significant UI scope, recommend: "Consider running /plan-design-review for a deep design review of this plan before implementation."
**STOP.** Ask with one structured choice prompt per issue. Do NOT batch. Recommend + WHY. If this section turned up zero findings, state "No issues, moving on" and proceed. If the section has findings, present a structured choice prompt — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan. Do NOT proceed until the user responds.
**Reminder: Do NOT make any code changes. Review only.**

## Outside Voice — Independent Plan Challenge (optional)

After all review sections are complete, run an independent skeptical pass if the environment supports delegated agents or independent review. This is informational, not a gate.

**Construct the plan review prompt.** Read the plan file being reviewed (the file the user pointed this review at, or the branch diff scope). If a CEO plan document was written in Step 0D-POST, inspect that too — it contains the scope decisions and vision.

Construct this prompt (substitute the actual plan content — if plan content exceeds 30KB, truncate to the first 30KB and note "Plan truncated for size"):

"You are a brutally honest technical reviewer examining a development plan that has already been through a multi-section review. Your job is NOT to repeat that review. Instead, find what it missed. Look for: logical gaps and unstated assumptions that survived the review scrutiny, overcomplexity (is there a fundamentally simpler approach the review was too deep in the weeds to see?), feasibility risks the review took for granted, missing dependencies or sequencing issues, and strategic miscalibration (is this the right thing to build at all?). Be direct. Be terse. No compliments. Just the problems.

THE PLAN:
<plan content>"

If delegated review is available, run it with fresh context and present findings under an `OUTSIDE VOICE (independent reviewer):` header. If unavailable, skip and state: "Outside voice unavailable. Continuing to outputs."

**Tension handling:**

After presenting outside voice findings, note any points where it disagrees with the review findings from earlier sections. Flag these as:

```
REVIEW TENSION:
  [Topic]: Review said X. Outside voice says Y. [Present both perspectives neutrally.
  State what context you might be missing that would change the answer.]
```

**User Sovereignty:** Do NOT auto-incorporate outside voice recommendations into the plan. Present each tension point to the user. Independent agreement is a strong signal — present it as such — but it is NOT permission to act. You may state which argument you find more compelling, but you MUST NOT apply the change without explicit user approval.

For each substantive tension point, ask with a structured choice prompt:

> "Review tension on [topic]. The review found [X] but the outside voice argues [Y]. [One sentence on what context you might be missing.]"
>
> RECOMMENDATION: Choose [A or B] because [one-line reason explaining which argument is more compelling and why]. Completeness: A=X/10, B=Y/10.

Options:
- A) Accept the outside voice's recommendation (I'll apply this change)
- B) Keep the current approach (reject the outside voice)
- C) Investigate further before deciding
- D) Add to TODOS.md for later

Wait for the user's response. Do NOT default to accepting because you agree with the outside voice. If the user chooses B, the current approach stands — do not re-argue.

If no tension points exist, note: "No review tension — both passes agree."

---

### Outside Voice Integration Rule

Outside voice findings are INFORMATIONAL until the user explicitly approves each one. Do NOT incorporate outside voice recommendations into the plan without presenting each finding with a structured choice prompt and getting explicit approval. This applies even when you agree with the outside voice. Independent consensus is a strong signal — present it as such — but the user makes the decision.

## Post-Implementation Design Audit (if UI scope detected)
After implementation, run `/design-review` on the live site to catch visual issues that can only be evaluated with rendered output.

## CRITICAL RULE — How to ask questions
Follow the structured choice prompt format from the Preamble above. Additional rules for plan reviews:
* **One issue = one structured choice prompt.** Never combine multiple issues into one question.
* Describe the problem concretely, with file and line references.
* Present 2-3 options, including "do nothing" where reasonable.
* For each option: effort, risk, and maintenance burden in one line.
* **Map the reasoning to my engineering preferences above.** One sentence connecting your recommendation to a specific preference.
* Label with issue NUMBER + option LETTER (e.g., "3A", "3B").
* **Zero findings:** if a section has zero findings, state "No issues, moving on" and proceed. Otherwise, use a structured choice prompt for each finding — a finding with an "obvious fix" is still a finding and still needs user approval before any change lands in the plan.

## Required Outputs

### "NOT in scope" section
List work considered and explicitly deferred, with one-line rationale each.

### "What already exists" section
List existing code/flows that partially solve sub-problems and whether the plan reuses them.

### "Dream state delta" section
Where this plan leaves us relative to the 12-month ideal.

### Error & Rescue Registry (from Section 2)
Complete table of every method that can fail, every exception class, rescued status, rescue action, user impact.

### Failure Modes Registry
```
  CODEPATH | FAILURE MODE   | RESCUED? | TEST? | USER SEES?     | LOGGED?
  ---------|----------------|----------|-------|----------------|--------
```
Any row with RESCUED=N, TEST=N, USER SEES=Silent → **CRITICAL GAP**.

### TODOS.md updates
Present each potential TODO as its own individual structured choice prompt. Never batch TODOs — one per question. Never silently skip this step. Follow the existing `TODOS.md` format in the project.

For each TODO, describe:
* **What:** One-line description of the work.
* **Why:** The concrete problem it solves or value it unlocks.
* **Pros:** What you gain by doing this work.
* **Cons:** Cost, complexity, or risks of doing it.
* **Context:** Enough detail that someone picking this up in 3 months understands the motivation, the current state, and where to start.
* **Effort estimate:** S/M/L/XL (human team) → with AI-assisted implementation: S→S, M→S, L→M, XL→L
* **Priority:** P1/P2/P3
* **Depends on / blocked by:** Any prerequisites or ordering constraints.

Then present options: **A)** Add to TODOS.md **B)** Skip — not valuable enough **C)** Build it now in this PR instead of deferring.

### Scope Expansion Decisions (EXPANSION and SELECTIVE EXPANSION only)
For EXPANSION and SELECTIVE EXPANSION modes: expansion opportunities and delight items were surfaced and decided in Step 0D (opt-in/cherry-pick ceremony). The decisions are persisted in the CEO plan document. Reference the CEO plan for the full record. Do not re-surface them here — list the accepted expansions for completeness:
* Accepted: {list items added to scope}
* Deferred: {list items sent to TODOS.md}
* Skipped: {list items rejected}

### Diagrams (mandatory, produce all that apply)
1. System architecture
2. Data flow (including shadow paths)
3. State machine
4. Error flow
5. Deployment sequence
6. Rollback flowchart

### Stale Diagram Audit
List every ASCII diagram in files this plan touches. Still accurate?

## Implementation Tasks

Before closing this review, synthesize the findings above into a flat list of
build-actionable tasks. Each task derives from a specific finding — no padding.
Emit the markdown section AND write a JSONL artifact that `/autoplan` can
aggregate across phases.

### Markdown section (always emit)

```markdown
## Implementation Tasks
Synthesized from this review's findings. Each task derives from a specific
finding above. Run with a coding agent or implement manually; checkbox as you ship.

- [ ] **T1 (P1, human: ~2h / AI: ~15min)** — <component> — <imperative title>
  - Surfaced by: <section name> — <specific finding text or line reference>
  - Files: <paths to touch>
  - Verify: <test command or manual check>
- [ ] **T2 (P2, human: ~30min / AI: ~5min)** — ...
```

Rules:
- P1 blocks ship; P2 should land same branch; P3 is a follow-up TODO.
- If a finding produced no actionable task, do not invent one.
- If a section had zero findings, emit `_No new tasks from <section>._`
- Effort uses the AI-compression table from CLAUDE.md.

### JSONL artifact (always write, even if zero tasks)

`/autoplan` reads this file to aggregate across phases. Build each line with
`jq -nc` so titles and source findings containing quotes, newlines, or
backslashes serialize cleanly — never use hand-rolled `echo` / `printf`.

```bash
TASKS_DIR="docs/plans/review-tasks"
mkdir -p "$TASKS_DIR"
TASKS_FILE="$TASKS_DIR/tasks-ceo-review-$(date +%Y%m%d-%H%M%S).jsonl"
COMMIT=$(git rev-parse HEAD 2>/dev/null || echo unknown)
BRANCH=$(git branch --show-current 2>/dev/null || echo unknown)
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-$$"

# Repeat ONE jq invocation per task identified during this review.
# Substitute the placeholders inline with shell variables you set per task:
#   TASK_ID (T1, T2, ...), PRIORITY (P1/P2/P3), COMPONENT, TITLE,
#   SOURCE_FINDING, EFFORT_HUMAN, EFFORT_AI, FILES_JSON (a JSON array literal
#   like '["browse/src/sanitize.ts","browse/src/server.ts"]').
jq -nc \
  --arg phase 'ceo-review' \
  --arg run_id "$RUN_ID" \
  --arg branch "$BRANCH" \
  --arg commit "$COMMIT" \
  --arg id "$TASK_ID" \
  --arg priority "$PRIORITY" \
  --arg component "$COMPONENT" \
  --arg effort_human "$EFFORT_HUMAN" \
  --arg effort_ai "$EFFORT_AI" \
  --arg title "$TITLE" \
  --arg source_finding "$SOURCE_FINDING" \
  --argjson files "$FILES_JSON" \
  '{phase:$phase, run_id:$run_id, branch:$branch, commit:$commit, id:$id, priority:$priority, component:$component, files:$files, effort_human:$effort_human, effort_ai:$effort_ai, title:$title, source_finding:$source_finding}' \
  >> "$TASKS_FILE"
```

If `jq` is not installed, fall back to skipping the JSONL write and warn
the user to install jq for autoplan aggregation. Never hand-roll JSONL.

If zero tasks were identified in this review, still touch the JSONL file
(`: > "$TASKS_FILE"`) so the aggregator sees that the phase produced output
this run (an empty file means "ran, no findings" — distinct from "didn't run").


### Completion Summary
```
  +====================================================================+
  |            MEGA PLAN REVIEW — COMPLETION SUMMARY                   |
  +====================================================================+
  | Mode selected        | EXPANSION / SELECTIVE / HOLD / REDUCTION     |
  | System Audit         | [key findings]                              |
  | Step 0               | [mode + key decisions]                      |
  | Section 1  (Arch)    | ___ issues found                            |
  | Section 2  (Errors)  | ___ error paths mapped, ___ GAPS            |
  | Section 3  (Security)| ___ issues found, ___ High severity         |
  | Section 4  (Data/UX) | ___ edge cases mapped, ___ unhandled        |
  | Section 5  (Quality) | ___ issues found                            |
  | Section 6  (Tests)   | Diagram produced, ___ gaps                  |
  | Section 7  (Perf)    | ___ issues found                            |
  | Section 8  (Observ)  | ___ gaps found                              |
  | Section 9  (Deploy)  | ___ risks flagged                           |
  | Section 10 (Future)  | Reversibility: _/5, debt items: ___         |
  | Section 11 (Design)  | ___ issues / SKIPPED (no UI scope)          |
  +--------------------------------------------------------------------+
  | NOT in scope         | written (___ items)                          |
  | What already exists  | written                                     |
  | Dream state delta    | written                                     |
  | Error/rescue registry| ___ methods, ___ CRITICAL GAPS              |
  | Failure modes        | ___ total, ___ CRITICAL GAPS                |
  | TODOS.md updates     | ___ items proposed                          |
  | Scope proposals      | ___ proposed, ___ accepted (EXP + SEL)      |
  | CEO plan             | written / skipped (HOLD/REDUCTION)           |
  | Outside voice        | ran (independent) / skipped                       |
  | Lake Score           | X/Y recommendations chose complete option   |
  | Diagrams produced    | ___ (list types)                            |
  | Stale diagrams found | ___                                         |
  | Unresolved decisions | ___ (listed below)                          |
  +====================================================================+
```

### Unresolved Decisions
If any structured choice prompt goes unanswered, note it here. Never silently default.

## Plan File Review Report

After producing the Completion Summary in conversation output, also update the **plan file** itself so review status is visible to anyone reading the plan.

### Detect the plan file

1. Check if there is an active plan file in this conversation (the host may provide plan file paths in system messages — look for plan file references in the conversation context).
2. If not found, skip this section silently — not every review runs in plan mode.

### Generate the report

Use this review's Completion Summary and any review artifacts produced in this session. Do not depend on external review logs.

Produce this markdown table:

```markdown
## PLAN REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | {status} | {mode, proposals accepted/deferred, critical gaps} |
| Outside Voice | independent review | Skeptical second pass | {0 or 1} | {ran/skipped} | {tension count or "none"} |
| Eng Review | `/plan-eng-review` | Architecture & tests (required before implementation) | {known runs or "not checked"} | {recommended/not checked} | {why it is or is not needed next} |
| Design Review | `/plan-design-review` | UI/UX gaps | {known runs or "not checked"} | {recommended/skipped/not checked} | {UI scope summary} |
```

Below the table, add these lines. **OUTSIDE VOICE** and **REVIEW TENSION** are optional (omit when empty); **VERDICT** is always present:

- **OUTSIDE VOICE:** (only if outside voice ran) — one-line summary
- **REVIEW TENSION:** (only if tension exists) — one-line summary
- **VERDICT:** list reviews that are CLEAR or recommended next (e.g., "CEO CLEARED — run ENG REVIEW before implementation").

**Unresolved-decisions status (MANDATORY — never omitted; the report's final non-whitespace line).** After VERDICT, end the report (content under the `## PLAN REVIEW REPORT` heading — a bold label, never a new `## ` heading) with exactly one: the exact unbolded line `NO UNRESOLVED DECISIONS` (a bolded one does NOT count), OR a `**UNRESOLVED DECISIONS:**` header + one bullet per open item (last bullet = final line).

### Write to the plan file

The report must always be the LAST section of the plan file — never mid-file. Use a single delete-then-append flow:

1. Inspect the plan file to see its full current content. Search for a `## PLAN REVIEW REPORT` heading anywhere in the file.
2. If found, delete the entire existing section. Match from `## PLAN REVIEW REPORT` through either the next `## ` heading or end of file, whichever comes first. Replace with the empty string. This applies regardless of where the section currently lives — mid-file deletion is intentional, not a special case. If the edit fails (e.g., concurrent edit changed the content), re-inspect the plan file and retry once.
3. After the delete (or skipped, if no section existed), append the new `## PLAN REVIEW REPORT` section at the END of the file.
4. Verify that `## PLAN REVIEW REPORT` is the last `## ` heading in the file before continuing. If it isn't, repeat steps 2-3 once.

Do NOT replace the section in place. The "replace mid-file" path can leave the report mid-file when an older report already lived there — the user then sees a plan whose review report is not at the bottom and rejects it.

## Next Steps — Review Chaining

After the CEO review, recommend the next review(s) based on what this review discovered.

**Recommend /plan-eng-review** when this review expanded scope, changed architecture, found significant implementation risk, or produced implementation tasks that need architectural/test planning. It is the normal pre-implementation gate for non-trivial work.

**Recommend /plan-design-review** if UI scope was detected — specifically if Section 11 (Design & UX Review) was NOT skipped, or if accepted scope expansions included UI-facing features. In SCOPE REDUCTION mode, skip this recommendation unless UI risk remains.

**If both are needed, recommend eng review first** (implementation gate), then design review.

Ask with a structured choice prompt. Include only applicable options:
- **A)** Run /plan-eng-review next
- **B)** Run /plan-design-review next (only if UI scope detected)
- **C)** Skip — I'll handle reviews manually

## docs/designs Promotion (EXPANSION and SELECTIVE EXPANSION only)

At the end of the review, if the vision produced a compelling feature direction, offer to promote the CEO plan to the project repo. Ask with a structured choice prompt:

"The vision from this review produced {N} accepted scope expansions. Want to promote it to a design doc in the repo?"
- **A)** Promote to `docs/designs/{FEATURE}.md` (committed to repo, visible to the team)
- **B)** Keep in `docs/plans/ceo-review/` only
- **C)** Skip

If promoted, copy the CEO plan content to `docs/designs/{FEATURE}.md` (create the directory if needed) and update the `status` field in the original CEO plan from `ACTIVE` to `PROMOTED`.

## Formatting Rules
* NUMBER issues (1, 2, 3...) and LETTERS for options (A, B, C...).
* Label with NUMBER + LETTER (e.g., "3A", "3B").
* One sentence max per option.
* After each section, pause and wait for feedback.
* Use **CRITICAL GAP** / **WARNING** / **OK** for scannability.

## Mode Quick Reference
```
  ┌────────────────────────────────────────────────────────────────────────────────┐
  │                            MODE COMPARISON                                     │
  ├─────────────┬──────────────┬──────────────┬──────────────┬────────────────────┤
  │             │  EXPANSION   │  SELECTIVE   │  HOLD SCOPE  │  REDUCTION         │
  ├─────────────┼──────────────┼──────────────┼──────────────┼────────────────────┤
  │ Scope       │ Push UP      │ Hold + offer │ Maintain     │ Push DOWN          │
  │             │ (opt-in)     │              │              │                    │
  │ Recommend   │ Enthusiastic │ Neutral      │ N/A          │ N/A                │
  │ posture     │              │              │              │                    │
  │ 10x check   │ Mandatory    │ Surface as   │ Optional     │ Skip               │
  │             │              │ cherry-pick  │              │                    │
  │ Platonic    │ Yes          │ No           │ No           │ No                 │
  │ ideal       │              │              │              │                    │
  │ Delight     │ Opt-in       │ Cherry-pick  │ Note if seen │ Skip               │
  │ opps        │ ceremony     │ ceremony     │              │                    │
  │ Complexity  │ "Is it big   │ "Is it right │ "Is it too   │ "Is it the bare    │
  │ question    │  enough?"    │  + what else │  complex?"   │  minimum?"         │
  │             │              │  is tempting"│              │                    │
  │ Taste       │ Yes          │ Yes          │ No           │ No                 │
  │ calibration │              │              │              │                    │
  │ Temporal    │ Full (hr 1-6)│ Full (hr 1-6)│ Key decisions│ Skip               │
  │ interrogate │              │              │  only        │                    │
  │ Observ.     │ "Joy to      │ "Joy to      │ "Can we      │ "Can we see if     │
  │ standard    │  operate"    │  operate"    │  debug it?"  │  it's broken?"     │
  │ Deploy      │ Infra as     │ Safe deploy  │ Safe deploy  │ Simplest possible  │
  │ standard    │ feature scope│ + cherry-pick│  + rollback  │  deploy            │
  │             │              │  risk check  │              │                    │
  │ Error map   │ Full + chaos │ Full + chaos │ Full         │ Critical paths     │
  │             │  scenarios   │ for accepted │              │  only              │
  │ CEO plan    │ Written      │ Written      │ Skipped      │ Skipped            │
  │ Phase 2/3   │ Map accepted │ Map accepted │ Note it      │ Skip               │
  │ planning    │              │ cherry-picks │              │                    │
  │ Design      │ "Inevitable" │ If UI scope  │ If UI scope  │ Skip               │
  │ (Sec 11)    │  UI review   │  detected    │  detected    │                    │
  └─────────────┴──────────────┴──────────────┴──────────────┴────────────────────┘
```
