#!/usr/bin/env python3
"""
Workspace snapshot and diff helpers for edit-scope audits.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import hashlib
from pathlib import Path

# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------


# ----------------- Module-level Configuration -----------------


def snapshot_workspace(root: Path) -> dict[str, str]:
    """Return path -> sha256 for all regular files under a workspace root."""
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            relative_path = path.relative_to(root).as_posix()
            snapshot[relative_path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def diff_workspace(
    before: dict[str, str],
    after: dict[str, str],
) -> list[str]:
    """Return added, removed, or modified paths between two snapshots."""
    changed: list[str] = []
    for path in sorted(set(before) | set(after)):
        if before.get(path) != after.get(path):
            changed.append(path)
    return changed
