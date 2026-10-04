# Canonical Layout v1 — Quickstart

The canonical layout fixes where configs, manifests, env files, data, venvs, state, runtime artifacts and cache
live for a **user-profile** installation — deb-package discipline for a per-user service stack. It is one of the
four founding-phase contracts of this repository, consumed by the manifest, service-lifecycle and
control-socket contracts.

## Normative spec

[spec.md](spec.md) — the normative contract (Russian canon, RFC 2119): the path table below is its §3 summary.
It also canonizes the manifests directory (`components.d/`) and the socket name (`control.sock`), which the
sibling contracts reference.

## Key paths (user profile)

| Area | Path |
|---|---|
| Common config | `~/.config/vesma/vesma.yaml` |
| Manifests (drop-in) | `~/.config/vesma/components.d/<name>.yaml` |
| Env files (secrets) | `~/.config/vesma/env/<name>.env` — file mode `0600` |
| Data | `~/.local/share/vesma/<component>/` |
| Component venvs | `~/.local/share/vesma/venvs/<component>/` |
| State: file logs | `~/.local/state/vesma/logs/<component>/` (only when journald is absent; rotation 10 MB × 5) |
| State: supervisor history | `~/.local/state/vesma/history/` |
| State: runtime fallback | `~/.local/state/vesma/run/` (only when `XDG_RUNTIME_DIR` is empty, with a warning) |
| Runtime (socket directory) | `${XDG_RUNTIME_DIR}/vesma/` — `control.sock` (0600), directory 0700 |
| Cache | `~/.cache/vesma/<component>/` — never holds secrets |
| System profile | `/etc/vesma`, `/var/lib/vesma`, `/run/vesma` — defined in the spec, implementation deferred (v2); `/var/log/vesma` is NOT created in v1 |

## Key rules

- **One managed venv per Python runtime unit** inside the layout, `PYTHONNOUSERSITE=1` injected unconditionally;
  two components sharing one venv is an error. `doctor` checks user-site leakage, venv ownership/permissions and
  `pip freeze` drift against the lock.
- **Env files live outside the manifests directory** — mode `0600`, owner = supervisor user; loading is
  fail-closed: a violated condition aborts the start with the ready-to-run fix command (component-manifest §3.5).
- **journald is the primary log store** — the unit sends everything to the journal (`StandardOutput=journal`);
  component lines are forwarded with `SYSLOG_IDENTIFIER=vesma-<component>`, so `vesma service logs` is a
  journalctl filter. When journald is absent (container, manual run), the only permitted file location is
  `~/.local/state/vesma/logs/<component>/` — no other log locations exist.
- **Cache is regenerable data only** — the cache API never accepts secret content.
- **Legacy path migration** — the spec's migration section maps the legacy tree onto canonical roots:
  `~/.config/mnemos-mesh/*.yaml` → `~/.config/vesma/{vesma.yaml, components.d/}` (legacy name),
  scattered logs (`ops/*.log`, ad-hoc files) → journald or `state/logs`, the token-bearing ops env file →
  `~/.config/vesma/env/<name>.env` (0600, fail-closed), legacy `venv-5.x` trees → `venvs/<name>/`;
  K3s-era helm revisions and the nohup launcher are discarded, not migrated. Actual prod migration is gated
  to after 2026-10-16 (B0 telemetry window) and lives in the engine track.

## Validate

No standalone layout suite yet — the executable gate for manifests lives in
[component-manifest](../component-manifest/v1/) (`tools/conformance/run.py`); adjacent checks cover env-file
placement (CM-09), socket directory and socket permissions (control-socket checks 1–2) and unit `ReadWritePaths`
(SL-17/SL-18). The layout conformance checklist: [conformance/checklist.md](conformance/checklist.md).

## Status

`1.0.0-draft.1` — shape ratified by the founding ArchCom (2026-10-04, ADR-0001); becomes stable with the first
engine implementation (`vesma service install` consuming this layout).

## See also

- [spec.md](spec.md) — normative canon (path tables, venv discipline, doctor checks, migration).
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — repo structure and contract discipline.
- [GLOSSARY.md](../../../GLOSSARY.md) — Canonical layout, venv discipline, Runtime directory.
