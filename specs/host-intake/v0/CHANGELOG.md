# Changelog — host-intake

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в [spec.md](spec.md) §7 и README репозитория.

## 0.1.0-draft.5 — 2026-10-29

### Changed

- Поправка discovery v10 (AGW-29, 2026-10-29; архитектурная директива
  владельца 2026-10-29 «Не надо заходить в контейнер, чтобы найти
  файлы его — все есть на хосте (как подключаемый том)!»): МЕХАНИЗМ
  контейнерных чтений §3.4c ЗАМЕНЁН — вместо fence-транспорта draft.4
  (`head -c 8192` + base64 + fenced-блоки + генерируемые скрипты через
  `distrobox enter`, вышел в релизе vesma v0.5.0) — ПРЯМЫЕ host-path
  чтения: дома distrobox-контейнеров — хост-видимые пути
  (`<root>/.distrobox/<box>/home/...`), FC-6/FC-7 читаются в них как
  обычные bounded host-файлы. Классы, поля, капы и проводная форма не
  менялись — для борды аддитивно (§7).
- §3.4c переписан (нумерация не тронута): обнаружение контейнерных
  домов — glob `<root>/.distrobox/*/home` (чистый stat, без CLI) на
  каждом discovery root; структурный гейтинг КАК У METAL —
  fingerprint-обнаруженные дома только (те же маркеры/правила FC-2);
  fence-транспорт draft.4 ДЕПРЕКИРОВАН и УДАЛЯЕТСЯ из агента; v4
  enter-нога (FC-4) остаётся — только binary/version пробы (её
  бюджет «30 с нога / 20 с проба» и машина честных вердиктов —
  без изменений); per-container таймбюджет проб конфигов (до 25 с)
  упразднён вместе с пробами — чтения едут в общем проходе discovery,
  ограничены капами файлов.
- Knob-уточнение (документировано точно): сам walk контейнерных домов
  и чтения models/mcp в них едут под `discovery_models: auto|off`;
  `discovery_distrobox` (v4-knob) гейтит ТОЛЬКО v4 CLI-ногу (FC-4) и
  для host-path чтений §3.4c НЕ требуется; новых knob'ов нет (§2,
  §3.4c).
- Контейнерное состояние не гейтит чтения: дом — host-путь, читается
  независимо от running/stopped; enter не исполняется, side effect
  невозможен по построению (§3.4c).
- Граница §3.5: контейнерно-транспортная строка draft.4 (bounded
  head-only байты, base64, fenced-блоки, «никогда из остановленных»)
  переформулирована под host-path механизм — контейнерный дом = обычные
  host-файлы: только названные файлы таблицы §3.3.2 под
  read-cap 8 KiB, ≤64 файлов на дом; никакого транспорта, никакого
  `distrobox enter`.
- §5: описание [examples/container-installation-row.json](examples/container-installation-row.json)
  синхронизировано (контейнерная строка БЕЗ артефактов транспорта —
  сами wire-примеры транспортных артефактов не несли и не менялись);
  §8: строки threat-модели контейнерной пробы переписаны под walk
  контейнерных домов (дрейф реестра путей/целые файлы/вне таблицы;
  раздутый обход) + остаточный риск подделанного
  `.distrobox/<box>/home`.
- §9: агентная v9/v10 — честно: draft.4 вышел в релизе vesma v0.5.0 с
  fence-транспортом; директива владельца 2026-10-29 (AGW-29) заменила
  механизм; fence-транспорт депрекирован и удаляется из агента;
  агентная нормативная форма — PROTOCOL addendum, amending
  «Container-surface addendum — discovery v9» (lands параллельно).
- Каталожный read-cap синхронизирован с агентной реализацией v0.12.1:
  записи `discovery_models_catalogs` (§3.3.2) читаются под ОТДЕЛЬНЫМ
  капом 64 KiB (`catalogReadLimit = 64 KiB`; grounding: реальный GCW
  `models.yaml` — 8949 байт — не влезал в кап 8 KiB); файл сверх
  64 KiB = honest absence записи; owner-declared явный путь — более
  высокий bounded кап честен для него; walked-конфиг-файлы харнесов
  сохраняют 8 KiB без изменений. Пропущенный sync: строка v8-бюджета
  (§10) и чеклист HI-19 оставались на 8 KiB.
- Версия контракта `0.1.0-draft.4` → `0.1.0-draft.5` (шапка, §7,
  скелет сьюта).

### Added

- Metal-wins dedupe (§3.4c): абсолютный путь дома, уже покрытый metal
  discovery root, НЕ пересканируется как контейнерный дом —
  собственный box-home агента есть metal-правда; правило тест-пиннено
  (тесты агента).
- Тихая деградация переформулирована: поддерево `.distrobox`
  отсутствует → ноль контейнерных домов, quiet zero — ОБЫЧНЫЙ кейс
  хостов без боксов; нечитаемый/не-регулярный дом = honest absence
  этого дома (P4).
- §10: ссылка на поправку discovery v10 (AGW-29) — TC-pinned deltas
  на директиву владельца; ссылка на v9 (AGW-28) помечена «механизм
  заменён v10» с перечнем переживших механизм решений (per-surface
  идентичность, суммарные капы, entry-level detector, pi
  existence-only, тихая деградация).
- Чеклист интегратора: секция волны v9 → v10 — HI-21…HI-24
  переписаны под host-path механизм.

### Decisions

- Замена (а не третий слой поверх fence-транспорта): директива
  владельца устраняет сам вход в контейнер ради файлов — дома и так
  на хосте; двойная механика (fence + host-path) была бы мёртвым
  кодом и вторым реестром путей, запрещённым инвариантом «тот же
  метод, что на metal» (§3.4c, AGW-29).
