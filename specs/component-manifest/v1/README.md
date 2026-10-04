# Component Manifest v1 — Quickstart

The Component Manifest is the declarative YAML description a component ships to join the VESMA ecosystem — the
single source of truth for the CLI and the supervisor on how the component runs, how its liveness is judged, how
it is stopped and what it depends on. The CLI is contract-driven (CLI-first, ADR-0001): a component declares
itself with a manifest — no per-component CLI code.

## Normative spec

- [spec.md](spec.md) — normative contract (Russian canon, RFC 2119 keywords).
- Full English mirror: [spec.en.md](spec.en.md).
- [schema/component-manifest.schema.json](schema/component-manifest.schema.json) — machine schema (JSON-Schema 2020-12); every manifest MUST validate against it.

## Key rules

- **Strict validation** — `additionalProperties: false` on every schema object; an unknown field is rejected, never passed through; evolution goes through `apiVersion` (additive fields = minor contract version).
- **`apiVersion` required** — must be `vesma.component/v1`; an unsupported version is rejected with the list of supported versions.
- **Reserved names** — `metadata.name` must never be `venv` or `venvs` (reserved for the layout's venv directories, specs/layout/v1 §3.8); the validator rejects the collision.
- **`artifact_sha256` by tier** — mandatory for `tier: core`; for `optional` it is optional, and its absence surfaces as a `doctor` WARN.
- **`argv` is a list, no shell** — a string array without shell metacharacters or `sh -c`; placeholders expand by supervisor allowlist only (`{config_path}`, `{data_dir}`, `{runtime_dir}`, `{venv_bin}`).
- **Secrets only via `env_file`** — never in the manifest or `env.vars`; the file lives outside the manifests directory, mode `0600`, owner = supervisor user; loading is fail-closed — any violation aborts the start.
- **In-process health = `liveness` by default** (module imported, factory ran); the optional `callback` probe runs in an isolated boundary — any exception or timeout yields `failed` and never crashes the supervisor.

## Examples

| File | Shows |
|---|---|
| [examples/python-inprocess.yaml](examples/python-inprocess.yaml) | in-process Python module (`board`): factory, `health.callback`, `config.schema_inline` |
| [examples/go-child.yaml](examples/go-child.yaml) | child-process Go binary (`mesh`): `launch.argv` with `{config_path}`, `health.http`, `artifact_sha256` |
| [examples/node-runtime.yaml](examples/node-runtime.yaml) | external Node runtime (`eyes`): `health.tcp`, `depends_on: [server]` |

## Validate

From the repo root: `python3 tools/conformance/run.py specs/component-manifest/v1`. The suite is
[conformance/cases.yaml](conformance/cases.yaml) — positive cases from `examples/` plus negative fixtures under
`conformance/fixtures/invalid/`. The runner (stdlib + `jsonschema`, declarations only) is a separate tooling
deliverable. Integrator checklist: [conformance/checklist.md](conformance/checklist.md) (CM-01…CM-17).

## Status

`1.0.0-draft.2` — deep-review wave 2 normative amendments (2026-10-05, pre-implementation): reserved
names `venv`/`venvs`, `artifact_sha256` mandatory for `tier: core`. Shape ratified by the founding
VESMA ArchCom on 2026-10-04 (ADR-0001); becomes stable (`1.0.0`) with the first conformant
implementation in the `vesma` engine.

## See also

- [spec.md](spec.md) — full normative text: error codes, threat model, migration.
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — repo structure, contract discipline, the i18n rule.
