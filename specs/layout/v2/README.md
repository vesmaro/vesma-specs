# Canonical Layout v2 — Quickstart

Layout v2 fixes where everything lives for a **dual-profile** VESMA
installation: the "per-user / system-wide" choice is a first-class product
decision at install time. The user profile is **self-contained** under
`~/.vesma/**` (one tree — one unit of backup, removal and audit; the
precedents are `~/.vscode` and `~/.nvm`). The system profile is full FHS
(`/etc/vesma`, `/var/lib/vesma`, `/usr/lib/vesma`, `/var/cache/vesma`,
journald) for system-wide deployments, containers and future deb/rpm.

Ratified form: ArchCom 2026-10-21, [ADR-0045](https://github.com/vesmaro/vesma/blob/main/docs/project/adr/0045-dual-profile-fhs-layout.md)
in the engine repo. Status: draft until the first conforming
implementation.

## Normative spec

[spec.md](spec.md) — the normative contract (Russian canon, RFC 2119); the
tables below are its §3 summary.

Full English mirror: [spec.en.md](spec.en.md).

## Key paths

| Area | User (v2, default) | System (FHS, opt-in) |
|---|---|---|
| Shared config | `~/.vesma/config.yaml` (`0600`) | `/etc/vesma/config.yaml` (`0640 root:vesma`, conffile) |
| Component manifests | `~/.vesma/components.d/<name>.yaml` | `/etc/vesma/components.d/<name>.yaml` (`0640 root:vesma`, conffile) |
| Env secrets | `~/.vesma/env.d/<name>.env` (`0600`, fail-closed) | `/etc/vesma/env.d/<name>.env` (`0600 root:vesma` — doctor FAIL gate) |
| Component data (default cwd) | `~/.vesma/components/<name>/` | `/var/lib/vesma/<name>/` (`0750 vesma:vesma`, DB `0600`) |
| Engine venv | `~/.vesma/venv/` | `/usr/lib/vesma/venv/` (root-owned) |
| Component venvs | `~/.vesma/venvs/<name>/` | `/usr/lib/vesma/venvs/<name>` — symlink revisions, atomic swap |
| Logs | journald canon; files-under-state `~/.vesma/logs/<name>/` | journald primary; `/var/log/vesma/<name>/` — opt-in only |
| Supervisor history | `~/.vesma/history/` | `/var/lib/vesma/history/` |
| Cache (never secrets) | `~/.vesma/cache/<name>/` (`0750`) | `/var/cache/vesma/<name>/` (`0750 vesma:vesma`) |
| Runtime (socket, pids) | `${XDG_RUNTIME_DIR}/vesma/` (fallback `~/.vesma/run/` + WARN) | `/run/vesma/` (`RuntimeDirectoryMode=0750`) |
| Install state | — | `/var/lib/vesma/install-state.yaml` → exact-inverse uninstall |
| Distro static | inside the wheel | `/usr/share/vesma/` |

## Key rules

- **The profile is a first-class install-time choice**: `vesma service
  install` (user, the default) vs `sudo vesma service install --system`
  (system). Both profiles on one data root = doctor FAIL (DR-14).
- **One declarative FHS manifest** (§3.12) is the single source of truth
  for the installer, the container build and future deb/rpm: paths, modes,
  owners, flags — nothing hardcodes paths outside it.
- **Working installations never break on a canon change**: an installed
  deployment is stamped with its layout generation (`v1.5` XDG-spread or
  `v2` self-contained); the resolver follows the stamp. Consolidating a
  v1.5 install into `~/.vesma` is an explicit operator step (§9.2).
- **One managed venv per Python unit**, `PYTHONNOUSERSITE=1`
  unconditionally, exact pins against the lock; system venvs are
  root-owned and materialized by the installer (`uv venv` + the
  same-build wheel — never `pip` as root), updated by an atomic
  symlink swap.
- **env.d is fail-closed in both profiles** — `0600`, only the supervisor
  account reads; any drift aborts the start with a ready fix command and
  is a doctor FAIL in system.
- **journald is the primary log store in both profiles**; file logs exist
  only as `files-under-state` (user, when journald is absent) or a system
  opt-in (`/var/log/vesma`); double writing is forbidden.
- **Units coexist without prefixes**: user `vesma.service` and system
  `vesma.service` in their systemd scopes; IPC is profile-derived.
- **Integration surfaces in foreign harnesses (mcp.json, shell rc) are
  external** — the layout documents them, it does not own them.

## Sibling contracts

[component-manifest v1](../../component-manifest/v1/spec.md) (what a
manifest is), [service-lifecycle v1](../../service-lifecycle/v1/spec.md)
(what the supervisor does with these paths),
[control-socket v1](../../control-socket/v1/spec.md) (socket protocol and
permissions), [layout v1](../v1/spec.md) (the previous version — the
legacy v1.5 generation).
