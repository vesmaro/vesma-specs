# vesma-specs v0.5.0 — host-intake 0.1.0-draft.4: container-surface §3.4c

The fifth repository release of **vesma-specs**: the discovery v9
amendment to the host-intake contract (AGW-28), published in lockstep
with the wire that vesma-agent v0.13.0 ships the same day. The FC-6/FC-7
"metal only" red line is lifted for config reads through distrobox
container probes — running containers join the collection surfaces as
the new normative section 3.4c, and config facts become per-surface.

## What is in the release (v0.4.0..main)

### host-intake amended: 0.1.0-draft.3 → 0.1.0-draft.4

- Authority: the owner's «делай» directive of 2026-10-29 (AGW-28);
  mirrored by the agent-side PROTOCOL addendum "Container-surface
  addendum — discovery v9 (AGW-28, 2026-10-29)".
- New normative §3.4c — container config surfaces: RUNNING containers
  only (a stopped container is an honest `not-running` fact, never
  booted); the probe script is GENERATED from the same built-in layout
  table §3.3.2 — no second registry, drift impossible by construction;
  per-file bounded transport out of containers (`head -c 8192`, base64,
  one fenced block per file, ≤ 64 files per container home) — named
  files only, never whole files, never anything outside the table,
  never from stopped containers. The §3.5 boundary gains the
  container-transport line; §3.5/§3.6 numbering untouched (the
  §3.4a/§3.4b precedent against renumbering churn).
- Per-surface row identity (§3.3.1, dictionary §2): a config-fact row
  is the tuple `(provider, base_url, model, harness, exec_env)` — the
  SAME provider+model configured on metal AND inside a container is
  TWO rows. The v4 "one namespace, one truth" dedupe keeps applying to
  ENVIRONMENT homes (the FC-2 exec_env merge), not to config-fact
  rows. FC-6 caps became surface-spanning totals: 64 rows / 16 KiB
  together across metal and all containers; `models[]` ≤ 50 stays
  per-row (§3.3.5).
- FC-7 from containers: MCP server entries via the entry-level
  detector, names and kinds only; the pi auth marker inside containers
  stays `test -f` existence-only — the container transport never reads
  the file's bytes.
- Knobs unchanged: container reads ride `discovery_models` AND
  `discovery_distrobox`, both in `auto` — no new knobs. Quiet
  degradation is normative: the distrobox CLI absent from the agent's
  view = the whole container leg quiet-zero; a container failing
  mid-read = the v4 honest-verdict machine.
- Conformance: two new wire examples (`container-installation-row.json`,
  `mcp-servers-container-entry.json` — placeholders/public values
  only), skeleton cases and the integrator checklist extended
  (HI-21…, the discovery v9 wave).
- Bilingual parity kept (spec.md RU canon + spec.en.md mirror);
  contract CHANGELOG carries the 0.1.0-draft.4 entry.

### Pending-merge drafts (not in this release)

- context-lifecycle v0 (`spec/context-lifecycle-0`, dac97f2) and
  integration-contract v0 (`spec/integration-contract-v0`, d930c9c)
  stay out-of-release drafts.

## Contract statuses at release time

host-intake `0.1.0-draft.4` — draft: FC-1…FC-9 as of v0.4.0; container
config surfaces (FC-6/FC-7 via §3.4c) normative since discovery v9
(this release). agent-discovery `0.1.0-draft.2` unchanged.
component-manifest `1.0.0-draft.2` unchanged.

## Versioning note

Repository release v0.5.0; the host-intake contract version moves
`0.1.0-draft.3` → `0.1.0-draft.4` (header, §7, §9, suite skeleton).
Additive + red-line lift only — no renumbering, no breaking changes
(breaking-check strict).

## Artifacts

- `vesma-specs-v0.5.0-contracts.tar.gz` — the contract tree at the
  tagged commit.
- `conformance-report.json` — the runner's JSON report from the
  tagged tree.
- `SHA256SUMS` — checksums over both artifacts.

## Verification

- The markdownlint gate on the main push is GREEN before the tag is
  cut (the institutionalized gate — a tagged tree that never went
  through a fresh main push cannot ship lint defects).
- Conformance re-runs on the tagged tree in the release workflow
  before anything is published.
- Bilingual sync, schema lint, and the breaking-change detector stay
  in CI on the push; gitleaks likewise.

## Links

- [README](https://github.com/vesmaro/vesma-specs/blob/main/README.md)
- [ECOSYSTEM](https://github.com/vesmaro/vesma-specs/blob/main/ECOSYSTEM.md)
- [host-intake spec](https://github.com/vesmaro/vesma-specs/blob/main/specs/host-intake/v0/spec.md),
  [EN mirror](https://github.com/vesmaro/vesma-specs/blob/main/specs/host-intake/v0/spec.en.md)
- [Roadmap](https://github.com/vesmaro/vesma-specs/blob/main/docs/roadmap.md)

---

**RU.** Пятый релиз репозитория vesma-specs (2026-10-29): поправка
host-intake 0.1.0-draft.4 — discovery v9 (AGW-28, директива владельца
«делай» от 2026-10-29), синхронно с проводом vesma-agent v0.13.0 того
же дня. Красная линия FC-6/FC-7 «metal only» снята для чтения конфигов
через distrobox container probes: новая нормативная секция §3.4c
(нумерация §3.5/§3.6 не тронута), running-контейнеры только
(остановленный — честный `not-running`, не бутится), скрипт пробы
генерируется из той же built-in таблицы §3.3.2 (второго реестра нет —
дрейф невозможен по построению), из контейнера — только bounded
head-only байты названных файлов (`head -c 8192`, base64, fenced-блоки,
≤ 64 файлов на дом), никогда целые файлы и ничего вне таблицы.
Идентичность config-строк — per-surface: кортеж `(provider, base_url,
model, harness, exec_env)`; один и тот же provider+model на metal и в
контейнере = ДВЕ строки; v4-дедуп остаётся домом окружений (FC-2).
Капы FC-6 суммарные по поверхностям: 64 строки / 16 KiB вместе,
`models[]` ≤ 50 per-строка. FC-7 из контейнеров — entry-level
детектор, только имена и виды; pi-маркер внутри контейнера —
`test -f` existence-only. Ручки без изменений: `discovery_models` +
`discovery_distrobox`, обе в `auto`; quiet-деградация нормативна
(нет distrobox CLI — вся контейнерная нога quiet-zero; сбой контейнера
— машина честных вердиктов). Conformance: два новых проводных примера
(`container-installation-row.json`, `mcp-servers-container-entry.json`),
скелет-кейсы и чеклист расширены (HI-21…, волна discovery v9);
двуязычная паритетность одним коммитом; CHANGELOG контракта несёт
запись 0.1.0-draft.4. Статусы: host-intake `0.1.0-draft.4`
(контейнерные config-поверхности нормативны с discovery v9);
agent-discovery `0.1.0-draft.2` и component-manifest `1.0.0-draft.2`
без изменений; context-lifecycle v0 и integration-contract v0 — вне
релиза. Версия репозитория v0.5.0; контракт `0.1.0-draft.3` →
`0.1.0-draft.4`, аддитив + снятие красной линии, без renumbering
(breaking-check strict). Линия: AGW-28 ↔ vesma-agent v0.13.0 (провод) —
контракт кодифицирует ровно то, что агент шлёт. Проверка: markdownlint
на пуше main зелёный ДО тега (институционализированный гейт);
conformance повторно на тегированном дереве в release-воркфлоу перед
публикацией; bilingual sync, schema-lint, breaking-check, gitleaks —
в CI на пуше.
