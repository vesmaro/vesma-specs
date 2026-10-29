# vesma-specs v0.6.0 — host-intake 0.1.0-draft.5: container reads via direct host paths

The sixth repository release of **vesma-specs**: the discovery v10
amendment to the host-intake contract (AGW-29), published in lockstep
with the wire that vesma-agent v0.14.0 ships the same day. The §3.4c
fence transport of draft.4 — generated scripts, base64, fenced blocks
through `distrobox enter` — is REPLACED by direct host-path reads:
a distrobox container home is a plain host-visible directory, so the
agent reads config facts in it like any other bounded host file. The
release also carries the catalog read-cap sync that draft.4 missed
(64 KiB, the vesma-agent v0.12.1 fix).

## What is in the release (v0.5.0..main)

### host-intake amended: 0.1.0-draft.4 → 0.1.0-draft.5

- Authority: the owner's directive of 2026-10-29 — «Не надо заходить в
  контейнер, чтобы найти файлы его — все есть на хосте (как
  подключаемый том)!» (AGW-29); mirrored by the agent-side PROTOCOL
  addendum implemented in vesma-agent v0.14.0.
- Mechanism replaced (§3.4c rewritten in place; §3.5/§3.6 numbering
  untouched — the §3.4a/§3.4b precedent): container homes are
  discovered per discovery root by the glob
  `<root>/.distrobox/*/home` (pure stat, no CLI); only
  fingerprint-discovered homes are structurally gated in — the same
  markers and rules as metal (FC-2). FC-6/FC-7 then read inside those
  homes as ordinary bounded host files. No `distrobox enter` is
  executed for reads — a side effect is impossible by construction.
- Container state does not gate reads: a home is a host path, readable
  whether the box is running or stopped (the draft.4 "never from
  stopped containers" red line is obsolete with the transport it
  bounded).
- The fence transport is deprecated and removed from the contract AND
  from the agent: bounded head-only bytes, base64, one fenced block
  per file, the ≤ 64 files per home budget, and the ≤ 25 s
  per-container config-probe budget are all gone with the probes they
  served.
- The v4 enter leg (FC-4) keeps a narrower job: binary/version probes
  only, budgets unchanged (30 s leg / 20 s probe) with the honest
  verdict machine.
- Knobs, stated precisely: the container-home walk and the models/mcp
  reads inside it ride `discovery_models: auto|off`;
  `discovery_distrobox` (the v4 knob) gates ONLY the v4 CLI leg and is
  NOT required for §3.4c host-path reads. No new knobs (§2, §3.4c).
- Classes, fields, caps and the wire shape are unchanged — additive
  for boards (§7).

### Catalog read cap: the 64 KiB sync (Flag-1 of the draft.5 review)

- §3.3.2 catalog block (RU + EN): owner-declared
  `discovery_models_catalogs` entries are read under a DEDICATED 64 KiB
  cap — synced with the agent implementation `catalogReadLimit` that
  shipped in vesma-agent v0.12.1 (the real GCW `models.yaml` is 8949
  bytes and died on the 8 KiB cap). A file over 64 KiB is the entry's
  honest absence (P4; skip + info log); walked harness config files
  keep the 8 KiB cap UNCHANGED. The §10 v8 budget line and checklist
  item HI-19 carried the stale 8 KiB figure — synced.

### Conformance and parity

- Conformance suites green on the merged release tree: 27/27
  (re-run by the releaser, matching the TL's runner verdict on the
  branch).
- Bilingual parity kept (spec.md RU canon + spec.en.md mirror); the
  contract CHANGELOG carries the 0.1.0-draft.5 entry.

### Pending-merge drafts (not in this release)

- context-lifecycle v0 (`spec/context-lifecycle-0`, dac97f2) and
  integration-contract v0 (`spec/integration-contract-v0`, d930c9c)
  stay out-of-release drafts.

## Contract statuses at release time

host-intake `0.1.0-draft.5` — draft: FC-1…FC-9 as of v0.4.0; container
config surfaces via DIRECT host-path reads normative since discovery
v10 (this release). agent-discovery `0.1.0-draft.2` unchanged.
component-manifest `1.0.0-draft.2` unchanged.

## Versioning note

Repository release v0.6.0; the host-intake contract version moves
`0.1.0-draft.4` → `0.1.0-draft.5` (header, §7, §9, suite skeleton).
A mechanism swap inside §3.4c with no class/field/wire changes —
additive only, no renumbering, no breaking changes (breaking-check
strict).

