# vesma-specs

The contract-and-specification layer of the **VESMA** ecosystem: component
interfaces, integration manifests, examples and conformance suites — in one
place, before and independently of the code.

**English** | [Русский](#русский)

## English

[Русский](#русский)

**Layer rule:** this repository holds **HOW** the components connect —
interfaces, manifests, examples, conformance checks. What was **promised
before measurement** (pre-regs, addenda, verdicts, calibration protocols)
lives in [vesma-canon](https://github.com/vesmaro/vesma-canon) — the private
evidentiary layer of the experimental track. Canon history is never
rewritten; living versions of integration contracts move here with pointers.

| Document | Contents |
|---|---|
| [docs/concept.md](docs/concept.md) | the layer concept: why it exists, boundaries, audiences, governance |
| [docs/brief-2026-10-04-archcom-founding.md](docs/brief-2026-10-04-archcom-founding.md) | founding session brief: the week's context, agenda item one = the ArchCom, inviolable decisions, inputs |
| [docs/roadmap.md](docs/roadmap.md) | phase 0–4 roadmap with checklists |
| [adrs/0001-repo-structure-and-governance.md](adrs/0001-repo-structure-and-governance.md) | ADR-0001: the founding ArchCom verdict — repository structure and governance |
| [GLOSSARY.md](GLOSSARY.md) | layer glossary: EN term — RU definition |
| [ECOSYSTEM.md](ECOSYSTEM.md) | ecosystem map: components, tiers, contracts being implemented, statuses |

### Repository structure

```
specs/<name>/vN/    spec-per-contract: spec.md, README.md (EN quickstart),
                    schema/, examples/, conformance/, CHANGELOG.md
adrs/               architectural decisions (ADR-NNNN) — ArchCom verdicts
templates/          templates: contract spec, component manifest, conformance suite
tools/conformance/  conformance runner (stdlib + jsonschema)
tools/ci/           CI checks: schema lint, breaking-change detector
GLOSSARY.md         terminology glossary
ECOSYSTEM.md        ecosystem map
```

Immutability rules for version directories and the full composition —
[ADR-0001](adrs/0001-repo-structure-and-governance.md).

### Governance

- Merged by the ArchCom Chair (TL). An ArchCom quorum ≥ 2 (including the
  zone owner) — for new contracts, MAJOR/breaking changes and deprecations;
  additive minor fields — TL + committee notification; prose, examples,
  tools — TL after review. `CODEOWNERS`: `specs/`, `adrs/`, `tools/`.
- An ArchCom verdict = ADR + PR, inseparable.
- Conformance gate: CI runs the runner on every PR touching `specs/**`; a
  green MUST-pass of a suite is the gate for integrating a component into
  the ecosystem.

Details (including the secrets and i18n discipline) —
[ADR-0001](adrs/0001-repo-structure-and-governance.md).

### Contract discipline

1. The contract is the source of truth; the implementation follows the
   contract.
2. SemVer: `v1.0.0` = the first stable contract; a breaking change = MAJOR.
3. Breaking-change detector in CI (the buf pattern, federation ArchCom
   2026-07-20).
4. Deprecation windows: breaking changes carry a transition period and
   dual support (precedent: the artifact manifest schema 2 transition,
   vesma-cortex ADR 0003).
5. Every specification ships with a minimum example and a conformance
   checklist.

### License

Apache-2.0 (the VESMA ecosystem family default, owner decision 2026-09-29).

---

## Русский

[English](#english)

Контрактно-спекификационный слой экосистемы **VESMA**: интерфейсы компонентов,
интеграционные манифесты, примеры и конформанс-сьюты — в одном месте, до и
независимо от кода.

**Правило слоя:** здесь живёт **КАК** компоненты соединяются — интерфейсы,
манифесты, примеры, проверки соответствия. Что мы **обещали до измерения**
(препреги, аддендумы, вердикты, протоколы калибровок) — живёт в
[vesma-canon](https://github.com/vesmaro/vesma-canon) (приватный
доказательный слой экспериментального трека). История canon не переписывается;
живущие версии интеграционных контрактов переезжают сюда с указателями.

| Документ | Что содержит |
|---|---|
| [docs/concept.md](docs/concept.md) | концепция слоя: зачем, границы, адресаты, governance |
| [docs/brief-2026-10-04-archcom-founding.md](docs/brief-2026-10-04-archcom-founding.md) | бриф учредительной сессии: контекст недели, первый пункт = АрхКом, нерушимые решения, входы |
| [docs/roadmap.md](docs/roadmap.md) | дорожная карта фаз 0–4 с чеклистами |
| [adrs/0001-repo-structure-and-governance.md](adrs/0001-repo-structure-and-governance.md) | ADR-0001: вердикт учредительного АрхКома — структура репозитория и governance |
| [GLOSSARY.md](GLOSSARY.md) | глоссарий слоя: термин EN — определение RU |
| [ECOSYSTEM.md](ECOSYSTEM.md) | карта экосистемы: компоненты, тиры, реализуемые контракты, статусы |

### Структура репозитория

```
specs/<name>/vN/    спека-на-контракт: spec.md, README.md (EN quickstart),
                    schema/, examples/, conformance/, CHANGELOG.md
adrs/               архитектурные решения (ADR-NNNN) — вердикты АрхКома
templates/          шаблоны: спека контракта, манифест компонента, conformance-сьют
tools/conformance/  conformance-раннер (stdlib + jsonschema)
tools/ci/           CI-проверки: линт схем, breaking-детектор
GLOSSARY.md         глоссарий терминов
ECOSYSTEM.md        карта экосистемы
```

Правила неизменности версий-директорий и полного состава —
[ADR-0001](adrs/0001-repo-structure-and-governance.md).

### Governance

- Мержит Chair АрхКома (TL). Кворум АрхКома ≥ 2 (включая владельца зоны) —
  для новых контрактов, MAJOR/breaking-изменений и deprecation; аддитивные
  минорные поля — TL + уведомление комитета; проза/примеры/tools — TL после
  ревью. `CODEOWNERS`: `specs/`, `adrs/`, `tools/`.
- Вердикт АрхКома = ADR + PR, неразделимы.
- Conformance-гейт: CI гоняет раннер на PR к `specs/**`; зелёный MUST-прогон
  сьюта — гейт интеграции компонента в экосистему.

Подробно (включая дисциплину секретов и i18n) —
[ADR-0001](adrs/0001-repo-structure-and-governance.md).

### Дисциплина контрактов

1. Контракт = source of truth; реализация следует за контрактом.
2. SemVer: `v1.0.0` = первый стабильный контракт; ломающее изменение = MAJOR.
3. Breaking-change-детектор в CI (паттерн buf из АрхКом федерации 2026-07-20).
4. Deprecation-окна: ломающие изменения несут переходный период и dual-поддержку
   (прецедент: манифест артефакта schema 2, vesma-cortex ADR 0003).
5. Каждая спецификация едет с примером-минимумом и конформанс-чеклистом.

### Лицензия

Apache-2.0 (семейный дефолт экосистемы VESMA, решение владельца 2026-09-29).
