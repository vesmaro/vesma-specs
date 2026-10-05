---
contract: control-socket
version: 1.0.0
status: stable
ratified: учредительный АрхКом VESMA, 2026-10-04; ратифицирован первой конформной реализацией — движок vesmaro/vesma, main 4a2da5a, 2026-10-05 (конформанс — docs/project/reports/service-conformance-2026-10-06.md в репо движка; раннер 24/24; чеклист CS-01…CS-16 green; live cross-uid лега — реальный прогон 2026-10-05, sudo+setpriv uid 65534, транскрипт в отчёте)
decisions: [ADR-0001]
language: en (informative mirror)
---

# Supervisor control socket — `control-socket` v1

> This is an informative English mirror of the normative Russian
> specification [spec.md](spec.md). In case of divergence, the Russian text
> prevails. The mirror is maintained in the same change as the Russian text
> (single-commit sync policy).
>
> **Status: stable (1.0.0).** Ratified by the first conforming
> implementation in the `vesma` engine on 2026-10-05 (main `4a2da5a`). The contract form —
> paths and permissions, the TOCTOU procedure, protocol, methods, error
> codes, limits, threat model — was ratified by the founding VESMA ArchCom
> on 2026-10-04 (ADR-0001) and is here **codified, not replayed**. Further
> changes happen only through the SemVer process (§ 8).

The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, MAY are to be interpreted
per RFC 2119. In the normative document the prose is Russian; identifiers,
method names, and field values are English (the ecosystem canon).

**Pattern:** docker CLI ↔ dockerd. The `vesma` CLI is a thin client to the
live supervisor over a unix socket; the supervisor is the single holder of
the truth about component state (not guessing from processes).

## 1. Scope

### 1.1 In scope of v1

- The "client ↔ supervisor" management channel over `AF_UNIX`,
  `SOCK_STREAM`.
- The user profile of an installation — the only one implemented in v1
  (including the fallback path when `XDG_RUNTIME_DIR` is empty).
- The JSON Lines protocol; the methods `hello`, `status`, `start`, `stop`,
  `restart`, `logs`, `health`.
- The "filesystem = authentication" model + `SO_PEERCRED` as
  defense-in-depth.
- Error codes, limits, a mini-STRIDE threat model, a conformance checklist.

### 1.2 Out of scope of v1

- **Method-level ACL** — v2, when a remote operator appears (note A to the
  table in § 3).
- **TCP and any network transport of the control plane — FORBIDDEN** by
  construction (§ 4.7).
- **BSD/macOS** (`getpeereid`) — a separate decision, outside v1; the v1
  scope is explicitly Linux-only.
- **FSM states, health aggregation, restart policies, stop timings** — the
  domain of [specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md);
  the socket carries them as opaque string values.
- **The shared layout** (configs, data, cache, venv) — the domain of
  [specs/layout/v1](../../layout/v1/spec.md); only the paths and
  permissions of the socket directories are fixed here.
- The supervisor implementation (child isolation, reaping) — the `vesma`
  engine.

### 1.3 Rejected alternatives (recorded by the ArchCom, do not replay)

- **Socket activation** (a systemd `.socket` unit: the socket is created
  before the process) — rejected by the owner on 2026-10-04. This is a
  **management** socket, not activation: the supervisor itself owns the
  path and itself performs probe/bind/unlink (§ 4.2). Revisit the
  discussion only when a real scenario appears (for example, management
  before supervisor initialization).
- **JSON-RPC 2.0** as the protocol — rejected by the committee:
  notifications, batch, and its error-code registry are unneeded. The
  envelope is deliberately kept compatible in form (`id`/`result`/`error`)
  so that a future bridge is cheap (§ 8).

## 2. Terminology

