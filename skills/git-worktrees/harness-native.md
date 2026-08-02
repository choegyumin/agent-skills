# Native harness workflow

Use only when the router selected a harness-native worktree primitive, such as an `EnterWorktree` or `WorktreeCreate` tool, a `/worktree` command, or a `--worktree` flag. This document owns creation through terminal reporting.

## 1. Create with the native tool

Pass the mode and target chosen in Step 0 when the tool supports them. Let the native tool own placement, branch creation, navigation, and cleanup. Do not also run `git worktree add`; creating state behind the harness prevents it from tracking, entering, or cleaning up the workspace.

If the native tool fails, preserve its state, report blocked, and request the required decision. Do not switch to manual Git or the current checkout automatically.

## 2. Verify the result

Capture the resulting workspace path from the tool result. Inside that workspace, verify Git state:

```bash
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
```

Confirm the path and requested branch or target commit match.

## 3. Install dependencies when the package manager is clear

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

## 4. Report and stop

Report with source `native harness`, then stop. On failure, preserve current state and request the required decision; do not switch workflows.
