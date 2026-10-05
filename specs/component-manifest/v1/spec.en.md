---
contract: component-manifest
version: 1.0.0
status: stable
decisions: [ADR-0001]
ratified: учредительный АрхКом VESMA, 2026-10-04; ратифицирован первой конформной реализацией — движок vesmaro/vesma, main 4a2da5a, 2026-10-05 (конформанс — docs/project/reports/service-conformance-2026-10-06.md в репо движка; раннер 24/24; чеклист интегратора CM-01…CM-17 green)
language: en (informative mirror)
---

# component-manifest v1 — component manifest contract

> This is an informative English mirror of the normative Russian
> specification [spec.md](spec.md). In case of divergence, the Russian text
> prevails. The mirror is maintained in the same change as the Russian text
> (single-commit sync policy).

The keywords MUST / MUST NOT / SHOULD / MAY are to be interpreted per
RFC 2119. In the normative document the prose is Russian; identifiers,
fields, and enum values are English; free text (`description`) is written
in the component's language.

## 1. Scope

The manifest is a declarative YAML description of a component: the single
source of knowledge for the CLI and the supervisor about how the component
runs, by what its liveness is judged, how it is stopped, and on what it
depends. The "CLI-first" principle (owner directive 2026-10-04): the CLI is
not extended per component — a component declares itself through a manifest
and is managed by common rules.

**In scope:**

- manifest shape: `apiVersion`, `kind`, `metadata`, `launch` / `in_process`,
  `health`, `stop`, `config`, `restart`, `depends_on`;
- strict validation: an unknown field = reject (evolution only through
  `apiVersion`; additive fields = a minor version of the contract);
- the manifest secrets policy (secrets only via `env_file`);
- write access to the manifest (who creates and modifies it);
- the machine schema (`schema/`), minimal examples (`examples/`), and the
  conformance suite (`conformance/`);
- validation error codes (§4).

**Out of scope (domains of neighboring contracts):**

- supervisor behavior: FSM, per-tier restart policies, the process model,
  the systemd unit — `specs/service-lifecycle/v1`;
- canonical layout paths (configs, state, cache, data, the manifest
  directory) — `specs/layout/v1`;
- the CLI ↔ live supervisor protocol — `specs/control-socket/v1`;
- the contents of the component config — the manifest fixes only the schema
  of its validation;
- capabilities/permissions, resource limits, replicas, metrics/alerts-webhook
  declarations — deliberately deferred beyond v1 (§7).

**Consumers:** the CLI install flow (the single writer of the manifest),
the `vesma` engine supervisor (the reader-executor), `doctor`, the
conformance runner `tools/conformance`, external integrators.

## 2. Terminology

The terms Component, In-process module, Child-process, Supervisor, Manifest,
Tier, Health check, Grace period, Canonical layout are defined in the
[glossary](../../../GLOSSARY.md) and are not redefined here. Contract terms
of this document:

| Term | Meaning |
|---|---|
| installation | the set of component manifests on one machine under one supervisor; manifest names are unique within an installation |
| manifest directory | the layout directory into which the install flow writes manifests; canonicalized by `specs/layout/v1` as `~/.config/vesma/components.d/` (drop-in: install puts a file, uninstall removes it) |
| placeholder | a token of the form `{name}` in an `argv` element, expanded by the supervisor at spawn according to a fixed allowlist |
| placeholder allowlist | `{config_path}` (the component's config file in the canonical layout), `{data_dir}` (the component's data directory), `{runtime_dir}`, `{venv_bin}` (the component's venv bin directory) |
| fail-closed loader | the `env_file` loader: any violation of the conditions (file missing, permissions not 0600, a foreign owner) = start refusal, not a warning |
| health pass | one successful result of a health check (`specs/service-lifecycle/v1` §2) |
| strict validation | the validation discipline: `additionalProperties: false` on every object of the schema; an unknown field = reject |

## 3. Contract

### 3.1 Ownership and write access

- **MUST**: the manifest is created and modified **only by the CLI install
  flow** (`vesma service install`).
- **MUST NOT**: a component writes its own manifest — otherwise the child
  rewrites its own `env`/`argv`, which is privilege escalation by
  construction.
- **MUST**: the manifest directory is not writable by components; the
  supervisor unit keeps write access only to the layout's state/cache/data
  (`ProtectSystem=strict`, `ReadWritePaths=` — specs/service-lifecycle/v1
  §3.6, SL-18).
- **SHOULD**: `doctor` cross-checks manifests against the actual
  installation (files, permissions, paths); a discrepancy is a loud
  diagnosable message, not a silent repair.

### 3.2 General shape and strict validation

- **MUST**: `apiVersion` equals `vesma.component/v1`. An unsupported
  version = reject; the error message **MUST** contain the array of versions
  supported by the loader.
- **MUST**: strict validation — `additionalProperties: false` on every
  object of the schema (`schema/component-manifest.schema.json`); an unknown
  field = reject, never smuggled through. Evolution happens via
  `apiVersion`; additive (non-breaking) fields = a minor version of the
  contract (ADR-0001 §2).
- **MUST**: durations are strings matching the pattern `^[0-9]+(ms|s|m|h)$`
  (`500ms`, `10s`, `5m`, `1h`); compound values (`1h30m`) and unitless
  numbers are forbidden.
- **MUST**: the manifest is valid against
  `schema/component-manifest.schema.json` (JSON-Schema 2020-12).

### 3.3 metadata

- **MUST**: `name` matches `^[a-z][a-z0-9-]{0,62}$`; unique within the
  installation.
- **MUST**: `name` is not in the reserved names set {`venv`, `venvs`} —
  collision with the layout's venv directories (specs/layout/v1 §3.8);
  the manifest validator MUST reject.
- **MUST**: `version` is the component's own SemVer 2.0.0.
- **MUST**: `tier` is `core` \| `optional`. The manifest encodes the tier;
  the per-tier restart policy is applied by the supervisor
  (specs/service-lifecycle/v1 §3.5) — the manifest does not describe restart
  behavior per tier.
- **MUST**: `description` is at most 200 characters.
- **MUST**: `provenance.repo` is an https-URL of the component's public
  repository.
- **MUST**: `provenance.license` is an SPDX license identifier (the
  ecosystem default is `Apache-2.0`).
- **MAY**: `provenance.artifact_sha256` — hex64. If set, the supervisor
  verifies the launch artifact hash **on every start** — this catches tamper
  and drift between install and spawn. Artifact signatures are v2 (they
  require a root key).
- **MUST**: with `tier: core` the artifact hash
  (`provenance.artifact_sha256`) is required; with `tier: optional` it is
  optional, and its absence = a `doctor` WARN (silent acceptance of
  substitution is not covered by the contract — see the threat model, §8).

### 3.4 kind and execution sections

- **MUST**: `kind` ∈ `in-process` \| `child-process`; the choice is mutually
  exclusive with the sections: `launch` is required and `in_process` is
  forbidden when `kind: child-process`; `in_process` is required and
  `launch` is forbidden when `kind: in-process`.

### 3.5 launch (child-process)

- **MUST**: `argv` is strictly an array of strings (`minItems: 1`); no
  shell strings. Elements **MUST NOT** contain shell metacharacters
  (``| & ; < > ( ) $ ` \ " ' * ?``) or whitespace; shell invocation is
  forbidden: a first element with the base name of a shell (`sh`, `bash`,
  `dash`, `ash`, `zsh`, `ksh`, `busybox`, `cmd`, `powershell`) and any
  element `-c` / `-lc`. Consequence by construction: shell injection is
  impossible, and the unit's `ExecStart` is generated as a single line
  (SL-17).
- **MUST**: placeholders in `argv` elements come only from the allowlist
  (`{config_path}`, `{data_dir}`, `{runtime_dir}`, `{venv_bin}`); the
  supervisor expands them at spawn; **there are no other substitutions** —
  no environment variable interpolation and no shell.
- **MUST**: `cwd` is a string (the working directory; canonical paths —
  `specs/layout/v1`).
- **MUST**: `env.vars` — non-secrets only. A key whose name contains
  (case-insensitive) `token`, `secret`, `password`, `passwd`, `api_key`,
  `apikey`, `private_key`, `credential` = reject (the `no_secret_in_vars`
  check).
- **MUST**: `env.env_file` is the only place for secrets. The file **MUST**
  lie outside the manifest directory, have permissions `0600`, and be owned
  by the supervisor user. The loader is fail-closed: a violation of any
  condition = start refusal with a ready remediation command (`chmod 600`,
  `chown`, moving the file) — a warning does not fix this.
- Note (unit and spawn): the components' argv never lands in the unit's
  lines — the unit's `ExecStart` is static (`vesma service run`); spawning
  is done with an execve array, so the "no shell" guarantee holds with any
  spaces in paths.
- The child environment semantics (constructed by the supervisor): a
  constructed PATH + `env.vars` + the contents of `env_file`; `env -i`
  semantics are mandatory (specs/service-lifecycle/v1 §3.2, SL-13).
- Note (residual risk): the `env_file` values are passed into the child's
  environment; a same-uid process can read `/proc/<pid>/environ` — a
  deliberate residual risk of v1 (a single trust domain,
  specs/service-lifecycle/v1 §3.2); the v2 horizon is fd-passing or an
  alternative secret transfer.

### 3.6 in_process

- **MUST**: `module` is an importable python module; `entrypoint` is a
  zero-argument factory `() -> Component`, invoked by the supervisor.
- **MUST**: `python.version` is an interpreter version constraint of the
  form `>=3.11` (operators `>=`, `>`, `<=`, `<`, `==`, `^`, `~` +
  `MAJOR.MINOR[.PATCH]`).
- An in-process component lives in the supervisor process: death of the
  in-process core = death of the supervisor → systemd unit restart
  (specs/service-lifecycle/v1 §3.1); no separate core restart mechanism is
  introduced.

### 3.7 health

- **MAY**: the `health` section is optional; without it
  `checker = liveness` (process alive / module loaded).
- **MUST**: `checker` ∈ `http` \| `tcp` \| `exec` \| `liveness` \|
  `callback`. The block matching `checker` is required; the other probe
  blocks are forbidden (dead configuration is unacceptable).
- **MUST**: probe blocks (`http` / `tcp` / `exec`) carry `interval`,
  `timeout`, `unhealthy_threshold` (the degradation threshold: consecutive
  failed probes → an FSM transition to `degraded`, T7 in
  specs/service-lifecycle/v1 §3.3).
- **MUST**: `callback` is for in-process only; format `module:attr`;
  signature `() -> {state, detail?}`, `state` ∈ `healthy` \| `degraded` \|
  `failed`. The supervisor invokes the callback **in an isolated boundary**:
  try/except + timeout; **any** exception or timeout = the result
  `state: failed`. A callback crash never takes down the supervisor.
- **MAY**: `startup` — startup window parameters: `grace` (how long to wait
  for the first successful health pass), `interval`, `timeout` of probes in
  the startup window.
- `liveness` without probes: for a child-process — "the process is alive";
  for in-process — "the module is imported and the factory has run".

### 3.8 stop

- **MUST**: with `kind: in-process` the `stop` section is **forbidden** —
  dead configuration; stopping an in-process component = stopping the
  supervisor (§3.6).
- **MUST**: `signal` ∈ `SIGTERM` \| `SIGINT` — the graceful stop signal.
- **MUST**: `grace_period` is a duration; on its expiry the supervisor
  sends SIGKILL to the child's entire process group (`kill(-pgid, …)` —
  specs/service-lifecycle/v1 §3.1, §3.5).
- The component **MUST** terminate on the graceful signal within
  `grace_period` — this is an obligation of the component's code, verified
  at conformance.

### 3.9 config

- **MUST**: `schema_file` XOR `schema_inline` — exactly one way to declare
  the schema; the schema is JSON-Schema 2020-12. `schema_file` is a path to
  the schema file; a relative path is resolved against the component's data
  directory (see `specs/layout/v1`,
  `~/.local/share/vesma/<name>/`); in a canonical installation the install
  flow places the schema there as well.
- **MUST**: the component's config = a section of the ecosystem's shared
  config; the section is validated against the schema from the manifest;
  **invalid configuration = start refusal (fail-fast)**, not a launch with
  defaults.
- **SHOULD**: the config schema itself follows the strictness discipline
  (`additionalProperties: false`).

### 3.10 restart

- **MAY**: the section is optional; without it the supervisor's tier
  defaults apply (specs/service-lifecycle/v1 §3.5).
- **MUST** (install-validation clamps): `backoff.base` ≥ `500ms`;
  `backoff.max` ≤ `5min`; `window.attempts` ≥ `3`. A value outside the
  clamps = reject (SL-18).
- Field semantics: `backoff` — exponential backoff from `base` up to the
  `max` cap; the counter resets after `reset_after` of continuous uptime;
  `window` — a budget of `attempts` tries per `per` window. Per-tier
  behavior (core — indefinitely, optional — budget + degradation) is applied
  by the supervisor.

### 3.11 depends_on

- **MAY**: the section is optional.
- **MUST**: elements are names of other manifests of the installation (per
  the name pattern); the dependency graph is **acyclic** — a cycle = an
  install-validation error.
- **MUST**: a dependency is considered up ("up") on the first successful
  health pass of the dependency component (T4 in specs/service-lifecycle/v1);
  start order is topological, stop order is reverse-topological.

## 4. Error codes

A unified registry of validation and start errors. The source is install
validation / the supervisor loader; the recipient (CLI, operator) receives
the code + the field path + a ready remediation command where applicable.

| Code | Meaning | Source | Recipient's reaction |
|---|---|---|---|
| `APIVERSION_UNSUPPORTED` | `apiVersion` ≠ a supported version | loader | reject; the error contains the array of supported versions |
| `MANIFEST_SCHEMA_INVALID` | the manifest fails JSON-Schema (type, format, unknown field) | install validation / loader | reject; show the field's JSON-path and the schema expectation |
| `NAME_DUPLICATED` | the name is already taken by another manifest of the installation | install validation | reject; show the conflicting manifest |
| `SHELL_IN_ARGV` | shell metacharacters / whitespace / shell invocation in `argv` | install validation | reject; show the element and its position |
| `PLACEHOLDER_UNKNOWN` | a placeholder outside the allowlist | install validation | reject; show the allowlist |
| `SECRET_IN_VARS` | a secret-like key name in `env.vars` | install validation | reject; delete the key, move the value to `env_file` |
| `ENV_FILE_UNSAFE` | `env_file` missing / permissions not 0600 / a foreign owner / located in the manifest directory | loader (fail-closed) | start refusal + a ready remediation command (`chmod 600`, `chown`, move) |
| `DURATION_INVALID` | a duration not matching the pattern | install validation | reject |
| `CLAMP_VIOLATION` | restart numbers outside the clamps (base < 500ms, max > 5min, attempts < 3) | install validation | reject |
| `DEPENDS_CYCLE` | a cycle in the `depends_on` graph | install validation | reject; show the cycle |
| `DEPENDS_MISSING` | a reference to a non-existent manifest of the installation | install validation | reject |
| `CONFIG_INVALID` | the component's config section fails its schema | loader (fail-fast) | start refusal; show the schema error |
| `ARTIFACT_HASH_MISMATCH` | the artifact hash does not match `artifact_sha256` | supervisor at start | start refusal; a tamper/drift signal, requires reinstall |
| `CALLBACK_FAILED` | an exception/timeout in a health callback | supervisor | component state failed; the supervisor stays alive |

## 5. Examples

A minimal example is mandatory for merging (ADR-0001 §1); the examples
contain only canonical layout paths and placeholders — no real machine
paths or secrets (ADR-0001 §6).

| File | What it shows |
|---|---|
| `examples/python-inprocess.yaml` | an in-process python component (`board`): `in_process` with a factory, `health.callback`, `config.schema_inline` (JSON-Schema with 2-3 properties) |
| `examples/go-child.yaml` | a child-process Go binary (`mesh`): `launch.argv` with the `{config_path}` placeholder, `health.http`, `provenance.artifact_sha256` |
| `examples/node-runtime.yaml` | a child-process Node runtime (`eyes`): `health.tcp`, `depends_on: [server]` |

## 6. Conformance

The suite is `conformance/cases.yaml`; the integrator's human checklist is
`conformance/checklist.md`. It is executed by the `tools/conformance` runner
(stdlib + `jsonschema`; it validates declarations only and executes no
components — ADR-0001 §4). A green MUST run of the suite = the gate for
integrating the component into the ecosystem.

**Semantics of the `schema_invalid` check:** the manifest is rejected by
contract validation — JSON-Schema (`schema/`) plus the normative rules of
§3 implemented by the runner (secrecy of `env.vars`, placement of
`env_file`, the `depends_on` graph). The static checks from the dictionary
provide the decomposition of the reason.

**Fixtures.** The `conformance/fixtures/invalid/` directory for the set
checks (`name_kebab_unique`, `depends_on_acyclic`) is treated as one
installation; each case targets its own file.

Check dictionary (the executor is `tools/conformance/run.py`, a separate
task):

| Check | What it does |
|---|---|
| `schema_valid` | the document is valid against `schema/component-manifest.schema.json` |
| `schema_invalid` | the document is rejected by contract validation (see the semantics above) |
| `api_version_present` | `apiVersion` is present and matches `^vesma\.component/v[0-9]+$` |
| `name_kebab_unique` | `metadata.name` matches the pattern and is unique within the installation |
| `name_not_reserved` | `metadata.name` is not in the reserved set {`venv`, `venvs`} (§3.3; collision with the layout's venv directories — specs/layout/v1 §3.8) |
| `tier_enum` | `metadata.tier` ∈ `core` \| `optional` |
| `duration_format` | all duration fields match the pattern `^[0-9]+(ms\|s\|m\|h)$` |
| `no_secret_in_vars` | no secrets in the manifest: (a) the key names of `launch.env.vars` are checked for secret-like ones (`token`, `secret`, `password`, `passwd`, `api_key`, `apikey`, `private_key`, `credential`; case-insensitive); (b) the values of all string scalars of the document are checked against 5 secret-like patterns (openai-style `sk-…`, github PAT `ghp_…`, PEM private key, long hex ≥ 40, long base64 ≥ 40). Value-scan exceptions: the `config` subtree (`schema_inline` contains legitimate patterns and defaults), `metadata.description`, `metadata.provenance.artifact_sha256` (hex64 by contract), placeholder values `<...>`; in diagnostics the values are masked |
| `no_shell_metacharacters` | `argv` (launch and health.exec) without shell metacharacters, whitespace, or shell invocation |
| `argv_placeholder_allowlist` | argv placeholders (`launch.argv`, `health.exec.argv`) only from the §2 allowlist; only well-formed placeholders of the form `{[a-z_]+}` outside the allowlist are flagged — literal `{}`, `{a` and the like are not placeholders and are not flagged |
| `checker_block_consistency` | `health.checker` ↔ the corresponding block (the if-coupling of §3.7); `callback` only with in-process |
| `kind_launch_consistency` | kind ↔ launch/in_process XOR (§3.4) |
| `env_file_outside_manifests_dir` | `env.env_file` outside the manifest directory |
| `depends_on_acyclic` | the installation's `depends_on` graph is acyclic |
| `license_spdx` | `provenance.license` — SPDX identifier form (regex `^[A-Za-z0-9.-]+(\+[A-Za-z0-9.-]+)?$`), not the registry |

Cases: three positive ones (the examples, `expect: pass`, the full set of
applicable checks, all `severity: must`) and negative ones over
`conformance/fixtures/invalid/` (all `severity: must`, `expect: fail`). The
checks `depends_on_acyclic`, `no_shell_metacharacters`,
`env_file_outside_manifests_dir`, `no_secret_in_vars` are also part of the
positive cases.

## 7. Compatibility

- **SemVer**: ratified 2026-10-05 by the first conforming implementation
  in the vesma engine (main `4a2da5a`): `1.0.0-draft.2` → `1.0.0`.
  A breaking change = MAJOR + a
  deprecation window of `max(90 days, 2 minor releases)` with dual support
  (ADR-0001 §2).
- **Additive fields** (new optional fields that do not break existing
  manifests) = a minor version of the contract; the strict schema with
  `additionalProperties: false` makes them detectable by the CI breaking
  detector (comparison of neighboring schema versions).
- **Contract consumers**: the supervisor reads
  `name/kind/tier/metadata/launch/in_process/health/stop/config/restart/depends_on`
  (reading requirements — specs/service-lifecycle/v1 §6); manifest and
  env-file paths — `specs/layout/v1`; live-supervisor management —
  `specs/control-socket/v1`.
- **Deferred beyond v1 (deliberately, v2 candidates):**
  capabilities/permissions; resource limits; replicas; the
  metrics/alerts-webhook declaration; artifact signatures (v1 provides only
  `artifact_sha256` — signatures require a root key).
- The template `templates/manifest-template.yaml` is derived from this
  spec; on divergence, the spec and `schema/` are normative.

## 8. Threat model (mini-STRIDE)

The manifest is a **local trusted file without privileges**: it is not
executed; it is read by the install flow and the supervisor. Trust is not
delegated across the boundary: a component is not a trusted writer of its
own manifest.

**Assets:** the children's `env`/`argv` (via the manifest), the secrets in
`env_file`, the dependency graph, the supervisor process.

**Boundary:** the manifest file ↔ loader/supervisor; component ↔ the
manifest directory.

| Category | Threat | Mitigation | Check |
|---|---|---|---|
| **T**ampering | a component/third-party process edits its own manifest (rewrites its own `env`/`argv`) | write access: only the install flow writes the manifest (§3.1); the manifest directory is outside the components' `ReadWritePaths` (hardening, SL-18) | operational control (directory permissions) + the CM checklist |
| **T**ampering | substitution of the launch artifact between install and spawn | `artifact_sha256` is verified by the supervisor on every start → `ARTIFACT_HASH_MISMATCH` | §3.3; the engine's start check |
| **T**ampering | smuggling junk through unknown fields | strict validation: `additionalProperties: false`, an unknown field = reject | `fix-unknown-field` (`schema_invalid`) |
| **I**nformation Disclosure | a secret in the manifest's `env.vars` | secrets in the manifest are forbidden; a secret-like key name = reject | `fix-secret-in-vars` (`no_secret_in_vars`) |
| **I**nformation Disclosure | an `env_file` with weakened permissions or in the manifest directory | fail-closed loader: outside the manifest directory, `0600`, owner = the supervisor user, otherwise start refusal with a remediation command | `fix-env-file-inside-manifest-dir` + operational control |
| **E**levation of Privilege | shell injection via `argv` | argv is a string array without shell by construction; metacharacters and `sh -c` are forbidden; the supervisor expands placeholders per the allowlist, there is no interpolation | `fix-argv-string` + `no_shell_metacharacters` / `argv_placeholder_allowlist` |
| **E**levation of Privilege | a child rewrites the dependency graph/tier via the manifest | the same write access (§3.1): the single writer is the install flow | operational control |
| **D**enial of Service | a health callback crashes the supervisor with an exception | an isolated invocation boundary: try/except + timeout; any exception = `state: failed` | §3.7 (engine) + `checker_block_consistency` |
| **D**enial of Service | a manifest forces a restart storm | clamps on the restart numbers (§3.10) + the supervisor's tier policies (SL §3.5) | `fix-bad-duration` / `CLAMP_VIOLATION` + SL-18 |
| **D**enial of Service | a dependency cycle hangs the start | the `depends_on` graph is acyclic: a cycle = an install-validation error | `fix-cyclic-dependson-*` (`depends_on_acyclic`) |
| **S/R**poofing / **R**epudiation | "who changed the manifest?" | the single writer is the install flow via the CLI; supervisor changes are visible in the journal's structural lines (SL §3.4); journald append-only | operational control |

Every mitigation is closed by a conformance check or marked "operational
control" — there are no silent unverifiable promises.

## 9. Migration from legacy

Legacy units with `env -i` in sh wrappers and `pkill` patterns are replaced
by manifests; the migration is manual, the single migration point is the
install flow. `doctor` cross-checks manifests against the actual
installation and highlights legacy leftovers.

| Legacy pattern (inventory 2026-10-04) | Contract answer |
|---|---|
| an sh wrapper with `env -i` (manual environment hygiene per component) | `launch.env.vars` + `env.env_file`; env semantics are built by the supervisor centrally (SL-13) |
| `pkill` patterns in ExecStop (inventorying by name) | `stop.signal` + `stop.grace_period`; the stop is performed by the supervisor over the process group (SL-04); pkill disappears |
| `ExecStart` with `sh -c` and concatenation | `launch.argv` as a list of strings; `ExecStart` is generated as a single line without shell (SL-17) |
| configs under legacy names scattered across the home directory | a shared config section validated by `config.schema_file`/`schema_inline`; canonical paths — `specs/layout/v1` |
| venv overlaps, manual interpreter symlinks | the `{venv_bin}` placeholder; the one-venv-per-component venv discipline — `specs/layout/v1` |
| hand edits of "live" launch scripts | only the install flow writes the manifest (§3.1); `doctor` cross-checks manifest ↔ installation |

Order: a `doctor` inventory → the install flow generates manifests → a
green MUST run of the component's suite → the old launch mechanisms are
retired. Legacy-deployment migration is not before the first observation
window of the founding track closes (founding context — see `docs/`;
roadmap phase 3, the engine track); the specs and the CLI code are not
subject to the window (as in specs/service-lifecycle/v1 §8).

**Historical note.** This spec is deliberately genericized (owner's
decision of 2026-10-04): the specifics of the founding environment — the
legacy names, the target machine, the details of the first observation
window — are preserved in the founding pack `docs/` (in particular, the
directives brief `docs/brief-2026-10-04-archcom-founding.md`) and in the
repository's history; for historical continuity, read them together with
this spec.

## 10. References

- `specs/service-lifecycle/v1` — the supervisor: consumes the manifest, defines the FSM, restart policies, the systemd unit
- `specs/control-socket/v1` — live-supervisor management
- `specs/layout/v1` — canonical paths: the manifest directory, env files, state/runtime/config
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — layer structure and governance; the form of this contract was ratified by the founding ArchCom on 2026-10-04
- [Founding ArchCom brief](../../../docs/brief-2026-10-04-archcom-founding.md) — the CLI-first directives, the supervisor architecture, the contract interface
- [Glossary](../../../GLOSSARY.md), [ecosystem map](../../../ECOSYSTEM.md)
- [Manifest template](../../../templates/manifest-template.yaml) — derived from this spec
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — keyword interpretation
- [JSON Schema 2020-12](https://json-schema.org/specification-links#2020-12) — the format of `schema/` and `config.schema_inline`
- [Semantic Versioning 2.0.0](https://semver.org/) — the `metadata.version` format
- [SPDX License List](https://spdx.org/licenses/) — the `provenance.license` format

## Translation note

- Last sync: 2026-10-05.
- Synced with the Russian spec.md in the same change (single-commit sync
  policy). In case of divergence, the Russian text prevails.
