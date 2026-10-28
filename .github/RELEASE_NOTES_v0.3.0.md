# vesma-specs v0.3.0 — host-intake v0, agent-discovery 0.1.0-draft.2, ADR-0003

The third repository release of **vesma-specs**: the host-intake
contract (the explicit "what the agent collects" catalog — the trust
and transparency surface), the agent-discovery re-key amendment
(0.1.0-draft.2), the decision record ADR-0003, and the markdownlint
hotfix already on main.

## What is in the release (v0.2.0..main)

### host-intake v0 — the explicit collection catalog (draft, new contract)

- [host-intake](https://github.com/vesmaro/vesma-specs/blob/main/specs/host-intake/v0/spec.md)
  `0.1.0-draft` — the COMPLETE explicit catalog of what the outbound
  agent collects on a host (clause 2 of the owner directive
  2026-10-28): the closed fact-class list FC-1…FC-9 with statuses and
  caps; the P1–P6 surface principles; the verbatim never-collected
  boundary (file contents outside the named exceptions, project
  names, prompts/session content, env VALUES, traffic, credential
  material); the field → FC map.
- Normative here: FC-6 — models keyed to DISCOVERED harnesses (the
  per-harness layout table: zcode/copilot agent frontmatter
  `model:`/`tier:`; codex, continue, claude-code, aider carried from
  v6; the pi auth-marker row; gemini/qwen absent); documented provider
  string forms with dual-form emission (raw strings + the parsed
  provider, never guess); the anonymous loopback probe — the fixed v6
  port table plus ≤8 harness-configured loopback base_urls (never
  credentialed — the H3 verdict); the v6 red lines carried verbatim.
  FC-7 — the additive top-level `mcp_servers` field
  (`{harness, exec_env, servers[] ≤30 sorted, count = full total}`;
  names + transport kind only; pi `mcp-cache.json` keys as names,
  values never decoded; the shared `discovery_models` knob).
- FC-8 (tooling) and FC-9 (compute envelope): catalogued, status
  **DEFERRED (v2)** — the owner's decision recorded at the draft gate.
- The transparency surface (P6): the board renders "what agents
  collect" FROM the contract per agent version — the contract text
  ships with the agent (build-pinned docs; the version handshake).
- `sessions[]` recorded OUTSIDE the agent's collection surface: the
  field is fed by the board's eyes-side scanner (the ME-062
  task-session-fact leg; the kora-scan ingest; the synthetic `hermes`
  executor id), verified in the board (`server/app.py`) and the agent
  (no session-fact construction in `internal/discovery`,
  `internal/board`) code on 2026-10-28.
- Authority trail: the agent-side contract draft
  (`docs/design/host-intake-contract-draft.md`, vesma-agent
  `feat/host-intake-contract`) with owner-approved gates (FC-6+FC-7
  this wave; the probe approved; dual-form emission approved;
  FC-8/FC-9 deferred); the carried fleet security-verdict red lines
  (832cd7a); the AGW-25/AGW-26 lineage. Ships with examples
  (a zcode frontmatter row, the pi auth-marker row, the `mcp_servers`
  field, credential-redaction before/after), a declarative conformance
  skeleton (`cases.skeleton.yaml` — the runner-profile precedent), an
  integrator checklist, and a mini-STRIDE threat model.
- Implementation status (honest, §9 of the spec): the agent side of
  this contract SHIPS TODAY — vesma-agent v0.11.0 (2026-10-28)
  implements exactly this wire (discovery v7 per-harness model rows +
  the `mcp_servers` fact class, live-verified on the core-51 host:
  a real model row from copilot frontmatter where the v6 table
  reported none); the board mirror + transparency rendering are the
  pending vesma-eyes wave; FC-8/FC-9 deferred to v2.

### agent-discovery v0 amended: 0.1.0-draft → 0.1.0-draft.2

- The `models` field's POPULATION rules re-keyed per host-intake
  (clause 1 of the owner directive): the v6 standalone table is
  superseded — it produced zero rows on the real fleet (verified live
  2026-10-28 on core-51); the per-harness layout table is ATTACHED to
  the fingerprint inventory, so a model row can only exist for a
  harness the agent actually discovered.
- The probe leg extended: harness-configured loopback base_urls may be
  probed anonymously (≤8 extra targets; never non-loopback, never
  credentialed).
- The `mcp_servers` field (FC-7) recorded as the additive sibling; the
  `discovery_models` knob governs both.
- NOT renumbered and NOT breaking: the released contract version stays
  within the draft status (0.1.0-draft.2); the §3.2 row form and the
  §3.11 board duties are unchanged; the wire is additive — old boards
  and old agents stay conformant.

### ADR-0003 — the explicit collection catalog decision

