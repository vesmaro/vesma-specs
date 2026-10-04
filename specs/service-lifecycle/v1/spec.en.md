---
contract: service-lifecycle
version: 1.0.0-draft.1
status: draft (ратифицируется первой реализацией в движке vesma)
decisions: [ADR-0001]
ratified: учредительный АрхКом VESMA, 2026-10-04
language: en (informative mirror)
---

# service-lifecycle v1 — supervisor contract

> This is an informative English mirror of the normative Russian
> specification [spec.md](spec.md). In case of divergence, the Russian text
> prevails. The mirror is maintained in the same change as the Russian text
> (single-commit sync policy).

The keywords MUST / MUST NOT / SHOULD / MAY are to be interpreted per
RFC 2119. In the normative document the prose is Russian; identifiers,
directives, and field values are English.

## 1. Scope

This contract defines the behavior of the **supervisor** — the single
long-lived `vesma` process that owns the lifecycle of all ecosystem
components on the machine: launch, health, restart, stop, observability.

**In scope:**

- the process model (sessions, groups, reaping, PID1 mode);
- isolation: a child crash ≠ a crash of the supervisor and the control
  socket;
- the child FSM and the transition table;
- structural observability lines (a fixed format);
- per-tier restart policies (core / optional) with contractual numbers;
- start and graceful-stop ordering (topological / reverse-topological);
- exactly one systemd unit above the vesma process: template + hardening
  block;
- threat model (mini-STRIDE) and migration from legacy launch mechanisms.

**Out of scope (domains of neighboring contracts):**

- the shape and fields of the component manifest —
  `specs/component-manifest/v1` (the manifest is the supervisor's input;
  the supervisor consumes, it does not define);
- the CLI ↔ live supervisor protocol — `specs/control-socket/v1`;
- canonical paths (configs, state, cache, data, socket) —
  `specs/layout/v1`;
- the health-probe semantics of a specific component — the health section
  of its manifest;
- server deployments (container/orchestrator profiles) — the engine track.

The supervisor is implemented by the `vesma` engine (card
`cli-service-management`); this contract is the source of requirements and
the gate of conformance checks.

## 2. Terminology

