#!/usr/bin/env python3
"""Structural lint for vesma-specs: JSON Schemas, YAML artifacts, references.

Phase-0 CI gate (founding ArchCom 2026-10-04). Checks:

1. Every ``*.schema.json`` in the repository parses as JSON and is itself a
   valid JSON-Schema Draft 2020-12 document
   (``jsonschema.Draft202012Validator.check_schema``).
2. Every ``*.yaml`` / ``*.yml`` under any ``examples/`` or ``fixtures/``
   directory parses with PyYAML (``safe_load_all``; multi-document tolerant).
3. For a parsed example declaring ``config.schema_file``, the referenced
   file must exist (resolved relative to the manifest directory, per spec.md
   §3.9). ``config.schema_inline`` documents are skipped: the schema is
   embedded, there is nothing to resolve.

Severity model:
  * JSON / meta-schema / PyYAML failures            -> ERROR (exit 1);
  * unresolvable ``config.schema_file`` in examples -> WARN by default.
    Rationale: example manifests are illustrative artifacts — the referenced
    config schema belongs to the component's own distribution, not to the
    contract repository; the reference documents the field format. Pass
    ``--strict`` to escalate warnings to errors once examples ship real
    schema files (or the contract mandates their presence).

Dependencies (installed by CI): jsonschema>=4.18, PyYAML>=6.0.
Exit codes: 0 = clean (warnings allowed), 1 = errors (or warnings in --strict).
"""

import argparse
import json
import os
import sys
from pathlib import Path

import jsonschema
import yaml

# Directories whose YAML files are treated as example/fixture artifacts.
ARTIFACT_DIRS = {"examples", "fixtures"}


def _is_hidden(path, root):
    """True if any path component between root and path starts with a dot."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    return any(part.startswith(".") and part not in (".", "..") for part in rel.parts)


def lint_schemas(root):
    """Check every *.schema.json: valid JSON + valid Draft 2020-12 schema."""
    findings = []
    checked = 0
    for path in sorted(root.rglob("*.schema.json")):
        if _is_hidden(path, root):
            continue
        checked += 1
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            findings.append((path, "ERROR", f"not valid JSON: {exc}"))
            continue
        # check_schema raises SchemaError on jsonschema 3.x/4.x alike (4.x
        # raise-on-first-error, not an error iterator) — report it as one
        # finding instead of crashing with a traceback.
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
        except jsonschema.SchemaError as err:
            findings.append(
                (path, "ERROR", f"invalid JSON-Schema 2020-12: {err.message}"))
    return checked, findings


def lint_yaml_artifacts(root):
    """Parse example/fixture YAML and verify config.schema_file references."""
    findings = []
    checked = 0
    paths = sorted(set(root.rglob("*.yaml")) | set(root.rglob("*.yml")))
    for path in paths:
        if _is_hidden(path, root):
            continue
        if not any(part in ARTIFACT_DIRS for part in path.parts):
            continue
        checked += 1
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append((path, "ERROR", f"unreadable: {exc}"))
            continue
        try:
            docs = list(yaml.safe_load_all(text))
        except yaml.YAMLError as exc:
            findings.append((path, "ERROR", f"PyYAML parse failure: {exc}"))
            continue
        for index, doc in enumerate(docs):
            if doc is None:
                continue
            if not isinstance(doc, dict):
                findings.append(
                    (path, "WARN",
                     f"document #{index}: not a mapping; schema_file check skipped"))
                continue
            config = doc.get("config")
            if not isinstance(config, dict):
                continue
            reference = config.get("schema_file")
            if not isinstance(reference, str) or not reference.strip():
                continue  # absent, schema_inline-only, or non-string: out of scope
            resolved = Path(os.path.expanduser(
                os.path.normpath(path.parent / reference.strip()))).resolve()
            if resolved.exists():
                continue
            findings.append(
                (path, "WARN",
                 f"document #{index}: config.schema_file {reference!r} does not "
                 f"resolve to an existing file (expected {resolved}); ship the "
                 f"schema file or use config.schema_inline"))
    return checked, findings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Lint JSON Schemas and example/fixture YAML artifacts.")
    parser.add_argument("root", nargs="?", default=".",
                        help="repository root (default: current directory)")
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as errors (exit 1)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 1

    schemas_checked, schema_findings = lint_schemas(root)
    yaml_checked, yaml_findings = lint_yaml_artifacts(root)
    findings = schema_findings + yaml_findings

    warnings = 0
    for path, severity, message in findings:
        print(f"[{severity}] {path.relative_to(root)}: {message}")
        if severity == "WARN":
            warnings += 1
    errors = len(findings) - warnings

    print(f"schema-lint: {schemas_checked} schema file(s), {yaml_checked} "
          f"example/fixture YAML file(s) checked; "
          f"{errors} error(s), {warnings} warning(s) (strict={str(args.strict).lower()})")
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
