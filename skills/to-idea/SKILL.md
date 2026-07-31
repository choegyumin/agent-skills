---
name: to-idea
description: Turn the current conversation into an idea document — no interview, just synthesis of what you've already discussed.
disable-model-invocation: true
---

Present the idea/design document in the conversation with `office-hours`. If the environment supports writing files, you may also save it to the project or workspace. This is the primary deliverable of the session.

### Idea doc template:

```markdown
# Idea: {title}

Generated on {date}
Status: DRAFT

## Problem Statement

{from Step 3 Depth Ladder + Step 4 Deep Dive — the core problem in the founder's own words. For IDEA mode, place it on the Problem Size x Frequency Matrix; otherwise test it against the mode-specific frameworks}

## Tarpit Check

{from evaluation-rubric Known Tarpits — if the idea matches a pattern (group payments/bill splitting, social-for-X, unfocused AI chatbot, marketplace with no supply plan, behavior-change consumer app, "Uber for X" at low frequency, resume/job-match), name the tarpit and why it fails. If no match: "No known tarpit match"}

## Demand Evidence

{from Step 3 "How do you know they want this?" + Step 4 question-bank Evidence & Validation — specific quotes, numbers, behaviors. Waitlists, signups, and "interest" do NOT count}

## Status Quo

{from Step 3 "What are they doing today without you?" — the concrete current workflow users live with today: tools duct-taped together, hours/money wasted, manual workarounds}

## Target User & Narrowest Wedge

{from Step 3 "Who is it for REALLY?" + question-bank IDEA Pre-Launch questions ("minimum version that delivers value", "Google Sheets + phone + email", "jankiest MVP you could ship this week") — the specific human (name, title, what gets them fired) and the smallest version someone would pay for this week}

## Constraints

{from Step 1 Context Gathering — the user's role, stage (pre-idea / pre-launch / post-launch / scaling), industry, and resources (team, budget, timeline)}

## Premises

{from Step 5 Premise Challenge — the 3-5 premises the founder agreed to, one per line. Note any premise that drew evidence-based pushback vs. compliance}

## Approaches Considered

### Approach A: {name}

{from Step 6B Alternatives — the MINIMAL VIABLE approach (fastest path to learning/validation). Fields: Summary, Effort [S/M/L/XL], Risk [Low/Med/High], Key advantage, Key risk}

### Approach B: {name}

{from Step 6B Alternatives — the IDEAL EXECUTION approach (best long-term outcome). Same fields. Add an Approach C (creative/lateral) only if a meaningfully different path exists}

## Recommended Approach

{the approach selected in Step 6B — state the recommendation and a one-line reason}

## Verdict

{from Step 8 — the direct assessment, do not soften. One of: PROCEED (evidence supports it, execute) / TEST FIRST (promising but unvalidated, the action plan IS the validation) / PIVOT (core assumption flawed, explore alternatives) / KILL (no demand, no unique insight, no founder-market fit). Ground it in the Step 6A Founder Signal Scorecard score (0-10) and the Verdict Decision Tree}

## Open Questions

{any unresolved questions from the office hours}

## Success Criteria

{measurable criteria surfaced in Step 4 — the ONE number that matters most right now (question-bank Focus & Priority) plus the mode-specific success metric}

## Distribution Plan

{from CAMPAIGN Channel & Distribution / GROWTH Go-To-Market questions — how users get the deliverable and how they find out about it; include the manual/personal-outreach channel before any paid one}
{omit this section if the deliverable is a web service with existing distribution}

## Campaign Score

{CAMPAIGN mode only — from evaluation-rubric Marketing Campaign Scorecard. Rate 1-10 each: Message Clarity, Audience Fit, Channel Strategy, CTA Strength, Differentiation. State the average and band: 8-10 ship / 6-7 revise weak dims / 4-5 rework weakest first / 1-3 start over. Omit in IDEA/GROWTH mode}

## Dependencies

{blockers, prerequisites, related work}

## The Assignment

{from Step 7 Action Plan + question-bank Action Templates (mode-specific) — ONE concrete real-world action, not "go build it": completable within 7 days, measurable, and uncomfortable}
```
