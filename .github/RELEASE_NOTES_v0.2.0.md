# vesma-specs v0.2.0 — DRAFT release notes (GWS curates at release time)

> **Draft status.** Written 2026-10-28 on branch `spec/agent-discovery-v0`
> as the release material. GWS owns the release movement (owner directive
> 2026-10-27): verify the published state, cut the tag, publish the
> release object, fill the artifact and verification numbers below from
> the actual release run. Nothing here is a release until the tag and the
> release object exist.

The second repository release of **vesma-specs**: the service-track
contracts ratified `1.0.0` stable by their first conforming
implementation, the first additive contract minor (CM 1.1.0), a new
draft generation of the layout contract (dual-profile), a new contract
for the model discovery wire (agent-discovery v0), and the discussion
basis for the component platform (platform-v2).

## What is in the release (v0.1.0..HEAD)

### Service track ratified stable (2026-10-05)

- [component-manifest](https://github.com/vesmaro/vesma-specs/blob/main/specs/component-manifest/v1/spec.md),
  [service-lifecycle](https://github.com/vesmaro/vesma-specs/blob/main/specs/service-lifecycle/v1/spec.md),
  [control-socket](https://github.com/vesmaro/vesma-specs/blob/main/specs/control-socket/v1/spec.md),
  [layout](https://github.com/vesmaro/vesma-specs/blob/main/specs/layout/v1/spec.md)
  v1 — `1.0.0-draft.2` → **`1.0.0` stable**, ratified by the first
  conforming implementation: the
  [vesma](https://github.com/vesmaro/vesma) engine, main `4a2da5a`.
  Evidence: SL-01..18 (incl. SL-06 podman PID1), CS-01..16 (live
  cross-uid leg), LY-01..14 (LY-13 n/a in v1; LY-12 = engine PR #497),
  CM-01..17, conformance runner 24/24.
- review-2 hardening on all four: the honest single-trust-domain
  isolation model, follow-stream limits, bind-first stale procedure,
  venv ReadOnlyPaths, PATH canon, downgrade allowlist, reserved
  `venv`/`venvs` names, artifact hash required for the core tier.
- `decision-provider` v1 stays **draft**: the engine conformance run of
  2026-10-05 is recorded, ratification awaits DP-01/06/12.

### CI and tooling

- Bilingual sync gate: `spec.en.md` mirror pairs are a required check.
- Breaking-change check flipped to **strict mode** — the `v0.1.0` tag
  is the baseline.
- Release workflow pins member mtimes in the contracts bundle.

### component-manifest 1.1.0 (additive, ratified stable)

- §3.5.1 `launch.python` — dependency declaration for python children:
  `version` constraint + `requirements[]` exact `name==version` pins,
  PyPI-only; `{engine_version}` placeholder inside requirements
  (vesmaro/vesma#515).
- §3.12 auth-injecting components and proxies as a named **trust
  boundary** (ADR-0042 condition (a) in the engine repo) — cascade
  review required for the spec version that first carries one.
- Ratified stable: first conformant implementation merged — engine main
  `aad0d0a` (2026-10-07); conformance runner 27/27 (TL re-run); engine
  suite 6328 passed / 8 skipped / 0 failed (TL personal re-run).

### Unit example parity (vesmaro/vesma#509)

- `RuntimeDirectory=vesma` + `RuntimeDirectoryMode=0700` in the unit
  example — unitgen parity with the engine.

### Platform-v2 proposals (discussion basis, not ratified here)

- `docs/proposals/`: the component-platform discussion document and the
  owner amendment (dual-profile reframe, cluster profile WS8, naming
  re-scope).

### layout v2 — dual-profile (draft)

- [layout v2](https://github.com/vesmaro/vesma-specs/blob/main/specs/layout/v2/spec.md)
  `2.0.0-draft.1` — the per-user / system-wide choice as a first-class
  install-time decision; the user profile is self-contained under
  `~/.vesma/**`; the system profile is full FHS (`/etc/vesma`,
  `/var/lib/vesma`, `/usr/lib/vesma`, `/var/cache/vesma`, journald).
  Ratified form: ArchCom 2026-10-21, [ADR-0045](https://github.com/vesmaro/vesma/blob/main/docs/project/adr/0045-dual-profile-fhs-layout.md)
  in the engine repo. v1 stays immutable as the legacy-generation norm.

### agent-discovery v0 — model discovery wire (draft, new contract)

- [agent-discovery](https://github.com/vesmaro/vesma-specs/blob/main/specs/agent-discovery/v0/spec.md)
  `0.1.0-draft` — the wire contract for the additive `models` field of
  the outbound agent's discovery report
  (`POST /api/executors/{id}/discovery`): names-only reads through a
  built-in per-harness layout table, `base_url` normalization with
  credential stripping, `auth` as an enum fact from field presence,
  caps with shrink-to-fit (64 rows / 50 models / 16 KiB / 8 KiB
  read-cap), the anonymous loopback probe leg, the leak discipline
  (row drop before marshal, loud local log with the value suppressed),
  the `discovery_models: auto|off` knob, snapshot/no-wipe semantics,
  board ingest duties (drop+audit, honest 422, the
  `models.credential_leak_suspected` detector), error codes, examples,
  a conformance skeleton, a mini-STRIDE threat model, and an honest
  implementation-status section.
- Codifies protocol amendment AGW-25 (vesma-agent,
  `feat/models-discovery`); authority trail: the three ratified
  models-fleet gates in vesma-eyes — discovery-contract-draft
  (`daf969b`), security-verdict (`832cd7a`), ux-blueprint (`cb166a8`)
  — plus the owner directive of 2026-10-28. Decision record:
  [ADR-0002](https://github.com/vesmaro/vesma-specs/blob/main/adrs/0002-agent-discovery-contract.md).
  The agent leg is merged; the board mirror (ingest into
  `GET /api/models`) is the next vesma-eyes wave.

### Pending-merge drafts (NOT in this release unless merged before the cut)

- `context-lifecycle` v0 skeleton — public extension spec draft (nhi-8
  wave 0): branch `spec/context-lifecycle-0` (dac97f2). Normative EN
  skeleton; RU bridge; no machine schema/examples in v0.
- `integration-contract` v0 skeleton — three-layer two-way integration
  contract (nhi-8): branch `spec/integration-contract-v0` (d930c9c).
- GWS: include these sections only if the branches are merged by the
  release commit.

## Contract statuses at release time

| Contract | Version | Status |
|---|---|---|
| component-manifest | 1.1.0 | stable |
| service-lifecycle | 1.0.0 | stable |
| control-socket | 1.0.0 | stable |
| layout | v1 1.0.0 / v2 2.0.0-draft.1 | stable / draft |
| decision-provider | 1.0.0-draft | draft |
| agent-discovery | 0.1.0-draft | draft |

## Versioning note

Repository releases stay on the `v0.x` scale while any contract is in
draft; the first stable repository release is v1.0.0, synchronized with
full contract ratification. Contract-level SemVer (`version:` in each
spec header) and repository-level tags are related but distinct scales.

## Artifacts (GWS: fill from the actual release run)

| Artifact | Contents |
|---|---|
| `vesma-specs-v0.2.0-contracts.tar.gz` | all `specs/*/v*/` contract directories (RU and EN specs, schemas, examples, conformance suites), `adrs/`, `GLOSSARY.md`, `ECOSYSTEM.md`, `LICENSE` |
| `conformance-report.json` | the conformance run against the tagged tree |
| `SHA256SUMS` | SHA-256 checksums — verify with `sha256sum -c SHA256SUMS` after download |

## Verification (GWS: fill from CI on the release commit)

CI on the release commit must be fully green: markdownlint; conformance
runner; schema-lint; breaking-change check (strict, baseline v0.1.0);
bilingual sync; gitleaks over the full history.

## Links

- [README](https://github.com/vesmaro/vesma-specs/blob/main/README.md)
- [ECOSYSTEM](https://github.com/vesmaro/vesma-specs/blob/main/ECOSYSTEM.md)
- [ADR-0001](https://github.com/vesmaro/vesma-specs/blob/main/adrs/0001-repo-structure-and-governance.md),
  [ADR-0002](https://github.com/vesmaro/vesma-specs/blob/main/adrs/0002-agent-discovery-contract.md)
- [Roadmap](https://github.com/vesmaro/vesma-specs/blob/main/docs/roadmap.md)

---

**RU.** Второй релиз репозитория vesma-specs: сервис-трек контрактов
(CM/SL/CS/LY v1) ратифицирован `1.0.0` stable первой конформной
реализацией (движок vesma, main `4a2da5a`, 2026-10-05); первый
аддитивный минор контракта — CM 1.1.0 (`launch.python` requirements для
python-чилдов #515 + auth-injecting прокси как trust boundary 3.12;
ратифицирован движком main `aad0d0a`, раннер 27/27); новая драфтовая
генерация лэйаута — v2 dual-profile (самодостаточный user-профиль
`~/.vesma` + FHS system, АрхКом 2026-10-21, ADR-0045 движка); новый
контракт провода discovery моделей — agent-discovery v0 (кодификация
AGW-25; три гейта флота моделей vesma-eyes: daf969b, 832cd7a, cb166a8;
ADR-0002); обсуждение компонентной платформы — platform-v2 proposals.
Черновики вне main на момент драфта: context-lifecycle v0
(`spec/context-lifecycle-0`) и integration-contract v0
(`spec/integration-contract-v0`) — включаются GWS только при влитии до
реза. Релизы репозитория остаются на шкале `v0.x`, пока хотя бы один
контракт в draft; первый стабильный — v1.0.0.