- [ADR-0003](https://github.com/vesmaro/vesma-specs/blob/main/adrs/0003-host-intake-catalog.md)
  (+ EN mirror) — why the collection catalog exists as a contract: the
  trust/transparency decision, the authority trail (the owner
  directive's two clauses + the approved contract draft), the scope
  (catalog + FC-6 re-key + FC-7; FC-8/9 deferred), the considered
  alternatives (implicit surface + code audits; extending the v6
  standalone table), and the wave obligations.

### Already on main (v0.2.0..origin/main before this branch)

- `070e012` — agent-discovery v0 EN mirror markdownlint fix (MD028:
  joined the mirror-note and status quotes with a blank quote line;
  was red on the release commit `d22f4cf`).

### Pending-merge drafts (not in this release)

- `context-lifecycle` v0 skeleton — public extension spec draft
  (nhi-8 wave 0): branch `spec/context-lifecycle-0` (dac97f2).
- `integration-contract` v0 skeleton — three-layer two-way integration
  contract (nhi-8): branch `spec/integration-contract-v0` (d930c9c).

## Contract statuses at release time

| Contract | Version | Status |
|---|---|---|
| component-manifest | 1.1.0 | stable |
| service-lifecycle | 1.0.0 | stable |
| control-socket | 1.0.0 | stable |
| layout | v1 1.0.0 / v2 2.0.0-draft.1 | stable / draft |
| decision-provider | 1.0.0-draft.2 | draft |
| agent-discovery | 0.1.0-draft.2 | draft |
| host-intake | 0.1.0-draft | draft |

## Versioning note

Repository releases stay on the `v0.x` scale while any contract is in
draft; the first stable repository release is v1.0.0, synchronized with
full contract ratification. Contract-level SemVer (`version:` in each
spec header) and repository-level tags are related but distinct scales.
The draft.N suffix is a pre-release increment WITHIN the draft status —
not a renumbering of a released contract version.

## Artifacts

| Artifact | Contents |
|---|---|
| `vesma-specs-v0.3.0-contracts.tar.gz` | all `specs/*/v*/` contract directories (RU and EN specs, schemas, examples, conformance suites), `adrs/`, `GLOSSARY.md`, `ECOSYSTEM.md`, `LICENSE` |
| `conformance-report.json` | the conformance run against the tagged tree |
| `SHA256SUMS` | SHA-256 checksums — verify with `sha256sum -c SHA256SUMS` after download |

## Verification

All gates green on the release commit, run before the cut:

- Conformance: the deterministic runner (`tools/conformance/run.py
  --all specs/`) reports **27 passed / 0 failed / 0 warned** on the
  release tree. The release workflow re-runs the identical suite as
  its publication gate and publishes only after it passes.
- Schema-lint (`tools/ci/schema_lint.py .`): 2 schema files and 28
  example/fixture YAML files checked, 0 errors, 0 warnings.
- Bilingual sync (`tools/ci/bilingual_check.py .`): 8 contract
  version dirs and 3 ADR mirror pairs checked, 0 violations.
- Breaking-change check (`tools/ci/breaking_check.py specs/
  --strict`, baseline = latest tag `v0.2.0`): 0 findings — no
  breaking schema change without a major bump.
- Secrets: gitleaks over the full history runs in CI on the push;
  the wave diff also passed a targeted sensitive-data scan at the
  cut.
- markdownlint gates CI on the push (it is deliberately not part of
  release.yml); the branch content passed a targeted markdown-rule
  check, and CI is verified green on the release commit before the
  tag is pushed.

## Links

- [README](https://github.com/vesmaro/vesma-specs/blob/main/README.md)
- [ECOSYSTEM](https://github.com/vesmaro/vesma-specs/blob/main/ECOSYSTEM.md)
- [ADR-0001](https://github.com/vesmaro/vesma-specs/blob/main/adrs/0001-repo-structure-and-governance.md),
  [ADR-0002](https://github.com/vesmaro/vesma-specs/blob/main/adrs/0002-agent-discovery-contract.md),
  [ADR-0003](https://github.com/vesmaro/vesma-specs/blob/main/adrs/0003-host-intake-catalog.md)
- [Roadmap](https://github.com/vesmaro/vesma-specs/blob/main/docs/roadmap.md)

---

**RU.** Третий релиз репозитория vesma-specs (2026-10-28): контракт
host-intake v0 — явный каталог «что агент
собирает на хосте» (поверхность доверия/прозрачности; пункт 2 директивы
владельца 2026-10-28): закрытый каталог FC-1…FC-9, принципы P1–P6,
дословная граница «никогда не собирается»; нормативно — FC-6
(per-harness re-key моделей; zcode/copilot frontmatter; pi
auth-маркерная строка; dual-form emission; loopback-probe с ≤8
harness-настроенными base_url; красные линии v6 verbatim) и FC-7
(`mcp_servers` — имена + transport kind, count = полный итог); FC-8/9 —
DEFERRED (v2). Поправка agent-discovery до 0.1.0-draft.2: re-key
населения `models` per host-intake (v6 standalone-таблица superseded —
ноль строк на реальном флоте, проверено живьём 2026-10-28), probe через
harness-настроенные loopback base_url, поле `mcp_servers`; без
перенумерации и без ломающих изменений (провод аддитивен). ADR-0003 —
запись решения. Уже на main: 070e012 — markdownlint-фикс EN-зеркала
agent-discovery (MD028). Полномочия: агентный драфт
`host-intake-contract-draft.md` (vesma-agent `feat/host-intake-contract`,
гейты утверждены владельцем), security-verdict 832cd7a (красные линии),
линия AGW-25/AGW-26. Вне релиза: черновики context-lifecycle v0
(`spec/context-lifecycle-0`, dac97f2) и integration-contract v0
(`spec/integration-contract-v0`, d930c9c). Статусы ног — честно:
агентная волна v7 (AGW-26) выпущена как vesma-agent v0.11.0
(2026-10-28; живая проверка на хосте core-51 — реальная строка моделей
из copilot frontmatter там, где таблица v6 давала ноль); борд-зеркало +
рендер прозрачности — ожидающая волна vesma-eyes. Проверка: все гейты
зелёные на релизном коммите — conformance 27 passed / 0 failed /
0 warned, schema-lint (0 ошибок), bilingual sync (0 нарушений),
breaking-check strict (0 находок), gitleaks и markdownlint — в CI на
пуше; CI проверен зелёным на релизном коммите до резки тега.
