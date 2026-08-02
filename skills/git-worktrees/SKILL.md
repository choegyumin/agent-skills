---
name: git-worktrees
description: Set up isolated git worktrees — create a new branch for fresh work, or attach a worktree to an existing branch/PR/commit to work on it in isolation. Use when starting isolated work or isolating an existing ref; detects existing isolation first.
---

# Git Worktree

Ensure the current work happens in an isolated workspace, without disturbing the user's main checkout. Most coding harnesses now create a worktree by default at session start, so the common case is that **isolation already exists** — detect that first and do not create a redundant one.

Order of operations: **decide whether isolation is needed -> detect existing isolation -> route to exactly one environment-specific document.** Never create a worktree the harness cannot see.

**Two modes, set by the caller's need:**

- **New work (default).** No specific ref named — create a fresh branch from a base (trunk).
- **Isolate an existing ref.** The caller names a ref to work on in isolation — a PR head, an existing branch, or a commit. Attach the worktree to that ref instead of creating a new branch. One hard git rule governs this mode: **a branch can be checked out in only one worktree at a time.** If the named ref is already checked out somewhere (most commonly because it is the current branch in the primary checkout), do **not** create a second worktree for it — report that it is already checked out at `<path>` and let the caller act (work there in place; or, only if a clean separate tree is essential, create a _detached_ worktree at the same commit). Never put one branch in two worktrees.

The detection and routing steps apply to both modes; the mode only changes what gets checked out and is reported back to the caller.

## When to create a worktree

Create one (Step 1/2) only when you are **not** already isolated and you need a separate workspace:

- Reviewing a PR while keeping the current checkout free for other work
- Running multiple features in parallel without branch-switching overhead

Do not create a worktree for single-task work that can happen on a branch in the current checkout — and never when Step 0 shows you are already in one.

## Step 0: Detect existing isolation

Before creating anything, check whether the current directory is already a linked worktree. Compare the **resolved absolute** git dir against the **resolved absolute** common git dir — resolve each to an absolute path first and compare those, not the raw `git rev-parse` output. Git mixes absolute and relative forms depending on the current directory (from a subdirectory of a normal checkout, `--git-dir` comes back absolute while `--git-common-dir` may be relative), so a raw string compare yields a false "already isolated":

```bash
git rev-parse --absolute-git-dir                     # absolute git dir for this worktree
(cd "$(git rev-parse --git-common-dir)" && pwd -P)   # absolute shared (common) git dir
```

If the two absolute paths are **equal**, this is a normal checkout — continue to Step 1.

If they **differ**, you are in a linked worktree _or_ a submodule. Distinguish them:

```bash
git rev-parse --show-superproject-working-tree
```

- **Non-empty** output: you are in a submodule; treat it as a normal checkout and continue to Step 1.
- **Empty** output: you are **already in an isolated worktree**. Report the worktree path (`git rev-parse --show-toplevel`) and current branch. Do not create another worktree — creating a worktree from another worktree lands in the wrong tree and is invisible to the harness that made the current one. Then **work in place**: in new-work mode, continue here; in isolate-an-existing-ref mode, check that ref out here (unless it is already the current branch) rather than nesting a worktree.

## Step 1: Route to environment-specific instructions

When Step 0 finds a normal checkout, identify environment and read exactly one document below. Do not continue in this file or return here after reading it.

- **Claude Code:** read `claude-code.md`.
- **Other harness's native worktree tool:** read `harness-native.md`.
- **No harness-provided native worktree tool:** read `git-only.md`.
