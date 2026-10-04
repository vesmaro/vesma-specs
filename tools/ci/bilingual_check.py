#!/usr/bin/env python3
"""Bilingual pairing gate for vesma-specs (bilingual pair policy,
templates/spec-template.md): every contract ships as a normative Russian
``spec.md`` plus an informative English mirror ``spec.en.md`` kept in sync
in the same change (single-commit sync).

Checks (mechanical, substring-based; no paraphrasing tolerance by design —
the sync note is a repository-wide fixed convention):

1. Every version directory ``specs/<contract>/v<N>/`` must contain
   ``spec.md`` AND its sibling mirror ``spec.en.md`` — checked in both
   directions (an orphan mirror without the Russian canonical is a
   violation too).
2. Every ``spec.en.md`` mirror must carry the ``language: en`` header
   marker and the sync note (substrings "informative English mirror" and
   "Russian text"). The normative ``spec.md`` carries no EN marker and
   none is checked — Russian is the canon.
3. ADR mirrors (``adrs/NNNN-<slug>.en.md``) are checked for pairing only,
   per the soft ADR convention: a Russian ADR ``adrs/NNNN-<slug>.md``
   requires a ``.en.md`` sibling if and only if its header block (text
   before the first ``##`` heading) declares an EN mirror ("EN mirror"
   line). An orphan ``.en.md`` mirror without the Russian counterpart is
   always a violation. ADR mirrors predate the spec front-matter
   convention and are not held to the ``language: en`` / sync-note
   substrings.

What this gate does NOT check:

- Marker pairing is not content synchrony: the gate verifies that the
  pair exists and carries the fixed markers, not that the English text
  actually matches the Russian norm. Content synchrony is enforced by
  the single-commit sync review discipline (ADR-0001 §5, the
  2026-10-05 amendment).

Exit codes: 0 = everything paired, 1 = pairing violation(s) found.
"""

import argparse
import re
import sys
from pathlib import Path

# Sync-note phrases required in every spec.en.md mirror (fixed marketing
# convention, templates/spec-template.md).
SYNC_NOTE_PHRASES = ("informative English mirror", "Russian text")
# Header language marker required in every spec.en.md mirror.
LANGUAGE_MARKER = "language: en"
# Header declaration gating the ADR mirror requirement (soft convention).
ADR_MIRROR_DECL = re.compile(r"\bEN mirror\b")
# Version-directory layout: specs/<contract>/v<N>/.
VERSION_DIR_RE = re.compile(r"v\d+")


def _read(path):
    """File text, or None when unreadable (reported by the caller)."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _header_block(text):
    """Everything before the first markdown '## ' heading (ADR header)."""
    match = re.search(r"(?m)^## ", text)
    return text if match is None else text[:match.start()]


def check_spec_dirs(root):
    """Pair spec.md <-> spec.en.md in every specs/<contract>/v<N>/ dir."""
    findings = []
    checked = 0
    version_dirs = sorted(
        d for d in (root / "specs").glob("*/*")
        if d.is_dir() and VERSION_DIR_RE.fullmatch(d.name))
    for vdir in version_dirs:
        checked += 1
        rel_dir = vdir.relative_to(root).as_posix()
        ru = vdir / "spec.md"
        en = vdir / "spec.en.md"
        if not ru.exists():
            findings.append(f"{rel_dir}: missing normative spec.md")
        if not en.exists():
            findings.append(f"missing EN mirror for {ru.relative_to(root).as_posix()}")
            continue  # no mirror file: content checks below do not apply
        text = _read(en)
        if text is None:
            findings.append(f"{en.relative_to(root).as_posix()}: unreadable")
            continue
        en_rel = en.relative_to(root).as_posix()
        if LANGUAGE_MARKER not in text:
            findings.append(f"{en_rel}: missing '{LANGUAGE_MARKER}' header marker")
        for phrase in SYNC_NOTE_PHRASES:
            if phrase not in text:
                findings.append(f"{en_rel}: missing sync-note phrase {phrase!r}")
    return checked, findings


def check_adr_mirrors(root):
    """Pair ADR files with their .en.md mirrors when a mirror is declared."""
    findings = []
    checked = 0
    adrs = root / "adrs"
    ru_files = sorted(p for p in adrs.glob("*.md")
                      if not p.name.endswith(".en.md"))
    en_leftovers = {p for p in adrs.glob("*.md") if p.name.endswith(".en.md")}

    for ru in ru_files:
        rel = ru.relative_to(root).as_posix()
        text = _read(ru)
        if text is None:
            findings.append(f"{rel}: unreadable")
            continue
        if ADR_MIRROR_DECL.search(_header_block(text)) is None:
            continue  # soft convention: no mirror declared, none required
        checked += 1
        en = ru.with_name(ru.stem + ".en.md")
        if en.exists():
            en_leftovers.discard(en)
        else:
            findings.append(f"missing EN mirror for {rel} (declared in header)")

    # An EN mirror without its Russian canonical means the canon was
    # deleted (or the mirror is misplaced) — always a violation.
    for en in sorted(en_leftovers):
        checked += 1
        findings.append(f"orphan EN mirror {en.relative_to(root).as_posix()}: "
                        f"no Russian ADR counterpart")
    return checked, findings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Bilingual pairing gate: every contract spec.md must "
                    "have its spec.en.md EN mirror (and vice versa).")
    parser.add_argument("root", nargs="?", default=".",
                        help="repository root (default: current directory)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 1
    if not (root / "specs").is_dir():
        # Fail loud: a gate that silently passes on an empty tree is a
        # silent degradation, not a green light.
        print(f"error: specs/ not found under {root}", file=sys.stderr)
        return 1

    specs_checked, spec_findings = check_spec_dirs(root)
    adrs_checked, adr_findings = check_adr_mirrors(root)
    findings = spec_findings + adr_findings

    for message in findings:
        print(f"[ERROR] {message}")
    print(f"bilingual-check: {specs_checked} contract version dir(s), "
          f"{adrs_checked} ADR mirror pair(s) checked; "
          f"{len(findings)} violation(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
