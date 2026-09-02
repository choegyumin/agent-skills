---
name: to-idea
description: Turn the current conversation into an idea document — no interview, just synthesis of what you've already discussed.
disable-model-invocation: true
---

Present the idea/design document in the conversation through an available office-hours-style skill (e.g. `yc-office-hours`). If the environment supports writing files, you may also save it to the project or workspace. This is the primary deliverable of the session.

Do not invent details or scores missing from the current conversation.

### Idea doc template:

```markdown
# Idea: {title}

Generated on {date}
Status: DRAFT

## Problem Statement

{the core problem in the founder's own words. Place it on the Problem Size x Frequency Matrix or test it against another relevant framework}

## Tarpit Check

{if the idea matches a pattern (group payments/bill splitting, social-for-X, unfocused AI chatbot, marketplace with no supply plan, behavior-change consumer app, "Uber for X" at low frequency, resume/job-match), name the tarpit and why it fails. If no match: "No known tarpit match"}

## Demand Evidence

{answer "How do you know they want this?" with specific quotes, numbers, and behaviors. Waitlists, signups, and "interest" do NOT count}

## Status Quo

{answer "What are they doing today without you?" with the concrete current workflow users live with today: tools duct-taped together, hours/money wasted, manual workarounds}

## Target User & Narrowest Wedge

{the specific human (name, title, what gets them fired) and the smallest version someone would pay for this week. Answer "Who is it for REALLY?" and consider the "minimum version that delivers value", a "Google Sheets + phone + email" version, or the "jankiest MVP you could ship this week"}

## Constraints

{the user's role, stage (pre-idea / pre-launch / post-launch / scaling), industry, and resources (team, budget, timeline)}

## Premises

{the 3-5 premises the founder agreed to, one per line. Note which premises drew evidence-based pushback and which were accepted without challenge}

## Approaches Considered

### Approach A: {name}

{the MINIMAL VIABLE approach (fastest path to learning/validation). Fields: Summary, Effort [S/M/L/XL], Risk [Low/Med/High], Key advantage, Key risk}

### Approach B: {name}

{the IDEAL EXECUTION approach (best long-term outcome). Same fields. Add an Approach C (creative/lateral) only if a meaningfully different path exists}

## Recommended Approach

{state the recommendation and a one-line reason}

## Verdict

{the direct assessment, do not soften. One of: PROCEED (evidence supports it, execute) / TEST FIRST (promising but unvalidated, the action plan IS the validation) / PIVOT (core assumption flawed, explore alternatives) / KILL (no demand, no unique insight, no founder-market fit). Ground it in explicit decision criteria and any 0-10 founder-signal score already established in the conversation}

## Open Questions

{any unresolved questions from the office hours}

## Success Criteria

{measurable criteria: the ONE number that matters most right now plus the relevant success metric}

## Distribution Plan

{how users get the deliverable and how they find out about it; include the manual/personal-outreach channel before any paid one}
{omit this section if the deliverable is a web service with existing distribution}

## Campaign Score

{for a marketing campaign, rate 1-10 each: Message Clarity, Audience Fit, Channel Strategy, CTA Strength, Differentiation. State the average and band: 8-10 ship / 6-7 revise weak dimensions / 4-5 rework the weakest first / 1-3 start over. Omit otherwise}

## Dependencies

{blockers, prerequisites, related work}

## The Assignment

{ONE concrete real-world action, not "go build it": possible to complete within 7 days, measurable, and uncomfortable}
```
