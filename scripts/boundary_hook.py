#!/usr/bin/env python3
"""PreToolUse hook: refuse a write into a Wurzel or Grundlage that lies inside the plugin repository.

Spec: lokale-struktur LS-2.4, konventionen R-9.9. The skills state the rule and the scripts refuse such a
Wurzel; this hook enforces it for the file tools of Claude Code (Write, Edit, MultiEdit, NotebookEdit), so
personal data cannot land in the plugin checkout even when the model skips the check.

Input: the hook JSON on stdin (`cwd`, `tool_name`, `tool_input` with `file_path` or `notebook_path`).
Active only when the Anker `job-application/konfiguration.md` exists in `cwd`; without it the hook has no
Wurzel to protect and exits 0. Exit 2 blocks the tool call and the message on stderr reaches the model.
Anything the hook cannot read (no JSON, no path) lets the call pass: a broken hook must not stop every
write of every session.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grundlage_hash import DEFAULT_GRUNDLAGE, DEFAULT_WURZEL, inside_plugin_repo, read_frontmatter  # noqa: E402

ANKER = os.path.join(DEFAULT_WURZEL, "konfiguration.md")


def protected_roots(cwd):
    """The Wurzel, the Grundlage and the index note as absolute paths, resolved against `cwd` (LS-2.6)."""
    config = read_frontmatter(os.path.join(cwd, ANKER))
    wurzel = os.path.normpath(os.path.join(cwd, config.get("wurzel") or DEFAULT_WURZEL))
    grundlage = config.get("grundlage")
    grundlage = os.path.normpath(os.path.join(cwd, grundlage)) if grundlage else os.path.join(wurzel, DEFAULT_GRUNDLAGE)
    roots = [wurzel, grundlage]
    if config.get("grundlage_index"):
        roots.append(os.path.normpath(os.path.join(cwd, config["grundlage_index"])))
    return roots


def is_within(target, root):
    root_dir = root if os.path.isdir(root) else os.path.dirname(root)
    try:
        return target == root or os.path.commonpath([target, root_dir]) == root_dir
    except ValueError:  # different drives on Windows
        return False


def decide(event):
    """Return the refusal message, or None when the call may pass."""
    cwd = event.get("cwd") or os.getcwd()
    if not os.path.isfile(os.path.join(cwd, ANKER)):
        return None
    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return None
    target = os.path.normpath(os.path.join(cwd, path))
    for root in protected_roots(cwd):
        if is_within(target, root) and inside_plugin_repo(root):
            return (
                f"Schreibzugriff abgelehnt (LS-2.4, R-9.9): {path} liegt in einer Wurzel oder Datengrundlage "
                f"innerhalb des Plugin-Repositorys ({root}). Lege Wurzel und Grundlage außerhalb ab und trage die "
                "Pfade in job-application/konfiguration.md (`wurzel`, `grundlage`) ein."
            )
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        print("boundary_hook: no JSON on stdin, call passes", file=sys.stderr)
        return 0
    if not isinstance(event, dict):
        return 0
    message = decide(event)
    if message:
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
