---
name: git-worktrees
description: Establish or reuse an isolated Git worktree for new work or a named branch, PR, tag, or commit. Use whenever the user asks to create or enter a worktree or separate Git checkout, wants parallel work without disturbing the current checkout, or another workflow requires Git checkout isolation.
---

# Git Worktrees

## Overview

Keep work isolated without disturbing the user's primary checkout. Isolation often already exists because a coding harness created it before the session began, so detect before creating anything.

This file owns the common workflow: **choose the mode -> detect existing isolation -> either reuse and finish here, or route once and finish in the selected environment document.**

## Operating contract

- Read exactly one environment document in Step 2. It owns creation through termination; do not return here or switch mechanisms automatically.
- Never nest a worktree or check out one branch in two worktrees. Report the owning path instead of forcing Git.
- Never fall back to the current checkout after isolation fails without explicit user approval.

## Result contract

Every terminal path reports:

```text
Workspace: <absolute-path | not created>
Mode: <new work | existing ref>
State: <branch-name | detached HEAD at commit | unavailable>
Source: <existing isolation | Claude Code | native harness | git>
Status: <ready | blocked: concise reason>
```

When blocked, quote the shortest decisive error and state the exact user decision needed. Do not claim readiness or silently continue in a different checkout.

## Step 0: Choose the mode

Choose from the caller's request:

- **New work (default):** no specific ref was named. Create a fresh branch from the requested base, or from the environment workflow's default base when none was named.
- **Existing ref:** the caller named a branch, PR, tag, or commit. Isolate that ref. Attach to an available local branch; use detached mode when the target cannot or should not own a branch in this worktree.

Mode changes what gets checked out. Detection, routing, and reporting stay the same.

## Step 1: Detect existing isolation

Resolve both Git directories to absolute paths before comparing them. Raw `git rev-parse` output may mix absolute and relative forms when invoked from a subdirectory.

```bash
git rev-parse --absolute-git-dir
(cd "$(git rev-parse --git-common-dir)" && pwd -P)
```

- **Paths equal:** current checkout is normal. Continue to Step 2.
- **Paths differ:** current checkout is either a linked worktree or a submodule. Distinguish them:

```bash
git rev-parse --show-superproject-working-tree
```

- **Non-empty output:** current checkout is a submodule. Treat it as normal and continue to Step 2.
- **Empty output:** isolation already exists. Reuse the current worktree and skip Step 2.

When reusing existing isolation, record its path and state. In new-work mode, continue there. In existing-ref mode, align this worktree to the requested ref unless it is already aligned. If another worktree owns the requested branch, report blocked with that path, request the caller's choice, and stop.

Verify the reused workspace:

```bash
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
```

Report with source `existing isolation` and stop. Do not continue to Step 2.

## Step 2: Route to one creation workflow

Route only when Step 1 found a normal checkout. Read one document fully and follow it through its terminal report:

- **Claude Code with `EnterWorktree`:** read [`claude-code.md`](claude-code.md).
- **Another harness with a native worktree tool:** read [`harness-native.md`](harness-native.md).
- **No native worktree tool:** read [`git-only.md`](git-only.md).

Do not load the other documents or return to this file.