- Полномочия дельты: TC-pinned contract deltas 2026-10-29 (TL) на
  архитектурную директиву владельца 2026-10-29 (AGW-29); зеркалируется
  addendum'ом в `docs/PROTOCOL.md` vesma-agent, amending addendum v9.
- Per-surface идентичность строк, суммарные капы, entry-level
  detector, pi existence-only, тихая деградация — ПЕРЕЖИЛИ замену
  механизма без изменений (unchanged-перечень TL-дельт).

## 0.1.0-draft.4 — 2026-10-29

### Changed

- Поправка discovery v9 (AGW-28, 2026-10-29; директива владельца
  «делай» 2026-10-29): красная линия FC-6/FC-7 «metal only» (§3.3.6)
  СНЯТА для чтения конфигов через distrobox container probes —
  running-контейнеры присоединяются к поверхностям сбора. Новая
  нормативная секция §3.4c (нумерация §3.5/§3.6 не тронута — прецедент
  §3.4a/§3.4b против renumbering-шума). Механизм пробы =
  ратифицированная v4 distrobox-дисциплина (FC-4), расширенная bounded
  транспортом. Агентная нормативная форма — addendum «Container-surface
  addendum — discovery v9 (AGW-28, 2026-10-29)» в `docs/PROTOCOL.md`
  vesma-agent, lands параллельно (ветка `feat/container-surface`).
- Per-surface идентичность config-fact строк (§3.3.1, словарь §2):
  кортеж `(provider, base_url, model, harness, exec_env)`; ОДИН И ТОТ
  ЖЕ provider+model на metal и в контейнере = ДВЕ строки; v4-дедуп
  «один namespace — одна правда» остаётся домом окружений (FC-2), не
  config-строк. Капы FC-6 стали СУММАРНЫМИ по поверхностям: 64 строки /
  16 KiB вместе, `models[]` ≤50 остался per-строка (§3.3.5).
- Граница §3.5 дополнена контейнерно-транспортной строкой: из
  контейнеров — ТОЛЬКО bounded head-only байты НАЗВАННЫХ файлов
  (`head -c 8192`, base64, fenced-блоки, ≤64 файлов на контейнерный
  дом), никогда целые файлы, ничего вне таблицы, никогда из
  остановленных контейнеров.
- §9: агентная v9 (container-surface) — в полёте на момент поправки
  (честно): `feat/container-surface` (AGW-28); pod-поверхности
  (`pod:<name>`) остаются последующей волной — «metal only» снят
  ТОЛЬКО для distrobox probes.
- Версия контракта `0.1.0-draft.3` → `0.1.0-draft.4` (шапка, §7,
  скелет сьюта).

### Added

- Нормативный §3.4c: running-контейнеры ТОЛЬКО (остановленный = честный
  `not-running`, никогда не бутится); скрипт пробы ГЕНЕРИРУЕТСЯ из ТОЙ
  ЖЕ built-in таблицы §3.3.2 (второго реестра нет — дрейф невозможен по
  построению); per-file транспорт `head -c 8192` + base64 + ОДИН
  fenced-блок на файл; ≤64 файлов на контейнерный дом; per-container
  таймбюджет в v4-семействе «30 с нога / 20 с проба» — config-carrying
  до 25 с пробы (документировано этой поправкой); декод — ТЕ ЖЕ сканеры,
  что на metal, names-only валидатор и капы без изменений; pi-маркер в
  контейнере — `test -f` existence-only, байты `auth.json` никогда не
  читаются; тихая деградация: distrobox CLI отсутствует → вся
  контейнерная нога quiet-zero (документированный laptop-кейс), сбоющий
  контейнер = v4-машина честных вердиктов; knobs без изменений —
  `discovery_models` + `discovery_distrobox` (оба `auto`), новых
  knob'ов нет.
- FC-7 из контейнеров (§3.4): контейнерный `mcp-cache.json` → элемент
  `exec_env="distrobox:<name>"`, detector ENTRY-LEVEL (элемент на пару
  harness × exec_env), капы без изменений.
- §5: [examples/container-installation-row.json](examples/container-installation-row.json)
  (контейнерная строка FC-6, per-surface идентичность) и
  [examples/mcp-servers-container-entry.json](examples/mcp-servers-container-entry.json)
  (metal-pi и container-pi = два элемента).
- §6: проверки `container_rows_shape` и `container_mcp_shape` +
  позитивные кейсы скелета; §8: строки threat-модели контейнерной пробы
  (drift/целые файлы/вне таблицы; раздутый вывод проб).
- Чеклист интегратора: секция волны discovery v9 — HI-21…HI-24;
  HI-10 синхронизирован со снятием «metal only» (§3.3.6).

### Decisions

- Красная линия снята ИМЕННО для distrobox probes: «metal only» был
  волновым ограничением поверх замороженного словаря `exec_env`
  (`metal | distrobox:<name> | pod:<name>`, agent-discovery §2) —
  значения контейнеров легальны словарём с v4, поэтому снятие
  расширяет НАСЕЛЕНИЕ, не форму строки (§7, аддитивно).
- Полномочия дельты: TC-pinned contract deltas 2026-10-29 (TL), гейт
  владельца — «делай» 2026-10-29 (container-surface волна AGW-28);
  зеркалируется addendum'ом «Container-surface addendum — discovery v9
  (AGW-28, 2026-10-29)» в `docs/PROTOCOL.md` vesma-agent.
- Негативные фикстуры контейнерных полей — вместе с runner-profile
  волной (прецедент draft/draft.3; позитивные кейсы примеров заведены
  сразу).

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
