---
name: orca-handoff
description: >-
  Perform a full ownership handoff to another agent through Orca. Defines the
  handoff contract and task brief, then routes workspace and terminal mechanics
  to Orca's version-matched `orca-cli` guide. Use for handoff, hand off,
  handover, delegation, or giving work to another agent without supervision. Do
  not use when the user asks to monitor completion, wait for results, coordinate
  multiple workers, or manage ask/reply flows.
---

# Orca handoff

A full handoff transfers complete ownership to another agent. This skill defines the ownership contract and task brief; Orca's version-matched `orca-cli` guide owns the commands, receipt fields, compatibility rules, and recovery mechanics.

## Outcome

**Result:** one receiving agent owns the handed-off task in the requested Orca context. **Next consumer:** that receiving agent. **Done:** the applicable `orca-cli` handoff flow reports that the prompt was accepted, the receiving context and agent handle are reported to the user, and the sending agent ends its turn without monitoring completion.

**Safe failure:** follow the loaded `orca-cli` guide's exact receipt and recovery rules. Never claim transfer without accepted input, resend merely because the receiving agent is silent, or continue the handed-off task after a failed handoff without a new user decision.

## Classify the role

| Current context | Role | Route |
| --- | --- | --- |
| The current prompt contains a live injected preamble with Task and Dispatch IDs | Dispatched worker | Follow the preamble; do not start an unsupervised full handoff |
| The user asks to supervise, monitor, wait for results, track completion, coordinate a DAG, or manage ask/reply | Coordinator | Use `orchestration`, not this skill |
| The user asks to hand off ownership or start another agent or workspace without supervision | Handoff owner | Use the canonical handoff below |
| No live preamble and no explicit handoff | Ordinary terminal agent | Do not transfer ownership |

Model or effort selection does not make a handoff supervised.

## Authority and safety floor

- A full handoff creates no orchestration Run, Task, or Dispatch. Never substitute orchestration commands or a non-Orca subagent tool.
- Folder workspaces are valid. Never require Git or assume that the receiving context is a worktree.
- Preserve the user's requested context, placement, agent, model, and effort. If the request, current context, and loaded guide do not supply a choice, ask before creating anything.

## Canonical handoff

`ORCA` is a placeholder for the executable selected for the current Orca environment. Substitute it before running commands, use that same executable for the full handoff, and never run `ORCA` literally.

Load the installed version's guide and confirm the runtime:

```text
ORCA skills get orca-cli
ORCA status --json
```

If status reports that Orca is not running:

```text
ORCA open --json
ORCA status --json
```

Any other status failure is blocking. Report it and stop.

Follow the loaded guide's **Full Handoffs** section and any applicable **Worktrees** or **Terminals** rules. Use the route that matches the actual context and user request.

Do not copy commands or result-field assumptions from another Orca version. Use the loaded guide and that version's `--help` when the guide directs it.

## Task-brief contract

The brief sent through `orca-cli` must be self-contained and name:

- **Target:** the files, component, environment, or problem in scope.
- **Change:** the concrete result to produce.
- **Current state:** relevant decisions, completed work, modified files, workspace or branch context, and known failures.
- **Constraints:** invariants, compatibility requirements, and do-not-touch boundaries.
- **Ownership:** that the receiving agent now owns execution and may make the stated edits and decisions.
- **Observable acceptance:** the test, output, or evidence that proves the task is complete.

Include exact paths, commands, identifiers, and user decisions when known. Do not tell the receiving agent to consult the sending agent or wait for coordinator approval; that would no longer be a full handoff.

## Completion accounting

Use the actual fields returned by the loaded `orca-cli` flow rather than hardcoding a version-specific result path or workspace type. Report the receiving context identity, the receiving agent or terminal handle, and that the prompt was accepted.

After that report, end the turn. If the handoff was not accepted, report the exact state and error returned by Orca plus any context or terminal that the receipt says remains. Preserve uncertain state and wait for the user's next decision.
