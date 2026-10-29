# vesma-specs v0.7.0 — agent-discovery 0.1.0-draft.3: the normative detector grammar

The seventh repository release of **vesma-specs**: the credential-shape
detector grammar, codified where it belongs — in the contract both
implementations read. §3.8 of agent-discovery v0 now carries the
normative class list shared by the agent's name validator and the
board-side detector (parity mandatory), published in lockstep with the
code half: vesma-agent v0.15.0 ships exactly these classes in its
models-leg validator the same day (2026-10-29).

## What is in the release (v0.6.0..main)

### agent-discovery amended: 0.1.0-draft.2 → 0.1.0-draft.3

- §3.8 extended with the normative credential-shape class list, two new
  classes:
  - **the JWT shape** — an `eyJ`-prefixed base64url header segment
    followed by at least one dot; a bare `eyJ`-prefixed id without a
    dot stays legal;
  - **the long mixed run** — a contiguous run of ≥ 32 characters of
    the base64url charset `[A-Za-z0-9_-]` (catches keyless vendor
    keys: 39-char Google-style form keys, 32-char opaque secrets).
- Token-prefix matching is fixed as **case-insensitive** (the
  lowercase `akia` form is covered, not only the uppercase).
- The false-positive direction is stated explicitly and normatively: a
  legitimate hash-like model id MAY false-positive into a loud row
  drop — the designed safe direction (a value is never mangled and
  never emitted past the gate).
- §6 `no_credential_material`: the hex threshold corrected to ≥ 20 per
  both implementations (`[0-9a-fA-F]{20,}`); the prose said
  "hex ≥ 40" while the code said 20 — the contract now matches the
  shipped behavior.
- Bilingual single-commit sync: `spec.en.md` mirrors all of the above;
  the contract CHANGELOG carries the 0.1.0-draft.3 entry.

### host-intake amended: 0.1.0-draft.5 → 0.1.0-draft.6 (pointer-only)

- Its own version line, mechanism unchanged: §3.5/§3.3.6 do NOT restate
  the grammar class list — §3.3.6 now carries the pointer to
  agent-discovery §3.8, making it the single source of truth for the
  credential shapes (no dual-maintenance drift). Bilingual sync; the
  contract CHANGELOG carries the 0.1.0-draft.6 entry.

### Conformance and parity

- Conformance suites green on the merged release tree: **27/27**
  (re-run by the releaser, matching the TL's runner verdict on the
  branch); schema-lint and the bilingual check stay green in CI on the
  main push.
- Parity line: spec §3.8 (this release) ↔ validator classes in
  vesma-agent v0.15.0 (the code half of vesmaro/vesma-specs#10, closed
  across the two repositories the same day).

### Pending-merge drafts (not in this release)

- context-lifecycle v0 (`spec/context-lifecycle-0`, dac97f2) and
  integration-contract v0 (`spec/integration-contract-v0`, d930c9c)
  stay out-of-release drafts.

## Contract statuses at release time

agent-discovery `0.1.0-draft.3` — draft: the normative detector grammar
is this release's addition. host-intake `0.1.0-draft.6` — draft:
pointer-only amendment, mechanism unchanged from the draft.5 released in
v0.6.0. component-manifest `1.0.0-draft.2` unchanged.

## Versioning note

Repository release v0.7.0; agent-discovery moves
`0.1.0-draft.2` → `0.1.0-draft.3` (additive grammar classes, a
case-sensitivity fix in the prefix rule, and a prose-vs-code threshold
sync — both implementations already ran ≥ 20, so no wire change);
host-intake moves `0.1.0-draft.5` → `0.1.0-draft.6` (pointer-only). No
breaking changes (breaking-check strict).

## Artifacts

- `vesma-specs-v0.7.0-contracts.tar.gz` — the contract tree at the
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
- [agent-discovery spec](https://github.com/vesmaro/vesma-specs/blob/main/specs/agent-discovery/v0/spec.md),
  [EN mirror](https://github.com/vesmaro/vesma-specs/blob/main/specs/agent-discovery/v0/spec.en.md)
- [host-intake spec](https://github.com/vesmaro/vesma-specs/blob/main/specs/host-intake/v0/spec.md),
  [EN mirror](https://github.com/vesmaro/vesma-specs/blob/main/specs/host-intake/v0/spec.en.md)
- [Roadmap](https://github.com/vesmaro/vesma-specs/blob/main/docs/roadmap.md)

---

**RU.** Седьмой релиз репозитория vesma-specs (2026-10-29): грамматика
детектора учётных данных, кодифицированная в контракте agent-discovery
v0 — §3.8 отныне несёт нормативный список классов, общий для валидатора
имён агента и борд-детектора (паритет обязателен). Публикация синхронна
кодовой половине: vesma-agent v0.15.0 везёт ровно эти классы в
models-ноге тем же днём. agent-discovery `0.1.0-draft.2` →
`0.1.0-draft.3`: новые классы — форма JWT (сегмент `eyJ` + минимум одна
точка; голый `eyJ`-id без точки легален) и длинная смешанная
последовательность
(≥ 32 символов `[A-Za-z0-9_-]` — ловит бесключевые вендорные ключи:
39-символьные Google-form, 32-символьные opaque); префикс-матчинг
зафиксирован регистронезависимым (строчная `akia` покрыта); направление
ложных срабатываний проговорено нормативно: легитимный хэш-подобный
MODEL id МОЖЕТ выпасть в громкое отбрасывание строки — безопасное
направление (значение никогда не искажается и не проходит шлюз); в §6
`no_credential_material` порог hex исправлен на ≥ 20 по обеим
имплементациям (проза говорила «hex ≥ 40», код — 20; контракт теперь
совпадает с поставленным поведением). Двуязычная синхронизация одним
коммитом, CHANGELOG контракта несёт запись draft.3. host-intake
`0.1.0-draft.5` → `0.1.0-draft.6` (только указатель): §3.5/§3.3.6 НЕ
дублируют список классов — §3.3.6 несёт указатель на agent-discovery
§3.8, единственный источник истины. Conformance на релизном дереве
27/27 (перепроверено релизером, совпадает с вердиктом ТЛ на ветке).
Вне релиза: context-lifecycle v0 (dac97f2) и integration-contract v0
(d930c9c). Статусы: agent-discovery `0.1.0-draft.3`, host-intake
`0.1.0-draft.6`, component-manifest `1.0.0-draft.2` без изменений.
Версия репозитория v0.7.0; без ломающих изменений (breaking-check
strict). Линия: §3.8 ↔ vesma-agent v0.15.0 — контракт и код закрыли
spec- и code-половины vesmaro/vesma-specs#10 в один день. Проверка:
markdownlint на пуше main зелёный ДО тега; conformance повторно на
тегированном дереве в release-воркфлоу перед публикацией (ожидание
27/27); bilingual sync, schema-lint, breaking-check, gitleaks — в CI
на пуше.
