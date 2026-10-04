---
contract: layout
version: 1.0.0-draft.1
status: draft (ратифицируется первой реализацией в движке vesma)
decisions: [ADR-0001]
ratified: учредительный АрхКом VESMA, 2026-10-04
language: en (informative mirror)
---

# layout v1 — canonical layout

> This is an informative English mirror of the normative Russian
> specification [spec.md](spec.md). In case of divergence, the Russian text
> prevails. The mirror is maintained in the same change as the Russian text
> (single-commit sync policy).
>
> **Status: draft.** The spec is ratified by the first implementation in
> the `vesma` engine (card `cli-service-management`). The contract form —
> installation profiles and paths, permissions, the uniqueness of log
> locations, venv discipline, doctor checks, migration from legacy — was
> ratified by the founding VESMA ArchCom on 2026-10-04 (ADR-0001) and is
> here **codified, not replayed**. Further changes happen only through the
> SemVer process (§7).

The keywords MUST / MUST NOT / SHOULD / MAY are to be interpreted per
RFC 2119. In the normative document the prose is Russian; identifiers and
paths are canonical (EN).

## 1. Scope

The layout is the deb-like directory discipline of a VESMA installation
(glossary: Canonical layout): where configs, manifests, secrets, data,
venv, logs, runtime, and cache live. The contract closes the legacy
inventory chaos — logs in three places, configs under legacy names, venv
overlaps (the inventory is in the brief of the
`vesma-cli-service-management` directive, see
[ADR-0001](../../../adrs/0001-repo-structure-and-governance.md)).

**In scope:**

- the user/system installation profiles and the 1:1 correspondence rule;
- the canonical paths and permissions of the user profile (the MUST table
  §3.2);
- canonicalizations that remove the placeholders of neighboring
  contracts: the manifest directory =
  `~/.config/vesma/components.d/<name>.yaml` (drop-in); the socket name =
  `control.sock`; the canonical place of env files; the canonical place of
  component config schemas
  `~/.local/share/vesma/<name>/config.schema.json` — the resolution of the
  manifest's `config.schema_file` against the component's data directory
  (§3.2);
- the expansion of argv placeholders (`{config_path}`, `{data_dir}`,
  `{runtime_dir}`, `{venv_bin}`) into concrete paths (§3.4);
- the uniqueness of log locations: journald / files-under-state, there are
  no other places;
- venv discipline: one venv per python unit, `PYTHONNOUSERSITE=1`, a
  dependency pin policy;
- the cache rule: regenerable content, never secrets (enforcement at the
  write-API level);
- installation doctor checks (`vesma doctor --service`, DR-01…DR-11);
- migration from legacy: target paths (§9) — the migration itself is not
  executed here.

**Out of scope (domains of neighboring contracts):**

- the manifest shape and the `env_file` rules —
  [specs/component-manifest/v1](../../component-manifest/v1/spec.md):
  the layout fixes **where**, the manifest — **what** and how it is
  validated;
- supervisor behavior, FSM, the unit template, hardening —
  [specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md): the
  layout provides the `ReadWritePaths` paths, SL — what the unit does with
  them;
- the socket protocol, TOCTOU procedure, peer authentication —
  [specs/control-socket/v1](../../control-socket/v1/spec.md): the layout
  fixes the place and the permissions of the socket directories;
- the contents of configs and the secrets inside them — the manifest's
  config schema (CM §3.9) and env files (CM §3.5);
- the legacy-deployment migration implementation — the engine (card
  `cli-service-management`), not before the first observation window of
  the founding track closes (founding context);
- hash-pinning tooling (the mechanics of `pip --require-hashes`, lock
  tooling) — v2.

**Consumers:** the `vesma` engine (the install flow — the installation's
single writer; the supervisor — the reader-executor; `doctor` — the
checker), components (they consume paths via placeholders, they do not
hardcode them), the conformance runner `tools/conformance`, external
integrators.

