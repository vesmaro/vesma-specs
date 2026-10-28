# Changelog — host-intake

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в [spec.md](spec.md) §7 и README репозитория.

## 0.1.0-draft.3 — 2026-10-29

### Changed

- Поправка discovery v8 (AGW-27, 2026-10-29; директива владельца
  «делай» 2026-10-29): FC-8 (tooling) и FC-9 (compute envelope)
  un-deferred — статус в каталоге §3.2 `DEFERRED (v2)` → **норматив**;
  новые нормативные секции §3.4a/§3.4b (нумерация §3.5/§3.6 не тронута
  — решение спека-фазы против renumbering-шума в перекрёстных
  ссылках). Агентная нормативная форма — addendum «discovery v8
  (AGW-27, 2026-10-29)» в `docs/PROTOCOL.md` vesma-agent, lands
  параллельно.
- Граница §3.5 «никогда не собирается» дополнена строками
  hardware-классов: аппаратные serials, utilization-телеметрия и PATH'и
  owner-declared каталогов (сверх фактов строк каталога) — никогда.
- §9: FC-8/FC-9 — норматив с discovery v8; контейнерные поверхности
  конфигов (`exec_env` сверх `metal`) остаются отложенной волной.
- Версия контракта `0.1.0-draft` → `0.1.0-draft.3` (шапка, §7,
  скелет сьюта).

### Added

- Нормативный FC-8 (§3.4a): knob `discovery_host_facts: auto|off`
  (дефолт `auto`; неизвестное значение — отказ старта), управляющий
  FC-8+FC-9 совместно; `off` → поля `tooling`/`compute` отсутствуют
  целиком. Дисциплина сбора (сам built-in список ~25–30 инструментов —
  агентная ратификация): LookPath + ОДИН вызов версии ≤2 с, quiet zero
  per инструмент, первая строка версии ≤200 рун через names-only
  валидатор, drop-on-shape; провод
  `{"tooling": {"tools": [{"name", "version"?}], "count"}}` — sorted
  ≤40 + честный `count`, 8 KiB shrink-to-fit.
- Нормативный FC-9 (§3.4b): провод
  `{"compute": {"cpu_cores"?, "mem_total_bytes"?, "disk_free_bytes"?,
  "gpus"?}}` — числа только, каждое поле omitempty НЕЗАВИСИМО (P4);
  GPU = ОДИН вызов `nvidia-smi -L`, только строки имён ≤8,
  валидатор-gated — никогда serials/utilization; линия приватности —
  hardware-envelope класс, без hostname'ов и serials.
- Каталожный knob `discovery_models_catalogs` (§3.3.2, расширение FC-6):
  YAML-список записей `{path, harness}` — ЯВНО объявленные владельцем
  файлы модельных каталогов (P1: агент пути не ищет сам; прецедент GCW
  `models.yaml` — tiers primary/fallback формы `Name (vendor)`); read-cap
  8 KiB, типизированный декод, ВСЕ строки моделей (primary+fallback);
  provider — документированные формы (суффикс-приоритет), иначе harness
  bucket; строки `source=config`, `auth=unknown`, note «model catalog
  (owner-declared)»; `harness` = написание записи владельца (допуск
  решает словарь борды); невалидная запись = skip + info-лог; едут под
  knob'ом `discovery_models`, PATH'и каталогов на провод не едут.
- §6: проверки `tooling_field_shape`, `tooling_version_discipline`,
  `compute_field_shape`, `compute_gpu_names_only`,
  `catalog_rows_shape`, `host_facts_knob_values` + позитивные кейсы
  скелета; §8: строка threat-модели для строк FC-8/FC-9.
- [examples/](examples/): `tooling-field.json`, `compute-envelope.json`,
  `catalog-row-owner-declared.json` (только плейсхолдеры/публичные
  формы, ADR-0001 §6).
- Чеклист интегратора: HI-17…HI-20 (tooling/compute/catalog/knobs);
  HI-01 синхронизирован с активацией FC-8/FC-9.

### Decisions

- Нумерация новых секций — §3.4a/§3.4b вместо сдвига §3.5/§3.6: §3.5 и
  §3.6 перекрёстно ссылочны (чеклист, оба языка, §1/§2) — решение
  спека-фазы против renumbering-шума (AGW-27, спека-фаза 2026-10-29).
- Полномочия дельты: TC-pinned contract deltas 2026-10-29 (TL), owners
  гейт — «делай» 2026-10-29 (un-defer FC-8/9 + каталожный knob);
  зеркалируется addendum'ом «discovery v8 (AGW-27, 2026-10-29)» в
  `docs/PROTOCOL.md` vesma-agent.
- Негативные фикстуры для новых полей — вместе с runner-profile волной
  (прецедент скелета; позитивные кейсы примеров заведены сразу).

## 0.1.0-draft — 2026-10-28

### Changed

- Reconciliation с wire AGW-26 (QA DOC-2, 2026-10-28): frontmatter-строки
  (zcode/copilot) note НЕ несут — server-only честность `(copilot)`
  живёт в описании layout-таблицы/каталоге; причина harness-bucket —
  факт локального лога, никогда провод (P4: note, которую код не может
  заполнить, не обещается). Pi-строка опускает поле `models` (omitempty;
  пустой список — ноль-и-отработал, ключ не эмитится). Примеры и
  чеклист синхронизированы (zcode-пример без note; pi-пример без ключа
  `models`).
