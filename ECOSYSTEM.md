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
| vesma agent | child-process (Go) | optional | component-manifest, service-lifecycle, agent-discovery (агент-нога), host-intake (каталог сбора) | манифест не заявлен (фаза 4); agent-discovery v0 (draft.2): v6 влита (AGW-25, superseded re-key'ем), борд-зеркало не влито; host-intake v0 (draft): агент v7 (AGW-26) — ветка feat/host-intake-contract, не влита | [vesma-agent](https://github.com/vesmaro/vesma-agent) |
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
- 2026-10-21: `layout` v2 (`2.0.0-draft.1`, dual-profile — a self-contained
  user profile `~/.vesma` + an FHS system profile) opened as a draft;
  ratified form: ADR-0045 in the engine repo. The v1 spec stays immutable
  as the legacy-generation norm.
- 2026-10-28: `agent-discovery` v0 (`0.1.0-draft`) opened as a draft —
  the wire contract for the additive `models` field of the outbound
  agent's discovery report (codifies protocol amendment AGW-25;
  authority trail: the three ratified models-fleet gates in
  vesma-eyes — discovery-contract-draft `daf969b`, security-verdict
  `832cd7a`, ux-blueprint `cb166a8` — plus the owner directive of
  2026-10-28; the decision record is ADR-0002). The agent leg is merged
  (vesma-agent main (merge b98960e)); the board mirror (ingest into
  `GET /api/models`) is not — intermediate states are conformant by the
  additive rule. Credential storage, grants and the proxy stay outside
  the contract (gate 2's domain). Amended to `0.1.0-draft.2` the same
  day: the field's POPULATION rules re-keyed per host-intake (the v6
  standalone table superseded; the probe extended with harness-
  configured loopback base_urls; the `mcp_servers` field added).
- 2026-10-28: `host-intake` v0 (`0.1.0-draft`) opened as a draft — the
  explicit collection catalog: the COMPLETE list of fact classes the
  agent gathers on a host (the trust/transparency surface, clause 2 of
  the owner directive 2026-10-28). Normative here: the per-harness
  models re-key (FC-6, superseding the v6 standalone table — zero rows
  on the real fleet, verified live 2026-10-28) and the new
  `mcp_servers` field (FC-7); FC-8/FC-9 catalogued DEFERRED (v2);
  `sessions[]` recorded OUTSIDE the agent's surface (it is fed by the
  eyes-side scanner). Authority: the agent-side contract draft
  (`docs/design/host-intake-contract-draft.md`, vesma-agent
  `feat/host-intake-contract`, owner-approved gates: FC-6+FC-7 this
  wave, the loopback probe approved, dual-form emission approved), the
  carried security-verdict red lines (832cd7a), the AGW-25/AGW-26
  lineage. Decision record: ADR-0003. The agent v7 wave (AGW-26) is in
  flight on `feat/host-intake-contract`; the board mirror + the
  transparency rendering are the pending vesma-eyes wave.

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
- 2026-10-21: `layout` v2 (`2.0.0-draft.1`, dual-profile — самодостаточный
  user-профиль `~/.vesma` + FHS system-профиль) открыт как draft;
  ратифицированная форма — ADR-0045 в репо движка. Спека v1 остаётся
  неизменной как норма legacy-генерации.
- 2026-10-28: `agent-discovery` v0 (`0.1.0-draft`) открыт как draft —
  проводной контракт аддитивного поля `models` в discovery-отчёте
  исходящего агента (кодификация протокольной поправки AGW-25;
  полномочия текста: три ратифицированных гейта флота моделей в
  vesma-eyes — discovery-contract-draft `daf969b`, security-verdict
  `832cd7a`, ux-blueprint `cb166a8` — плюс директива владельца
  2026-10-28; запись решения — ADR-0002). Агентная нога влита
  (vesma-agent main (merge b98960e)); борд-зеркало (ingest в
  `GET /api/models`) не влито — промежуточные состояния конформны по
  правилу аддитивности. Хранение credential'ов, гранты и прокси — вне
  контракта (дом гейта 2). В тот же день поправлен до
  `0.1.0-draft.2`: правила НАСЕЛЕНИЯ поля re-key'нуты per host-intake
  (v6 standalone-таблица superseded; probe расширен
  harness-настроенными loopback base_url; добавлено поле
  `mcp_servers`).
- 2026-10-28: `host-intake` v0 (`0.1.0-draft`) открыт как draft —
  явный каталог сбора: ПОЛНЫЙ перечень классов фактов, которые агент
  собирает на хосте (поверхность доверия/прозрачности, пункт 2
  директивы владельца 2026-10-28). Нормативно здесь: per-harness
  re-key моделей (FC-6, superseding v6 standalone-таблицу — ноль строк
  на реальном флоте, проверено живьём 2026-10-28) и новое поле
  `mcp_servers` (FC-7); FC-8/FC-9 каталогизированы DEFERRED (v2);
  `sessions[]` записано ВНЕ поверхности агента (поле наполняет
  eyes-сканер). Полномочия: агентный драфт контракта
  (`docs/design/host-intake-contract-draft.md`, vesma-agent
  `feat/host-intake-contract`, гейты утверждены владельцем: FC-6+FC-7 —
  эта волна, loopback-probe утверждён, dual-form emission утверждён),
  перенесённые красные линии security-verdict (832cd7a), линия
  AGW-25/AGW-26. Запись решения — ADR-0003. Агентная волна v7 (AGW-26)
  в полёте на `feat/host-intake-contract`; борд-зеркало + рендер
  прозрачности — ожидающая волна vesma-eyes.

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
