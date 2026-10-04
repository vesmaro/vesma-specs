#!/usr/bin/env python3
"""Contract breaking-change detector — STUB (ratified as phase 0,
founding ArchCom 2026-10-04).

Compares every ``specs/**/*.schema.json`` at HEAD against the same
repository paths in a baseline git ref:

  * ``--baseline <ref>`` when given;
  * otherwise the newest tag (``git describe --tags --abbrev=0``);
  * with no tags, the repository root commit(s);
  * if the baseline snapshot contains no ``*.schema.json``, this is a
    silent no-op: "no baseline yet" (exit 0).

Detected breaking changes (recursive walk over ``properties`` / ``$defs`` /
``patternProperties`` / ``items`` / ``additionalProperties`` / ``not``):

  * property removal       — a key disappears from ``properties``/``$defs``;
  * type narrowing         — the new ``type`` set is a strict subset of the
                             old one (only when BOTH sides declare ``type``);
  * enum value removal     — an old ``enum`` value is missing from the new;
  * ``required`` extension — a newly required key was not required before.

A finding counts as breaking-without-major-bump when the contract's
``<contract-dir>/spec.md`` ``version:`` major (regex ``^version: X.Y.Z``) is
unchanged between baseline and HEAD; a major bump legitimizes the change
([MAJOR] instead of [BREAK]).

Known stub limitations (documented, accepted for phase 0):
  * ``$ref`` aliases are not resolved; nodes are compared positionally;
  * an untyped old node that gains a ``type`` is NOT flagged as narrowing;
  * minimum/maxLength/pattern tightening, ``additionalProperties`` flips and
    oneOf/allOf shape changes are not detected;
  * semantic (non-schema) spec.md edits are out of scope.

Mode: REPORT by default — every finding is printed, exit code stays 0 while
the contracts are at 1.0.0-draft. Pass ``--strict`` (after the versioning
policy is ratified) to exit 1 on breaking-without-major-bump findings.

Exit codes: 0 = clean / report-only / nothing to compare;
            1 = --strict and breaking-without-major-bump findings;
            2 = infrastructure error (git failure, unparseable schema).
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

VERSION_RE = re.compile(r"(?m)^\s*version:\s*(\d+)\.(\d+)\.(\d+)")

# (key -> sub-schema) mappings compared pairwise, key by key.
MAP_KEYS = ("properties", "$defs", "patternProperties")
# Single sub-schema children compared when both sides are dict schemas.
SCHEMA_KEYS = ("items", "additionalProperties", "not")


class GitError(Exception):
    """A git command failed."""


def git(cwd, *args):
    proc = subprocess.run(("git", "-C", str(cwd), *args),
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def norm_type(value):
    """Normalize a JSON-Schema `type` to a frozenset, or None if absent."""
    if isinstance(value, str):
        return frozenset((value,))
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return frozenset(value)
    return None


def walk(old, new, path, out):
    """Collect breaking-change findings between two schema nodes."""
    if not isinstance(old, dict) or not isinstance(new, dict):
        return

    old_type, new_type = norm_type(old.get("type")), norm_type(new.get("type"))
    if old_type is not None and new_type is not None and new_type < old_type:
        out.append(f"{path}: type narrowed "
                   f"{sorted(old_type)} -> {sorted(new_type)}")

    old_enum, new_enum = old.get("enum"), new.get("enum")
    if isinstance(old_enum, list) and isinstance(new_enum, list):
        removed = [v for v in old_enum if v not in new_enum]
        if removed:
            out.append(f"{path}: enum value(s) removed: {removed!r}")

    old_req, new_req = old.get("required"), new.get("required")
    if isinstance(old_req, list) and isinstance(new_req, list):
        added = [k for k in new_req if k not in old_req]
        if added:
            out.append(f"{path}: required extended with {added!r}")

    for key in MAP_KEYS:
        old_map, new_map = old.get(key), new.get(key)
        if not (isinstance(old_map, dict) and isinstance(new_map, dict)):
            continue
        for name, old_child in old_map.items():
            child_path = f"{path}.{name}" if key == "properties" \
                else f"{path}.{key}.{name}"
            if name not in new_map:
                out.append(f"{path}: property removed: {name!r} (under {key})")
            else:
                walk(old_child, new_map[name], child_path, out)

    for key in SCHEMA_KEYS:
        old_child, new_child = old.get(key), new.get(key)
        if isinstance(old_child, dict) and isinstance(new_child, dict):
            walk(old_child, new_child, f"{path}.{key}", out)


def baseline_schemas(cwd, ref):
    """Repo-relative *.schema.json paths present in the baseline snapshot."""
    listing = git(cwd, "ls-tree", "-r", "--name-only", ref)
    return [line for line in listing.splitlines() if line.endswith(".schema.json")]


def spec_major(cwd, ref, schema_rel, read_head):
    """Major version from the contract's spec.md, or None when unknown."""
    spec_rel = str(PurePosixPath(schema_rel).parent.parent / "spec.md")
    try:
        if read_head:
            text = (cwd / spec_rel).read_text(encoding="utf-8")
        else:
            text = git(cwd, "show", f"{ref}:{spec_rel}")
    except (OSError, GitError):
        return None
    match = VERSION_RE.search(text)
    return int(match.group(1)) if match else None


