#!/usr/bin/env python3
"""VESMA conformance runner v0.

Validates component DECLARATIONS (YAML manifests) against a ratified contract
suite; it NEVER executes component code (ADR-0001 §4 — component code
execution is the v2 trust boundary). One suite = <spec-dir>/conformance/cases.yaml.

Usage:
    python3 tools/conformance/run.py <spec-dir> [--format=text|json]
    python3 tools/conformance/run.py --all <specs-root> [--format=text|json]

Dependencies: Python 3.9+ stdlib + `jsonschema` (JSON-Schema Draft 2020-12),
required only when a suite uses schema_valid / schema_invalid checks.
PyYAML is OPTIONAL: if importable it parses all YAML; otherwise a built-in
mini-parser (the manifest YAML subset: nested maps/lists, scalars, quotes,
comments, inline maps/lists) takes over — see MINI_YAML_NOTE.

Exit codes: 0 = all `must` cases green; 1 = at least one `must` case failed
(expect/fact mismatch of any kind); 2 = infrastructure error (suite unreadable,
schema or target missing, jsonschema missing where required, bad CLI args).
"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

try:  # optional dependency; the mini-parser below is the fallback
    import yaml as _pyyaml
except ImportError:
    _pyyaml = None

try:  # required only when a suite uses schema_valid / schema_invalid
    import jsonschema
except ImportError:
    jsonschema = None

MINI_YAML_NOTE = ("PyYAML not found: using the built-in mini YAML parser "
                  "(manifest subset). Install PyYAML for full YAML support.")
_UNSET = object()


class InfraError(Exception):
    """Runner infrastructure failure -> exit code 2."""


class YamlError(Exception):
    """Input outside the mini-parser's supported YAML subset."""


# ---------------------------------------------------------------------------
# Contract vocabulary (normative source: specs/component-manifest/v1/spec.md)
# ---------------------------------------------------------------------------

APIVERSION_RE = re.compile(r"^vesma\.component/v[0-9]+$")
NAME_RE = re.compile(r"^[a-z][a-z0-9-]{0,62}$")
DURATION_RE = re.compile(r"^[0-9]+(ms|s|m|h)$")
SPDX_RE = re.compile(r"^[A-Za-z0-9.-]+(\+[A-Za-z0-9.-]+)?$")
ANY_BRACES_RE = re.compile(r"\{[^{}]*\}")
WELL_FORMED_PLACEHOLDER_RE = re.compile(r"^\{[a-z_]+\}$")  # spec.md §6: only {token} counts
PLACEHOLDER_VALUE_RE = re.compile(r"^<[^>]*>$")  # e.g. <sha256-of-binary>, <token>
ARGV_ALLOWLIST = {"config_path", "data_dir", "runtime_dir", "venv_bin"}
TIERS = {"core", "optional"}

# spec.md §3.5: argv elements must not contain shell metacharacters or
# whitespace; no shell invocation (shell basename as argv[0], -c/-lc flags).
SHELL_META_CHARS = set("|&;<>()$`\\\"'*?")
SHELL_BASENAMES = {"sh", "bash", "dash", "ash", "zsh", "ksh", "busybox", "cmd", "powershell"}
SHELL_FLAGS = {"-c", "-lc"}

# spec.md §6 (canon): secret-like key names are rejected in launch.env.vars;
# values of ALL string scalars are scanned against the 5 secret-like patterns.
# Exemptions (§6): the `config` subtree (schema_inline carries legit patterns
# and defaults), metadata.description, metadata.provenance.artifact_sha256
# (a contract-declared hex64 hash, spec §3.3) and <placeholder> values.
# Diagnostics never print the matched values (masked).
SECRET_KEY_RE = re.compile(
    r"token|secret|password|passwd|api_key|apikey|private_key|credential", re.I)