| Term | Meaning |
|---|---|
| supervisor | the `vesma` process, holder of the socket and parent of the components; the supervisor contract is [specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md) |
| component | a child unit of the ecosystem declared by a manifest ([specs/component-manifest/v1](../../component-manifest/v1/spec.md)) |
| manifest registry | the set of components known to the supervisor from the loaded manifests |
| bind side | the supervisor that creates and listens on the socket |
| peer | a client that has connected to the socket (the CLI or another) |
| DAC | filesystem discretionary access control (the path's permissions and owner) |
| `SO_PEERCRED` | a Linux mechanism (`unix(7)`): obtaining the peer's uid/gid/pid of a unix socket from the kernel, without trusting the client |
| stale socket | a socket file left over from a dead supervisor instance |
| FSM state | a component's state per [specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md) |
| user / system profile | the installation profiles per [specs/layout/v1](../../layout/v1/spec.md) |
| control plane | the totality of the supervisor management channels |

## 3. Paths and permissions (MUST)

| Profile | Socket directory | Socket | Authentication |
|---|---|---|---|
| **user (v1)** | `${XDG_RUNTIME_DIR}/vesma/`, mode 0700 | `control.sock`, mode 0600 | DAC: the directory owner; `SO_PEERCRED` defense-in-depth: peer uid == the socket owner, otherwise immediate close |
| **user fallback** | `~/.local/state/vesma/run/`, mode 0700, + a WARN in the log (applied when `XDG_RUNTIME_DIR` is empty) | `control.sock`, mode 0600 | the same + the mandatory stale procedure (§ 4.2) |
| **system** (v2 horizon: defined in the spec, the implementation deferred) | `/run/vesma/`, mode 0750, `root:vesma-oper` | `control.sock`, mode 0660 | `SO_PEERCRED` on EVERY accept: uid=root or gid=vesma-oper, otherwise deny + an audit line |

Notes (MUST):

- **A. The filesystem = authentication.** Tokens over the socket are not
  needed in v1: the attacker class does not change — whoever can connect
  can also kill the process with the same account. Method-level ACL — v2,
  when a remote operator appears (the system profile).
- **B. Socket permissions MUST NOT depend on umask.** After `bind`, the
  permissions are set explicitly (`chmod`) and verified with `fstat`
  (§ 4.2, step 5).
- **C. Linux-only.** The v1 scope is fixed explicitly; BSD/macOS
  (`getpeereid`) is a separate decision beyond this version.
- **D. The `vesma-oper` group is NOT created by the installer by default**
  — the group is the operator-equivalent (the docker-socket lesson:
  membership in the docker group is equivalent to root). The group is only
  documented; creating it is a deliberate operator action on the v2
  horizon.
- The peer uid/gid check is performed by the supervisor on EVERY accept,
  before reading any data from the connection.

## 4. Contract

### 4.1 Client pre-flight (protection against lax home directories) — MUST

When connecting, the CLI (and any client implementation SHOULD behave the
same way) refuses to work if the socket directory:

- is group-writable, or
- is world-writable, or
- is owned by a user other than the current one.

On refusal the client prints a ready remediation command with the real
path (for example `chmod 0700 /run/user/1000/vesma`), but does NOT execute
it automatically. The supervisor on the bind side SHOULD perform the same
check before creating the directory/socket (a symmetric hardening of the
same threat).

### 4.2 Bind side: TOCTOU/SYMLINK procedure — MUST

At startup the supervisor performs the procedure strictly in this order:

1. **Target path** — per the profile from § 3 (user profile: the directory
   from `XDG_RUNTIME_DIR`; if it is empty → the fallback path + a WARN
   line in the log).
2. **`bind` on the target path.** Success → step 5. `EADDRINUSE` →
   **a `connect()`-probe of the live instance**:
   - a live instance answered (connect succeeded and a valid response to
     hello arrived within the response timeout) → **exit "already
     running"** (single-instance guard): do not unlink, do not bind;
   - `ECONNREFUSED`/`ENOENT` → the path is stale → step 3;
   - any other error (`EACCES`, `ELOOP`, ...) → start refusal with
     diagnostics, delete nothing.
3. **Before unlink — `lstat`**:
   - delete ONLY a socket file owned by the current process's user
     (`S_ISSOCK` and `st_uid == geteuid()`);
   - the path is a symlink → **start refusal + an alert, NEVER follow**;
   - a non-socket (a regular file, a directory) or a foreign owner → start
     refusal + an alert; do not delete foreign objects.
4. **`unlink` + a retry `bind` + `listen`** on the target path. The loop
   "bind → EADDRINUSE → probe → lstat → unlink → retry bind" runs at most
   3 attempts; exhausted → start refusal with diagnostics. Between the
   probe and the unlink the directory is kept under one's own ownership
   (`0700`): a race between FOREIGN supervisors is impossible by
   construction (a foreign uid does not own the directory), and two starts
   of ONE supervisor are handled by the single-instance guard (step 2: a
   live probe → exit).
5. **After bind — `fstat` of the bound fd**: verify the mode and the owner
   (user profile: 0600 and own uid; see note B to § 3). A mismatch →
   fatal at startup.
6. **A blind `unlink` of a live socket is forbidden by the contract.**
   A probe before unlink is mandatory for all profiles; for user fallback
   (`~/.local/state/...` survives reboots) the stale scenario is the norm,
   the procedure is mandatory on every start.

### 4.3 Protocol (envelope) — MUST

- Transport: `AF_UNIX`, `SOCK_STREAM`, UTF-8.
- Framing: **JSON Lines** — one line = one request, the delimiter `\n`;
  one line = one response (the exception — the `logs follow` stream,
  § 4.5).
- Request: `{"id": N, "method": "...", "params": {...}}`; `params` is
  optional (absent → treated as `{}`).
- Response: exactly one of
  `{"id": N, "result": {...}}` or
  `{"id": N, "error": {"code": N, "message": "...", "data": {...}}}`;
  `data` is optional.
- `id` is an integer generated by the client; the server returns it
  unchanged.
- Batch and notifications are absent (rejected along with JSON-RPC 2.0,
  § 1.3).

### 4.4 `hello` and versioning — MUST

`hello` is the MANDATORY first request of every client on every
connection. Any other method before `hello` → error 4
`version_unsupported` with
`data: {"reason": "hello_required", "supported": [<supported majors>]}`.
Rationale: before `hello` the protocol version is not agreed, so the
server must refuse along the same branch as on a major mismatch; the
recovery path is single — send `hello` (the client continues the session
as usual after such an error).

- Request: `{"id": N, "method": "hello", "params": {"protocol_version": 1}}`
  — `protocol_version` is mandatory.
- The server compares the client's **major** version with its own. A major
  mismatch → error 4 `version_unsupported`, with `data.supported` carrying
  the supported majors.
- Response on success:

```json
{"id": N, "result": {"protocol_version": 1, "min_protocol": 1,
                     "server_version": "<engine semver>", "pid": 4312}}
```

- `protocol_version` — the server's current protocol version;
  `min_protocol` — the lower bound of dual support during future
  transitions; `server_version` — the engine's version (not the
  contract's); `pid` — diagnostics (a pidfile is not provided by the
  contract: single-instance is decided by the probe, § 4.2).

