#!/usr/bin/env python3
"""Compute the Datengrundlage hash and stand (spec R-9.1, R-9.5, R-9.10, LS-2.5).

Usage: grundlage_hash.py [konfiguration.md]

Reads the frontmatter keys `wurzel`, `grundlage` and `grundlage_index` from the
konfiguration file (default: job-application/konfiguration.md, relative to the
working directory). A missing file or key falls back to the defaults of R-9.10.

Prints a JSON object with `modus`, `grundlage`, `dateien`, `hash` and `stand`.
Exits 1 with a `Blocker:` line on stderr when the Grundlage cannot be hashed.
Standard library only.
"""

import argparse
import hashlib
import json
import os
import re
import sys

PLUGIN_NAME = "job-application"
DEFAULT_WURZEL = "job-application"
DEFAULT_GRUNDLAGE = os.path.join("grundlage", "lebenslauf-chronologisch.md")


class Blocker(Exception):
    pass


def read_frontmatter(path):
    """Return the simple `key: value` pairs of a file's YAML frontmatter."""
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.S)
    data = {}
    if match:
        for line in match.group(1).splitlines():
            pair = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
            if pair:
                data[pair.group(1)] = pair.group(2).strip("\"'")
    return data


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def inside_plugin_repo(path):
    """True when `path` or an ancestor directory is this plugin's repository (R-9.9, LS-2.4).

    A directory is checked itself first (LS-2.4: "including the directory itself"); a file starts at its folder.
    """
    directory = os.path.abspath(path)
    if not os.path.isdir(directory):
        directory = os.path.dirname(directory)
    while True:
        manifest = os.path.join(directory, ".claude-plugin", "plugin.json")
        if os.path.isfile(manifest):
            try:
                with open(manifest, encoding="utf-8") as handle:
                    if json.load(handle).get("name") == PLUGIN_NAME:
                        return True
            except (OSError, ValueError):
                pass
        parent = os.path.dirname(directory)
        if parent == directory:
            return False
        directory = parent


def resolve(path):
    return os.path.normpath(os.path.abspath(path))


def directory_entries(directory, index):
    """Map real path -> hash label for every note of a directory Grundlage.

    Labels are `file:<relpath>` for notes below the directory and `index:<name>`
    for an index file outside it. Hidden entries and non-Markdown files are skipped.
    """
    entries = {}
    for root, dirs, names in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in names:
            if name.startswith(".") or not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            relpath = os.path.relpath(path, directory).replace(os.sep, "/")
            entries[os.path.realpath(path)] = "file:" + relpath
    index_real = os.path.realpath(index)
    if index_real not in entries:
        entries[index_real] = "index:" + os.path.basename(index)
    return entries


def compute(konfiguration):
    config = read_frontmatter(konfiguration)
    wurzel = resolve(config.get("wurzel") or DEFAULT_WURZEL)
    if config.get("grundlage"):
        grundlage = resolve(config["grundlage"])
    else:
        grundlage = os.path.join(wurzel, DEFAULT_GRUNDLAGE)
    if inside_plugin_repo(grundlage):
        raise Blocker(
            f"Grundlage liegt im Plugin-Repository ({grundlage}). "
            "Pfad in job-application/konfiguration.md (Schlüssel `grundlage`) außerhalb ablegen (R-9.9)."
        )

    index_value = config.get("grundlage_index")
    if os.path.isfile(grundlage):
        if index_value and resolve(index_value) != grundlage:
            raise Blocker("`grundlage_index` ist nur bei einem Verzeichnis als `grundlage` erlaubt (R-9.10).")
        modus = "datei"
        stand_file = grundlage
        digest = sha256_file(grundlage)
        dateien = 1
    elif os.path.isdir(grundlage):
        if not index_value:
            raise Blocker("Verzeichnis als Grundlage, aber `grundlage_index` fehlt in konfiguration.md (R-9.10).")
        index = resolve(index_value)
        if not os.path.isfile(index):
            raise Blocker(f"Index der Grundlage nicht gefunden: {index}")
        entries = directory_entries(grundlage, index)
        lines = [f"{label}\n{sha256_file(real)}\n" for real, label in entries.items()]
        lines.sort(key=lambda line: line.split("\n", 1)[0])
        digest = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
        modus = "verzeichnis"
        stand_file = index
        dateien = len(entries)
    else:
        raise Blocker(f"Grundlage nicht gefunden: {grundlage}")

    stand = read_frontmatter(stand_file).get("stand")
    if not stand or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stand):
        raise Blocker(f"Frontmatter `stand: JJJJ-MM-DD` fehlt oder ist ungültig in {stand_file} (R-9.5).")

    return {
        "modus": modus,
        "grundlage": grundlage,
        "dateien": dateien,
        "hash": digest,
        "stand": stand,
    }


def main():
    parser = argparse.ArgumentParser(description="Hash and stand of the Datengrundlage (R-9.5).")
    parser.add_argument(
        "konfiguration",
        nargs="?",
        default=os.path.join(DEFAULT_WURZEL, "konfiguration.md"),
        help="path to job-application/konfiguration.md",
    )
    args = parser.parse_args()
    try:
        result = compute(args.konfiguration)
    except Blocker as error:
        print(f"Blocker: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
