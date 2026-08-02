# Git-only workflow

Use only when the router found no harness-native worktree tool. This document owns manual creation through terminal reporting.

## 1. Run from the repository root

The `.worktrees/` and `.gitignore` paths below are repository-root-relative. The skill may start from a subdirectory, so move to the root first:

```bash
cd "$(git rev-parse --show-toplevel)"
```

Without this, `.worktrees/<branch>` and `.gitignore` edits may land in a subdirectory such as `src/.worktrees/` or `src/.gitignore`.

## 2. Choose the branch name and base branch

Use a meaningful branch name from the work description, such as `feat/login` or `fix/email-validation`. Avoid opaque auto-generated names. Use the origin's default branch when available; otherwise use `main`.

## 3. Ensure `.worktrees/` is gitignored before creating anything

```bash
git check-ignore -q .worktrees/
```

Use the trailing slash. It honors an existing directory-only `.worktrees/` rule even before the directory exists. If the path is not ignored, add a `.worktrees/` line to `.gitignore`.

## 4. Refresh the base branch when possible

```bash
git fetch origin <from-branch>
```

This is non-fatal. If it fails because there is no `origin` remote, the remote has another name, or the branch is local-only, continue with the local ref.

## 5. Create the worktree

**New work:** Create a new branch from the base:

```bash
git worktree add -b <branch-name> .worktrees/<branch-name> origin/<from-branch>
```

Use the local `<from-branch>` ref if `origin/<from-branch>` does not exist. This creates a new branch from the base.

**Isolate an existing branch or tag:** Attach the worktree to the target ref:

```bash
git worktree add .worktrees/<slug> <target-ref>
```

**Isolate a PR:** Fetch its head ref into a local branch, then attach the worktree to that branch:

```bash
git fetch origin pull/<n>/head:pr-<n>
git worktree add .worktrees/pr-<n> pr-<n>
```

Never use a detached `FETCH_HEAD`; that orphans the fix loop's commits instead of updating the PR.

If Git reports that a branch is already checked out elsewhere, do not retry with force. Git includes the existing worktree path in the error. Report that path and ask whether to work there or create a detached worktree at the target commit.

## 6. Copy `.worktreeinclude` files into the new worktree

Run this from the source checkout while the new worktree still exists:

```bash
python <skill-root>/scripts/copy_worktreeinclude.py \
  --source-root "$(git rev-parse --show-toplevel)" \
  .worktrees/<branch-name>
```

Use `.worktrees/<slug>` or `.worktrees/pr-<n>` for other modes. Preserve all warning and error output.

## 7. Switch into the new worktree

```bash
cd .worktrees/<branch-name>
```

Use the corresponding `<slug>` or `pr-<n>` path for other modes.

If `git worktree add` fails with a sandbox or permission error, the requested isolation could not be created. This needs a blocking user decision before touching the current checkout; do not silently continue there. Report the failure and ask via the platform's blocking question tool:

- `AskUserQuestion` in Claude Code. Call `ToolSearch` with `select:AskUserQuestion` first if its schema is not loaded.
- `request_user_input` in Codex.
- `ask_question` in Antigravity CLI (`agy`).
- `ask_user` in Pi through the `pi-ask-user` extension.

Offer options such as working in the current checkout or stopping to resolve the permission issue. If no blocking tool exists or the call errors, present numbered options in chat and wait for the reply. Never skip confirmation, retry alternative paths automatically, or work in the current checkout without explicit confirmation.

## 8. Verify the result

Inside the created worktree, verify the final location and Git state:

```bash
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
```

Confirm the path and requested branch or target commit match.

## 9. Install dependencies when the package manager is clear

Ask if ambiguous. Skip only if the user asked to skip or no dependency files exist.

```bash
# Node.js
if [ -f package.json ] && [ -f pnpm-lock.yaml ]; then pnpm install --frozen-lockfile;
elif [ -f package.json ] && [ -f yarn.lock ] && [ -f .yarnrc.yml ]; then yarn install --immutable;
elif [ -f package.json ] && [ -f yarn.lock ]; then yarn install --frozen-lockfile;
elif [ -f package.json ] && [ -f package-lock.json ]; then npm ci;
elif [ -f package.json ]; then npm install;
fi

# Python
if [ -f pyproject.toml ] && [ -f uv.lock ]; then uv sync;
elif [ -f requirements.txt ] && [ -f uv.lock ]; then uv pip sync requirements.txt;
elif [ -f pyproject.toml ] && [ -f poetry.lock ]; then poetry install;
elif [ -f requirements.txt ]; then pip install -r requirements.txt;
fi

# Dart or Flutter
if [ -f pubspec.yaml ] && grep -Eq '^[[:space:]]*flutter:|^[[:space:]]*sdk:[[:space:]]*["'\"']?flutter["'\"']?[[:space:]]*$' pubspec.yaml; then flutter pub get;
elif [ -f pubspec.yaml ]; then dart pub get;
fi

# Rust
if [ -f Cargo.toml ]; then cargo build;
fi

# Go
if [ -f go.mod ]; then go mod download;
fi
```

## 10. Report and stop

Report with source `git`, then stop. On failure, preserve current state and request the required decision; do not switch workflows.

## Reference: other worktree operations

Use `git` directly — no wrapper is needed:

```bash
git worktree list                          # list worktrees
git worktree remove .worktrees/<branch>    # remove a worktree
cd .worktrees/<branch>                     # switch to a worktree
cd "$(git rev-parse --show-toplevel)"      # return to the current checkout root
```

## Reference: troubleshooting

**"Worktree already exists"**: The path is in use. Switch to it:

```bash
cd .worktrees/<branch>
```

Or remove it:

```bash
git worktree remove .worktrees/<branch>
```

**"Cannot remove worktree: it is the current worktree"**: Change directories out of the worktree, then remove it.