### 4.5 Methods of v1

#### `hello`

| Request | Response | Errors |
|---|---|---|
| `params: {"protocol_version": N}` | `{"protocol_version": 1, "min_protocol": 1, "server_version": "...", "pid": N}` | 4 (+`data.supported`), 3, 1 |

#### `status`

A state map (the FSM states from specs/service-lifecycle/v1; as of v1:
`stopped`, `starting`, `healthy`, `degraded`, `backoff`, `blocked` — the
source of truth: the transition table of service-lifecycle § 3.3) +
health flags.

| Request | Response | Errors |
|---|---|---|
| no params — the whole tree; `params: {"component": "<name>"}` — one component | `{"supervisor": {"pid": N, "health": "..."}, "components": {"<name>": {"state": "<fsm-state>", "health": "healthy\|degraded\|down"}}}`; with `component` the `supervisor` key is omitted | 100 |

The minimal component record is `state` + `health`; additional fields
(tier, restart counters) are additive; their composition is defined by
service-lifecycle.

#### `start` — idempotent (MUST)

| Request | Response | Errors |
|---|---|---|
| `params: {"component": "<name>"}` | already running → `{"state": "already-running"}`; otherwise `{"state": "<fsm-state>"}` | 100, 101, 102 |

#### `stop` — idempotent (MUST)