| Term | Meaning |
|---|---|
| supervisor | the `vesma` process owning the components' lifecycle; in in-process mode it also hosts the core (memory server + API) |
| child (child process) | a component's child process spawned by the supervisor according to the launch manifest |
| component | an ecosystem unit declared by a manifest (`specs/component-manifest/v1`); an in-process component lives in the supervisor process, a child-process runs as a separate process |
| tier | the criticality tier: `core` (the mandatory core) or `optional` |
| FSM | the child's finite state machine: `stopped → starting → healthy → degraded → backoff → stopped`, plus `blocked` |
| health pass | one successful result of a health check from the component's manifest |
| "up" | the component state = the first successful health pass after spawn |
| backoff | the pause before the next restart attempt (exponential, with jitter) |
| crash-loop | a series of restarts without reaching healthy; for core — 10 attempts |
| grace period | the window between SIGTERM and SIGKILL at stop (from the manifest's stop semantics) |
| pgid | the process-group id; the child's pgid == pid (setsid) |
| subreaper | a process with `prctl(PR_SET_CHILD_SUBREAPER, 1)`: orphaned descendants are reparented to it |
| lazy-retry | a rare background restart attempt without alert spam (for optional after the budget is exhausted) |
| control socket | the unix socket for managing the live supervisor (`specs/control-socket/v1`) |
| unit | the generated systemd unit `vesma.service` (user or system profile) |

## 3. Contract

### 3.1 Process model

**Sessions and groups.** Every child is started with
`start_new_session=True` (setsid): the child's pgid == its pid.
Consequence: the child and all its descendants form one POSIX session
addressable by a single number. Stopping a component is `kill(-pgid, …)`
over the group. **Inventorying processes by name (pkill) is forbidden and
unnecessary by construction** — the chaos-inventory antipattern (killing
other people's processes by a name pattern) disappears constructively.

**Reaping.** SIGCHLD → an `os.waitpid(-1, WNOHANG)` loop until exhaustion
(ECHILD). No exited child remains a zombie.

**Subreaper.** MUST: the supervisor sets
`prctl(PR_SET_CHILD_SUBREAPER, 1)`. Orphaned grandchildren (descendants of
children that outlive their parent) are reparented to the supervisor and
reaped by it — zombies do not settle in init and are not lost from under
control.

**PID1 mode (container).** The same binary; the supervisor takes the role
of the container's PID 1. MUST: mandatory SIGTERM/SIGINT handlers; reap of
all orphans; a graceful stop of the children BEFORE exit. Conformance case:
"PID1 reaps an orphaned grandchild".

**In-process core.** The memory server + API is an in-process component
living in the supervisor process. Death of the in-process core = death of
the supervisor → systemd unit restart. Fail-fast is covered naturally; no
separate core restart mechanism is introduced — recorded deliberately.

### 3.2 Isolation (MUST)

1. The crash of ANY subset of children leaves the supervisor and the
   control socket alive. Management availability (status/stop/logs) is an
   invariant, not a "healthy day" privilege.
2. An exception in per-child code is caught at the boundary (the child's
   FSM → backoff); the main loop never dies. No execution path of per-child
   logic takes the supervisor out of the loop.
3. Children do not receive the control socket fd or its path in env
   (rationale — the threat model, §7).
4. Children do not trust each other: IPC happens only through explicit API
   contracts. The supervisor builds no hidden "child → child" channels.
5. **The child's env** = a constructed PATH + the manifest's `env.vars` +
   the contents of `env_file`. `env -i` semantics are mandatory: no host
   variable leaks into the child except the listed ones — the lesson of
   the "401 storm" of host env leakage. Conformance: the child prints its
   environment, the runner cross-checks it with an allow-list (SL-13).

### 3.3 The child FSM

States: `stopped → starting → healthy → degraded → backoff → stopped`, plus
`blocked` (for dependents while a core dependency is not up).

Transition table (normative; the implementation MUST NOT allow the
forbidden transitions — SL-07):

| # | from | event | to | Norm |
|---|---|---|---|---|
| T1 | stopped | child spawn (start, restart, lazy-retry, manual start) | starting | MUST |
| T2 | stopped | a start request while a core dependency is not up | blocked | MUST |
| T3 | blocked | the core dependency reached healthy | starting | MUST |
| T4 | starting | the first successful health pass | healthy | MUST (the definition of "up") |
| T5 | starting | process exit before healthy | backoff | MUST (the tier restart policy, §3.5) |
| T6 | starting | manual stop / supervisor shutdown | stopped | MUST |
| T7 | healthy | health probes failing (the degradation threshold from the manifest) | degraded | MUST |
| T8 | healthy | process exit while the restart budget is alive | backoff | MUST |
| T9 | degraded | a health pass recovery | healthy | MUST (recovery) |
| T10 | degraded | process exit while the budget is alive | backoff | MUST |
| T11 | degraded | exit with the budget exhausted (optional) | degraded | MUST (the terminal degradation state) |
| T12 | backoff | backoff timer expiry → respawn | starting | MUST |
| T13 | backoff | manual stop / supervisor shutdown | stopped | MUST |
| T14 | any | supervisor graceful shutdown | stopped | MUST (reverse-topological order, §3.5) |

Notes:

- The supervisor's global health is a separate supervisor-level flag, not
  an FSM state: a core crash-loop drops the global health to `degraded`
  while the child itself continues the backoff/starting cycle.
- The degradation threshold (T7) and the health mechanics of a specific
  component are the domain of the health section of its manifest
  (`specs/component-manifest/v1`).

### 3.4 Observability — part of the contract

Every lifecycle unit publishes **exactly one fixed structural line**. The
format (grammar, normative — SL-08):

```
vesma.supervisor component=<name> event=<spawn|exit|health|degraded> pid=<n|none> [<key>=<value> ...]
```

Component names and field values are `[a-z0-9_.-]` tokens, without spaces
or quotes; additional fields MAY be added after the mandatory ones without
breaking the prefix and the order of the mandatory ones.

| event | Mandatory extra fields (in this order) | Semantics |
|---|---|---|
| `spawn` | — (MAY: `attempt=<n>`) | a child was spawned; `pid` is the new pid |
| `exit` | `code=<n\|none> signal=<NAME\|none>` | exactly one field carries a value: died by code → `code=<n> signal=none`; by signal → `code=none signal=<NAME>` (without the `SIG` prefix) |
| `health` | `from=<state> to=<state>` | an FSM transition per T4/T7/T9 |
| `degraded` | `state=degraded reason=<token> attempts=<n> window=<Ns\|none>` | supervisor-level degradation: `reason=restart-budget-exhausted` (optional) or `reason=crash-loop` (core); `pid` is the last spawned instance |

Severity levels: `spawn`/`health` — INFO; `exit` with code 0 — INFO, with a
non-zero code or a signal — WARNING; `degraded` — ERROR.

`pid` on a `degraded` line is the last pid of the component's instance; if
the instance was never spawned — `pid=none` (a codification note: in the
verdict text the optional-degradation line is quoted without the prefix
and pid; the canonical prefix `vesma.supervisor` and `pid` are always
present).

**The history/ journal (MUST).** Every FSM transition of every component
and every change of the supervisor's global health is additionally written
to the supervisor journal `~/.local/state/vesma/history/` — append-only;
the record format is the same structural lines of this paragraph with an
ISO-8601 timestamp. The journal's path, permissions, and append-only
semantics — `specs/layout/v1`.

**Child lines in journald.** The supervisor tags child lines with
`SYSLOG_IDENTIFIER=vesma-<component>` when relaying them to journald (the
tagging is performed by the supervisor, not the child).
`vesma service logs --component=X` is a journalctl filter by identifier,
not a grep over mush.

### 3.5 Restart policies

The numbers below are **contractual defaults**. A manifest MAY override
them via `restart.*` within the clamps: `base` ≥ 500ms, `max` ≤ 5min,
`attempts` ≥ 3 (the clamps are checked by install validation, SL-18).

**core** — restarts indefinitely:

- exponential backoff: base 1s, ×2, cap 30s, jitter ±20%;
- the counter resets after 300s of continuous uptime;
- crash-loop: 10 attempts without reaching healthy → global health =
  `degraded` + an alert line (§3.4, `reason=crash-loop attempts=10
  window=none`); the restart continues — the supervisor stays alive.

**optional** — budget discipline:

- at most 5 attempts per 300s window;
- exhausted → state `degraded` + a health flag + **EXACTLY ONE** structural
  ERROR line:
  `vesma.supervisor component=<name> event=degraded pid=<n> state=degraded reason=restart-budget-exhausted attempts=5 window=300s`;
- then lazy-retry once per 300s **without alert spam** (subsequent attempts
  and their outcomes — INFO; no new ERROR lines are published);
- a manual `vesma service start --component=X` resets the budget.

**In-process core**: death of the in-process core (memory server + API) =
death of the supervisor → systemd unit restart (see §3.1).

**Start order.** Topological over `depends_on` (a cycle = an
install-validation error); independent components start in parallel. "up" =
the first successful health pass (T4). A core dependency did not come up →
the dependents wait indefinitely with backoff logs (FSM: `blocked`, T2/T3)
— there is no bounded timeout for waiting on a core dependency.

**Stop.** SIGTERM to the supervisor (the default systemd signal — see
§3.6) → reverse-topological order: the dependents stop before their
dependencies. Each child: `kill(-pgid, SIGTERM)` within the grace period
(from the manifest's stop semantics) → on expiry — `kill(-pgid, SIGKILL)`
of the group. The total internal child-stop budget is designed strictly
below the unit's `TimeoutStopSec` (a margin of ≥ 25%). The supervisor exits
only after reaping all children (PID1 mode: the same before exit).

### 3.6 systemd: exactly one unit

systemd manages **exactly one** unit above the `vesma` process; **systemd
NEVER knows about the children** (the contractual wording): neither the
unit directives nor the systemd stop logic mention components — the entire
order of stopping children is the supervisor's responsibility. The unit is
generated by `vesma service install` (user profile:
`~/.config/systemd/user/vesma.service`).

**Unit template (a MUST table — SL-17):**

| Directive | Value | Rationale |
|---|---|---|
| `Type=` | `exec` | the start counts as successful only after a successful `exec()`; a launch error = unit failure |
| `ExecStart=` | a single line **without `sh -c`** | the arguments come from the launch manifests; shell concatenation is a legacy antipattern |
| `ExecStop=` | **NOT generated** | the default SIGTERM to the main process = the contractual stop (§3.5); the pkill antipattern disappears |
| `KillSignal=` | `SIGTERM` | matches the contractual stop |
| `KillMode=` | `mixed` | SIGTERM to the main process → an orderly graceful stop of the children by the supervisor; at `TimeoutStopSec` systemd SIGKILLs the whole cgroup as a backstop |
| `TimeoutStopSec=` | `90` | the internal child-stop budget + a margin |
| `Restart=` | `on-failure` | supervisor death (including the in-process core) → unit restart |
| `RestartSec=` | `5s` | the pause between unit restarts |
| `StartLimitIntervalSec=` | `300` | the window for detecting an ordinary unit crash-loop |
| `StartLimitBurst=` | `5` | the threshold: 5 failures per 300s → the unit gives up (fail-fast outward, not an endless loop) |
| `StandardOutput=` | `journal` | everything to journald |
| `StandardError=` | `journal` | everything to journald |

The `SYSLOG_IDENTIFIER=vesma-<component>` tagging is performed by the
supervisor when relaying child lines (§3.4) — it is not expressible at the
unit level.

**WatchdogSec / sd_notify — v2** (deliberately deferred).

**THE UNIT HARDENING BLOCK (MUST — SL-18):**

| Directive | Value | Note |
|---|---|---|
| `NoNewPrivileges=` | `true` | forbids escalation via setuid/sgid |
| `ProtectSystem=` | `strict` | the whole filesystem read-only except `ReadWritePaths` |
| `ReadWritePaths=` | the layout's state/cache/data (`specs/layout/v1`) | the only writable paths |
| `ProtectHome=` | `read-only` (user) / `true` (system) | home not writable (user) / hidden (system) |
| `PrivateTmp=` | `yes` | an isolated /tmp |
| `PrivateDevices=` | `yes` | no device access |
| `ProtectKernelTunables=` | `yes` | no writes to /proc/sys |
| `ProtectKernelModules=` | `yes` | no module loading |
| `ProtectKernelLogs=` | `yes` | no access to the kernel log |
| `ProtectControlGroups=` | `yes` | no writes to the cgroup hierarchy |
| `RestrictSUIDSGID=` | `yes` | forbids creating suid/sgid files |
| `LockPersonality=` | `yes` | personality locked |
| `RestrictRealtime=` | `yes` | no RT scheduling |
| `CapabilityBoundingSet=` | empty | no capabilities at all |
| `RestrictAddressFamilies=` | `AF_UNIX AF_NETLINK AF_INET AF_INET6` | the other socket families are forbidden |
| `SystemCallFilter=` | `@system-service` | **Tier B**: activated after the bare/distrobox/podman smoke matrix; until then the generator MAY print the directive commented out with a loud marker |

`MemoryDenyWriteExecute` — **deliberately excluded**: it breaks CPython
native extensions (JIT/WX memory in native modules); enabling it would
mean a non-working supervisor for the sake of a checkbox — recorded here
so that a "security audit" does not silently bring the directive back.

**Containers.** In containers only a LOUD, documented downgrade of the
filesystem directives (not applicable without a real systemd host) is
acceptable: it is printed in the install output and visible in
`vesma service status`. There are no silent degradations.

### 3.7 Error codes — not applicable

The contract defines no protocol error codes: lifecycle errors are
expressed as FSM states (§3.3) and structural observability lines (§3.4).
The protocol codes for managing the live supervisor are the domain of
`specs/control-socket/v1` (§4.6).

## 4. Examples

Minimal artifacts in `examples/`:

| File | What it shows |
|---|---|
| `examples/example-unit.service` | a generated user-profile unit: the full MUST table + the full hardening block, ExecStart as a single line |
| `examples/example-log-lines.txt` | 8 structural lines: spawn, health transitions, exit (by code and by signal), an optional degraded alert, a core crash-loop degraded alert |
| `examples/example-status.json` | a `vesma service status` response: supervisor + a component map "name → record" (`state` + `health` + additive fields), healthy and degraded records (with reason); the shape matches the `status` of specs/control-socket/v1 §4.5 |

The paths in the examples (state/cache/data, unit, socket) are placeholders
over the canonical roots; the final names are fixed by `specs/layout/v1`
and `specs/control-socket/v1`.

## 5. Conformance

The implementation conformance checklist is `conformance/checklist.md`
(SL-01…SL-18): isolation, pgid stop, subreaper, PID1 reap, FSM transitions,
structural lines, restart numbers, env semantics, the unit template,
hardening, graceful order, lazy-retry without spam. The contract status is
`draft` until the checklist is first passed by an implementation in the
vesma engine (ratification by implementation).

## 6. Compatibility

- **SemVer**: `1.0.0-draft.1` → `1.0.0` upon ratification by
  implementation. A breaking change = MAJOR + a deprecation window with
  dual support (the discipline of the README "Contract discipline"
  section).
- **Consumed contracts**: the fields `metadata` (name/tier), `kind`,
  `launch`/`in_process`, `health`, `stop`, `config`, `depends_on`,
  `env.vars`/`env_file`, `restart.*`, `artifact_sha256` — from
  `specs/component-manifest/v1`; the live-supervisor management protocol
  (status/logs/start/stop) — `specs/control-socket/v1`; the
  state/cache/data/socket paths — `specs/layout/v1`.
- **Deferred to v2**: `WatchdogSec`/`sd_notify`; `SystemCallFilter`
  activation (Tier B); per-component unit resource limits; secret redaction
  in relayed lines.
- **Incompatibilities with legacy are deliberate**: see §8 (they are the
  very point of the contract).

## 7. Threat model (mini-STRIDE)

The supervisor is a **trust boundary**: it owns the environment, the signal
space, and the journal of all components.

**Assets:** the children's processes; the children's env; the control
socket; the cgroup.

**Boundaries:** (1) supervisor ↔ children (spawn, env, fd inheritance,
signals, reap); (2) systemd ↔ supervisor (unit, cgroup, KillMode);
(3) operator/CLI ↔ control socket — a boundary of the
`specs/control-socket/v1` domain.

| Category | Threat | Mitigation | Check |
|---|---|---|---|
| **S**poofing | a third-party local process impersonates the CLI/a component and connects to the control socket | socket permissions 0600 + a peer-credentials check (the `control-socket/v1` domain); the children get no access descriptors to the socket | SL-14 + operational control of layout permissions |
| **S**poofing | a child forges log-line attribution (writes under a foreign identifier) | `SYSLOG_IDENTIFIER` is set by the supervisor at relay; the child does not write to the journal directly | SL-08; operational control |
| **T**ampering | substitution of the launch artifact between install and spawn | `artifact_sha256` from the manifest is verified at spawn | SL-18 (clamps/validation); manifest conformance |
| **T**ampering | manual edits of the generated unit (a silent weakening of hardening) | the unit is a generated artifact ("generated, do not edit"); regeneration by `install` overwrites | SL-17; operational control |
| **R**epudiation | "who killed the component?" — no provable history | structural exit lines with `pid/code/signal` + spawn/health/degraded in append-only journald | SL-08 |
| **I**nformation Disclosure | host env leaking into children (the 401 storm) | `env -i` semantics are mandatory: env = PATH + `env.vars` + `env_file` | SL-13 (the child prints its env, the runner cross-checks with an allow-list) |
| **I**nformation Disclosure | a leak of the control socket's fd/path into the children | the fd is not inherited, the path is absent from the child's env | SL-14 (`/proc/<pid>/fd` + env) |
| **I**nformation Disclosure | secrets in child lines get into the journal | component contracts forbid printing secrets; the supervisor does not filter the content (redaction — v2) | operational control |
| **D**enial of Service | zombie processes accumulate and exhaust the process table | subreaper + the `waitpid(-1, WNOHANG)` loop | SL-05 |
| **D**enial of Service | a stuck child blocks the stop | grace period → SIGKILL of the group; `TimeoutStopSec=90` as the systemd backstop | SL-04, SL-16 |
| **D**enial of Service | a child monopolizes CPU/RAM | the unit's shared cgroup limits the user profile's blast radius; per-component limits — v2 | operational control |
| **E**levation of Privilege | a child tries to reach the control socket | the fd is not inherited; the path is not in env; the peer check on the socket | SL-14 |
| **E**levation of Privilege | escalation via setuid/writes to system paths | `NoNewPrivileges=true`, `CapabilityBoundingSet=` (empty), `ProtectSystem=strict` | SL-18 |
| **E**levation of Privilege | a child reaches kernel surfaces | `ProtectKernel*`, `PrivateDevices`, `RestrictAddressFamilies` | SL-18 |

Every mitigation is closed by a conformance check or marked "operational
control" (file permissions, regulations, review) — there are no silent
unverifiable promises.

## 8. Migration from legacy

Units with pkill-ExecStop and `sh -c`-ExecStart **are replaced by
generation**: `vesma service install` creates the new unit per §3.6; the
old units are retired (disable + stop) — a manual transfer of directives is
not provided; the single migration point is the generator.

| Legacy pattern (inventory 2026-10-04) | Contract answer |
|---|---|
| 5 launch mechanisms (distrobox sh wrappers, podman exec, host-native binaries, nohup/&, cron) | one supervisor: launching a component = spawn by manifest (§3.1) |
| pkill patterns in ExecStop (inventorying by name) | `kill(-pgid, …)` by construction; ExecStop is not generated at all (§3.6) |
| `env -i` in an sh wrapper (manual environment hygiene per component) | the supervisor's `env -i` semantics are mandatory, constructed centrally (§3.2) |
| `sh -c "…"` with concatenation in ExecStart | ExecStart = a single line without `sh -c`, the arguments from the launch manifests (§3.6) |
| 2 unit scopes, duplicate services (board ×2) | exactly one unit above the vesma process; systemd NEVER knows about the children; a duplicate = an install-validation error (§3.6) |
| grep over log mush | `SYSLOG_IDENTIFIER=vesma-<component>`; `vesma service logs --component=X` = a journalctl filter (§3.4) |

Migration of the legacy deployment is not before the first observation
window of the founding track closes (founding context — see `docs/`;
restarts segment the observation) — roadmap phase 3, the engine track. The
specs and the CLI code are not subject to this window.

**Historical note.** This spec is deliberately genericized (owner's
decision of 2026-10-04): the specifics of the founding environment — the
legacy names, the target machine, the details of the first observation
window — are preserved in the founding pack `docs/` (in particular, the
directives brief `docs/brief-2026-10-04-archcom-founding.md`) and in the
repository's history; for historical continuity, read them together with
this spec.

## 9. References

- `specs/component-manifest/v1` — the component manifest (the supervisor's input)
- `specs/control-socket/v1` — live-supervisor management
- `specs/layout/v1` — canonical paths (state/cache/data/socket/unit)
- `adrs/ADR-0001` — the repository's founding ADR (structure + governance)
- RFC 2119 — keyword interpretation
- `docs/brief-2026-10-04-archcom-founding.md` — the brief and the unbreakable decisions
- `docs/concept.md`, `docs/roadmap.md` — the layer concept and phases
- systemd.exec(5), systemd.service(5) — unit directive semantics
- setsid(2), prctl(2) `PR_SET_CHILD_SUBREAPER` — the process model

## Translation note

- Mirror date: 2026-10-04; base commit of the normative Russian source:
  `01fb6ed` (`specs/service-lifecycle/v1/spec.md`).
- This is an informative mirror; in case of divergence the Russian
  `spec.md` prevails.
- Sync policy: the mirror is updated in the same change (single commit) as
  the Russian text; a standalone edit of this file is a process violation.