- Reconciliation с landed-реализацией AGW-26 (2026-10-28): default
  model — ТОЛЬКО из указателей, названных таблицей (codex top-level
  `model` → per-row note); frontmatter-строки (zcode/copilot) default
  НЕ эмитят — `model:`/`tier:` декодируются, но не интерпретируются
  (модели per-agent; единственный «per-harness default» был бы
  догадкой). §3.4: форма pi `mcp-cache.json` зафиксирована как
  СЛОВАРЬ — имена = dict-KEYS, значения не декодируются (списковая
  формулировка `{version, servers[]}` драфта контракта была ошибочной;
  правится на стороне репо агента).

### Added

- [spec.md](spec.md) — нормативная спека явного каталога сбора
  хост-агента (пункт 2 директивы владельца 2026-10-28 — «поверхность
  сбора агента = явный контракт»): принципы поверхности P1–P6;
  закрытый каталог классов фактов FC-1…FC-9 со статусами, капами и
  полной картой «поле провода → FC-id»; дословная граница «никогда не
  собирается»; нормативный FC-6 — models per-harness (структурная
  атрибуция по обнаруженным харнесам, built-in per-harness
  layout-таблица: zcode/copilot frontmatter `model:`/`tier:`, codex,
  continue, claude-code, aider, pi auth-маркер; документированные
  провайдерные формы строк с dual-form emission и never-guess;
  анонимный loopback-probe — фиксированная таблица + ≤8
  harness-настроенных base_url; капы 64/50/16 KiB/8 KiB; красные линии
  v6 перенесены дословно); нормативный FC-7 — mcp_servers
  (`{harness, exec_env, servers[] ≤30 sorted, count = полный итог}`,
  pi `mcp-cache.json` — только имена, knob `discovery_models`);
  FC-8/FC-9 каталогизированы как DEFERRED (v2) — решение владельца;
  поверхность прозрачности борды (рендер «что агенты собирают» из
  контракта, version handshake); коды ошибок — наследование маршрута
  §4 agent-discovery; конформанс-словарь; мини-STRIDE; честный статус
  реализации (v6 superseded → v7 в полёте; борд-зеркало pending;
  `sessions[]` вне поверхности агента — проверено 2026-10-28).
- [spec.en.md](spec.en.md) — информативное EN-зеркало (single-commit
  sync; норматив — русская версия).
- [README.md](README.md) — EN quickstart интегратора.
- [examples/](examples/) — пример-минимум (гейт мержа, ADR-0001 §1):
  zcode frontmatter-строка (dual-form), pi auth-маркерная строка,
  поле `mcp_servers`, credential-redaction до/после (включая правило
  probe: credentialed endpoint не наблюдается никогда).
- [conformance/](conformance/) — декларативный скелет сьюта
  (`cases.skeleton.yaml` — имя сознательное, прецедент agent-discovery:
  раннер — одиночный профиль словаря CM, CI `run.py --all` остаётся
  зелёным; словарь проверок §6, фикстуры `fixtures/invalid/`) +
  чеклист интегратора.

### Decisions

- Полномочия текста (authority trail): директива владельца 2026-10-28 —
  два пункта (per-harness re-key; явный контракт поверхности сбора);
  агентный драфт контракта (`docs/design/host-intake-contract-draft.md`,
  vesma-agent `feat/host-intake-contract`) — источник каталога,
  принципов и дисциплин; его гейты утверждены владельцем: FC-6+FC-7 —
  эта волна, FC-8/FC-9 — DEFERRED v2, loopback-probe утверждён,
  dual-form emission утверждён. Красные линии перенесены из
  security-verdict (832cd7a, gate 2). Линия протокола: AGW-25 (v6) →
  AGW-26 (v7). Запись решения —
  [ADR-0003](../../../adrs/0003-host-intake-catalog.md).
- Скоуп — каталог + FC-6 re-key + FC-7: проводная дисциплина формы
  строки `models` остаётся домом agent-discovery v0 (этот контракт её
  населяет, не переигрывает); хранение credential'ов, гранты, прокси —
  дом gate 2; UX ростера — дом gate 3; борд-зеркало — отдельная волна
  vesma-eyes.
- Спека-фазовые решения поверх утверждённых гейтов (per OQ-5 и literal
  провода брифа): default model — per-row note (wire остаётся
  аддитивным; top-level `notes` omitempty); `base_url` omitempty для
  endpoint-less источников; карта `transports` — omitempty; бюджет ≤64
  frontmatter-файлов и ≤8 probe-целей.
- OQ-4 закрыт проверкой: `sessions[]` discovery-отчёта наполняется
  eyes-сканером борды (ME-062; kora-scan; синтетический executor id
  `hermes`), агент session-фактов не конструирует — поле записано вне
  поверхности сбора агента (§1, §9).
- Машинная JSON-Schema и исполняемый сьют — вместе с борд-зеркальной
  волной (прецедент agent-discovery / decision-provider).

### Status

Draft, не ратифицирована. Агентная волна v7 (AGW-26) — ветка
`feat/host-intake-contract`; борд-зеркало (ingest per-harness `models` +
`mcp_servers`, рендер прозрачности) НЕ влито. Ратификация stable —
конформанс обеих сторон зелёный.
