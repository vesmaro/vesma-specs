# vesma-specs v0.1.0 — founding release

The founding release of **vesma-specs**, the contract-and-specification
layer of the VESMA ecosystem: four integration contracts, the governance
decision that defines them (ADR-0001), a deterministic conformance runner,
and a CI pipeline that enforces all of it on every change. Contracts live
here before and independently of the code — this release is the baseline
the engine implements against.

## What is in the release

- Four integration contracts at `1.0.0-draft.1`, each with a Russian
  canon spec, an English mirror, and an English quickstart README:
  - [component-manifest](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/specs/component-manifest/v1/spec.md) — how a component declares itself: identity, execution kind, lifecycle hooks, environment policy, dependencies. Ships a JSON Schema (Draft 2020-12) and a 22-case conformance suite.
  - [service-lifecycle](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/specs/service-lifecycle/v1/spec.md) — states, transitions, supervision, and the history journal every service keeps.
  - [control-socket](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/specs/control-socket/v1/spec.md) — the engine control API: a text protocol over a unix socket with JSON payloads and a fixed status map.
  - [layout](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/specs/layout/v1/spec.md) — the on-disk world: config schema location, engine venv path, reserved names, 0600 system env files.
- [ADR-0001](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/adrs/0001-repo-structure-and-governance.md) — the founding Architectural Committee verdict: repository structure, version-directory immutability, governance, i18n and secrets discipline.
- Conformance runner v0 (`tools/conformance/run.py`) — validates declarations, never executes component code; stdlib plus jsonschema, with a fallback mini-YAML parser.
- CI pipeline — five jobs on every PR and push: markdownlint, conformance, schema-lint, breaking-change check, gitleaks.

## Contract status: draft

All four contracts are `1.0.0-draft.1`. A draft is ratified by its first
implementation in the engine — the `cli-service-management` card, phase 3
of the [roadmap](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/docs/roadmap.md).
Until ratification the contracts may still change in any part; after it, a
breaking change requires a contract MAJOR bump and a deprecation window.

## Versioning note

Repository releases are numbered `v0.x` while the contracts are in draft.
The first stable repository release will be **v1.0.0**, synchronized with
the ratification of the contracts. Contract-level SemVer (`version:` in
each `spec.md`) and repository-level SemVer (tags) are related but
distinct scales.

## Artifacts

| Artifact | Contents |
|---|---|
| `vesma-specs-v0.1.0-contracts.tar.gz` | all four `specs/*/v1/` contract directories (RU and EN specs, schemas, examples, conformance suites), `adrs/`, `GLOSSARY.md`, `ECOSYSTEM.md`, `LICENSE` |
| `conformance-report.json` | the conformance run against the tagged tree: 22 passed, 0 failed, 0 warned |
| `SHA256SUMS` | SHA-256 checksums of both files above — verify with `sha256sum -c SHA256SUMS` after download |

Checksums are computed by the release workflow over the exact published
binaries — see the `SHA256SUMS` asset.

## Verification

CI on the release commit is fully green: markdownlint; conformance
(22 of 22 MUST cases passed); schema-lint (2 schemas and 22 example and
fixture files); breaking-change check (report mode for this release — the
v0.1.0 tag becomes its baseline, and CI flips to strict mode immediately
after); gitleaks over the full history.

## Links

- [README](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/README.md) — repository overview (EN primary, RU mirror)
- [ECOSYSTEM](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/ECOSYSTEM.md) — ecosystem map: components, tiers, contract statuses
- [ADR-0001](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/adrs/0001-repo-structure-and-governance.md) — founding governance decision
- [Roadmap](https://github.com/vesmaro/vesma-specs/blob/v0.1.0/docs/roadmap.md) — phases 0–4 with checklists

---

**RU.** Учредительный релиз контрактно-спекификационного слоя VESMA: четыре
интеграционных контракта в статусе `1.0.0-draft.1` (component-manifest,
service-lifecycle, control-socket, layout — русский канон плюс английские
зеркала и quickstart), ADR-0001 о структуре и governance репозитория,
конформанс-раннер v0 и CI из пяти зелёных джоб. Контракты-черновики
ратифицируются первой реализацией в движке (карточка
`cli-service-management`, фаза 3 роадмапа); пока контракты в draft, релизы
репозитория нумеруются `v0.x`, первый стабильный релиз — v1.0.0, синхронно
с ратификацией. Целостность артефактов проверяется по файлу `SHA256SUMS`
из приложенных к релизу ассетов.
