#!/usr/bin/env python3
"""Copy files selected by a repository's `.worktreeinclude` file."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy files selected by `.worktreeinclude` into a worktree."
    )
    parser.add_argument(
        "destination",
        type=Path,
        help="Path to an existing destination worktree",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        help="Source checkout root; defaults to the current Git checkout",
    )
    return parser.parse_args()


def git_root(source_root: Path | None) -> Path:
    command = ["git"]
    if source_root is not None:
        command.extend(["-C", os.fspath(source_root)])
    command.extend(["rev-parse", "--show-toplevel"])
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        message = getattr(error, "stderr", "") or str(error)
        raise RuntimeError(f"cannot determine Git source root: {message.strip()}") from error
    return Path(result.stdout.strip()).resolve()


def git_common_dir(worktree_root: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(worktree_root), "rev-parse", "--git-common-dir"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        message = getattr(error, "stderr", "") or str(error)
        raise RuntimeError(
            f"cannot determine Git common directory for {worktree_root}: {message.strip()}"
        ) from error
    common_dir = Path(result.stdout.strip())
    return (
        worktree_root / common_dir if not common_dir.is_absolute() else common_dir
    ).resolve()


def worktree_roots(source_root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(source_root), "worktree", "list", "--porcelain"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        message = getattr(error, "stderr", "") or str(error)
        raise RuntimeError(f"cannot list Git worktrees: {message.strip()}") from error

    roots = []
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            roots.append(Path(line.removeprefix("worktree ")).resolve())
    return roots


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def validate_worktree_relationships(source_root: Path, target_root: Path) -> None:
    if source_root == target_root:
        raise RuntimeError("source checkout and destination worktree must differ")

    source_common_dir = git_common_dir(source_root)
    target_common_dir = git_common_dir(target_root)
    if source_common_dir != target_common_dir:
        raise RuntimeError(
            "source and destination must belong to the same Git repository"
        )

    if is_within(source_root, target_root):
        raise RuntimeError("source worktree cannot be inside destination worktree")

    for existing_root in worktree_roots(source_root):
        if existing_root in (source_root, target_root):
            continue
        if is_within(target_root, existing_root) or is_within(
            existing_root, target_root
        ):
            raise RuntimeError(
                "destination worktree cannot be nested within another existing worktree"
            )


def selected_paths(source_root: Path, include_file: Path) -> list[Path]:
    command = [
        "git",
        "-C",
        os.fspath(source_root),
        "ls-files",
        "--others",
        "--ignored",
        "--full-name",
        "--exclude-from",
        os.fspath(include_file),
        "-z",
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        message = getattr(error, "stderr", b"")
        if isinstance(message, bytes):
            message = os.fsdecode(message)
        raise RuntimeError(
            f"cannot read matches from `.worktreeinclude`: {message.strip()}"
        ) from error
    return [Path(os.fsdecode(path)) for path in result.stdout.split(b"\0") if path]


def is_git_internal_path(relative_path: Path) -> bool:
    return ".git" in relative_path.parts


def copy_path(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        os.symlink(os.readlink(source), destination)
    elif source.is_file():
        shutil.copy2(source, destination)
    else:
        raise OSError("source is neither a regular file nor a symbolic link")


def main() -> int:
    args = parse_args()
    try:
        source_root = git_root(args.source_root.resolve() if args.source_root else None)
        target_root = git_root(args.destination.resolve())
        validate_worktree_relationships(source_root, target_root)
    except (AttributeError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    include_file = source_root / ".worktreeinclude"
    if not include_file.is_file():
        return 0

    try:
        paths = selected_paths(source_root, include_file)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    had_errors = False
    for relative_path in paths:
        if is_git_internal_path(relative_path):
            continue

        source_path = source_root / relative_path
        destination_path = target_root / relative_path
        if os.path.lexists(destination_path):
            print(f"warning: skipped existing path: {relative_path}", file=sys.stderr)
            continue

        try:
            copy_path(source_path, destination_path)
        except OSError as error:
            had_errors = True
            print(f"error: failed to copy {relative_path}: {error}", file=sys.stderr)

    return 1 if had_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