| Request | Response | Errors |
|---|---|---|
| `params: {"component": "<name>", "force"?: false}` | already stopped → `{"state": "already-stopped"}`; otherwise `{"state": "<fsm-state>"}` | 100, 101, 103 |

`force: true` → skips the graceful phase (a POSIX termination signal and
waiting for the exit); SIGKILL after a short delay. The length of the
delay and the stop timings are the domain of specs/service-lifecycle/v1.

#### `restart`

| Request | Response | Errors |
|---|---|---|
| `params: {"component": "<name>"}` | `{"state": "<fsm-state>"}` | 100, 101, 102, 103 |

Phase semantics and behavior in edge states — specs/service-lifecycle/v1;
the socket contract fixes only the envelope. Idempotency is not claimed
for `restart`.

#### `logs`

| Request | Response | Errors |
|---|---|---|
| `params: {"component": "<name>", "follow"?: false, "tail"?: 100}` | see below | 100, 3 |

- `follow: false` (default) → a single response:
  `{"result": {"lines": ["...", "..."]}}` — up to `tail` lines,
  `tail ≤ 10000`.
- `follow: true` → a **STREAM** of frames
  `{"id": N, "stream": {"component": "<name>", "line": "..."}}` until the
  final response. A normal end of the source (the component stopping) →
  the final response `{"id": N, "result": {"state": "<fsm-state>"}}`; an
  internal error → error. The client MAY break the connection at any
  moment; the server MUST release the subscription resources. The limits
  and timeouts of follow streams (subscriptions per peer/installation, the
  idle timeout, the duration cap) — § 4.7.

#### `health`

Global / per-component health. Values: `healthy` \| `degraded` \| `down`.

| Request | Response | Errors |
|---|---|---|
| no params — global + all components; `params: {"component": "<name>"}` — one | without params: `{"health": "...", "components": {"<name>": "..."}}`; with component: `{"health": "..."}` | 100 |

The aggregation rules (the core/optional tiers) —
specs/service-lifecycle/v1.

### 4.6 Error codes — MUST

| Code | Name | Meaning |
|---|---|---|
| 1 | `bad_request` | a malformed frame, an envelope violation (a request before `hello` — code 4, § 4.4) |
| 2 | `unknown_method` | the method does not exist (clients MAY probe new methods and handle the refusal correctly) |
| 3 | `invalid_params` | wrong types/values of params (including a name regex failure, `tail` out of range) |
| 4 | `version_unsupported` | a major mismatch; any request before `hello` (the version not agreed, `data.reason="hello_required"`); `data.supported` is MANDATORY |
| 100 | `unknown_component` | the name is well-formed but absent from the manifest registry |
| 101 | `invalid_state` | the transition is forbidden by the current FSM state |
| 102 | `start_failed` | the start failed; the reason is in `data` |
| 103 | `stop_timeout` | the graceful timeout expired without the process exiting |
| 200 | `permission_denied` | authorization refused on the server (system profile: the peer check failed; a future ACL) |
| 500 | `internal` | an internal error; the details go to the supervisor logs, not to the client |

Ranges: `<100` — protocol; `100–199` — lifecycle; `200` — authz; `500` —
infra. A client that receives an unknown code MUST interpret it by range.
A new code inside an existing range is an additive change (MINOR, § 8).

**Error-data hygiene for the 100–199 range (MUST).** Only machine-formable
fields are allowed in `data`: the component name, the FSM state, the exit
code. Paths, env strings, and argv are FORBIDDEN in error data — they may
carry secrets and internal installation details.

### 4.7 Limits and prohibitions — MUST