## Artifacts

- `vesma-specs-v0.6.0-contracts.tar.gz` — the contract tree at the
  tagged commit.
- `conformance-report.json` — the runner's JSON report from the
  tagged tree.
- `SHA256SUMS` — checksums over both artifacts.

## Verification

- The markdownlint gate on the main push is GREEN before the tag is
  cut (the institutionalized gate — a tagged tree that never went
  through a fresh main push cannot ship lint defects).
- Conformance re-runs on the tagged tree in the release workflow
  before anything is published (27/27 expected).
- Bilingual sync, schema lint, and the breaking-change detector stay
  in CI on the push; gitleaks likewise.

## Links

- [README](https://github.com/vesmaro/vesma-specs/blob/main/README.md)
- [ECOSYSTEM](https://github.com/vesmaro/vesma-specs/blob/main/ECOSYSTEM.md)
- [host-intake spec](https://github.com/vesmaro/vesma-specs/blob/main/specs/host-intake/v0/spec.md),
  [EN mirror](https://github.com/vesmaro/vesma-specs/blob/main/specs/host-intake/v0/spec.en.md)
- [Roadmap](https://github.com/vesmaro/vesma-specs/blob/main/docs/roadmap.md)

---

**RU.** Шестой релиз репозитория vesma-specs (2026-10-29): поправка
host-intake 0.1.0-draft.5 — discovery v10 (AGW-29, директива владельца
«Не надо заходить в контейнер, чтобы найти файлы его — все есть на
хосте (как подключаемый том)!»), синхронно с проводом vesma-agent
v0.14.0 того же дня. Механизм §3.4c ЗАМЕНЁН: дома distrobox-контейнеров
— обычные хост-видимые пути; обнаружение — glob
`<root>/.distrobox/*/home` (чистый stat, без CLI) на каждом discovery
root, структурный гейтинг как на metal (fingerprint-дома только, те же
маркеры FC-2); FC-6/FC-7 читаются в них как обычные bounded host-файлы.
Enter для чтений не исполняется — side effect невозможен по
построению; состояние контейнера чтения не гейтит (running/stopped
одинаково). Fence-транспорт draft.4 (head-only байты, base64,
fenced-блоки, ≤ 64 файлов на дом, бюджет проб ≤ 25 с) депрекирован и
удалён из контракта и агента; v4-нога (FC-4) остаётся — только
binary/version пробы (30 с нога / 20 с проба, машина честных вердиктов
без изменений). Ручки: walk и чтения models/mcp едут под
`discovery_models`; `discovery_distrobox` гейтит только v4 CLI-ногу и
для §3.4c не требуется; новых ручек нет. Классы, поля, капы и проводная
форма не менялись — для борды аддитивно. Плюс sync прочтён ревью
draft.5 (Flag-1): каталоговые записи `discovery_models_catalogs`
(§3.3.2) читаются под ОТДЕЛЬНЫМ капом 64 KiB (`catalogReadLimit`,
sync vesma-agent v0.12.1; реальный GCW `models.yaml` — 8949 байт — не
влезал в 8 KiB); сверх 64 KiB — honest absence записи (P4); walked-конфиги
харнесов сохраняют 8 KiB; строка бюджета §10 и HI-19 синхронизированы.
Conformance на релизном дереве 27/27 (перепроверено релизером,
совпадает с вердиктом ТЛ на ветке); двуязычный паритет одним коммитом;
CHANGELOG контракта несёт запись 0.1.0-draft.5. Статусы: host-intake
`0.1.0-draft.5`; agent-discovery `0.1.0-draft.2` и component-manifest
`1.0.0-draft.2` без изменений; context-lifecycle v0 и
integration-contract v0 — вне релиза. Версия репозитория v0.6.0;
контракт `0.1.0-draft.4` → `0.1.0-draft.5`, замена механизма внутри
§3.4c без изменений классов/полей/провода — аддитив, без renumbering
(breaking-check strict). Линия: AGW-29 ↔ vesma-agent v0.14.0 (провод) —
контракт кодифицирует ровно то, что агент шлёт. Проверка: markdownlint
на пуше main зелёный ДО тега (институционализированный гейт);
conformance повторно на тегированном дереве в release-воркфлоу перед
публикацией; bilingual sync, schema-lint, breaking-check, gitleaks —
в CI на пуше.
