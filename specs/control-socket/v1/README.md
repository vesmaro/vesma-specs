# Control Socket v1 — Quickstart

The control socket is the management API between the `vesma` CLI and a live supervisor — the docker CLI ↔
dockerd pattern: the CLI is a thin client, the supervisor is the single holder of truth about component state
(no guessing from processes). Transport is an `AF_UNIX` stream socket; TCP — any network transport for the
control plane — is forbidden by construction. v1 is Linux-only and ships the user profile.

## Normative spec

[spec.md](spec.md) — normative text (Russian canon, RFC 2119): paths and permissions, the TOCTOU/symlink bind
procedure, the JSON Lines protocol, methods, error codes, limits, mini-STRIDE threat model.

Full English mirror: [spec.en.md](spec.en.md).

## Key rules

- **Filesystem permissions ARE the authentication** — user scope is `${XDG_RUNTIME_DIR}/vesma/control.sock`, socket mode `0600`, directory `0700`; `SO_PEERCRED` is defense-in-depth: a peer whose uid is not the socket owner is closed immediately, before any data is read.
- **JSON Lines protocol** — one request per line (`{"id", "method", "params"}`); the response is `result` XOR `error`; no batch, no notifications (JSON-RPC 2.0 was rejected; the envelope stays shape-compatible).
- **`hello` is the mandatory first request** on every connection (version negotiation); any other method before it gets error 4 `version_unsupported`.
- **Methods** — `hello`, `status`, `start`, `stop`, `restart`, `logs`, `health`; `start`/`stop` are idempotent (`already-running` / `already-stopped`); `logs` with `follow: true` is a frame stream.
- **Error codes come in ranges** — `<100` protocol, `100–199` lifecycle, `200` authz, `500` infra; a client maps unknown codes by range.
- **System scope is defined but deferred** — `/run/vesma` (`0750`, `root:vesma-oper`, `SO_PEERCRED` on every accept + audit) is specified for the v2 horizon; v1 uses the user profile, with a fallback directory when `XDG_RUNTIME_DIR` is empty.

## Examples

[examples/example-session.txt](examples/example-session.txt) — a minimal session: `hello` → `status` → `start`
→ `status` → `logs` → `stop` → idempotent repeat `stop` + one error. All values are placeholders.

## Validate

[conformance/checklist.md](conformance/checklist.md) — 16 executable checks (permissions independent of umask,
bind-first with a liveness probe, `hello` gating, idempotency, limits incl. follow-stream caps, unix-only
transport); system-profile items are `n/a (v2)`.

## Status

`1.0.0-draft.2` — deep-review wave 2 normative amendments (2026-10-05, pre-implementation):
follow-stream limits, bind-first stale procedure, error-data hygiene. Shape ratified by the
founding VESMA ArchCom on 2026-10-04 (ADR-0001); becomes stable (`1.0.0`) with the first conformant
implementation in the `vesma` engine.

## See also

- [spec.md](spec.md) — full normative text: bind procedure, method tables, threat model.
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — repo structure and contract discipline.