## 2. Terminology

The terms Canonical layout, Runtime directory, venv discipline, Supervisor,
Component, Manifest are defined in the [glossary](../../../GLOSSARY.md)
and are not redefined here. Contract terms:

| Term | Meaning |
|---|---|
| installation profile | user (v1, implemented) or system (defined §3.3, the implementation deferred beyond v2); system is built by a 1:1 mapping table to the user paths |
| canonical path | a path from the tables §3.2/§3.3; hardcoding other places in installation artifacts is a contract violation |
| drop-in directory | a directory whose unit of content is a single file `<name>.yaml`; install puts the file, uninstall removes it; the operations never touch foreign files |
| files-under-state | the file mode of logs in `~/.local/state/vesma/logs/<name>/` — only when journald is unavailable (container / manual mode) |
| fallback runtime | `~/.local/state/vesma/run/` — the runtime directory when `XDG_RUNTIME_DIR` is empty + a WARN line (control-socket v1 spec §3) |
| fail-closed loader | defined in [specs/component-manifest/v1](../../component-manifest/v1/spec.md) §2: any violation of the `env_file` loading conditions = start refusal, not a warning |
| freeze drift | a divergence between the actual venv contents (`pip freeze`) and the installation's lock file |
| user-site | the interpreter's per-user site-packages directory (PEP 370); a leak = user-site ending up in the process's `sys.path` |
| history | the append-only journal of supervisor transitions: `~/.local/state/vesma/history/` |
| doctor | the diagnostic command `vesma doctor --service`; the checklist DR-01…DR-11 (§3.10) |
| first observation window | the founding track's first telemetry window (founding context); the legacy-deployment migration is not executed before it closes (roadmap phase 3; details — the founding pack `docs/`) |

## 3. Contract

### 3.1 Profiles and base directories

- **MUST**: the user profile is the only one implemented in v1.
- **MUST**: the user profile's paths are built per the XDG Base Directory
  Specification: `$XDG_CONFIG_HOME` (default `~/.config`),
  `$XDG_DATA_HOME` (default `~/.local/share`), `$XDG_STATE_HOME` (default
  `~/.local/state`), `$XDG_CACHE_HOME` (default `~/.cache`); an empty
  variable = the default. In the tables below the paths are written per
  the defaults.
- **MUST**: the owner of all user-profile paths is the supervisor user.
- **MUST**: directory and file permissions are set explicitly at creation
  (`chmod` after `mkdir` / before use), not inherited from umask
  (symmetric to note B of §3 of the control-socket v1 spec).
- **MUST**: a directory whose permissions are weaker than the §3.2 table
  is fail-closed for the corresponding operation (§3.5): the operation is
  not performed "with a warning".

### 3.2 User profile (v1, normative)

MUST table:

| Path | Contents | Permissions |
|---|---|---|
| `~/.config/vesma/vesma.yaml` | the shared config; a component's config = a section of the shared config (CM §3.9) | directory `0700` |
| `~/.config/vesma/components.d/<name>.yaml` | component manifests (drop-in; install puts, uninstall removes) | directory `0700` |
| `~/.config/vesma/env/<name>.env` | secret env files | file `0600`; fail-closed loading (not `0600` / a foreign owner = start refusal + a ready remediation command) |
| `~/.local/share/vesma/<name>/` | component data; the child's default cwd | directory `0700` |
| `~/.local/share/vesma/<name>/config.schema.json` | the component's config schema; placed by the install flow together with the component's data; the resolution of the manifest's `config.schema_file` (CM §3.9) — against the component's data directory | directory `0700` (the component's data directory) |
| `~/.local/share/vesma/venv/` | the engine venv (supervisor runtime): the engine + in-process modules (§3.8); the only venv outside `venvs/`; the component names `venv`/`venvs` are reserved (the name validator rejects them) | directory `0700` |
| `~/.local/share/vesma/venvs/<name>/` | a child python component's venv | directory `0700` |
| `~/.local/state/vesma/logs/<name>/` | file logs (when there is no journald); rotation 10 MB × 5 | directory `0700` |
| `~/.local/state/vesma/history/` | the supervisor transitions journal (append-only) | directory `0700` |
| `~/.local/state/vesma/run/` | fallback runtime (socket, pids) when `XDG_RUNTIME_DIR` is empty + WARN | directory `0700` |
| `${XDG_RUNTIME_DIR}/vesma/` | the canonical runtime: `control.sock` `0600`, pids | directory `0700` |
| `~/.cache/vesma/<name>/` | regenerable content; NEVER secrets (a rule at the write-API level, §3.9) | directory `0750` |

Notes:

- **a.** The child's default cwd is the component's data directory
  (`{data_dir}`, §3.4); the manifest may set `cwd` explicitly (CM §3.5),
  the install flow fills in the canonical default value.
- **b.** `venvs/<name>/` is created **only** for child python components;
  in-process components live on the engine venv (§3.8) and have no venv of
  their own; non-python children have no venv.
- **c.** File logs exist only in files-under-state mode (§3.7); under
  systemd the `logs/` directory may not be created at all.
- **d.** The cache **MAY** not exist — it is created lazily on first
  write; deleting the cache directory is safe at any moment.
- **e.** pids are diagnostic pid files; single-instance is ensured by the
  connect-probe (control-socket v1 §4.2), not by a pid file.
- **f.** The shared config files (`vesma.yaml`) **SHOULD** not be
  group-/world-readable (`0600`): secrets in `vesma.yaml` are forbidden
  (the domain of env files), but the config need not be public.

### 3.3 System profile (defined, the implementation deferred)

**The system-profile implementation is deferred beyond the
legacy-deployment migration — not before the first observation window of
the founding track closes (founding context); v2 horizon**
([ADR-0001](../../../adrs/0001-repo-structure-and-governance.md), v2
horizon). The 1:1 XDG mapping table is normative as a design reference;
the system profile's conformance items are `n/a (v2)`.

| Purpose (user, §3.2) | System path | Permissions |
|---|---|---|
| shared config | `/etc/vesma/vesma.yaml` | `0640 root:vesma` |
| component manifests | `/etc/vesma/components.d/<name>.yaml` | `0640 root:vesma` |
| secret env files | `/etc/vesma/env/<name>.env` | `0600 root:vesma` |
| component data / default cwd | `/var/lib/vesma/<name>/` | fixed at implementation (v2) |
| python components' venv | `/var/lib/vesma/venvs/<name>/` | fixed at implementation (v2) |
| runtime (socket, pids) | `/run/vesma/` | `0750 root:vesma-oper`; `control.sock` `0660` — see [specs/control-socket/v1](../../control-socket/v1/spec.md) §3 |
| file logs | `/var/log/vesma` is **NOT created** in v1 | — |

- **MUST NOT**: `/var/log/vesma` is created neither in the user nor in
  the system profile of v1.
- **MUST**: secret env files are `0600 root:vesma`, a single rule with
  the user profile (§3.2): group-readable secrets contradict the
  fail-closed loader (CM §3.5, `ENV_FILE_UNSAFE`); the shared config and
  the manifests are not secrets, they stay `0640 root:vesma`.
- The remaining system-mapping rows (history, cache) are built at the v2
  implementation under the same 1:1 principle and **MUST NOT** contradict
  this table.
- The `vesma-oper` group is **NOT created** by the installer by default
  (control-socket v1 §3, note D): creating it is a deliberate operator
  action on the v2 horizon.

### 3.4 Expansion of argv placeholders

The manifest placeholders (allowlist — CM §2) are expanded by the
supervisor at spawn according to the MUST table:

| Placeholder | User profile | System profile |
|---|---|---|
| `{config_path}` | `~/.config/vesma/vesma.yaml` | `/etc/vesma/vesma.yaml` |
| `{data_dir}` | `~/.local/share/vesma/<name>/` | `/var/lib/vesma/<name>/` |
| `{runtime_dir}` | `${XDG_RUNTIME_DIR}/vesma/` (fallback: `~/.local/state/vesma/run/`) | `/run/vesma/` |
| `{venv_bin}` | `~/.local/share/vesma/venvs/<name>/bin` | `/var/lib/vesma/venvs/<name>/bin` |

- **MUST**: there are no other substitutions — no environment variable
  interpolation and no shell (CM §3.5); the expansion is performed by the
  supervisor.
- **MUST**: `{venv_bin}` is not expanded for a component without a venv;
  a missing venv with a reference to `{venv_bin}` = start refusal
  (fail-closed) with diagnostics.

### 3.5 The manifest directory and env files

- **MUST**: the manifest directory = `~/.config/vesma/components.d/`; the
  manifest of component `<name>` is the file `components.d/<name>.yaml`.
  The canonicalization removes the `~/.config/vesma/manifests/`
  placeholder from CM §2.
- **MUST**: the manifest file name == `metadata.name`; every file in
  `components.d/` must be a valid manifest — an invalid file = an
  installation loading error (fail-closed), not a silent skip.
- **MUST**: drop-in discipline: install atomically creates/updates the
  manifest file (tmp + rename), uninstall deletes the file; the single
  writer is the install flow (CM §3.1); the components and the supervisor
  get no write access to the directory (`ReadWritePaths` of the unit —
  SL §3.6).
- **MUST**: secret env files live at `~/.config/vesma/env/<name>.env`,
  file `0600`, owner — the supervisor user; `<name>` == the component's
  `metadata.name`.
- **MUST**: the env file lies **outside the manifest directory** and is
  loaded fail-closed: not `0600` / a foreign owner / declared but missing
  = start refusal with a ready remediation command (CM §3.5, the code
  `ENV_FILE_UNSAFE`).
- **MUST**: the install flow places the env files it creates only in
  `env/<name>.env`.
- **SHOULD**: `doctor` highlights a manifest's `env_file` outside the
  canonical place as drift (WARN + a move command via install).
- **MUST**: the directories `~/.config/vesma/`, `components.d/`, `env/`
  are `0700`.

### 3.6 The runtime directory and the socket

- **MUST**: the canonical runtime = `${XDG_RUNTIME_DIR}/vesma/`, directory
  `0700`; the socket is `control.sock`, `0600` (the name canonicalization
  is agreed with [specs/control-socket/v1](../../control-socket/v1/spec.md)
  §3).
- **MUST**: `XDG_RUNTIME_DIR` empty → the fallback
  `~/.local/state/vesma/run/` (`0700`) + a WARN line in the log
  (control-socket v1 §3).
- **MUST**: the socket artifacts are wholly subordinate to control-socket
  v1: the bind side's TOCTOU/SYMLINK procedure (§4.2), peer
  authentication, the TCP prohibition; the layout fixes only the place and
  the permissions.
- **MUST**: pids are diagnostic pid files inside the runtime directory;
  **MUST NOT** be used as a single-instance or locking mechanism
  (control-socket v1 §4.2: the probe decides).
- **MUST NOT**: persistent state is not placed in the runtime — the
  runtime lives under the tmpfs semantics of `XDG_RUNTIME_DIR`; for
  persistent things there are state/data/history.

### 3.7 Logs and the transitions journal

- **MUST** (the canon under systemd): everything to journald; the
  `SYSLOG_IDENTIFIER=vesma-<component>` tagging is performed by the
  supervisor when relaying child lines (SL §3.4); `vesma service logs` =
  a journalctl filter by identifier (control-socket v1 §4.5/4.8), not a
  grep over files.
- **MUST** (container / manual mode, journald unavailable):
  files-under-state — `~/.local/state/vesma/logs/<name>/`; rotation
  10 MB × 5 files; the line format is the structural lines of SL §3.4.
- **MUST**: exactly one mode is chosen: journald available → journald
  (file logs are not written); unavailable → files-under-state. Double
  writing to both places is forbidden.
- **MUST NOT**: no other log places — neither scattered legacy file logs,
  nor logs in the data directory, nor in the cache, nor `/var/log/vesma`
  (§3.3). The appearance of a "third place" = a contract violation (it
  closes the inventory chaos of "logs in 3 places": journald + scattered
  legacy file logs + misc).
- **MUST**: `~/.local/state/vesma/history/` — the append-only journal of
  supervisor transitions (`0700`); the contents are structural lines (the
  SL §3.4 domain); the layout fixes the path, the permissions, and the
  append-only semantics.

### 3.8 venv discipline

- **MUST**: one managed venv per runtime python unit. Two classes:
  (a) the engine venv — the engine + all in-process modules; (b) a child
  python component's venv — `venvs/<name>/` from the manifest.
- **MUST**: TWO components on one venv = an error (install validation /
  doctor DR-04). A venv is not shared between components, nor between a
  component and the engine.
- **MUST**: `venvs/<name>/` (`0700`) — only for child python components.
  The engine venv (supervisor runtime) is `~/.local/share/vesma/venv/`
  (`0700`, the §3.2 table): the only venv outside `venvs/`; it reserves
  the name — the component names `venv` and `venvs` are RESERVED (the
  manifest name validator rejects them). The engine venv **MUST NOT**
  overlap with any `venvs/<name>/` (DR-06).
- **MUST**: `PYTHONNOUSERSITE=1` is injected by the supervisor
  **unconditionally** into every python process (engine and children) — a
  user-site leak into `sys.path` is excluded by construction; `doctor`
  confirms it with an import test in a clean environment (DR-03).
- **MUST**: dependencies are pinned exactly (`==`) against the
  installation's lock file — v1.
- **SHOULD**: hash-pinning (`pip --require-hashes`) — the v1 default;
  mandatory — v2 (lock tooling is needed).
- **MUST**: package sources are PyPI only; side URLs/wheels (direct
  links, third-party indexes) are forbidden in v1.
- **MUST**: a venv's site-packages are not world- and not group-writable;
  the venv owner is the supervisor user (a supply chain boundary, §8).
- **SHOULD**: a venv is populated only by install-flow regeneration; a
  manual `pip install` into `venvs/<name>/` = freeze drift → a doctor
  finding DR-02.

### 3.9 Cache

- **MUST**: `~/.cache/vesma/<name>/` (`0750`) — regenerable content only;
  deleting the directory at any moment does not change the installation's
  correctness (the content is restored).
- **MUST**: the cache **NEVER** contains secrets. Enforcement is at the
  level of the engine's write API: a write to the cache happens only
  through the write API, which **MUST** refuse a value originating from
  an env file / a secret installation context; bypassing the API is a
  contract violation.
- **MUST NOT**: configs, manifests, env contents, logs, and state data
  are not placed in the cache (their home is the §3.2 table).

### 3.10 Doctor checks (`vesma doctor --service`)

The MUST list of installation checks (the execution is the engine's; the
DR-xx identifiers are referenced by the threat model §8 and the
checklist):

| ID | Check | Details |
|---|---|---|
| DR-01 | permissions/ownership of config/state/env | directories `0700`, env files `0600`, owner — the user; a deviation → WARN/FAIL + a command |
| DR-02 | venv integrity | site-packages not world- and not group-writable; the owner matches; `pip freeze` against the lock (drift = FAIL) |
| DR-03 | a user-site leak | an import test in a clean environment (equivalent to `PYTHONNOUSERSITE`); user-site in `sys.path` = FAIL |
| DR-04 | two manifests on one venv | venv uniqueness per python unit; a collision = FAIL |
| DR-05 | the venv's python version vs the manifest | the manifest's `python.version` constraint (CM §3.6) against the venv interpreter; a mismatch = FAIL |
| DR-06 | venv ≠ the engine interpreter; reserved names | `venvs/<name>/` is not (and does not symlink) the engine venv/interpreter; the component name is not among the reserved {venv, venvs} |
| DR-07 | "generated unit vs installed" drift | the installed unit (SL §3.6) == the regenerated one; a divergence = FAIL + the `vesma service install` command |
| DR-08 | socket liveness | connect-probe + `hello` per control-socket v1 §4.2; a live supervisor → OK; stale/absent → a status, not an error per se |
| DR-09 | http/tcp health-port collisions | an intersection of health-probe ports (`health.http`/`health.tcp`, CM §3.7) across the installation's manifests = FAIL |
| DR-10 | free space | the volumes of the canonical roots (config/data/state/cache/runtime); the WARN/FAIL thresholds — the engine implementation |
| DR-11 | `Storage=persistent` for journald | systemd contexts only; a volatile journal = WARN (logs are lost on reboot); outside systemd — n/a |

- **MUST**: every finding carries a severity `OK`/`WARN`/`FAIL` and a
  ready remediation command with the real path (the "committee rule":
  doctor issues a ready fix command, not scolding).
- **MUST**: doctor does **NOT** execute the remediation commands itself
  (symmetric to control-socket v1 §4.1).
- **MUST**: a FAIL finding of DR-01 on an env file is coordinated with the
  fail-closed loader: the corresponding component's start is refused until
  fixed.

## 4. Error codes

Not applicable: the contract introduces no protocol and no registry of
its own. Codes of the adjacent boundaries: `ENV_FILE_UNSAFE` (the
fail-closed `env_file` loader) —
[specs/component-manifest/v1](../../component-manifest/v1/spec.md) §4;
the socket protocol codes —
[specs/control-socket/v1](../../control-socket/v1/spec.md) §4.6.
Doctor-finding codes **MAY** be introduced additively (a minor version)
during the engine implementation.

## 5. Examples

A minimal example is mandatory for merging (ADR-0001 §1); the examples
contain only placeholders — no real tokens, machine paths, or secrets
(ADR-0001 §6).

| File | What it shows |
|---|---|
| `examples/example-tree.txt` | the canonical user-profile path tree with permissions in comments |
| `examples/example-doctor-report.txt` | mock output of `vesma doctor --service`: OK lines, a WARN with a ready remediation command, a FAIL |

## 6. Conformance

The checklist is [conformance/checklist.md](conformance/checklist.md)
(LY-01…LY-14): directory/file permissions, env fail-closed, the
`components.d` drop-in, venv rules, `PYTHONNOUSERSITE`, the uniqueness of
log locations, a secret-free cache, conformance to the system table. The
check types are "auto" (the engine's test suite / the runner) and
"manual" (artifact inspection) — as in
[specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md) §5; the
`tools/conformance` runner validates declarations, the file checks are
executed by the engine (ADR-0001 §4). The contract status is `draft`
until the checklist is first passed by an implementation in the `vesma`
engine (ratification by implementation).

## 7. Compatibility

- **SemVer**: `1.0.0-draft.1` → `1.0.0` upon ratification by
  implementation. A breaking change (moving an existing path, changing
  permissions, changing the semantics of log places) = MAJOR + a
  deprecation window with dual support (ADR-0001 §2). Additive (a new
  directory, a new doctor check, a new doctor-finding code) = a minor
  version.
- **The canonicalizations remove the placeholders of neighboring
  contracts**: the `components.d/` manifest directory (the
  `~/.config/vesma/manifests/` placeholder in CM §2), the `control.sock`
  name (agreed with control-socket v1 §3), the target paths of the
  `{config_path}/{data_dir}/{runtime_dir}/{venv_bin}` placeholders (the
  CM §2 allowlist), files-under-state (the path of the SL examples).
  Edits to the examples/prose of neighboring specs are separate additive
  PRs; this contract does not execute them and does not touch their
  files.
- **Contract consumers**: CM (the placement of `env_file`,
  `ENV_FILE_UNSAFE`), SL (`ReadWritePaths=` of the layout's
  state/cache/data; the unit path `~/.config/systemd/user/vesma.service`),
  control-socket (paths/permissions §3, the fallback WARN).
- **Deferred (v2)**: the system-profile implementation; the hash-pinning
  mandate and lock tooling; secret redaction in relayed lines (SL §6).

## 8. Threat model (mini-STRIDE)

**Assets:** env files with secrets; the venv as a supply chain (code
executed by the supervisor and the children); component data; history
(the transitions journal); the cache as a leak surface when the rule is
violated.

**The contract's boundary:** the layout's filesystem ↔ supervisor /
loader / install flow / doctor (installation and permissions).

The remaining boundaries are the domains of neighboring contracts; here
"trust boundaries: none": the socket (peer authentication, TOCTOU) —
[specs/control-socket/v1](../../control-socket/v1/spec.md) §5; env
passing to the children and the signal space —
[specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md) §7;
manifest loading —
[specs/component-manifest/v1](../../component-manifest/v1/spec.md) §8.

| Category | Threat | Mitigation | Check |
|---|---|---|---|
| **I**nformation Disclosure | lax permissions on env/config (umask, a manual `chmod`) — a secret is read by another local process | fail-closed loader (start refusal on non-`0600` / a foreign owner) + `0700` directories + doctor DR-01 | LY-01, LY-03 |
| **I**nformation Disclosure | secrets in the cache | the write-API rule: a value from an env file is not written; the cache `0750` | LY-12 |
| **I**nformation Disclosure | logs with secrets spread over unaccounted places | the uniqueness of log locations (journald / files-under-state); double writing and "third places" are forbidden | LY-09; line contents — operational control (redaction — v2, SL §6) |
| **T**ampering | tampering with venv/site-packages (a supply chain: substituting a child's/the engine's dependencies) | `0700` permissions, not world-/group-writable site-packages; the owner; freeze drift against the lock; exact-pin `==` | LY-05, LY-06, LY-08, DR-02 |
| **T**ampering | substitution of an env file (a symlink, a foreign owner, a move into the manifest directory) | the fail-closed `ENV_FILE_UNSAFE` loader: outside `components.d`, `0600`, own owner | LY-02, LY-03 |
| **T**ampering | manual edits of the unit/manifest bypassing the install flow | the single writer is the install flow (CM §3.1); doctor drift detection | DR-07, LY-02 |
| **E**levation of Privilege | a user-site leak/overlap of a venv (foreign code in the process's `sys.path`) | `PYTHONNOUSERSITE=1` unconditionally into every python process + doctor DR-03 | LY-07 |
| **E**levation of Privilege | two components on one venv — mutual dependency overlap / module substitution | one venv per python unit; a collision = an error | LY-05, DR-04 |
| **D**enial of Service | disk overflow with logs / history / cache | rotation 10 MB × 5; the cache is regenerable; doctor DR-10 | LY-09, DR-10 |
| **R**epudiation | "who changed the installation?" | the single writer is the install flow (CM §3.1); history append-only; journald append-only | operational control |
| **S**poofing | supervisor/CLI substitution at the socket path | "trust boundaries: none" in this contract — the boundary is the control-socket v1 §5 domain (DAC + `SO_PEERCRED` + the TOCTOU procedure) | the control-socket v1 checklist |

Every mitigation is closed by a conformance check (LY/DR) or marked
"operational control" — there are no silent unverifiable promises.

## 9. Migration from legacy

This contract's main section: the layout exists so that the legacy chaos
gets a target path. The "legacy path → canonical path" table (the
inventory is in the brief of the `vesma-cli-service-management` directive,
2026-10-04):

| Legacy path | Canonical path (layout v1) | Note |
|---|---|---|
| legacy configs under former names in `~/.config` | `~/.config/vesma/vesma.yaml` (shared config) + `~/.config/vesma/components.d/<name>.yaml` (per component) | the legacy name is not preserved: the content is disassembled by purpose — component configs vs shared settings |
| scattered legacy file logs ("logs in 3 places") | journald (systemd) / `~/.local/state/vesma/logs/<name>/` (non-systemd) | one place per mode (§3.7); the old files are archived by the operator and not continued |
| a legacy env file with a token (`0600`) outside the canonical paths | `~/.config/vesma/env/<name>.env` (`0600`, fail-closed loading) | **SHOULD**: the token is rotated on transfer (ADR-0001 §6: rotate first) |
| the former deployment's data with test names | `~/.local/share/vesma/<name>/` | renaming the test names is a separate engine wave, not part of this contract |
| legacy venv trees with versions in the name | `~/.local/share/vesma/venvs/<name>/` | one venv per python unit; versions in the venv name disappear; rebuilt from the lock, not a directory copy |
| artifacts of the retired orchestrator | retired (not migrated) | — |
| ad-hoc launchers (nohup scripts, sh wrappers) | retired (not migrated) | launching = the supervisor by manifests (SL) |

**Migration order:** 1) a `doctor` inventory (DR-01…DR-11 + the
legacy-path list) → 2) transfer per the table (the install flow creates
manifests / env / venvs; the data is moved with owner and permissions) →
3) the component's green conformance → 4) retirement of the legacy
mechanisms (disable + stop of the old units — SL §8).

