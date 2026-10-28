# vesma-specs v0.4.0 — host-intake 0.1.0-draft.3: FC-8/9 normative, catalog knob

The fourth repository release of **vesma-specs**: the discovery v8
amendment to the host-intake contract (AGW-27), published in lockstep
with the wire that vesma-agent v0.12.0 ships the same day. FC-8
(tooling) and FC-9 (compute envelope) — catalogued as DEFERRED (v2)
since the founding draft — become normative, and the owner-declared
model-catalog knob lands as the FC-6 extension. Plus, already on main
from the v0.3.0 follow-up: the markdownlint gate on the tagged tree
(closes #8).

## What is in the release (v0.3.0..main)

### host-intake amended: 0.1.0-draft → 0.1.0-draft.3

- Authority: the owner's «делай» directive of 2026-10-29 (AGW-27) —
  FC-8/FC-9 un-deferred to normative status, the host-facts knob, and
  the catalog knob; mirrored by the agent-side PROTOCOL.md addendum
  "discovery v8 (AGW-27, 2026-10-29)".
- FC-8 tooling (new §3.4a): the pinned 28-binary table; LookPath plus
  ONE version-class call each (2 s budget, quiet zero); the version =
  the banner's first line through the names-only validator (a shaped
  line drops the ENTRY — loud suppressed log); sorted, ≤ 40 rows with
  the honest full `count`; whole-object 8 KiB shrink-to-fit (entries
  drop, `count` stays).
- FC-9 compute envelope (new §3.4b): `cpu_cores`, `mem_total_bytes`,
  `disk_free_bytes` (statfs on the agent's state dir), `gpus` (ONE
  anonymous `nvidia-smi -L`, names only, ≤ 8). Numbers and names only —
  the never-collected boundary now names hardware serials, utilization
  telemetry, and catalog PATHS explicitly. Every field independently
  omitted on honest absence; 422 honest-absence caps specified for
  tooling / compute / gpus.
- One knob over both legs: `discovery_host_facts: auto|off` (default
  `auto`, unknown values refused at startup; `off` = both payload
  fields absent entirely). §3.5/§3.6 numbering untouched — no
  cross-reference churn.