def resolve_baseline(cwd, explicit):
    """Return (ref, description) or (None, reason) when no baseline exists."""
    if explicit:
        return explicit, f"explicit --baseline {explicit}"
    try:
        tag = git(cwd, "describe", "--tags", "--abbrev=0").strip()
        return tag, f"newest tag {tag}"
    except GitError:
        pass
    try:
        roots = git(cwd, "rev-list", "--max-parents=0", "HEAD").split()
    except GitError as exc:
        raise GitError(f"cannot enumerate repository root commits: {exc}")
    for ref in roots:
        if baseline_schemas(cwd, ref):
            return ref, f"repository root commit {ref[:12]} (no tags exist)"
    return None, "no tags and no root-commit schema snapshot"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Stub breaking-change detector for contract schemas "
                    "(report mode by default).")
    parser.add_argument("specs_root", nargs="?", default="specs",
                        help="path to the specs root (default: specs)")
    parser.add_argument("--baseline",
                        help="git ref to compare against (default: newest "
                             "tag, else repository root commit)")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 on breaking-without-major-bump findings")
    args = parser.parse_args(argv)

    specs_root = Path(args.specs_root).resolve()
    if not specs_root.is_dir():
        print(f"error: specs root not found: {specs_root}", file=sys.stderr)
        return 2
    try:
        cwd = Path(git(specs_root, "rev-parse", "--show-toplevel").strip())
    except GitError as exc:
        print(f"error: not a git repository: {exc}", file=sys.stderr)
        return 2

    try:
        baseline, how = resolve_baseline(cwd, args.baseline)
        if baseline is None:
            print(f"breaking-check: no baseline yet ({how}) — "
                  f"nothing to compare, exit 0")
            return 0
        base_paths = baseline_schemas(cwd, baseline)
        if not base_paths:
            print(f"breaking-check: baseline {baseline} contains no "
                  f"*.schema.json — no baseline yet, exit 0")
            return 0

        head_paths = sorted(p for p in specs_root.rglob("*.schema.json")
                            if ".git" not in p.parts)
        head_rels = {p.relative_to(cwd).as_posix() for p in head_paths}

        allowed, breaking = [], []
        for rel in base_paths:
            if rel not in head_rels:
                breaking.append(f"[BREAK]   {rel}: schema file removed")
        for path in head_paths:
            rel = path.relative_to(cwd).as_posix()
            try:
                old = json.loads(git(cwd, "show", f"{baseline}:{rel}"))
            except GitError:
                allowed.append(f"[ADDED]   {rel} "
                                f"(no baseline counterpart — not breaking)")
                continue
            try:
                new = json.loads(path.read_text(encoding="utf-8"))
            except ValueError as exc:
                print(f"error: cannot parse HEAD schema {rel}: {exc}",
                      file=sys.stderr)
                return 2
            findings = []
            walk(old, new, "$", findings)
            if not findings:
                continue
            old_major = spec_major(cwd, baseline, rel, read_head=False)
            new_major = spec_major(cwd, baseline, rel, read_head=True)
            bumped = (old_major is not None and new_major is not None
                      and new_major > old_major)
            bucket = allowed if bumped else breaking
            for finding in findings:
                tag = "[MAJOR]  " if bumped else "[BREAK]  "
                suffix = (f" (major bump {old_major} -> {new_major}: allowed)"
                          if bumped else "")
                bucket.append(f"{tag}{rel}: {finding}{suffix}")
    except GitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"breaking-check (stub): baseline = {how}")
    for line in allowed + breaking:
        print(line)
    print(f"summary: {len(allowed)} allowed/additional, "
          f"{len(breaking)} breaking-without-major-bump finding(s)")
    if args.strict:
        print("mode: strict (findings fail CI). Baseline: the latest tag.")
    else:
        print("mode: report (warning-only). Pass --strict to fail CI on "
              "breaking-without-major-bump findings.")
    if args.strict and breaking:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