SECRET_VALUE_PATTERNS = [
    ("openai-style key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("github PAT", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("PEM private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("long hex (>=40 chars)", re.compile(r"\b[0-9a-fA-F]{40,}\b")),
    ("long base64 (>=40 chars)", re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b")),
]
SECRET_SCAN_EXEMPT_PATHS = {
    "$.metadata.description",
    "$.metadata.provenance.artifact_sha256",
}
CANONICAL_MANIFESTS_DIR = Path(os.path.expanduser("~/.config/vesma/components.d"))

# Duration-bearing leaves per spec §3.5/3.7/3.8/3.10: section path -> leaves.
DURATION_LEAVES = {
    ("health", "http"): ("interval", "timeout"),
    ("health", "tcp"): ("interval", "timeout"),
    ("health", "exec"): ("interval", "timeout"),
    ("health", "startup"): ("grace", "interval", "timeout"),
    ("stop",): ("grace_period",),
    ("restart", "backoff"): ("base", "max", "reset_after"),
    ("restart", "window"): ("per",),
}


def _secret_scan_exempt(path):
    # spec.md §6 value-scan exemptions: the config subtree + named leaves.
    return (path in SECRET_SCAN_EXEMPT_PATHS
            or path == "$.config" or path.startswith("$.config."))


# ---------------------------------------------------------------------------
# YAML loading: PyYAML when available, else a built-in manifest-subset parser.
# ---------------------------------------------------------------------------

def _strip_comment(line):
    out, in_s, in_d = [], False, False
    for i, ch in enumerate(line):
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == "#" and not in_s and not in_d and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _split_top_level(text, sep=","):
    """Split on `sep` outside quotes/brackets (mini-parser helper)."""
    parts, buf, depth, in_s, in_d = [], [], 0, False, False
    for ch in text:
        if in_s:
            if ch == "'":
                in_s = False
        elif in_d:
            if ch == '"':
                in_d = False
        elif ch == "'":
            in_s = True
        elif ch == '"':
            in_d = True
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == sep and depth == 0:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    parts.append("".join(buf))
    return parts


def _key_split(text):
    """Return (key, rest) for 'key: value'/'key:' (colon followed by space/EOL,
    outside quotes), else None — distinguishes map entries from scalars."""
    in_s = in_d = False
    for i, ch in enumerate(text):
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == ":" and not in_s and not in_d:
            if i + 1 == len(text) or text[i + 1] in " \t":
                return text[:i].strip(), text[i + 1:].strip()
    return None


def _parse_scalar(text):
    s = text.strip()
    if s == "":
        return None
    if s[0] in "|>" and set(s) <= set("|>+-"):
        raise YamlError(f"block scalar {s!r} is outside the supported YAML subset "
                        "(install PyYAML for full YAML support)")
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1].replace("''", "'")
    if s[0] == "[" and s[-1] == "]":
        inner = s[1:-1].strip()
        return [] if not inner else [_parse_scalar(p) for p in _split_top_level(inner)]
    if s[0] == "{" and s[-1] == "}":
        inner, result = s[1:-1].strip(), {}
        if inner:
            for pair in _split_top_level(inner):
                if ":" not in pair:
                    raise YamlError(f"inline map entry without ':': {pair!r}")
                k, v = pair.split(":", 1)
                key = _parse_scalar(k) if k.strip()[:1] in "'\"" else k.strip()
                result[key] = _parse_scalar(v)
        return result
    low = s.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("null", "~"):
        return None
    for cast in (int, float):
        try:
            return cast(s)
        except ValueError:
            pass
    return s


def _mini_parse_block(lines, i, indent, source):
    if lines[i][1] == "-" or lines[i][1].startswith("- "):
        return _mini_parse_list(lines, i, indent, source)
    return _mini_parse_map(lines, i, indent, source)


def _mini_parse_map(lines, i, indent, source):
    result = {}
    while i < len(lines) and lines[i][0] == indent:
        text, lineno = lines[i][1], lines[i][2]
        if text == "-" or text.startswith("- "):
            break
        kv = _key_split(text)
        if kv is None:
            raise YamlError(f"{source}:{lineno}: expected 'key: value', got {text!r}")
        key, rest = kv
        i += 1
        if rest == "":
            if i < len(lines) and lines[i][0] > indent:
                result[key], i = _mini_parse_block(lines, i, lines[i][0], source)
            else:
                result[key] = None
        else:
            result[key] = _parse_scalar(rest)
            if i < len(lines) and lines[i][0] > indent:
                raise YamlError(f"{source}:{lines[i][2]}: unexpected indent after inline value")
    if i < len(lines) and lines[i][0] > indent:
        raise YamlError(f"{source}:{lines[i][2]}: unexpected indentation")
    return result, i


def _mini_parse_list(lines, i, indent, source):
    items = []
    while i < len(lines) and lines[i][0] == indent and (
            lines[i][1] == "-" or lines[i][1].startswith("- ")):
        text, lineno = lines[i][1], lines[i][2]
        m = re.match(r"^-(\s+)(.*)$", text)
        i += 1
        if not m or not m.group(2):
            if i < len(lines) and lines[i][0] > indent:
                value, i = _mini_parse_block(lines, i, lines[i][0], source)
            else:
                value = None
            items.append(value)
            continue
        content = m.group(2)
        if _key_split(content) is None:
            # scalar list item (subset: single line only)
            if i < len(lines) and lines[i][0] > indent:
                raise YamlError(f"{source}:{lineno}: multi-line scalar list items "
                                "are not supported")
            items.append(_parse_scalar(content))
            continue
        col = indent + 1 + len(m.group(1))
        sub = [(col, content, lineno)]
        while i < len(lines) and lines[i][0] > indent:
            sub.append(lines[i])
            i += 1
        value, consumed = _mini_parse_block(sub, 0, col, source)
        if consumed < len(sub):
            raise YamlError(f"{source}:{sub[consumed][2]}: unexpected indentation in list item")
        items.append(value)
    return items, i


def mini_yaml_loads(text, source="<mini-yaml>"):
    """Parse the manifest YAML subset (no anchors, tags, block scalars, flows)."""
    lines = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = raw.lstrip(" ")
        if raw[: len(raw) - len(stripped)].find("\t") >= 0:
            raise YamlError(f"{source}:{lineno}: tab in indentation is not supported")
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        lines.append((len(line) - len(line.lstrip(" ")), line.strip(), lineno))
    if not lines:
        return None
    value, i = _mini_parse_block(lines, 0, lines[0][0], source)
    if i < len(lines):
        raise YamlError(f"{source}:{lines[i][2]}: unexpected content (bad dedent?)")
    return value


def load_yaml(text, source="<yaml>"):
    """PyYAML when available (full YAML); otherwise the mini-parser fallback."""
    if _pyyaml is not None:
        return _pyyaml.safe_load(text)
    return mini_yaml_loads(text, source)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(doc, *keys):
    node = doc
    for k in keys:
        if not isinstance(node, dict) or k not in node:
            return None
        node = node[k]
    return node


def _walk_strings(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk_strings(v, f"{path}.{k}")
    elif isinstance(node, list):
        for idx, v in enumerate(node):
            yield from _walk_strings(v, f"{path}[{idx}]")
    elif isinstance(node, str):
        yield path, node


def _find_cycle(graph, start):
    """Return a cycle path through `start` in graph {node: [deps]}, else None."""
    stack, seen = [(start, [start])], set()
    while stack:
        node, path = stack.pop()
        for nxt in graph.get(node, ()):
            if nxt == start:
                return path + [start]
            if nxt in seen or nxt not in graph:
                continue
            seen.add(nxt)
            stack.append((nxt, path + [nxt]))
    return None


class Ctx:
    """Per-case context with suite-level caches (schema validator, dir graph)."""

    def __init__(self, spec_dir, target, schema_path, cache):
        self.spec_dir, self.target = spec_dir, target
        self.target_dir = target.parent
        self.schema_path = schema_path
        self._cache = cache
        self._validator = _UNSET

    def validator(self):
        if self._validator is _UNSET:
            if jsonschema is None:
                raise InfraError("jsonschema is not installed "
                                 "(pip install jsonschema); schema checks cannot run")
            if self.schema_path is None:
                raise InfraError(f"no schema/*.schema.json found in {self.spec_dir / 'schema'}")
            try:
                schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                raise InfraError(f"cannot load schema {self.schema_path}: {e}")
            self._validator = jsonschema.Draft202012Validator(schema)
        return self._validator

    def dir_index(self):
        """{name: [files]} and edges {name: [in-dir deps]} for the target dir."""
        key = str(self.target_dir)
        if key not in self._cache:
            names, docs = {}, {}
            for p in sorted(list(self.target_dir.glob("*.yaml")) +
                            list(self.target_dir.glob("*.yml"))):
                try:
                    d = load_yaml(p.read_text(encoding="utf-8"), str(p))
                except Exception:
                    continue  # unparseable sibling contributes no node
                name = _get(d, "metadata", "name") if isinstance(d, dict) else None
                if isinstance(name, str):
                    names.setdefault(name, []).append(p.name)
                    docs[name] = d
            graph = {}
            for name, d in docs.items():
                deps = d.get("depends_on") if isinstance(d, dict) else None
                graph[name] = [x for x in (deps or []) if isinstance(x, str) and x in names]
            self._cache[key] = (names, graph)
        return self._cache[key]


# ---------------------------------------------------------------------------
# Check vocabulary (spec.md §6). Each check returns (ok, detail); ok=True
# means the document complies with that check.
# ---------------------------------------------------------------------------

def ch_schema_valid(doc, ctx):
    errors = sorted(ctx.validator().iter_errors(doc), key=lambda e: list(e.absolute_path))
    if errors:
        e = errors[0]
        path = "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in e.absolute_path)
        more = f" (+{len(errors) - 1} more)" if len(errors) > 1 else ""
        return False, f"JSON-Schema violation at {path}: {e.message}{more}"
    return True, f"valid per {ctx.schema_path.name} (Draft 2020-12)"


def ch_schema_invalid(doc, ctx):
    """Rejected by contract validation = JSON-Schema failure OR any normative
    runner rule (spec.md §6: secret vars, env_file placement, depends_on graph
    and the other §3 rules are not expressible in JSON-Schema)."""
    reasons = []
    ok, detail = ch_schema_valid(doc, ctx)
    if not ok:
        reasons.append(f"JSON-Schema: {detail}")
    for name in NORMATIVE_CHECKS:
        cok, cdetail = run_check(name, doc, ctx)
        if not cok:
            reasons.append(f"{name}: {cdetail}")
    if reasons:
        shown = "; ".join(reasons[:6]) + (f" (+{len(reasons) - 6} more)" if len(reasons) > 6 else "")
        return False, f"rejected by contract validation: {shown}"
    return True, "accepted by contract validation (schema + normative rules)"


def ch_api_version_present(doc, ctx):
    v = doc.get("apiVersion") if isinstance(doc, dict) else None
    if not isinstance(v, str):
        return False, "apiVersion missing or not a string"
    if not APIVERSION_RE.match(v):
        return False, f"apiVersion {v!r} does not match ^vesma\\.component/v[0-9]+$"
    return True, f"apiVersion={v}"


def ch_name_kebab_unique(doc, ctx):
    name = _get(doc, "metadata", "name")
    if not isinstance(name, str) or not NAME_RE.match(name):
        return False, f"metadata.name {name!r} does not match ^[a-z][a-z0-9-]{{0,62}}$"
    names, _ = ctx.dir_index()
    dupes = [f for f in names.get(name, []) if f != ctx.target.name]
    if dupes:
        return False, (f"name {name!r} duplicated in {ctx.target_dir.name}/: "
                       f"also defined in {', '.join(dupes)}")
    return True, f"name {name!r} unique in {ctx.target_dir.name}/"


def ch_tier_enum(doc, ctx):
    tier = _get(doc, "metadata", "tier")
    if tier not in TIERS:
        return False, f"metadata.tier must be one of {sorted(TIERS)}, got {tier!r}"
    return True, f"tier={tier}"


def ch_duration_format(doc, ctx):
    bad = []
    for prefix, leaves in DURATION_LEAVES.items():
        node = _get(doc, *prefix)
        if not isinstance(node, dict):
            continue
        for leaf in leaves:
            if leaf in node and (not isinstance(node[leaf], str)
                                 or not DURATION_RE.match(node[leaf])):
                bad.append(f"{'.'.join(prefix)}.{leaf}={node[leaf]!r}")
    if bad:
        return False, "duration(s) not matching ^[0-9]+(ms|s|m|h)$: " + "; ".join(bad)
    return True, "all duration fields well-formed"


def ch_no_secret_in_vars(doc, ctx):
    hits = []
    vars_map = _get(doc, "launch", "env", "vars")
    if isinstance(vars_map, dict):
        for key in vars_map:
            if SECRET_KEY_RE.search(str(key)):
                hits.append(f"launch.env.vars key {key!r} has a secret-like name "
                            "(secrets belong in env_file)")
    for path, value in _walk_strings(doc):
        if _secret_scan_exempt(path):
            continue  # spec.md §6 exemptions: config subtree, description, artifact_sha256
        if PLACEHOLDER_VALUE_RE.match(value):
            continue  # declared placeholder convention
        for label, pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(value):
                hits.append(f"{path}: value matches secret-like pattern ({label}); value masked")
                break
    if hits:
        return False, "; ".join(hits)
    return True, "no secret-like key names or values found"


def _argv_hits(argv, where):
    if argv is None:
        return []  # section/field absent: nothing to constrain here
    hits = []
    if not isinstance(argv, list) or not all(isinstance(e, str) for e in argv):
        return [f"{where}: argv must be an array of strings"]
    for pos, el in enumerate(argv):
        bad = sorted({c for c in el if c in SHELL_META_CHARS or c.isspace()})
        if bad:
            hits.append(f"{where}[{pos}] {el!r} contains forbidden character(s) {''.join(bad)!r}")
    if argv and os.path.basename(argv[0]) in SHELL_BASENAMES:
        hits.append(f"{where}[0]: shell invocation ({os.path.basename(argv[0])}) is forbidden")
    if any(el in SHELL_FLAGS for el in argv):
        hits.append(f"{where}: shell flag -c/-lc is forbidden")
    return hits


def ch_no_shell_metacharacters(doc, ctx):
    hits = _argv_hits(_get(doc, "launch", "argv"), "launch.argv")
    hits += _argv_hits(_get(doc, "health", "exec", "argv"), "health.exec.argv")
    if hits:
        return False, "; ".join(hits)
    return True, "no shell metacharacters, whitespace or shell invocation in argv"


def _placeholder_hits(argv, where):
    hits = []
    if not isinstance(argv, list):
        return hits
    for pos, el in enumerate(argv):
        if not isinstance(el, str):
            continue
        for m in ANY_BRACES_RE.finditer(el):
            # spec.md §6: only well-formed placeholders {[a-z_]+} are flagged;
            # literal braces (e.g. {} or {a) are not placeholders — ignored
            if WELL_FORMED_PLACEHOLDER_RE.match(m.group(0)) is None:
                continue
            token = m.group(0)[1:-1]
            if token not in ARGV_ALLOWLIST:
                hits.append(f"{where}[{pos}]: placeholder {m.group(0)!r} outside allowlist")
    return hits


def ch_argv_placeholder_allowlist(doc, ctx):
    hits = _placeholder_hits(_get(doc, "launch", "argv"), "launch.argv")
    hits += _placeholder_hits(_get(doc, "health", "exec", "argv"), "health.exec.argv")
    if hits:
        return False, "; ".join(hits)
    return True, "all argv placeholders within allowlist"


def ch_checker_block_consistency(doc, ctx):
    health = doc.get("health") if isinstance(doc, dict) else None
    if health is None:
        return True, "no health section (implicit liveness)"
    if not isinstance(health, dict):
        return False, "health section must be a mapping"
    checker = health.get("checker")
    if not isinstance(checker, str):
        return False, "health.checker missing while health section is present"
    hits = []
    if checker in ("http", "tcp", "exec"):
        if not isinstance(health.get(checker), dict):
            hits.append(f"health.checker={checker} requires a health.{checker} mapping")
    elif checker == "callback":
        if not isinstance(health.get("callback"), str):
            hits.append("health.checker=callback requires a health.callback string (module:attr)")
    for block in ("http", "tcp", "exec", "callback"):
        if block != checker and block in health:
            hits.append(f"health.{block} present but health.checker={checker} "
                        "(extra probe block forbidden)")
    if checker == "callback" and doc.get("kind") != "in-process":
        hits.append(f"health.checker=callback requires kind=in-process, got {doc.get('kind')!r}")
    if hits:
        return False, "; ".join(hits)
    return True, f"checker={checker} consistent with probe blocks"


def ch_kind_launch_consistency(doc, ctx):
    kind = doc.get("kind") if isinstance(doc, dict) else None
    has_launch = isinstance(_get(doc, "launch"), dict)
    has_inproc = isinstance(_get(doc, "in_process"), dict)
    if kind == "child-process":
        hits = []
        if not has_launch:
            hits.append("kind=child-process requires the launch section")
        if has_inproc:
            hits.append("kind=child-process forbids the in_process section")
    elif kind == "in-process":
        hits = []
        if not has_inproc:
            hits.append("kind=in-process requires the in_process section")
        if has_launch:
            hits.append("kind=in-process forbids the launch section")
    else:
        return False, f"kind must be 'child-process' or 'in-process', got {kind!r}"
    if hits:
        return False, "; ".join(hits)
    return True, f"kind={kind} consistent with launch/in_process sections"


def ch_env_file_outside_manifests_dir(doc, ctx):
    env_file = _get(doc, "launch", "env", "env_file")
    if env_file is None:
        return True, "no env_file declared"
    if not isinstance(env_file, str) or not env_file.strip():
        return False, "launch.env.env_file must be a non-empty string"
    expanded = os.path.expanduser(env_file.strip())
    resolved = Path(os.path.normpath(
        expanded if os.path.isabs(expanded) else os.path.join(ctx.target_dir, expanded)))
    real = Path(os.path.realpath(resolved))
    inside = []
    for label, base in (("manifests dir of this run", Path(os.path.realpath(ctx.target_dir))),
                        ("canonical manifests dir", Path(os.path.realpath(CANONICAL_MANIFESTS_DIR)))):
        if real == base or base in real.parents:
            inside.append(f"{label} ({str(base).replace(home, '~')})")
    if inside:
        shown = str(resolved).replace(home, "~")
        return False, (f"env_file {env_file!r} resolves to {shown}, which is inside: "
                       + "; ".join(inside))
    return True, f"env_file {env_file!r} lies outside the manifests dir"


def ch_depends_on_acyclic(doc, ctx):
    name = _get(doc, "metadata", "name")
    deps = doc.get("depends_on") if isinstance(doc, dict) else None
    deps = deps if isinstance(deps, list) else []
    if not isinstance(name, str):
        return False, "metadata.name missing: cannot place the manifest in the dependency graph"
    _, graph = ctx.dir_index()
    cycle = _find_cycle(graph, name)
    if cycle:
        return False, (f"depends_on cycle in installation {ctx.target_dir.name}/: "
                       + " -> ".join(cycle))
    return True, (f"no depends_on cycle through {name!r} "
                  f"({len(deps)} declared dependency(ies); links outside the "
                  "directory are an install-time concern, not a cycle)")


def ch_license_spdx(doc, ctx):
    lic = _get(doc, "metadata", "provenance", "license")
    if not isinstance(lic, str):
        return False, "metadata.provenance.license missing or not a string"
    if not SPDX_RE.match(lic):
        return False, f"license {lic!r} is not of SPDX identifier form"
    return True, f"license={lic}"


CHECKS = {
    "schema_valid": ch_schema_valid,
    "schema_invalid": ch_schema_invalid,
    "api_version_present": ch_api_version_present,
    "name_kebab_unique": ch_name_kebab_unique,
    "tier_enum": ch_tier_enum,
    "duration_format": ch_duration_format,
    "no_secret_in_vars": ch_no_secret_in_vars,
    "no_shell_metacharacters": ch_no_shell_metacharacters,
    "argv_placeholder_allowlist": ch_argv_placeholder_allowlist,
    "checker_block_consistency": ch_checker_block_consistency,
    "kind_launch_consistency": ch_kind_launch_consistency,
    "env_file_outside_manifests_dir": ch_env_file_outside_manifests_dir,
    "depends_on_acyclic": ch_depends_on_acyclic,
    "license_spdx": ch_license_spdx,
}
NORMATIVE_CHECKS = [n for n in CHECKS if n not in ("schema_valid", "schema_invalid")]


def run_check(name, doc, ctx):
    """Dispatch one check; a crashing check counts as a violation (fail-closed)."""
    fn = CHECKS.get(name)
    if fn is None:
        raise InfraError(f"unknown check {name!r} (vocabulary: spec.md §6)")
    try:
        return fn(doc, ctx)
    except InfraError:
        raise
    except Exception as e:  # noqa: BLE001 — diagnostic, never a runner crash
        return False, f"check error: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Suite execution
# ---------------------------------------------------------------------------

def run_suite(spec_dir):
    spec_dir = Path(spec_dir)
    cases_path = spec_dir / "conformance" / "cases.yaml"
    if not cases_path.is_file():
        raise InfraError(f"suite not found: {cases_path}")
    raw = cases_path.read_bytes()
    try:
        suite = load_yaml(raw.decode("utf-8"), str(cases_path))
    except Exception as e:
        raise InfraError(f"cannot parse {cases_path}: {e}")
    if not isinstance(suite, dict) or not isinstance(suite.get("cases"), list):
        raise InfraError(f"{cases_path}: expected a mapping with a 'cases' list")

    def bad(msg):
        raise InfraError(f"{cases_path}: {msg}")

    for field in ("suite", "contract", "version"):
        if not isinstance(suite.get(field), str):
            bad(f"missing or non-string field {field!r}")

    schema_files = sorted((spec_dir / "schema").glob("*.schema.json")) \
        if (spec_dir / "schema").is_dir() else []
    if len(schema_files) > 1:
        bad(f"schema/: expected a single *.schema.json, found {len(schema_files)}")
    schema_path = schema_files[0] if schema_files else None
    needs_schema = any(isinstance(c, dict) and
                       {"schema_valid", "schema_invalid"} & set(c.get("checks", []))
                       for c in suite["cases"])
    if needs_schema and jsonschema is None:
        bad("jsonschema is required by this suite's schema checks but is not "
            "installed (pip install jsonschema)")
    if needs_schema and schema_path is None:
        bad(f"no schema/*.schema.json found in {spec_dir / 'schema'}")

    cache, results = {}, []
    for case in suite["cases"]:
        for field in ("id", "severity", "target", "checks", "expect"):
            if field not in case:
                bad(f"case missing field {field!r}: {case!r}")
        cid = case["id"]
        if case["severity"] not in ("must", "should"):
            bad(f"case {cid!r}: severity must be must|should, got {case['severity']!r}")
        if case["expect"] not in ("pass", "fail"):
            bad(f"case {cid!r}: expect must be pass|fail, got {case['expect']!r}")
        if not isinstance(case["checks"], list) or not case["checks"]:
            bad(f"case {cid!r}: checks must be a non-empty list of check names")
        for name in case["checks"]:
            if name not in CHECKS:
                bad(f"case {cid!r}: unknown check {name!r} (vocabulary: spec.md §6)")
        target = spec_dir / case["target"]
        if not target.is_file():  # missing target = infrastructure, not conformance
            bad(f"case {cid!r}: target not found: {target}")
        try:
            doc = load_yaml(target.read_text(encoding="utf-8"), str(target))
            parse_error = None
        except Exception as e:
            doc, parse_error = None, str(e)
        ctx = Ctx(spec_dir, target, schema_path, cache)

        check_results = []
        for name in case["checks"]:
            if parse_error is not None:
                detail = f"target not parseable: {parse_error}"
                check_results.append({"check": name, "ok": False, "detail": detail})
            else:
                ok, detail = run_check(name, doc, ctx)
                check_results.append({"check": name, "ok": bool(ok), "detail": detail})

        rejected = any(not r["ok"] for r in check_results)
        severity, expect = case["severity"], case["expect"]
        if expect == "pass":
            verdict = "pass" if all(r["ok"] for r in check_results) else \
                ("warn" if severity == "should" else "fail")
        else:  # expect: fail — green when the document is indeed rejected
            if not rejected:
                verdict = "warn" if severity == "should" else "fail"
            else:
                diag = [r for r in check_results if r["check"] != "schema_invalid"]
                # rejected, but the diagnostic checks singled out nothing:
                # the fixture may no longer exercise its intended defect
                verdict = "warn" if diag and all(r["ok"] for r in diag) else "pass"
        results.append({"case": cid, "severity": severity, "target": case["target"],
                        "expect": expect, "checks": check_results, "verdict": verdict})

    return {"suite": suite["suite"], "contract": suite["contract"],
            "version": suite["version"], "spec_dir": str(spec_dir),
            "results": results,
            "summary": {"passed": sum(r["verdict"] == "pass" for r in results),
                        "failed": sum(r["verdict"] == "fail" for r in results),
                        "warned": sum(r["verdict"] == "warn" for r in results)},
            "suite_sha256": hashlib.sha256(raw).hexdigest()}


def suite_exit_code(report):
    return 1 if any(r["verdict"] == "fail" for r in report["results"]) else 0


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_text_report(rep, out=sys.stdout):
    print(f"suite {rep['suite']} (contract {rep['contract']}, version {rep['version']})", file=out)
    print(f"spec dir: {rep['spec_dir']}", file=out)
    for r in rep["results"]:
        mark = {"pass": "PASS", "fail": "FAIL", "warn": "WARN"}[r["verdict"]]
        print(f"[{mark}] {r['case']} ({r['severity']}) expect={r['expect']} "
              f"target={r['target']}", file=out)
        for c in r["checks"]:
            state = "ok  " if c["ok"] else "fail"
            print(f"    {state} {c['check']}: {c['detail']}", file=out)
    s = rep["summary"]
    print(f"summary: {s['passed']} passed / {s['failed']} failed / {s['warned']} warned "
          f"(suite_sha256={rep['suite_sha256'][:12]}…)", file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="run.py",
        description="VESMA conformance runner v0: validates declarations, "
                    "never executes component code.")
    ap.add_argument("path", help="spec dir (e.g. specs/component-manifest/v1) "
                                 "or, with --all, a specs root")
    ap.add_argument("--all", action="store_true",
                    help="run every <root>/*/*/conformance/cases.yaml suite")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    args = ap.parse_args(argv)
    root = Path(args.path)
    if _pyyaml is None:
        print(f"note: {MINI_YAML_NOTE}", file=sys.stderr)

    try:
        if args.all:
            dirs = sorted({p.parents[1] for p in root.glob("*/*/conformance/cases.yaml")})
            if not dirs:
                raise InfraError(f"no suites under {root} "
                                 "(expected */*/conformance/cases.yaml)")
            reports = [run_suite(d) for d in dirs]
            # InfraError propagates to the exit-2 handler; only 0/1 remain here.
            code = 1 if any(suite_exit_code(r) for r in reports) else 0
        else:
            reports = [run_suite(root)]
            code = suite_exit_code(reports[0])
        if args.format == "json":
            payload = reports[0]
            if args.all:
                payload = {"suites": reports,
                           "summary": {k: sum(r["summary"][k] for r in reports)
                                       for k in ("passed", "failed", "warned")}}
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for r in reports:
                print_text_report(r)
                if len(reports) > 1:
                    print()
    except InfraError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return code


if __name__ == "__main__":
    sys.exit(main())
