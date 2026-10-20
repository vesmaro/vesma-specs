---
contract: layout
version: 2.0.0-draft.1
status: draft
decisions: [ADR-0001, "ADR-0045 (vesmaro/vesma)"]
language: en (informative mirror)
---

# layout v2 — dual-profile layout (user `~/.vesma` + system FHS)

> This is an informative English mirror of the normative Russian
> specification [spec.md](spec.md). In case of divergence, the Russian text
> prevails. The mirror is maintained in the same change as the Russian
> text (single-commit sync policy).
>
> **Status: draft (2.0.0-draft.1).** The contract form — the dual-profile
> installation model (user profile = canon/default, system profile = FHS),
> the single declarative FHS manifest, the `install --system` mechanics,
> doctor gates, unit coexistence — was ratified by the VESMA ArchCom on
> 2026-10-21 ([ADR-0045](https://github.com/vesmaro/vesma/blob/main/docs/project/adr/0045-dual-profile-fhs-layout.md)
> in the engine repository) and is **codified here, not replayed**.
> Stable ratification follows the first conforming implementation
> (wave plan — §7). Post-ratification changes go through the SemVer
> process only.

The keywords MUST / MUST NOT / SHOULD / MAY are to be interpreted per
RFC 2119.

## 1. Scope

Layout v2 fixes the **dual-profile** directory discipline of a VESMA
installation: the "per-user / system-wide" choice is a **first-class
product decision** made at install time, not an environment-driven
technical default. v1 closed the legacy inventory chaos in the user
profile; v2 solves the next pair of problems: (a) the user profile becomes
**self-contained** under `~/.vesma/**` — one tree, one unit of backup,
removal and audit (precedents: `~/.vscode`, `~/.nvm`); (b) the system
profile gets a full FHS implementation — `/etc/vesma`, `/var/lib/vesma`,
`/usr/lib/vesma`, `/var/cache/vesma`, journald — for system-wide
deployments, containers and future deb/rpm packages.

**In scope:**

- the dual-profile model and the profile-choice rule at install time (§3.1);
- user profile v2: the self-contained `~/.vesma/**` tree, the full path
  and permission table, the explicit list of OS-mandated exceptions (§3.2);
- the legacy user-profile generation v1.5 (the v1 XDG spread): normative
  resolution via the generation stamp, without breaking working
  installations (§3.3);
- the system profile: the full FHS table of paths, modes and owners (§3.4);
- the ecosystem placement table: every ecosystem artifact (engine,
  MCP server/entrypoint, agent children, board, metrics, mesh, timers)
  embeds into one structure of both profiles; integration surfaces inside
  foreign harnesses are external (§3.5);
- the argv placeholder extension (§3.6);
- the drop-in manifests directory, `env.d`, the conffile zone (§3.7);
- runtime and profile-derived IPC: user/system units coexist without
  prefixes (§3.8);
- uniqueness of log locations: journald is the canon in both profiles;
  `/var/log/vesma` is a system-profile opt-in (§3.9);
- venv discipline of both profiles: one venv per python unit; in system —
  root-owned venvs with atomic symlink-swap updates (§3.10);
- cache: regenerable, never secrets (§3.11);
- **one declarative FHS manifest** (paths/modes/owners) — the source of
  truth for the installer, the container build and future deb/rpm (§3.12);
- system-profile install/update/uninstall: canonical
  `sudo vesma service install --system`, the install-state manifest →
  exact-inverse uninstall (§3.13);
- doctor gates v2: DR-14…DR-19 (§3.14);
- migration: the v1.5 → v2 user consolidation without breakage; the
  `migrate-store --target=system` reservation (§9).

**Out of scope (domains of sibling contracts and future waves):**

- the component manifest form and `env_file` rules —
  [specs/component-manifest/v1](../../component-manifest/v1/spec.md):
  layout fixes **where**, the manifest fixes **what**;
- supervisor behavior, FSM, the unit template, hardening —
  [specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md);
- the socket protocol, TOCTOU, peer authentication —
  [specs/control-socket/v1](../../control-socket/v1/spec.md): layout
  fixes place and permissions;
- executing the v1.5 → v2 consolidation and the system mover — the engine
  (waves of the ADR-0045 plan); the spec fixes target paths, semantics
  and gates;
- deb/rpm packaging — a future wave: thin wrappers over the FHS manifest
  introducing no packaging logic of their own (§3.12, §7);
- the hash-pinning mandate and lock tooling — deferred (inherited from
  v1 §7);
- secret redaction in forwarded lines — the SL domain (v1 §7).

**Consumers:** the `vesma` engine (the install flow — the single writer
of an installation; the supervisor — the reader-executor; doctor — the
checker; the path resolver — the single source of paths in code),
components (consume paths via placeholders), the container build
(consumes the FHS manifest), future deb/rpm packagers, the conformance
runner `tools/conformance`, external integrators.

## 2. Terminology

The terms Canonical layout, Runtime directory, venv discipline,
Supervisor, Component, Manifest are defined in the
[glossary](../../../GLOSSARY.md) and are not redefined here. The v2
contract terms:

| Term | Meaning |
|---|---|
| installation profile | user (canon/default, self-contained `~/.vesma/**`) or system (FHS, opt-in); the choice is a product decision at install time, recorded by the installation and visible to doctor |
| layout generation | the generation of the user-profile form of a specific installation: `v1.5` (the XDG spread, [layout v1](../v1/spec.md)) or `v2` (self-contained `~/.vesma/**`); stamped at install/consolidation time; the path resolver follows the stamp, not the "current canon" |
| self-contained profile | a profile whose artifacts all live in one root tree (`~/.vesma/**`); exceptions are only OS-mandated points (the explicit list §3.2-a) |
| FHS manifest | the single declarative file of system-profile paths/modes/owners; the source of truth for the installer, the container build and future deb/rpm (§3.12) |
| conffile zone | files that updates (installer, future packages) never silently overwrite: an operator edit is detected, preserved into a backup, and the update does not destroy it (§3.7) |
| install-state | the installation state manifest of the system profile — `/var/lib/vesma/install-state.yaml`: the complete list of what was created (units, files, venv revisions, the sysusers fragment); uninstall is its exact inverse (§3.13) |
| symlink revision | the venv form in the system profile: `venvs/<name>` is a symlink to `venvs/<name>-<rev>/`; an update is an atomic symlink swap (§3.10) |
| IPC directory | the socket and pids directory derived from the profile: user — `${XDG_RUNTIME_DIR}/vesma/`, system — `/run/vesma/` (§3.8) |
| consolidation | the v1.5 → v2 user-profile migration step: moving venv/cache (and the service stack) into `~/.vesma`; does not break a working installation (§9.2) |
| external surface | an integration surface in someone else's domain (harness mcp.json, shell rc lines): the layout documents it, but does not own or maintain it (§3.5) |
| round-trip soak | the observation period of full-cycle runs (install → run → update → uninstall → restore) on a real machine before the production migration executes (pillar 7 of the product-grade standard) |
| doctor | the diagnostic command `vesma doctor --service`; the v1 registry DR-01…DR-13 + the v2 DR-14…DR-19 (§3.14) |

## 3. Contract

### 3.1 Profiles and profile choice

- **MUST**: dual profile — user and system; the profile choice is an
  explicit install-time decision (first class), not a hidden environment
  default.
- **MUST**: the user profile is the canon and the default:
  `vesma service install` without flags installs the user profile;
  system is installed only explicitly: `sudo vesma service install
  --system` (§3.13).
- **MUST**: the installation profile is recorded at install time (the
  profile and layout-generation stamp) and read by the resolver, doctor
  and the CLI; silently switching the profile of an existing installation
  is forbidden.
- **MUST**: the user and system profiles of one machine have **distinct**
  data roots; pointing both profiles at one data root is a configuration
  error, doctor → FAIL (DR-14; the verdict's "ERROR").
- **MAY**: both profiles coexist on one machine (a user's personal stack
  plus the system stack) — with separated IPC and data (§3.8, §3.4).
- **MUST**: paths are resolved **only** by the engine resolver from the
  tables §3.2/§3.4 and the generation stamp; hardcoding paths outside the
  resolver violates the contract.
- **MUST**: a working installation does not change its path resolution
  without an explicit operator migration step (consolidation §9.2, the
  system mover §9.3): a canon change does not rewrite live installations.

### 3.2 User profile v2 (self-contained `~/.vesma/**`, normative)

The user profile v2 is one tree `~/.vesma/`, owned by the supervisor
user. The existing `~/.vesma` content (the engine store home: `vesma.db`,
`data/`, `vault/`, `config.yaml`, `completion/`, `logs/vesma.log` + audit
journals) stays as is — the table does **not** replay the engine store
home (the ADR-0044 canon); it embeds the service stack into the same
tree.

MUST table (root `~/.vesma`, directory `0700` unless stated otherwise):

| Path | Contents | Mode |
|---|---|---|
| `~/.vesma/config.yaml` | the shared config; a component's config = a section of the shared config (CM §3.9) | file `0600` |
| `~/.vesma/components.d/<name>.yaml` | component manifests (drop-in; install adds, uninstall removes) | dir `0700` |
| `~/.vesma/env.d/<name>.env` | env files of secrets | file `0600`; fail-closed loading (CM §3.5) |
| `~/.vesma/components/<name>/` | component data; the child's default cwd; the component's `config.schema.json` (`config.schema_file` resolves from the component data dir, CM §3.9) | dir `0700` |
| `~/.vesma/venv/` | the engine venv (supervisor runtime): the engine + in-process modules; the only venv outside `venvs/` | dir `0700` |
| `~/.vesma/venvs/<name>/` | the venv of a python child component | dir `0700` |
| `~/.vesma/logs/<name>/` | file logs (files-under-state mode, §3.9); rotation 10 MB × 5 | dir `0700` |
| `~/.vesma/history/` | the supervisor transition journal (append-only) | dir `0700` |
| `~/.vesma/run/` | the runtime fallback (socket, pids) when `XDG_RUNTIME_DIR` is empty/unusable + WARN | dir `0700` |
| `~/.vesma/cache/<name>/` | regenerable; NEVER secrets (§3.11) | dir `0750` |
| `${XDG_RUNTIME_DIR}/vesma/` | the canonical runtime: `control.sock` `0600`, pids | dir `0700` |

Notes:

- **a. OS-mandated exceptions** (the complete list; everything else lives
  inside `~/.vesma`):
  1. **the systemd user unit dir** — `~/.config/systemd/user/`: systemd
     reads user units only from there. The canonical unit storage is
     `~/.vesma/systemd/user/vesma.service`; the install flow places a
     copy/symlink into the systemd dir and refreshes `daemon-reload`.
     Canonical ↔ installed drift is caught by doctor (DR-18).
  2. **`${XDG_RUNTIME_DIR}/vesma/`** — sockets must live on a runtime FS
     (tmpfs semantics); the `~/.vesma/run/` fallback + WARN is the v1
     rule (control-socket v1 §3), preserved.
  3. **shell rc lines** (sourcing completion) — an external surface:
     documented, not maintained by the layout.
  4. **journald** — the canonical log sink under systemd (an OS service,
     not a path).
- **b.** The XDG variables (`XDG_CONFIG_HOME`, `XDG_DATA_HOME`,
  `XDG_STATE_HOME`, `XDG_CACHE_HOME`) do **not** participate in the v2
  user-profile resolution; the profile's only XDG variable is
  `XDG_RUNTIME_DIR` (item a.2).
- **c.** Modes are set explicitly at creation (never inherited from
  umask); a directory with weakened permissions is fail-closed for the
  corresponding operation (the v1 §3.1 rule is preserved).
- **d.** The engine store-home tree (`data/`, `vault/`, top-level `logs/`,
  `vesma.db`) is the ADR-0044 canon domain; component subdirectories
  `logs/<name>/` do not collide with engine files in `logs/`.
- **e.** Component names are validated against the **reserved-name
  registry of the tree**: `venv`, `venvs`, `components`, `components.d`,
  `env.d`, `cache`, `logs`, `history`, `run`, `completion`, `systemd`,
  `data`, `vault`, `install-state.yaml`; a collision = an install
  validation refusal (the v1 §3.8 mechanism extended additively; the
  registry MAY grow in a minor version).
- **f.** `venvs/<name>/` is only for python child components; in-process
  components live on the engine venv; non-python children have no venv
  (the v1 §3.8 rule is preserved).

### 3.3 User profile v1.5 (legacy generation, normative for existing installs)

- **MUST**: installations deployed in the [layout v1](../v1/spec.md) form
  (generation `v1.5` — the XDG spread `~/.config/vesma`,
  `~/.local/share/vesma`, `~/.local/state/vesma`, `~/.cache/vesma`)
  keep resolving paths per the v1 tables until the consolidation runs
  (§9.2): a canon change does not break working installations
  (zero-regression; pin tests for both generations — wave 1 of the
  ADR-0045 plan).
- **MUST**: new user installations are created only in the v2 form (§3.2).
- **MUST NOT**: the engine never writes to the v1.5 paths of a v2
  installation or vice versa; mixed writing (part of the artifacts in
  v1.5, part in v2 places of one installation) is drift, doctor → FAIL
  (DR-17).
- **SHOULD**: doctor flags a v1.5 installation with an advisory finding
  (DR-19) carrying the ready-to-run consolidation command.

### 3.4 System profile (FHS, normative)

The system profile is for system-wide deployments: a dedicated service
account, system units, package-grade discipline. Root decisions:

- the `vesma:vesma` service account is created by a sysusers.d fragment
  (a system user, shell login forbidden, home `/var/lib/vesma`);
- configuration is root-owned and group-readable by `vesma`; secrets
  (`env.d`) are `0600`, group/world reading is excluded;
- variable data (including the engine store home) — `/var/lib/vesma`;
- code (venvs) — `/usr/lib/vesma`, distro static — `/usr/share/vesma`;
  the runtime never writes into these trees.

MUST table:

| Path | Contents | Mode/owner |
|---|---|---|
| `/etc/vesma/` | the configuration root | dir `0750 root:vesma` |
| `/etc/vesma/config.yaml` | the shared config (CM §3.9) | file `0640 root:vesma`; conffile zone |
| `/etc/vesma/components.d/<name>.yaml` | component manifests (drop-in) | file `0640 root:vesma`; conffile zone; dir `0750 root:vesma` |
| `/etc/vesma/env.d/<name>.env` | env files of secrets | file `0600 root:vesma`¹; dir `0750 root:vesma` |
| `/usr/lib/sysusers.d/vesma.conf` | the sysusers fragment: user+group `vesma` | file `0644 root:root` |
| `/etc/systemd/system/vesma.service` | the system supervisor unit (generated by the install flow) | file `0644 root:root` |
| `/usr/lib/vesma/venv/` | the engine venv; symlink revisions (§3.10) | tree `0755 root:root`; site-packages not group/world-writable |
| `/usr/lib/vesma/venvs/<name>` | a python component's venv; a symlink to the `<name>-<rev>/` revision | as above |
| `/usr/share/vesma/` | distro static: bundle manifests, config schemas, unit templates, completion | dirs `0755 root:root`, files `0644 root:root`; runtime reads only |
| `/var/lib/vesma/` | the data root: the engine store home (vesma.db, `data/`, `vault/`) + component data | dir `0750 vesma:vesma` |
| `/var/lib/vesma/vesma.db` | the engine store DB | file `0600 vesma:vesma` |
| `/var/lib/vesma/<name>/` | component data; the child's default cwd | dir `0750 vesma:vesma`; DB and secret-like files `0600` |
| `/var/lib/vesma/history/` | the supervisor transition journal (append-only) | dir `0750 vesma:vesma` |
| `/var/lib/vesma/install-state.yaml` | the installation state manifest (exact-inverse uninstall, §3.13) | file `0640 root:vesma`; the writer is the install flow |
| `/var/cache/vesma/<name>/` | regenerable, never secrets (§3.11) | dir `0750 vesma:vesma` |
| `/var/log/vesma/<name>/` | file logs — **opt-in only** (§3.9) | dir `0750 vesma:vesma`; not created without opt-in |
| `/run/vesma/` | IPC: `control.sock`, pids | `RuntimeDirectory=vesma`, `RuntimeDirectoryMode=0750`; owned by the unit `User=`/`Group=`; the socket — control-socket v1 §3 |

¹ The owner of `env.d` files is the service account the supervisor reads
under (design default `root:vesma`; the final pin is the units wave of
the ADR-0045 plan). The invariant is normative: `0600`, no group/world
read, only the supervisor service account reads; any drift is a doctor
FAIL (DR-15), loading is fail-closed (CM §3.5).

Notes:

- **a.** The user → system role mapping (the v1 1:1 principle is
  preserved where the OS does not mandate otherwise): configuration
  `~/.vesma` → `/etc/vesma`; data/state `~/.vesma` → `/var/lib/vesma`;
  code (venvs) `~/.vesma` → `/usr/lib/vesma`; static (inside the wheel in
  user) → `/usr/share/vesma`; file logs → `/var/log/vesma` (opt-in);
  runtime → `/run/vesma`.
- **b.** The `vesma-oper` group from the v1 §3.3 design table is **not
  introduced**; operator group access to the system socket is an open
  question of the units wave (the ADR-0045 registry); until then,
  system-IPC access is root.
- **c.** `/var/log/vesma` does not exist in the user profile in any form;
  in system it is opt-in only (§3.9).

### 3.5 Ecosystem placement table

Every ecosystem artifact embeds into the one structure of both profiles.
Runtime classes: the engine and in-process components — the engine venv;
python children — their own venv; non-python children — an executable
without a venv; timers — systemd timer units (the OS zone §3.2-a).

| Ecosystem artifact | Class | user (v2) | system |
|---|---|---|---|
| the `vesma` engine (supervisor, API, MCP server/entrypoint) | in-process (engine venv) | `~/.vesma/venv/` | `/usr/lib/vesma/venv/` |
| a python child component (e.g. the worker class) | component venv | `~/.vesma/venvs/<name>/` | `/usr/lib/vesma/venvs/<name>` (symlink revisions) |
| a non-python child component (e.g. the mesh class) | binary without a venv | inside the engine venv / bundle | `/usr/share/vesma/` (static) |
| board, metrics (the in-process bundle) | in-process | `~/.vesma/venv/` | `/usr/lib/vesma/venv/` |
| agent children (per manifests) | per the child class | the §3.2 table slots | the §3.4 table slots |
| a component manifest | configuration | `~/.vesma/components.d/<name>.yaml` | `/etc/vesma/components.d/<name>.yaml` |
| the shared config | configuration | `~/.vesma/config.yaml` | `/etc/vesma/config.yaml` |
| component env secrets | secrets | `~/.vesma/env.d/<name>.env` | `/etc/vesma/env.d/<name>.env` |
| component data | data | `~/.vesma/components/<name>/` | `/var/lib/vesma/<name>/` |
| supervisor state (history) | data | `~/.vesma/history/` | `/var/lib/vesma/history/` |
| logs (journald canon; the file mode) | logs | `~/.vesma/logs/<name>/` (files-under-state) | journald primary; `/var/log/vesma/<name>/` — opt-in |
| a component's cache | cache | `~/.vesma/cache/<name>/` | `/var/cache/vesma/<name>/` |
| socket and pids | IPC | `${XDG_RUNTIME_DIR}/vesma/` | `/run/vesma/` |
| the supervisor unit | OS unit | canonical `~/.vesma/systemd/user/vesma.service` → `~/.config/systemd/user/` (§3.2-a.1) | `/etc/systemd/system/vesma.service` |
| timer units (e.g. self-update) | OS unit | `~/.config/systemd/user/` (canonical in `~/.vesma/systemd/user/`) | `/etc/systemd/system/` |
| distro static (bundle manifests, schemas) | delivery | inside the wheel (`importlib.resources`) | `/usr/share/vesma/` |
| completion | delivery | `~/.vesma/completion/` (the rc line — external) | `/usr/share/vesma/completion/` (the rc line — external) |
| integrations in foreign harnesses (a harness's mcp.json) | **external surface** | outside the tree; documented, not maintained | outside the tree; documented, not maintained |

- **MUST**: a component never hardcodes its placement — it receives
  paths via placeholders (§3.6) and the canonical slots of the tables; a
  new ecosystem entity embeds through the table (an additive change, a
  minor version).
- **MUST**: external surfaces are not maintained by the layout: creating
  entries in foreign domains (mcp.json, shell rc) belongs to the
  corresponding engine integration flow; the layout only requires that
  such entries point at the canonical paths of this contract.

### 3.6 Argv placeholder extension

Manifest placeholders (the allowlist — CM §2) are expanded by the
supervisor at spawn per the MUST table:

| Placeholder | User (v2) | System |
|---|---|---|
| `{config_path}` | `~/.vesma/config.yaml` | `/etc/vesma/config.yaml` |
| `{data_dir}` | `~/.vesma/components/<name>/` | `/var/lib/vesma/<name>/` |
| `{runtime_dir}` | `${XDG_RUNTIME_DIR}/vesma/` (fallback `~/.vesma/run/`) | `/run/vesma/` |
| `{venv_bin}` | `~/.vesma/venvs/<name>/bin` | `/usr/lib/vesma/venvs/<name>/bin` (through the symlink revision) |

- **MUST**: there are no other substitutions — no shell, no environment
  interpolation (CM §3.5); the supervisor performs the expansion.
- **MUST**: `{venv_bin}` is not expanded for a component without a venv;
  a `{venv_bin}` reference without a venv = a fail-closed start refusal.
- **MUST**: for the legacy v1.5 generation, placeholders expand per the
  v1 §3.4 table (the generation stamp, §3.3).

### 3.7 Manifests directory, env.d and the conffile zone

- **MUST**: the manifests directory = the profile's `components.d/`
  (§3.2/§3.4); the file name == `metadata.name`; every file in the
  directory must be a valid manifest — an invalid one is a fail-closed
  loading error (the v1 §3.5 rule preserved).
- **MUST**: drop-in discipline: install atomically creates/updates the
  file (tmp + rename), uninstall removes it; the only writer is the
  install flow.
- **MUST (conffile zone)**: `config.yaml` and `components.d/` of both
  profiles are the conffile zone: an update (the installer, a future
  package) never silently overwrites a file carrying an operator edit;
  the divergence is detected, the edit is preserved into a backup (the
  engine `.pre-regen.bak` discipline), and the operator gets an explicit
  choice. Future deb/rpm must declare these paths conffiles of their
  package format.
- **MUST**: env files live at the profile's `env.d/<name>.env`, mode
  `0600`, fail-closed loading (not `0600` / foreign owner / declared but
  missing = a start refusal with the ready-to-run fix command; CM §3.5,
  `ENV_FILE_UNSAFE`); in the system profile, an env.d permission drift is
  a doctor FAIL (DR-15, the verdict's gate).
- **MUST**: the install flow places created env files only at
  `env.d/<name>.env`.

### 3.8 Runtime, IPC and unit coexistence

- **MUST**: user/system units coexist **without prefixes**: both are
  named `vesma.service` in their systemd scopes
  (`~/.config/systemd/user/` and `/etc/systemd/system/`); they are
  distinguished by the systemd scope, not the name.
- **MUST**: IPC is derived from the profile: user —
  `${XDG_RUNTIME_DIR}/vesma/` (`0700`, fallback `~/.vesma/run/` + WARN),
  system — `/run/vesma/` (`RuntimeDirectory=vesma`,
  `RuntimeDirectoryMode=0750`).
- **MUST**: socket artifacts are governed by control-socket v1 in full
  (the TOCTOU/SYMLINK bind procedure, peer authentication, no TCP); the
  layout fixes place and permissions.
- **MUST**: CLI commands touching both profiles distinguish the profiles
  explicitly; the default is user; the flag mechanics are the engine's
  implementation freedom.
- **MUST NOT**: no persistent state in the IPC directory (tmpfs
  semantics; the v1 §3.6 rule preserved).

### 3.9 Logs and the transition journal

- **MUST** (the canon under systemd, both profiles): everything to
  journald; the supervisor stamps `SYSLOG_IDENTIFIER=vesma-<component>`
  (SL §3.4); `vesma service logs` is a journalctl filter, not a file
  grep.
- **MUST** (user, container/manual mode): files-under-state —
  `~/.vesma/logs/<name>/`, rotation 10 MB × 5.
- **MUST** (system): `/var/log/vesma/<name>/` is **opt-in**: file logs
  are created only when the operator explicitly enables them; the default
  is journald only. Opt-in never enables double writing: exactly one mode.
- **MUST NOT**: no "third places" for logs; double writing to both places
  is forbidden (the v1 §3.7 rule preserved).
- **MUST**: history is append-only, at the table paths (§3.2/§3.4);
  contents are structured lines (SL §3.4).

### 3.10 venv discipline

Both profiles inherit the v1 §3.8 rules: one managed venv per python
unit; two components on one venv = an error; `PYTHONNOUSERSITE=1`
injected unconditionally into every python process; dependencies pinned
exactly (`==`) against the lock; sources — PyPI only; site-packages not
world- or group-writable; a manual `pip install` into a managed venv is a
freeze drift (DR-02). Profile additions:

- **MUST** (user): the venv tree — `~/.vesma/venv/` (engine) and
  `~/.vesma/venvs/<name>/` (children), `0700`, owned by the user.
- **MUST** (system): venvs are root-owned (`/usr/lib/vesma/venv`,
  `/usr/lib/vesma/venvs/<name>`), tree `0755 root:root`; runtime writes
  are excluded (only the install flow modifies, from root).
- **MUST** (system): a component venv is a **symlink revision**:
  `<name>-<rev>/` is the materialized revision (the revision name is the
  installation content id), `venvs/<name>` is the symlink to the active
  revision; an update = an atomic symlink swap (tmp + rename), and the
  previous revision is removed only after a successful swap and a
  liveness check.
- **MUST** (system): the installer materializes venvs: `uv venv` +
  installing **the wheel of the same build** the installer runs from;
  `sudo pip` / pip-as-root are forbidden.
- **MUST** (system): a revision symlink resolves inside its own root
  (`/usr/lib/vesma/venvs/`); a symlink pointing outside is a doctor FAIL
  (DR-16).

### 3.11 Cache

- **MUST**: the profile's `cache/<name>/` (`~/.vesma/cache/<name>/`
  `0750`; `/var/cache/vesma/<name>/` `0750 vesma:vesma`) holds only
  regenerable content; removing it at any moment does not change the
  installation's correctness.
- **MUST**: the cache NEVER contains secrets; enforcement is the engine's
  taint write-API (the v1 §3.9 rule, LY-12 preserved).
- **MUST NOT**: configs, manifests, env content, logs and state data are
  never placed in the cache.

### 3.12 The FHS manifest — the single source of truth for paths

- **MUST**: there is **one** declarative FHS-path manifest (shipped with
  the engine distribution) enumerating every system-profile path and its
  user-profile correspondence; minimum fields — `role` (the semantic role
  of the §3.2–§3.5 table row), `user_path`, `system_path`, `mode`,
  `owner`, `group`, `flags` (e.g. `conffile`, `opt-in`,
  `symlink-revision`).
- **MUST**: manifest consumers: the `install --system` installer, the
  container build, future deb/rpm packaging; each builds its artifacts
  from the manifest, not from its own path lists.
- **MUST**: in engine code, system-profile paths are resolved only
  through the manifest (the resolver); duplicating paths in code/units/
  scripts bypassing the manifest violates the contract (DR-15 cross-checks
  the unit and the tree against the manifest).
- **MAY**: the operator override the placement base (e.g. an `/opt/
  vesma`-shape) via an explicit manifest override mechanism; an override
  is validated at install time and checked by doctor; an unvalidated
  override = WARN.
- **MUST**: the serialization form is YAML; the field schema is fixed by
  this contract's `examples/example-fhs-manifest.yaml`; narrowing/renaming
  fields = MAJOR.

### 3.13 Install, update, uninstall (system profile)

- **MUST**: the canonical system-profile installer is `sudo vesma service
  install --system`; the install is idempotent (a re-run is a no-op or an
  explicit refresh, never duplicate artifacts).
- **MUST**: the installer creates the service account through the
  sysusers.d fragment (idempotent: a re-run does not duplicate the
  account).
- **MUST**: the installer maintains the install-state
  (`/var/lib/vesma/install-state.yaml`): every created artifact (a unit,
  a file, a venv revision, the sysusers fragment, a directory) is recorded
  at/before creation.
- **MUST**: uninstall (`sudo vesma service uninstall --system`) is the
  exact inverse of the install-state: only the recorded artifacts are
  removed, in reverse order; foreign files are never touched; a
  state ↔ filesystem drift is a loud refusal offering doctor (DR-17),
  never a silent skip.
- **MUST**: a system-profile update is mode-aware: the new venv revision
  is materialized nearby, the symlink is swapped atomically, and the
  previous revision is removed after a successful swap + health check
  (pillar 4 of the product-grade standard).
- **MUST NOT**: the system-profile installer never runs `pip` as root
  (§3.10) and never writes into foreign venvs (the environment-isolation
  rule — the owner's global rule 8).

### 3.14 Doctor gates v2 (`vesma doctor --service`)

The v1 registry (DR-01…DR-13) applies to the user profile up to the
generation paths (§3.3). v2 adds:

| ID | Check | Details |
|---|---|---|
| DR-14 | profile data-root isolation | user and system profiles on one data root (overlapping data/config roots) = FAIL (the verdict's "ERROR") + the fix command |
| DR-15 | system-profile permissions | cross-check the tree against the FHS manifest: `/etc/vesma` `0640/0750 root:vesma`, `env.d` `0600` (drift = FAIL — the verdict's gate), `/var/lib/vesma` `0750 vesma:vesma`, DB `0600`, cache/logs `0750`; the unit matches the manifest |
| DR-16 | system venv revisions | the `venvs/<name>` symlink resolves inside `/usr/lib/vesma/venvs/`, the target is root-owned and not group/world-writable; the active revision's `freeze` == lock; orphan revisions — WARN |
| DR-17 | install-state ↔ filesystem | a dry inversion of the state manifest: every artifact in place, no foreign intrusion into canonical roots; drift = FAIL (system) / FAIL (user: mixed generations §3.3) |
| DR-18 | unit drift of both profiles | the installed unit == the canonical storage (`~/.vesma/systemd/user/`, `/etc/systemd/system/`) == the install-flow regeneration; a mismatch = FAIL + the command |
| DR-19 | the user-profile layout generation | a v1.5 installation: an advisory (INFO/WARN) with the ready consolidation command; a mixed tree = FAIL (DR-17) |

- **MUST**: every finding carries an `OK`/`WARN`/`FAIL` severity and a
  ready-to-run fix command with the real path; doctor never executes the
  commands itself (the v1 §3.10 rules preserved).

## 4. Error codes

Not applicable: the contract introduces no protocol and no code registry
of its own. Sibling-boundary codes: `ENV_FILE_UNSAFE` — CM v1 §4; socket
protocol codes — control-socket v1 §4.6; doctor finding codes MAY be
added additively (a minor version) during engine implementation.

## 5. Examples

The minimum example is mandatory for merging (ADR-0001 §1); examples
carry placeholders only — no real tokens, machine paths or secrets
(ADR-0001 §6).

| File | What it shows |
|---|---|
| `examples/example-tree-user-v2.txt` | the self-contained user-profile v2 tree with modes in comments |
| `examples/example-system-tree.txt` | the system-profile (FHS) tree with modes and owners |
| `examples/example-fhs-manifest.yaml` | the FHS manifest form: roles, both profiles' paths, modes, owners, flags |

## 6. Conformance

The checklist — [conformance/checklist.md](conformance/checklist.md).
The v2 gate consists of three series:

- **LY-01…LY-14** — the user-profile rules, retargeted to the §3.2 table
  (semantics inherited from v1; v1's LY-13 is superseded by the SY
  series);
- **LY-15, LY-16** — layout generations: pinning existing v1.5
  installations (zero-regression) and the mixed-writing ban;
- **SY-01…SY-12** — the system profile: §3.4 modes/owners, the conffile
  zone, the env.d FAIL gate, symlink revisions, install-state
  exact-inverse, the DR-14 isolation gate.

Check types — "auto"/"manual" as in v1; the `tools/conformance` runner
validates declarations, file checks are executed by the engine
(ADR-0001 §4). The contract is ratified by the first full green pass per
the ADR-0045 wave plan (§7); waves introduce the SY series as
implementation lands.

## 7. Compatibility

- **SemVer**: `2.0.0-draft.1`; ratification by implementation →
  `2.0.0` stable. A MAJOR version: the user-profile table is redrawn
  (the XDG spread → self-contained `~/.vesma`), the shared-config name is
  aligned with the engine canon (v1 `vesma.yaml` → `config.yaml`), the
  env directory is renamed (`env/` → `env.d/`), the v1 §3.3 system table
  is replaced in full (venvs → `/usr/lib/vesma`, `/var/log/vesma`
  MUST NOT → opt-in, `vesma-oper` not introduced). The breaking change is
  legitimized by the MAJOR bump (the CI breaking-change detector).
- **Continuity of deployed installations**: the generation stamp (§3.1,
  §3.3) preserves the resolution of working v1.5 installations; the
  transition happens only through an explicit consolidation (§9.2). This
  is the MAJOR-inclusion condition: the contract breaks, working
  installations do not.
- **The v1 spec**: the `v1/` directory is immutable (ADR-0001 §2); at v2
  ratification, v1 receives `deprecated(v1→v2)` with the window per
  ADR-0001 §2 (the window decision is an act of ratification, not of
  this wave).
- **Consumers**: CM (`env_file` → `env.d/`, placeholders §3.6), SL
  (`ReadWritePaths` from the tables, unit paths §3.8), control-socket
  (IPC paths §3.8); prose/example edits of sibling specs are separate
  additive PRs — this contract neither executes nor touches their files.
- **Deferred (inherited from v1 §7)**: the hash-pinning mandate and lock
  tooling; secret redaction in forwarded lines (SL §6).

## 8. Threat model (mini-STRIDE)

**Assets** (inherited from v1 §8): env files of secrets; venvs as a
supply chain; component data and the engine store; history; the cache.
**New v2 assets**: the install-state (tampered → a wrong uninstall); the
venv revision symlinks; the `~/.vesma` tree itself as the user's single
private contour.

**Contract boundary:** the layout filesystem ↔ supervisor / loader /
install flow / doctor; in the system profile — the root ↔ service account
boundary (DAC).

| Category | Threat | Mitigation | Check |
|---|---|---|---|
| **I**nformation Disclosure | lax env.d/config permissions (both profiles) | env.d `0600` + the fail-closed loader; `/etc/vesma` `0640/0750 root:vesma`; `~/.vesma` `0700` | LY-01/LY-03, SY-03 |
| **I**nformation Disclosure | secrets in the cache | the taint write-API; cache `0750` | LY-12 |
| **I**nformation Disclosure | logs in unaccounted places | uniqueness of log places; `/var/log/vesma` — a system opt-in, forbidden in user | LY-09, SY-06 |
| **T**ampering | venv substitution (supply chain) | user: `0700`, owned; system: root-owned, tree `0755 root:root`, tampering requires root; freeze == lock | LY-05/LY-06, SY-07 |
| **T**ampering | a venv revision symlink pointing outside (code substitution via a link) | the symlink must resolve inside its own root | DR-16, SY-07 |
| **T**ampering | install-state tampering → uninstall removes/keeps the wrong things | the state is written only by the install flow (`0640 root:vesma`); a drift = a loud uninstall refusal; only recorded artifacts are removed | DR-17, SY-09 |
| **T**ampering | a silent overwrite of operator configs by an update | the conffile zone: the edit is detected, backup + an explicit choice | SY-05 |
| **E**levation of Privilege | user-site leakage; two components on one venv | `PYTHONNOUSERSITE=1`; one venv per unit (inherited from v1) | LY-07, DR-03/04 |
| **E**levation of Privilege | pip-as-root / writes into foreign venvs | venvs materialized by `uv venv` + the same-build wheel; foreign venvs refused | SY-08 |
| **D**enial of Service | disk overflow by logs/cache | rotation 10 MB × 5; the cache is regenerable; DR-10 (inherited) | LY-09, DR-10 |
| **R**epudiation | "who changed the installation?" | the only writer is the install flow; the install-state append/update; history append-only; journald | SY-09, operational control |
| **S**poofing | substitution on the socket path | "trust boundaries: none" — the control-socket v1 §5 domain; the profiles' IPC directories are isolated (`/run/vesma` vs the user runtime) | the control-socket v1 checklist, DR-14 |

Every mitigation is closed by a conformance check or marked "operational
control" — no silent unverifiable promises.

## 9. Migration

### 9.1 Legacy (inherited from v1 §9)

The v1 §9 "legacy path → canonical path" table applies to the v1.5 form;
the order (doctor inventory → transfer → green conformance → disposal of
legacy mechanisms) and the founding-window constraint are preserved. The
v1 table's target paths map into the v2 canon through §3.2 (the
consolidation below).

### 9.2 Consolidation of user installations v1.5 → v2

- **MUST**: the consolidation is an explicit operator migration step,
  never a side effect of an update; the candidate vehicle — an extension
  of `vesma self-update apply` / `vesma service install` (the choice
  belongs to the mover wave of the ADR-0045 plan).
- **MUST**: the order: a doctor inventory → stop the stack → transfer the
  artifacts per the correspondence table (venv → `~/.vesma/venv|venvs/`,
  cache → `~/.vesma/cache/`, the service stack `components.d`/`env.d`/
  `components/` into `~/.vesma/`) → stamp generation v2 → a green doctor.
  The transfer is a verified move; the source is removed only after the
  green check (the ADR-0044 discipline: staging → verify → publish).
- **MUST**: a working v1.5 installation without consolidation keeps
  working (§3.3): the consolidation does not break, it converts.
- **MUST NOT**: the consolidation never touches the engine store home
  (`vesma.db`, `data/`, `vault/`, `config.yaml` — already in `~/.vesma`)
  or external surfaces (mcp.json, shell rc — only their own flows
  regenerate those pointers).

### 9.3 Production migration to the system profile — NOT now

- **MUST NOT**: an executed migration of the existing production into the
  system profile is not part of this wave and never runs without a
  separate owner's word.
- **MUST**: `vesma migrate-store` reserves the `--target=system`
  extension (the goal — moving the store home and the service stack into
  the §3.4 FHS trees); the target's contract is a separate ratification
  at activation time.
- **MUST**: the activation precondition is the system-profile round-trip
  soak (full install → run → update → uninstall → restore cycles on a
  real machine; pillar 7 of the product-grade standard).

## 10. References

- [specs/layout/v1](../v1/spec.md) — the previous contract version (the
  XDG-form user profile; the legacy generation §3.3)
- [ADR-0045](https://github.com/vesmaro/vesma/blob/main/docs/project/adr/0045-dual-profile-fhs-layout.md)
  (vesmaro/vesma) — the ArchCom verdict of 2026-10-21: dual-profile, the
  FHS manifest, `install --system`, the wave plan
- [ADR-0044](https://github.com/vesmaro/vesma/blob/main/docs/project/adr/0044-store-migration.md)
  (vesmaro/vesma) — the store mover: the staging → verify → publish
  discipline carried over to the consolidation and the system mover
- [specs/component-manifest/v1](../../component-manifest/v1/spec.md) —
  the placeholder allowlist, `env_file` rules, `ENV_FILE_UNSAFE`
- [specs/control-socket/v1](../../control-socket/v1/spec.md) — the
  socket: `control.sock`, paths/modes §3, the fallback WARN
- [specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md) — the
  supervisor: structured lines, `SYSLOG_IDENTIFIER`, unit hardening
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — the
  structure and governance of the specs layer
- [Glossary](../../../GLOSSARY.md), [ecosystem map](../../../ECOSYSTEM.md)
- the 7-pillar product-grade distribution standard — pillars: idempotent
  install (2), exact-inverse uninstall (3), mode-aware update (4), state
  tracking (5), round-trip acceptance (7) — the GCW canon
  `product-grade-distribution`
- [FHS 3.0](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html) —
  `/etc`, `/var/lib`, `/var/cache`, `/var/log`, `/usr/lib`, `/usr/share`
- systemd: [sysusers.d](https://www.freedesktop.org/software/systemd/man/latest/systemd-sysusers.html),
  [RuntimeDirectory](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — keyword
  interpretation
