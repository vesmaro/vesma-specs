# VESMA Ecosystem Map / Карта экосистемы VESMA

**EN.** Who is who in the ecosystem: the criticality tier, the execution
mode, the contract a component implements, and where its code lives.
Component code lives in its own repositories; this one holds only the
contracts and their statuses. A component enters this map by manifest
(admission is by contract — [ADR-0001](adrs/0001-repo-structure-and-governance.md);
component adoption — phase 4 of the [roadmap](docs/roadmap.md)).

**RU.** Кто есть кто в экосистеме: тир критичности, способ исполнения,
реализуемый контракт и дом кода. Код компонентов живёт в своих репозиториях;
здесь — только контракты и их статусы. Компонент появляется в этой карте
манифестом (приём по контракту —
[ADR-0001](adrs/0001-repo-structure-and-governance.md); усыновление
компонентов — фаза 4 [roadmap](docs/roadmap.md)).

Terminology / Терминология — [GLOSSARY.md](GLOSSARY.md).

| Компонент | Тип | Тир | Реализуемый контракт | Статус | Репа |
|---|---|---|---|---|---|
| vesma server | in-process | core | component-manifest, service-lifecycle, control-socket (реализует как супервайзер) | супервайзер движка; первая конформная реализация контрактов — main `4a2da5a`, 2026-10-05 | [vesma](https://github.com/vesmaro/vesma) |
| vesma board | in-process (python) | optional | component-manifest | манифест не заявлен (фаза 4) | [vesma](https://github.com/vesmaro/vesma) |
| vesma mesh | child-process (Go) | optional | component-manifest, service-lifecycle | манифест не заявлен (фаза 4) | [vesma-mesh](https://github.com/vesmaro/vesma-mesh) |
| vesma eyes | web-сервис (python / FastAPI-uvicorn) | optional | component-manifest, service-lifecycle | манифест не заявлен (фаза 4) | [vesma-eyes](https://github.com/vesmaro/vesma-eyes) |
| vesma agent | child-process (Go) | optional | component-manifest, service-lifecycle | манифест не заявлен (фаза 4) | [vesma-agent](https://github.com/vesmaro/vesma-agent) |
| vesma cortex-metrics | child-process (python / скрипт) | optional | component-manifest, service-lifecycle | манифест не заявлен (фаза 4) | [vesma-cortex](https://github.com/vesmaro/vesma-cortex) |

Notes (EN):

- `vesma board` and `vesma cortex-metrics` live inside the `vesma` and
  `vesma-cortex` repositories respectively; they have no repositories of
  their own.
- The `component-manifest`, `service-lifecycle`, `control-socket`, `layout`
  contracts were created in phase 1 of the [roadmap](docs/roadmap.md);
  on 2026-10-05 they were ratified `1.0.0` stable by the first conforming
  implementation — the [vesma](https://github.com/vesmaro/vesma) engine,
  main `4a2da5a` (conformance report in the engine repo).
- `decision-provider` v1 (draft) — the decision-provider family contract; a
  provider is not a supervisor component (no manifest is created for one);
  migrated from [vesma-canon](https://github.com/vesmaro/vesma-canon)
  ADR-0004 in phase 2 of the [roadmap](docs/roadmap.md).
- The "manifest not declared" status is lifted by the appearance of the
  component's manifest plus a green MUST-pass of its conformance suite (the
  integration gate).

Примечания (RU):

- `vesma board` и `vesma cortex-metrics` живут внутри реп `vesma` и
  `vesma-cortex` соответственно; отдельных репозиториев у них нет.
- Контракты `component-manifest`, `service-lifecycle`, `control-socket`,
  `layout` созданы в фазе 1 [roadmap](docs/roadmap.md); 2026-10-05
  ратифицированы как `1.0.0` stable первой конформной реализацией —
  движок [vesma](https://github.com/vesmaro/vesma), main `4a2da5a`
  (конформанс-отчёт — в репо движка).
- `decision-provider` v1 (draft) — контракт семейства провайдеров решений;
  провайдер — не компонент супервайзера (манифест не заводится);
  мигрирован из [vesma-canon](https://github.com/vesmaro/vesma-canon)
  ADR-0004 в фазе 2 [roadmap](docs/roadmap.md).
- Статус «манифест не заявлен» снимается появлением манифеста компонента и
  зелёным MUST-прогоном его conformance-сьюта (гейт интеграции).

## specs layer vs canon / Слой specs vs canon

**EN.** Boundary rule: **"HOW they connect → specs; WHAT was promised before
measurement → canon"**. This repository holds the living integration
contracts, manifests, examples and conformance; the sealed promises
(pre-regs, addenda, experiment verdicts, calibration protocols) live in the
append-only [vesma-canon](https://github.com/vesmaro/vesma-canon). Canon
history is never rewritten; moving living contracts here happens with
pointers (phase 2).

**RU.** Правило границы: **«КАК соединяются → specs; ЧТО обещано до
измерения → canon»**. Здесь живут живущие интеграционные контракты,
манифесты, примеры и конформанс; запечатанные обещания (препреги,
аддендумы, вердикты экспериментов, протоколы калибровок) — в append-only
[vesma-canon](https://github.com/vesmaro/vesma-canon). История canon не
переписывается; перенос living-контрактов сюда — с указателями (фаза 2).

## Links / Ссылки

- [ADR-0001: структура репозитория и governance / repo structure and governance](adrs/0001-repo-structure-and-governance.md) — откуда взяты правила карты / where the map's rules come from.
- [docs/roadmap.md](docs/roadmap.md) — фазы появления контрактов и усыновления компонентов / phases of contract creation and component adoption.
- [docs/concept.md](docs/concept.md) — концепция спек-слоя / the spec-layer concept.