| Limit | Value | On violation |
|---|---|---|
| Request line length | ≤ 1 MiB | error 1 and/or closing the connection |
| Response timeout | 10 s (except follow streams) | the client closes the connection; retrying idempotent operations is safe |
| Concurrent follow subscriptions | at most 2 per peer and at most 8 per installation | beyond — error 3 `invalid_params` |
| Follow framing idle timeout | 60 s | no data for a frame — the server closes the stream with a final response |
| Follow stream duration | ≤ 3600 s (a hard cap) | auto-close with a final response; the client resubscribes |
| `tail` | ≤ 10000, default 100 | error 3 |
| Component name | `^[a-z][a-z0-9-]{0,62}$` (the full manifest name pattern) and presence in the manifest registry | a regex failure → 3; not in the registry → 100 (protection against name injection in `logs`) |
| Transport | `AF_UNIX` only | a TCP control plane is FORBIDDEN by default; its appearance = a new trust boundary → MAJOR + a full threat model |

### 4.8 CLI mapping

| CLI | Socket method |
|---|---|
| `vesma service status` | `status` |
| `vesma service logs [--follow] [--tail N]` | `logs` |
| `vesma service start <component>` | `start` |
| `vesma service stop <component> [--force]` | `stop` |
| `vesma service restart <component>` | `restart` |

A 1:1 mapping. The CLI is a thin client: it takes the truth about state
from the socket (first-hand), not from processes. The CLI does NOT hold a
persistent connection, except `logs --follow` (MUST). The `health` method
is available to any client; a dedicated CLI command — MAY (an additive
extension).

## 5. Threat model (mini-STRIDE)

**Assets.**
A1 — control over the lifecycle of the child processes (start/kill) = full
control over the user's system. A2 — the component log stream. A3 — the
supervisor's availability as the single point of management.

**Trust boundaries.**
B1 — filesystem → socket (whoever reached the path). B2 — peer connection
→ supervisor (who actually connected). B3 (v2 horizon) — operator → system
socket.