- **Legacy-deployment migration — not before the first observation window
  closes** (the founding track's telemetry window, founding context — see
  `docs/`); the executor is the engine (card `cli-service-management`);
  the spec fixes the target paths, it does not execute the migration. The
  specs and the CLI code are not subject to the window (as in SL §8).
- The migration point is single: the install flow; a manual transfer of
  directives and scripts is not provided.

**Historical note.** This spec is deliberately genericized (owner's
decision of 2026-10-04): the specifics of the founding environment — the
legacy names, the target machine, the details of the first observation
window — are preserved in the founding pack `docs/` (in particular, the
directives brief `docs/brief-2026-10-04-archcom-founding.md`) and in the
repository's history; for historical continuity, read them together with
this spec.

## 10. References

- [specs/component-manifest/v1](../../component-manifest/v1/spec.md) — the manifest: the placeholder allowlist, the `env_file` rules, `ENV_FILE_UNSAFE`
- [specs/control-socket/v1](../../control-socket/v1/spec.md) — the socket: `control.sock`, paths/permissions §3, the fallback WARN
- [specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md) — the supervisor: structural lines, `SYSLOG_IDENTIFIER`, the unit §3.6, `ReadWritePaths`
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — layer structure and governance; the contract form was ratified by the founding ArchCom on 2026-10-04
- [Founding ArchCom brief](../../../docs/brief-2026-10-04-archcom-founding.md) — the CLI-first directives, the supervisor architecture, the contract interface
- [Glossary](../../../GLOSSARY.md), [ecosystem map](../../../ECOSYSTEM.md)
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/) — the profiles' base directories
- PEP 370 (per-user site-packages), PEP 405 (venv) — venv discipline
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — keyword interpretation

## Translation note

- Mirror date: 2026-10-04; base commit of the normative Russian source:
  `01fb6ed` (`specs/layout/v1/spec.md`).
- This is an informative mirror; in case of divergence the Russian
  `spec.md` prevails.
- Sync policy: the mirror is updated in the same change (single commit) as
  the Russian text; a standalone edit of this file is a process violation.
