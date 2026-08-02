# Claude Code workflow

Use only when the router selected Claude Code with `EnterWorktree`. This document owns creation through terminal reporting.

## 1. Choose the worktree mode and target

**New work:** Resolve `BASE_SHA` from the requested starting ref, or use the current `HEAD` when no ref was provided. Choose a new branch name.

**Isolate an existing ref:** Resolve `TARGET_SHA` with `git rev-parse --verify '<ref>^{commit}'`. Use the existing local branch when the target is a local branch; use detached mode for a tag, commit, or a ref that must not be attached to a branch.

For a PR identified by number, fetch its head ref into a local branch before continuing:

```bash
git fetch origin pull/<n>/head:pr-<n>
```

Treat `pr-<n>` as `TARGET_REF` and resolve `TARGET_SHA` from that local branch. If the fetch fails, stop and report the error; do not call `EnterWorktree`.

Do not rely on shell variables across separate Bash calls. Claude Code does not preserve shell state. After resolving a value, keep it in conversation context and re-declare it inside later Bash commands.

If a requested non-PR ref cannot be resolved locally, stop and ask whether to correct the ref or allow a fetch. Do not fetch it automatically.

## 2. Validate the target before creating anything

**New work:** Validate the requested branch name and confirm it does not already exist:

```bash
BRANCH='<branch-name>'
git check-ref-format --branch "$BRANCH" || exit 1
git show-ref --verify --quiet "refs/heads/$BRANCH" && exit 1
```

If invalid or already existing, stop and ask for a new branch name or an existing worktree to enter. Do not force-overwrite.

**Existing local branch:** Check whether another worktree already owns it before calling `EnterWorktree`:

```bash
TARGET_BRANCH='<branch-name>'
TARGET_WORKTREE=$(
  git worktree list --porcelain |
  awk -v branch="branch refs/heads/$TARGET_BRANCH" '
    /^worktree / { path=substr($0, 10) }
    $0 == branch { print path; exit }
  '
)
```

If `TARGET_WORKTREE` is non-empty, do not create a second worktree for that branch. Report the existing path and ask whether to work there or create a detached worktree at `TARGET_SHA`.

## 3. Create the worktree with Claude Code's native tool

```text
EnterWorktree({})
```

This creates a random worktree path and temporary branch, and processes the root `.worktreeinclude` file. Do not use `git worktree add` or `EnterWorktree({ path })` to create the worktree.

If `EnterWorktree({})` fails, stop and ask whether to retry, continue in the current checkout, or resolve the failure. Do not silently work in the current checkout.

## 4. Set the requested branch and revision inside the new worktree

**New work:** Rename the generated branch and reset it to the chosen base commit:

```bash
BRANCH='<branch-name>'
BASE_SHA='<resolved-base-sha>'
git branch --show-current
git branch -m "$BRANCH"
git reset --hard "$BASE_SHA"
```

Use `git branch -m`, not `git branch -M`, unless the user explicitly approved overwriting an existing branch name.

**Existing ref:** Switch from the generated temporary branch to the requested target, then delete only that temporary branch:

```bash
TARGET_REF='<resolved-ref>'
TARGET_SHA='<resolved-target-sha>'
TEMP_BRANCH=$(git branch --show-current)
test -n "$TEMP_BRANCH" || exit 1
```

For an available local branch, attach the worktree to that branch:

```bash
git switch "$TARGET_REF"
```

For a tag, commit, or an existing branch that must remain attached elsewhere, use detached mode:

```bash
git switch --detach "$TARGET_SHA"
```

Then delete the generated temporary branch:

```bash
git branch -D "$TEMP_BRANCH"
```

Never delete the target branch. If switching or deleting the temporary branch fails, stop and report the error.

If resetting or switching fails, the worktree is not aligned to the requested target. Stop and report the error; ask whether to remove it and create a fresh one.

## 5. Verify the result

```bash
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
```

For new work, confirm the branch equals `BRANCH` and `HEAD` equals `BASE_SHA`. For existing-ref work, confirm `HEAD` equals `TARGET_SHA` and confirm the requested branch is checked out when attached mode was selected.

## 6. Install dependencies when the package manager is clear

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

## 7. Report and stop

Report with source `Claude Code`, then stop. On failure, preserve current state and request the required decision; do not switch workflows.

## Reference: cleanup

When the user later asks to leave the worktree:

- No changes or commits need preservation:

```text
ExitWorktree({ action: "remove" })
```

- Changes or commits should be preserved:

```text
ExitWorktree({ action: "keep" })
```

Do not discard changes without explicit user approval.