| Threat | Class | Mitigation | Check |
|---|---|---|---|
| A stranger local user connects to the socket | S (Spoofing) | DAC 0700/0600; `SO_PEERCRED` defense-in-depth: peer uid == the socket owner, otherwise immediate close (system profile: uid=root or gid=vesma-oper on every accept + audit) | conformance 1, 3 |
| Symlink substitution of the socket path, substitution of the directory | T (Tampering) | `lstat` before unlink (only one's own socket file; a symlink → refusal + an alert, never follow); `fstat` after bind; the client pre-flight on lax directories (§ 4.1) | conformance 2, 5, 6 |
| A stale socket as a false instance, loss of single-instance | E / D | the `connect()`-probe before unlink; a pidfile is not needed — the probe decides; a blind unlink of a live socket is forbidden | conformance 4, 7 |
| Component-name injection into `logs` (path traversal) | E (Elevation of Privilege) | the regex `^[a-z][a-z0-9-]{0,62}$` + validation against the manifest registry | conformance 13 |
| TCP exposure of the control plane | I / S | forbidden by construction (unix-only; enabling = MAJOR + a full threat model) | conformance 15 |
| Protocol downgrade | T | `hello`: a major check of `protocol_version`; a mismatch → error 4 + `supported` | conformance 9 |
| A flood of connections / giant lines against the supervisor | D (DoS) | the 1 MiB line limit; the 10 s response timeout; the CLI holds no persistent connections except `logs --follow` | conformance 12, 14 |
| "Who did this?" | R (Repudiation) | the v1 user profile: one owner = one operator — the risk is low; the supervisor logs the methods to its own log; the system profile (v2): deny + a mandatory audit line | operational control; v2 — conformance |

Every mitigation is either a conformance-checklist item (the number is
given) or "operational control". Log-content hygiene (secrets and the
like) is outside the socket contract: the domain of the components and
service-lifecycle; the socket adds no surface here.

## 6. Examples

Minimal session: [examples/example-session.txt](examples/example-session.txt)
(hello → status → start → status → logs → stop → an idempotent stop retry
and one error). The values in the example are placeholders.

## 7. Conformance

Checklist: [conformance/checklist.md](conformance/checklist.md) — 16 items
of executable conformance checking against the v1 contract. An item
without coverage = the implementation is non-conformant. The system-profile
items are outside the v1 checklist (the implementation is deferred to the
v2 horizon along with the implementation).

## 8. Compatibility and evolution

- **SemVer** per the repository rules (README, "Contract discipline"):
  MAJOR — breaking (the envelope format, method semantics,
  paths/permissions); MINOR — additive (a new method, a new code in an
  existing range, a new response field); PATCH — editorial.
- **The negotiation mechanism** — `hello` with a major-only check (§ 4.4);
  a breaking change to the protocol version = a new MAJOR + a dual window
  via `min_protocol`.
- **Unknown methods** — error 2; a client MAY probe new methods and
  degrade correctly (the basis of dual support).
- **Unknown error codes** — interpreted by range (§ 4.6).
- **Unknown fields** of `result`/`stream` the client MUST ignore (the
  additive evolution of responses).
- **A JSON-RPC 2.0 bridge** — the envelope is deliberately compatible in
  form; a future bridge is cheap (§ 1.3).

## 9. Migration from legacy

Before 2026-10-04, component management was ad hoc (the inventory is in
the brief of the `vesma-cli-service-management-directive-20261004`
directive): 5 launch mechanisms, 2 scopes of systemd units, pkill patterns
in `ExecStop`, duplicate services, status "by processes" (pgrep/pkill).
The contract replaces:

- the truth about state — from the socket, not from processes;
- stopping — via the supervisor (the manifests' stop semantics), not pkill
  patterns;
- a single systemd unit above the supervisor process (the service-lifecycle
  domain);

Transition rules:

1. The engine implementation (card `cli-service-management`) introduces
   the socket before the mass migration of components; the spec status
   changed `draft` → `stable` on 2026-10-05 by the first conformant
   implementation (main `4a2da5a`).
2. For a migrated component (a manifest present in the registry),
   management happens only per the contract; parallel channels (TCP/HTTP
   control plane, sockets outside the layout) are forbidden by § 4.7.
3. The old mechanisms may launch components that have not yet migrated
   during the coexistence period; their retirement follows the founding
   brief's list (founding context, `docs/`).
4. Migration of the legacy deployment happens no earlier than the close
   of the founding track's first observation window (founding context —
   see `docs/`; restarts segment the observation).

**Historical note.** The spec is intentionally genericized (owner
decision 2026-10-04): the specifics of the founding environment — legacy
names, the target machine, the first observation window details — are
preserved in the founding docs pack (in particular, the directive brief
`docs/brief-2026-10-04-archcom-founding.md`) and in the repository
history; for story connectivity, read them together with this spec.

## 10. References

- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md)
  (the founding VESMA ArchCom, 2026-10-04: the repository structure and
  governance) — recorded in phase 0 on 2026-10-04.
- [specs/service-lifecycle/v1](../../service-lifecycle/v1/spec.md) —
  the supervisor = the socket holder: FSM, health aggregation, restart
  policies.
- [specs/layout/v1](../../layout/v1/spec.md) — the installation profile
  paths.
- [specs/component-manifest/v1](../../component-manifest/v1/spec.md) —
  the manifest registry, component names.
- [docs/concept.md](../../../docs/concept.md),
  [docs/brief-2026-10-04-archcom-founding.md](../../../docs/brief-2026-10-04-archcom-founding.md).
- External: RFC 2119; `unix(7)` (`SO_PEERCRED`); the XDG Base Directory
  Specification; the pattern precedent — docker CLI ↔ dockerd
  (`/var/run/docker.sock`).

## Translation note

- Last sync: 2026-10-05.
- Synced with the Russian spec.md in the same change (single-commit sync
  policy). In case of divergence, the Russian text prevails.