- Catalog knob `discovery_models_catalogs` (§3.3.2, FC-6 extension):
  owner-declared `{path, harness}` entries (the agent never discovers
  catalog paths by itself); the GCW tier-catalog shape (`tiers` →
  primary+fallback strings, `version` decoded and ignored), dedupe,
  documented provider string forms with suffix-wins parsing; rows
  marked as owner-declared (`auth: unknown`, note "model catalog
  (owner-declared)") through the SAME builder as every models row —
  same validator, same caps; an invalid entry is a skip + info log,
  never a startup error.
- Conformance: new vocabulary (`catalog_rows_shape`,
  `host_facts_knob_values`) plus positive skeleton cases; three new
  wire examples (`tooling-field.json`, `compute-envelope.json`,
  `catalog-row-owner-declared.json` — placeholders/public values only).
- Integrator checklist: HI-17…HI-20 (tooling / compute / catalog /
  knobs); HI-01 synced with the FC-8/FC-9 activation. Bilingual parity
  kept (spec.md RU canon + spec.en.md mirror, single commit).

### Already on main (v0.3.0..this release): release.yml lint gate (#8)

- The markdownlint gate now runs on the TAGGED tree, ordered before
  conformance (closes #8 — the v0.2.0 MD028 lesson institutionalized;
  v0.3.0 caught its MD038 the hard way on the main push). A tagged
  tree that never went through a fresh main push can no longer ship
  lint defects.

### Pending-merge drafts (not in this release)

- context-lifecycle v0 (`spec/context-lifecycle-0`, dac97f2) and
  integration-contract v0 (`spec/integration-contract-v0`, d930c9c)
  stay out-of-release drafts.

## Contract statuses at release time

host-intake `0.1.0-draft.3` — draft: FC-1…FC-7 live/approved; FC-8 /
FC-9 normative since discovery v8 (this release). agent-discovery
`0.1.0-draft.2` unchanged. component-manifest `1.0.0-draft.2`
unchanged.

## Versioning note

Repository release v0.4.0; the host-intake contract version moves
`0.1.0-draft` → `0.1.0-draft.3` (header, §7, §9). Additive only — no
renumbering, no breaking changes (breaking-check strict, 0 findings).

## Artifacts

- `vesma-specs-v0.4.0-contracts.tar.gz` — the contract tree at the
  tagged commit.
- `conformance-report.json` — the runner's JSON report from the
  tagged tree.
- `SHA256SUMS` — checksums over both artifacts.

## Verification

- Conformance on the merged main (worktree run, 2026-10-29): 27
  passed / 0 failed / 0 warned; the tagged-tree conformance re-runs
  in the release workflow before anything is published.
- markdownlint runs in CI on the main push (the authoritative check —
  the one local gap on this box) AND on the tagged tree before
  conformance; the tag is cut only after the main-push CI is verified
  green.
- Bilingual sync, schema lint, and the breaking-change detector stay
  in CI on the push; gitleaks likewise.

## Links

- [README](https://github.com/vesmaro/vesma-specs/blob/main/README.md)
- [ECOSYSTEM](https://github.com/vesmaro/vesma-specs/blob/main/ECOSYSTEM.md)
- [host-intake spec](https://github.com/vesmaro/vesma-specs/blob/main/specs/host-intake/v0/spec.md),
  [EN mirror](https://github.com/vesmaro/vesma-specs/blob/main/specs/host-intake/v0/spec.en.md)
- [ADR-0003](https://github.com/vesmaro/vesma-specs/blob/main/adrs/0003-host-intake-catalog.md)
- [Roadmap](https://github.com/vesmaro/vesma-specs/blob/main/docs/roadmap.md)

---

**RU.** Четвёртый релиз репозитория vesma-specs (2026-10-29): поправка
host-intake 0.1.0-draft.3 — discovery v8 (AGW-27, директива владельца
«делай» от 2026-10-29), синхронно с проводом vesma-agent v0.12.0 того
же дня. FC-8 (tooling, §3.4a) и FC-9 (compute envelope, §3.4b) —
норматив: закреплённая таблица 28 бинарей (LookPath + один
version-class вызов, бюджет 2 с, ≤ 40 строк с честным `count`), ядра/
память/диск/GPU (имена без серийников), общая ручка
`discovery_host_facts: auto|off` (неизвестные значения отвергаются на
старте; `off` — поля отсутствуют целиком); граница «никогда не
собирается» дополнена явно: аппаратные серийники, утилизация, PATH
каталогов. Каталожная ручка `discovery_models_catalogs` (§3.3.2,
расширение FC-6): владельчески объявленные `{path, harness}`-записи,
форма GCW-каталога (tiers → primary+fallback), суффикс-приоритет
провайдерных форм, строки через тот же билдер с той же валидацией и
капами (`auth: unknown`, note «model catalog (owner-declared)»);
невалидная запись — skip + info-лог, никогда не ошибка старта.
Conformance: новая лексика (`catalog_rows_shape`,
`host_facts_knob_values`) + скелет-кейсы, три новых проводных примера;
чеклист HI-17…HI-20, HI-01 синхронизирован; двуязычная паритетность —
одним коммитом. Уже на main: гейт markdownlint по тегированному дереву
в release.yml перед conformance (закрывает #8 — урок v0.2.0 MD028
институционализирован). Статусы: host-intake `0.1.0-draft.3`
(FC-1…FC-7 живые/утверждены; FC-8/9 норматив с discovery v8);
agent-discovery `0.1.0-draft.2` и component-manifest `1.0.0-draft.2`
без изменений; context-lifecycle v0 и integration-contract v0 — вне
релиза. Версия репозитория v0.4.0; контракт 0.1.0-draft →
0.1.0-draft.3, только аддитив (breaking-check strict — 0 находок).
Линия: AGW-27 ↔ vesma-agent v0.12.0 (провод) — контракт кодифицирует
ровно то, что агент шлёт. Проверка: conformance на слитой main —
27 passed / 0 failed / 0 warned (локальный прогон в worktree,
2026-10-29); markdownlint — авторитетно в CI на пуше main (таг режется
только после зелёного CI) и повторно на тегированном дереве перед
conformance; bilingual sync, schema-lint, breaking-check, gitleaks —
в CI на пуше.
