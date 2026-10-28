---
contract: host-intake
version: 0.1.0-draft
status: draft
decisions: [ADR-0001, ADR-0002, "директива владельца 2026-10-28 (два пункта: per-harness re-key моделей + явный контракт поверхности сбора)", "агентный драфт контракта — docs/design/host-intake-contract-draft.md (vesmaro/vesma-agent, ветка feat/host-intake-contract); гейты драфта утверждены владельцем (FC-6+FC-7 эта волна; FC-8/9 — DEFERRED v2; loopback-probe утверждён; dual-form emission утверждён)", "перенесённые гейты: fleet security-verdict (vesma-eyes, feat/models-fleet-blueprint, 832cd7a) — красные линии", "линия AGW-25/AGW-26 (discovery v6 → v7 re-key)"]
ratified: |-
  Не ратифицирована (draft). Полномочия текста: директива владельца
  2026-10-28 — два пункта (per-harness re-key моделей; явный контракт
  поверхности сбора как поверхность доверия/прозрачности); агентный
  драфт контракта (docs/design/host-intake-contract-draft.md,
  vesmaro/vesma-agent, feat/host-intake-contract) — источник каталога,
  принципов, per-harness таблицы и дисциплин; его гейт-решения
  утверждены владельцем (FC-6+FC-7 в этой волне, FC-8/9 отложены в v2,
  loopback-probe утверждён, dual-form emission утверждён); красные
  линии чтения конфигов перенесены из ратифицированного вердикта
  security-verdict (832cd7a, гейт 2 флота моделей); линия протокола —
  AGW-25 (discovery v6, влит) → AGW-26 (v7 re-key, ветка
  feat/host-intake-contract). Ратификация stable — первая конформная
  реализация каталожных ног агентом (v7) и зелёный конформанс.
---

# host-intake v0 — контракт явного каталога сбора хост-агента

> **Статус: draft (0.1.0-draft).** Контракт фиксирует ПОЛНЫЙ явный
> каталог того, что исходящий ЦУП-агент (`vesmaro-agent`) собирает на
> хосте, — поверхность доверия и прозрачности флота (пункт 2 директивы
> владельца 2026-10-28) — и нормативно определяет две новые/переключённые
> ноги: FC-6 (models per-harness — re-key, superseding v6 standalone-таблицу
> AGW-25) и FC-7 (mcp_servers). Всё, что не названо в каталоге §3.2, агент
> не собирает. Изменения формы после ратификации — только через
> SemVer-процесс (ADR-0001 §2).

Ключевые слова MUST / MUST NOT / SHOULD / MAY интерпретируются по
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Проза — русская;
идентификаторы, поля и enum-значения — EN. Нормативный источник каждого
требования — агентный драфт контракта («contract §…» =
`docs/design/host-intake-contract-draft.md`, гейты драфта утверждены
владельцем 2026-10-28), перенесённый вердикт security-verdict («gate 2»,
832cd7a) либо линия протокола AGW-25/AGW-26; в тексте они помечены.
Бюджеты, названные «(brief 2026-10-28)», — спека-фазовые бюджеты волны
поверх утверждённых гейтов (перечислены в §10).

## 1. Scope

Контракт фиксирует **явный каталог сбора** — полный перечень классов
фактов (fact classes, FC), которые агент вправе собирать на хосте, с
принципами поверхности (P1–P6), нормативными формами провода новых ног
(FC-6, FC-7) и границей «никогда не собирается». Принцип доверия:
**владелец может увидеть полный список «что агенты собирают»** — каталог
публичен, версионирован и диффабелен по релизам; каждое поле провода
отчёта отображается ровно на один FC-id (§3.6).

**В скоупе:**

- принципы поверхности сбора P1–P6 (§3.1);
- каталог классов фактов FC-1…FC-9 со статусами и капами (§3.2);
- граница «никогда не собирается» — дословно (§3.5);
- FC-6 — models per-harness: структурная атрибуция по обнаруженным
  харнесам, built-in per-harness layout-таблица, провайдерные формы
  строк, анонимный loopback-probe (фиксированная таблица +
  harness-настроенные loopback base_url), капы, перенесенные красные
  линии v6 (§3.3);
- FC-7 — mcp_servers per harness: имена + transport kind из
  документированных кэшей/конфигов, форма провода, капы (§3.4);
- поверхность прозрачности борды: рендер «что агенты собирают» ИЗ этого
  контракта, по версии агента; карта поле → FC-id (§3.6);
- честный статус реализации (§9).

**Вне скоупа (домены соседних документов):**

- FC-8 (tooling) и FC-9 (compute envelope) — **каталогизированы, статус
  DEFERRED: v2** — решение владельца зафиксировано на гейте драфта;
  реализация — отдельная волна классов v2 (§3.2);
- проводная дисциплина СУЩЕСТВУЮЩЕГО поля `models` (форма строки,
  нормализация `base_url`, snapshot/no-wipe, обязанности борды на
  ingest) — норма [agent-discovery](../../agent-discovery/v0/spec.md) v0;
  этот контракт переигрывает только ПРАВИЛА НАСЕЛЕНИЯ строк (per-harness
  re-key) и добавляет `base_url`-optional расширение для источников без
  endpoint'а (§3.3);
- `sessions[]` discovery-отчёта — **вне поверхности сбора агента**:
  поле существует на проводе, но наполняется eyes-сканером борды, а не
  агентом (проверено 2026-10-28, см. §9); контрактом каталогизировано
  как «не агентский факт» (§3.2, карта §3.6);
- хранение credential'ов, sharing-гранты, pull-прокси — вердикт gate 2
  (H1/H2); UX ростера — гейт 3; managed allowlist и shim-волна —
  отдельные, не трогаемые поверхности (contract §2);
- борд-зеркальная волна (ingest новых полей) — отдельное решение
  vesma-eyes (contract §9).

**Потребители:** агент `vesmaro-agent` (соблюдение каталога), борда
`vesma-eyes` (рендер «что агенты собирают» из контракта; ingest
аддитивных полей), владелец (аудит поверхности доверия), интеграторы
сторонних агентов, conformance-раннер слоя.

## 2. Терминология

Термины **discovery (агент → борда)**, **provider (fleet)**, **model
(fleet)**, **installation (model)**, **harness**, **quiet zero**,
**shrink-to-fit** определены в [глоссарии](../../../GLOSSARY.md) и
[agent-discovery §2](../../agent-discovery/v0/spec.md) и здесь не
переопределяются. Контрактные термины этого документа:

| Термин | Значение |
|---|---|
| fact class (FC) | Класс фактов каталога сбора: единица поверхности «что агент собирает». Каждому FC принадлежит: что собирается, источник на хосте, форма эмиссии, капы, статус (live / re-key / DEFERRED). Каталог §3.2 — закрытый перечень; добавление класса = поправка контракта с гейтом владельца (P1). |
| per-harness атрибуция | Структурное правило FC-6/FC-7: строка факта может нести только такой `harness`, который агент ДЕЙСТВИТЕЛЬНО обнаружил на этом хосте по inventory (FC-1/FC-2). Скан моделей/MCP исполняется ПОВЕРХ результатов inventory — строка для необнаруженного харнеса невозможна по построению (contract §3.1). |
| никогда не собирается | Дословная граница каталога: содержимое файлов (вне названных per-class исключений), имена проектов/workspace'ов, промпты и содержимое сессий, значения env-переменных, сетевой трафик, credential-материал в любой форме (§3.5). |
| surface прозрачности | Рендер бордой «что агенты собирают» ИЗ текста этого контракта, по версии агента: карточка на FC-id (что, зачем, капы, линия приватности); построение — по handshake версий контракт↔агент (§3.6; contract §7). |
| harness bucket | Провайдерная атрибуция строки FC-6, когда ни одна документированная форма строки модели не распарсилась: provider = slug харнеса, `note` называет причину; имя advisory для борды (§3.3.3). Угадывание провайдера запрещено (contract §3.2; гейт драфта OQ-3: never guess). |
| dual-form emission | Утверждённая гейтом OQ-3 форма эмиссии FC-6: `models[]` несёт СЫРЫЕ строки frontmatter/конфига verbatim; распарсенный provider едет в поле `provider` строки — и только когда документированная форма распарсилась (§3.3.3). |
| DEFERRED (v2) | Статус класса каталога: класс описан (что, источник, капы), реализация отложена решением владельца в волну классов v2; агент его НЕ собирает до активации (§3.2, §9). |

## 3. Контракт

### 3.1 Принципы поверхности сбора (P1–P6)

- **P1 — Explicit surface.** Каталог §3.2 — ПОЛНЫЙ перечень собираемого.
  Не названное — не собирается. **MUST**: агент собирает только классы,
  названные каталогом. Добавление класса = поправка контракта с гейтом
  владельца (contract §1 P1).
- **P2 — Names and enums, never contents.** Дисциплина v3 в генеральной
  форме: содержимое файлов никогда не покидает машину; каждое
  ограниченное content-read исключение названо per-class и эмитит
  имена, булевы или enum-факты. **MUST NOT**: «looks-like-a-model»
  сканирование — никогда (contract §1 P2; gate 2 §2 поправка 1 —
  прецедент layout-таблицы).
- **P3 — Credential material never.** Значения key/token/secret никогда
  не читаются для отчёта, не держатся в retention-структурах, не
  эмитятся ни в какой кодировке. Credentials появляются только как
  PRESENCE-маркеры (`auth: configured | anonymous | unknown`) в полях и
  файлах, названных built-in таблицей. **MUST** (contract §1 P3;
  gate 2 §2 п.3, §4.1).
- **P4 — Honest absence.** Отсутствующая, недокументированная или
  непарсируемая поверхность — пустой факт (quiet zero), не ошибка и не
  догадка. Строки «not determinable» опускаются из таблицы, не
  изобретаются. **MUST** (contract §1 P4).
- **P5 — Additive and versioned.** Классы фактов несут since-версии;
  провод остаётся аддитивным (правило неизвестного поля, 404-silence —
  без изменений). **MUST** (contract §1 P5; agent-discovery §3.1, §7).
- **P6 — Transparency surface.** Борда рендерит «что агенты собирают»
  ИЗ этого контракта, по версии агента: каждое поле провода отображается
  на FC-id (§3.6). Новой ноги нет — текст контракта едет с агентом
  (docs, pinned на build; version handshake вскрывает пару
  контракт↔агент). **MUST** (contract §1 P6, §7).

### 3.2 Каталог классов фактов

Закрытый перечень (P1). Столбец «Статус»: `live (vN)` — нога ходит по
проводу с версии N протокола агента (`docs/PROTOCOL.md` §3, AGW-реестр
vesma-agent); `re-key (v7)` — переключение населения в этой волне
(AGW-26); `DEFERRED (v2)` — каталогизирован, реализация отложена
владельцем (гейт драфта).

| id | Класс | Что агент собирает | Источник | Эмиссия | Капы | Статус |
|---|---|---|---|---|---|---|
| FC-1 | `harnesses[]` | Известные CLI-харнесы на PATH: name, version, path | exec.LookPath + discovery_extra | имена/версии/пути | 32 строки | live (v1) |
| FC-2 | `environments[]` | Дома харнесов из built-in fingerprint-таблицы: kind, markers, session_hints (имя стора + count), exec_env merge | stat/glob по discovery_roots | факты без содержимого | 8 KiB/env | live (v2+v4) |
| FC-3 | `environments[].capabilities` | Names-only инвентарь харнеса: specialists, skills, plugins, instructions + counts + булевы | dir-walks + 2 названных content-read (pi `packages[]`, zcode gcw-маркер) | имена/counts/булевы | 50/50/30/30, 8 KiB | live (v3) |
| FC-4 | `distrobox_containers` | Честные вердикты per-container; identity для exec_env merge | distrobox list/probe (read-only) | факты | нога 30 с | live (v4) |
| FC-5 | `runtime`, `k8s_nodes/pods/verdicts` | Честность runtime-поверхности; content-free списки кластера | multi-signal detect; stdlib REST | факты | нога 30 с | live (v5) |
| FC-6 | `models` per-harness | Per ОБНАРУЖЕННЫЙ харнес: сконфигурированные провайдеры (name, base_url normalized, auth enum), доступные модели (что называют конфиг/каталог + анонимная доступность локальных серверов), default model | per-harness layout-таблица §3.3.2 | имена/enums/нормализованные URL | 64 строки, 50/строку, 16 KiB, 8 KiB/файл | **re-key (v7, AGW-26)** — superseding v6 standalone-таблицу |
| FC-7 | `mcp_servers` per harness | Имена MCP/extension-серверов + transport kind | документированные кэши/конфиги (pi `mcp-cache.json`; zcode/copilot mcp-секции где документированы) | только имена/kinds — никогда argv, env, URLs | ≤30 имён/harness, 8 KiB | **утверждён (v7)** — новый |
| FC-8 | tooling | Наличие + версия ФИКСИРОВАННОГО built-in списка хост-инструментов (git, podman, docker, python3, node, go, …) | LookPath + одна строка `--version` | имена/версии | ≤40 инструментов, read-cap 4096 симв. | **DEFERRED (v2)** |
| FC-9 | compute envelope | CPU cores, RAM total, disk free на state-томе, GPU presence (только имя) | /proc + statvfs + `nvidia-smi -L` (строка имени) | hardware-факты | one-shot per pass | **DEFERRED (v2)** |

**MUST**: FC-8 и FC-9 агентом НЕ собираются до активации волны v2 —
каталогизация ≠ активация (гейт драфта; contract §2 строки PROPOSED →
решение владельца «deferred»). **MUST**: статусная колонка обновляется
только поправкой контракта (P5).

**Карта поле → FC** (полная; основа рендера §3.6):

| Поле discovery-отчёта | FC |
|---|---|
| `harnesses[]` | FC-1 |
| `environments[]` | FC-2 |
| `environments[].capabilities` | FC-3 |
| `distrobox_containers` | FC-4 |
| `runtime`, `k8s_nodes`, `k8s_pods`, `k8s_verdicts` | FC-5 |
| `models` | FC-6 |
| `mcp_servers` (с v7) | FC-7 |
| `sessions[]` | **НЕ агент** — eyes-сканер борды (см. §9) |

### 3.3 FC-6 — models per-harness (переключённое ядро)

#### 3.3.1 Атрибуция (структурная)

- **MUST**: строка installation несёт `harness` = имя, которое inventory
  (FC-1/FC-2) ДЕЙСТВИТЕЛЬНО обнаружило на этом хосте; словарь борды
  решает допуск, как всегда. Скан моделей исполняется ПОВЕРХ результатов
  inventory — строка моделей для необнаруженного харнеса невозможна по
  построению (contract §3.1).
- **MUST**: v6 standalone-таблица (codex/continue/claude-code/aider как
  detached-набор конфигов) SUPERSEDED: её строки НЕ удалены, а вошли в
  per-harness таблицу §3.3.2 как строки соответствующих харнесов;
  таблица ATTACHED к fingerprint-inventory — один built-in реестр с
  per-harness секциями (contract §0).

#### 3.3.2 Per-harness layout-таблица (built-in, типизированные декоды, дисциплина v3)

| harness | источник | поля, названные таблицей | credential-маркер (presence only) | grounded |
|---|---|---|---|---|
| zcode | `~/.zcode/agents/*.md` frontmatter (frontmatter-first read; ≤64 файлов, 8 KiB/файл — brief 2026-10-28) | `model:` (scalar или list — try-in-order), `tier:`, agent `name:` (provider из документированных форм строк: `(provider)` суффикс, `provider/model` префикс; display-name и qualified id — обе легальны) | — (tier-массивы несут provider-слаги) | 2026-10-28: GCW-инсталлер рендерит fleet `models.yaml` в эти файлы; живые id документированы (`ollama-cloud/glm-5.3-flash`, `z/glm-5.3`) (contract §3.2) |
| copilot | `~/.copilot/agents/*.agent.md` frontmatter (те же бюджеты) | те же `model:`/`tier:` поля; конвенция суффикса `" (copilot)"` | — | 2026-10-28: `model: GLM 5.3 Flash (ollama-cloud)`, `tier: 1` проверены живьём; GitHub-side каталоги моделей server-only — ЛОКАЛЬНЫЙ факт = то, что называют определения (честная note на строке) (contract §3.2) |
| codex | `~/.codex/config.toml` | top-level `model`, `model_provider`; `model_providers.<name>.{name, base_url, env_key}` | `env_key` непуст → configured | v6, перенесено (contract §3.2; AGW-25) |
| continue | `~/.continue/config.json` | `models[].{provider, model, apiBase, apiKey}` | поле `apiKey` присутствует → configured | v6, перенесено (AGW-25) |
| claude-code | `~/.claude/settings.json` | `model`; из `env` — ТОЛЬКО ИМЕНА ключей с префиксом `ANTHROPIC_` | любое имя `ANTHROPIC_*` → configured; ни одного → unknown | v6, перенесено (contract §3.2; AGW-25) |
| aider | `~/.aider.conf.yml` | `model`, `openai-api-base`, `openai-api-key` | `openai-api-key` присутствует → configured; отсутствует → unknown | v6, перенесено (AGW-25) |
| pi | `<home>/.pi/agent/` | документированного каталога моделей сегодня НЕТ → honest absence (строки моделей — none); `auth.json` EXISTENCE → pi auth-факт | `auth.json` существует → configured (значение НИКОГДА не читается); файла нет → anonymous | 2026-10-28: `auth.json` присутствует на pi core-51 (contract §3.2); эмиссия: одна строка provider `pi` с пустым `models[]` (brief 2026-10-28) |

- **MUST**: таблица built-in и версионируется в агенте; чтение ТОЛЬКО по
  названным полям на уровне JSON-pointer/секционного пути;
  parse-and-scan эвристики запрещены (gate 2 §2 поправка 1 —
  перенесено; contract §3.2).
- **MUST**: gemini и qwen строк НЕ ИМЕЮТ: ни v6-таблица (AGW-25), ни
  grounded-набор драфта их не называют (brief 2026-10-28: absent;
  упоминание «gemini / qwen» в строке draft §3.2 «continue / aider /
  gemini / qwen — as v6 rows» superseded — в v6 таких строк не было).
- **MUST**: файл сверх read-cap 8 KiB, не-regular или непарсируемый в
  пределах капа = honest absence строки, никогда не ошибка (contract
  §3.4; P4).
- **MUST**: default model — из названных таблицей указателей (tier-1 /
  primary scalar frontmatter; codex top-level `model`). Wire-форма
  re-key — per-row note (решение спека-фазы в рамках утверждённого OQ-5:
  «default model of harness `<slug>`» едет в `note` строки, чей
  `models[]` содержит строку default'а; top-level `notes` MAY
  опускаться — поле omitempty и в agent-discovery §3.2, устаревший
  глобальный `default_model` scalar-факт per-harness мир не честен).
- **MUST**: `base_url` строки MAY отсутствовать (omitempty) для
  источников, не называющих endpoint (frontmatter-строки zcode/copilot;
  pi-строка) — honest absence, угадывание URL запрещено (P4; расширение
  формы строки agent-discovery §3.2, аддитивное: поле опционально в
  новых источниках, обязательные поля остальных не тронуты).

#### 3.3.3 Провайдерные формы строк (dual-form emission, never guess)

Документированные формы строк моделей frontmatter/конфигов (contract
§3.2; гейт драфта OQ-3 утверждён):

- **MUST**: форма 1 — суффикс `(provider)`: `Имя Модели (provider-slug)`
  → provider = slug; сырая строка едет в `models[]` verbatim.
- **MUST**: форма 2 — префикс `provider/model`: qualified id
  (`ollama-cloud/glm-5.3-flash`) → provider = префикс, model id = остаток.
- **MUST**: форма 3 — literal vendor-форма `(copilot)`: суффикс
  ` (copilot)` → provider = `copilot`; GitHub-side каталог server-only —
  `base_url` НЕ синтезируется (honest absence), `note` строки фиксирует
  server-only факт.
- **MUST**: ни одна документированная форма не распарсилась →
  harness bucket: provider = slug харнеса, `note` называет причину
  («no documented provider form»); имя advisory для борды
  (agent-discovery §3.11). **MUST NOT**: угадывание провайдера,
  display-name → id конвертация, любые эвристики «похоже на провайдера».
- **MUST**: dual-form emission — `models[]` несёт СЫРЫЕ строки
  verbatim (sorted, ≤50); распарсенный provider едет в `provider`
  строки; оба факта в одной строке (гейт OQ-3: raw string + parsed pair
  только при парсируемости документированной формы).
- **MUST**: `model:` scalar ИЛИ list — try-in-order (contract §3.2).

#### 3.3.4 Probe-нога: анонимный loopback (фиксированная таблица + harness-настроенные base_url)

- **MUST**: фиксированная v6 таблица loopback-серверов без изменений:
  ollama 11434 `GET /api/tags`; LM Studio 1234, llama.cpp server 8080,
  vLLM 8000 — `GET /v1/models`; один GET на сервер, timeout 2 с, без
  credentials; разобраются ТОЛЬКО документированные формы ответа
  (`{"models":[{"name":…}]}` ollama; `{"data":[{"id":…}]}` OpenAI-формы);
  неудача/мёртвый порт — quiet zero (contract §3.3; AGW-25).
- **MUST** (утверждённый гейт OQ-2): `base_url`, сконфигурированный
  ОБНАРУЖЕННЫМ харнесом и резолвящийся LOOPBACK, MAY опрашиваться
  анонимно — один GET model-list, короткий timeout, quiet zero;
  бюджет ≤8 дополнительных целей за проход (brief 2026-10-28); цель —
  факты доступности локальных/self-hosted провайдеров, которые харнес
  реально использует (contract §3.3).
- **MUST NOT**: non-loopback endpoints никогда не опрашиваются; endpoints
  с credential-маркером (`auth: configured`) никогда не опрашиваются — у
  агента нет ключа и ключ никогда не добывается (вердикт H3 gate 2
  стоит; contract §3.3).
- **MUST**: probe-клиент zero-redirect (contract §3.4; перенесено).
- **MUST**: только loopback (`127.0.0.1`, `::1`, `localhost`) — прицел
  на внешний хост конструкцией исключён (AGW-25; gate 2 §1 H3).

#### 3.3.5 Капы и shrink-to-fit

- **MUST**: `provider` ≤ 60 символов; `models[]` sorted ≤ 50 на строку;
  `installations[]` ≤ 64 строк; объект `models` ≤ 16 KiB marshaled;
  read-cap на файл — жёсткие 8 KiB (contract §2 FC-6, §3.4; AGW-25).
- **MUST**: frontmatter-first read zcode/copilot: ≤64 файлов определений
  агентов за проход (brief 2026-10-28), каждый под 8 KiB read-cap'ом.
- **MUST**: объект ужимается ДО отправки (shrink-to-fit); усечение
  факта едет в `note` затронутой строки; отправка сверх капов
  невозможна по построению (AGW-25; contract §3.4).
- **MUST**: отсутствие конфига, мёртвый probe-порт, отсутствие
  маркерных полей — quiet zero: info-факт, не ошибка, не ретрай (P4;
  AGW-25).

#### 3.3.6 Красные линии v6 — перенесены дословно

Следующие дисциплины AGW-25/gate 2 переигрываются БЕЗ ИЗМЕНЕНИЙ
(contract §3.4 «carried verbatim»):

- **MUST**: names-only валидатор — drop, never mangle: каждая
  эмитируемая строка (provider slug, model id, base_url, note) проходит
  length-caps + credential-shape скан.
- **MUST**: нормализация `base_url` → `scheme://authority[/base-path]`;
  query/fragment обдираются всегда; userinfo обдирается;
  credential-подобный query-параметр (детект по НАЛИЧИЮ имени) →
  host-only либо omit — значение никогда не эхоится.
- **MUST**: `auth` ∈ `configured | anonymous | unknown` — ТОЛЬКО из
  НАЛИЧИЯ маркерных полей, названных таблицей; значения маркерных полей
  никогда не читаются в payload ни в какой кодировке.
- **MUST**: credential-подобная строка в неожиданном поле → ВСЯ строка
  drop ДО marshal + ГРОМКИЙ локальный лог, reason которого НИКОГДА не
  несёт значения (mask-first: маскировать до truncate).
- **MUST**: агент НЕ эмитит событий — инцидент-детектор
  `models.credential_leak_suspected` БОРД-СТОРОННИЙ (ingest);
  обязанности агента исчерпываются drop'ом и локальным логом.
- **MUST**: credential материал никогда не читается в память для целей
  отчёта и никогда не эмитится ни в какой кодировке (P3; gate 2 §2 п.3,
  §4.1).
- **MUST**: `exec_env` — только `"metal"` в этой волне; контейнерные
  поверхности конфигов едут в последующую волну (contract §3.4).

### 3.4 FC-7 — mcp_servers per harness (норматив)

- **MUST**: провод — аддитивный top-level элемент семейства (прецедент
  capabilities/FC-3), рядом с `models`:

```json
{"mcp_servers": [{"harness": "pi", "exec_env": "metal",
  "servers": ["context7", "playwright"],
  "count": 5}]}
```

- **MUST**: элемент = `{harness, exec_env, servers[], count}`;
  атрибуция структурная (§3.3.1): `harness` — только обнаруженный
  харнес; `exec_env` — только `"metal"` в этой волне.
- **MUST**: `servers[]` — sorted имена ≤30 на harness (contract §4);
  **MUST**: `count` — ПОЛНЫЙ итог найденных имён, даже когда
  `servers[]` усечён до 30 (честный счётчик; brief 2026-10-28).
- **MUST**: источники — ТОЛЬКО документированные кэши/конфиги, типовые
  декоды: pi `~/.pi/agent/mcp-cache.json` — ТОЛЬКО имена из
  документированной структуры (`servers[]` / dict-KEYS как имена);
  значения кэша НИКОГДА не декодируются; zcode/copilot mcp-секции —
  где документированы (contract §4).
- **MUST NOT**: argv, env, URLs и любые значения кэша/конфига не
  декодируются и не эмитятся — только имена и transport kind
  (contract §2 FC-7, §4).
- **MUST**: transport kind (`stdio`/`http`), когда документированный
  источник его называет, едет опциональной картой `transports`
  (`{name: kind}`, omitempty) в элементе; форма кодировки — решение
  спека-фазы в
  рамках утверждённого гейта FC-7 (contract §4 собирает имена + kind;
  literal провода brief'а называет `servers ≤30 sorted`).
- **MUST**: честное отсутствие в остальных местах: нет документированного
  кэша/секции → элемент харнеса отсутствует (zero-and-ran семьи поля);
  незадокументированные источники НЕ сканируются (P2, P4).
- **MUST**: FC-7 управляется тем же knob'ом `discovery_models: auto|off`
  (дефолт `auto`); `off` = поля `models` и `mcp_servers` отсутствуют
  целиком (brief 2026-10-28; knob-прецедент agent-discovery §3.9).
- **MUST**: кап семейства — 8 KiB на элемент (contract §4); усечение —
  `count` остаётся полным, усечение фиксируется честным счётчиком
  (строка выше).
- Обязанности борды на ingest наследуются от семейства
  [agent-discovery §3.11](../../agent-discovery/v0/spec.md): неизвестный
  `harness`/`exec_env` → drop + аудит; сверх-кап объект → честный 422.

### 3.5 Никогда не собирается (дословная граница)

**Никогда не собирается** (contract §2, дословно): содержимое файлов
(вне названных per-class исключений), имена проектов и workspace'ов,
промпты и содержимое сессий, значения environment-переменных, сетевой
трафик, credential-материал в любой форме. MANAGED allowlist и
shim-волна — отдельные, этим контрактом не трогаемые поверхности.

- **MUST NOT**: ни один класс каталога не читает и не эмитит ничего из
  перечисленного; конфликт каталога с этой границей разрешается в
  пользу границы до выяснения (P2, P3 лексикон).

### 3.6 Поверхность прозрачности (deliverable P6)

- **MUST**: текст этого контракта pinned в агент (docs + build-time
  stamp контракт-версии, вскрываемый через version handshake) — пара
  «версия агента ↔ версия контракта» наблюдаема (contract §7).
- **MUST**: борда рендерит статический вид «что агенты собирают» ИЗ
  контракта: одна карточка на FC-id — что, зачем, капы, линия
  приватности; рендер привязан к версии контракта, соответствующей
  версии агента (contract §7).
- **MUST**: каждое поле payload'а, которое агент когда-либо отправляет,
  отображается ровно на один FC-id (карта §3.2); поле без FC-id =
  дефект реализации, а не новая поверхность (P1).
- Полный список сбора — публичный, версионированный, диффабельный по
  релизам: это user-trust deliverable (contract §7).

## 4. Коды ошибок

Новых кодов контракт не вводит: каталожные ноги (FC-6, FC-7) едут по
СУЩЕСТВУЮЩЕМУ маршруту `POST /api/executors/{executor_id}/discovery`, и
реестр исходов маршрута наследуется от
[agent-discovery §4](../../agent-discovery/v0/spec.md) без изменений:
`200` (принято, `last_seen` тикнул), `401`/`403` (token/identity/revoked),
`404` (pre-1.38 борда → 404-silence), `422` (честная валидация капов
семейства), `429` (бюджет 60/60 с). События аудита — `discovery.rejected`
(неизвестный `harness`/`exec_env`) и `models.credential_leak_suspected`
(bord-сторонний incident-детектор) — те же.

| Код | Применение к полям этого контракта |
|---|---|
| `422` | `models` сверх 16 KiB marshaled; `installations[]` > 64; `models[]` > 50; `mcp_servers` элемент сверх 8 KiB; `servers[]` > 30; неизвестное enum-значение формы — честный отказ, никогда тихий trim (shrink-to-fit агента делает сверх-кап отправку дефектом агента) |
| `404` | нога FC-6/FC-7 молчит ниже info на борде без маршрута — аддитивность не создаёт нового расписания и новых ретраев (§3.1 P5) |

## 5. Примеры

Пример-минимум обязателен к мержу (ADR-0001 §1). Файлы в `examples/`
рядом со спекой; только плейсхолдеры и публичные документированные
endpoint'ы — никаких реальных токенов, путей и hostname'ов машин
владельца (ADR-0001 §6).

| Файл | Что показывает |
|---|---|
| `examples/zcode-frontmatter-installation.json` | zcode-строка, выведенная из frontmatter: `models[]` — сырые строки verbatim (display-форма и qualified id), provider распарсен документированной формой суффикса; `base_url` omitempty (frontmatter endpoint не называет); default model — per-row note |
| `examples/pi-auth-marker-row.json` | pi auth-маркерная строка: provider `pi`, пустой `models[]` (документированного каталога нет — honest absence), `auth: configured` из EXISTENCE `auth.json` (значение никогда не читается) |
| `examples/mcp-servers-field.json` | аддитивный top-level `mcp_servers`: элемент pi из `mcp-cache.json` — только имена, sorted, `count` = полный итог, опциональная карта `transports` |
| `examples/credential-redaction.json` | дисциплина до/после: нормализация `base_url`; harness-настроенный loopback `base_url` БЕЗ маркера → анонимный probe разрешён; с маркером → НИКОГДА не наблюдается; credential-строка в неожиданном поле → строка dropped до marshal |

## 6. Conformance

Сьют — `conformance/cases.skeleton.yaml`; человеческий чеклист
интегратора — `conformance/checklist.md`. Исполняется раннером
`tools/conformance` (stdlib + `jsonschema`; валидирует только
декларации — ADR-0001 §4). **Статус исполнения — честно** (прецедент
agent-discovery §6): раннер — одиночный профиль словаря
component-manifest, поэтому скелет лежит под именем
`cases.skeleton.yaml` (CI-гейт `run.py --all` остаётся зелёным);
исполнение проверок этого словаря — волна runner-profile (изменение
`tools/` — через TL-ревью). Машинная JSON-Schema появляется вместе с
борд-зеркальной волной новых полей. Зелёный MUST-прогон сьюта после
заведения runner-profile = гейт интеграции агента по этому контракту.

Словарь проверок (исполнитель — будущий профиль раннера):

| Проверка | Что делает |
|---|---|
| `models_field_shape` | top-level `models` несёт `installations[]` строк формы agent-discovery §3.2; `base_url` omitempty ТОЛЬКО у endpoint-less источников (§3.3.2) |
| `fc6_harness_attribution` | `harness` каждой строки — написание обнаруженного харнеса из словаря; строк необнаруженных харнесов нет (§3.3.1) |
| `provider_parse_forms` | `provider` — результат документированной формы (суффикс/префикс/`copilot` vendor) либо harness bucket с `note`-причиной; угаданных провайдеров нет (§3.3.3) |
| `auth_enum` | `auth` ∈ `configured` \| `anonymous` \| `unknown`, выведен только из наличия маркерных полей (§3.3.6) |
| `base_url_normalized` | присутствующий `base_url` = `scheme://authority[/base-path]`, без query/fragment/userinfo (§3.3.6) |
| `row_caps` | `provider` ≤ 60; `models[]` sorted ≤ 50; `installations[]` ≤ 64; усечение — в `note` (§3.3.5) |
| `no_credential_material` | names-only валидатор §3.3.6 как статический скан wire-shape документов; пояснительный `credential-redaction.json` — вне скана (прецедент CM `no_secret_in_vars` / agent-discovery §6) |
| `mcp_servers_field_shape` | элементы `{harness, exec_env, servers[], count}`; `count` — полный итог; `exec_env` = `"metal"` (§3.4) |
| `mcp_names_cap30` | `servers[]` sorted ≤ 30 на harness (§3.4) |
| `mcp_names_only` | в `servers[]`/`transports` нет argv/env/URL-подобных строк — имена и kinds только (§3.4) |
| `knob_values` | декларация knob'а `discovery_models` — только `auto` \| `off`; управляет FC-6 и FC-7 совместно (§3.4) |

Кейсы: позитивные — wire-примеры §5 (`examples/…`; `expect: pass`,
`severity: must`; пояснительный `credential-redaction.json` — вне
кейсов); негативные — фикстуры `conformance/fixtures/invalid/`
(`expect: fail`).

## 7. Совместимость

- **SemVer**: `0.1.0-draft`; ратификация stable — первая конформная
  реализация агентом (v7) и зелёный конформанс. Ломающее изменение =
  MAJOR + окно `max(90 дней, 2 минорных релиза)` с dual-поддержкой;
  до 1.0 окно — 14 дней (ADR-0001 §2).
- **Аддитивность**: FC-7 (`mcp_servers`) — новое аддитивное top-level
  поле: борда, игнорирующая его, конформна (правило неизвестного поля);
  старый агент (без поля) конформен. Re-key FC-6 меняет ПРАВИЛА
  НАСЕЛЕНИЯ существующего поля `models` (per-harness атрибуция,
  frontmatter-строки, `base_url` omitempty для endpoint-less
  источников) при НЕизменной форме строки: старая борда читает новые
  строки как обычные installations — аддитивно (§3.1 P5;
  agent-discovery §7).
- **REMOVING именованного поля = MAJOR** (наследуется); расширение
  per-harness таблицы (новый харнес, новое названное поле) — минорное
  изменение с уведомлением комитета; активация DEFERRED классов
  (FC-8/FC-9) — минорное изменение ЭТОГО контракта с гейтом владельца
  (P1: добавление собираемого класса — всегда гейт).
- **Потребители**: агент — соблюдает каталог и формы §3.3/§3.4; борда —
  ingest по семейству agent-discovery §3.11 + рендер прозрачности
  §3.6; FE — гейт 3 (ux-blueprint MF1/MF2) для ростера.

## 8. Threat model (мини-STRIDE)

Ассеты контракта: **отсутствие credential материала на проводе** (как в
agent-discovery §8) и **полнота/правдивость каталога** — прозрачность
не врёт о поверхности сбора. Границы: (а) конфиги/кэши харнесов ↔
reader агента; (б) агент ↔ борда (аутентифицированный POST); (в) ingest
борды ↔ зеркало/рендер прозрачности. Центральные контроли — names-only
дисциплина и closed catalog (P1); каждая митигация — ссылка на MUST §3
либо «операционный контроль».

| Категория | Угроза | Митигация | Проверка |
|---|---|---|---|
| **I**nformation Disclosure | credential материал из конфига/кэша в payload | маркерные поля — только presence → `auth` (§3.3.6); значения `mcp-cache.json` никогда не декодируются (§3.4); read-cap 8 KiB сужает поверхность чтения (§3.3.5) | `no_credential_material`, `mcp_names_only` |
| **I**nformation Disclosure | новая нога читает сверх названных таблицей полей (drift каталога) | closed catalog P1 + layout-таблица на уровне JSON-pointer; scan-эвристики запрещены (§3.1, §3.3.2); рендер прозрачности показывает ВСЁ собираемое — расхождение кода с каталогом видимо владельцу (§3.6) | `models_field_shape` + ревью таблицы (операционный контроль) |
| **I**nformation Disclosure | credential-подобная строка в свободном поле (`note`) | names-only валидатор: drop ВСЕЙ строки до marshal, громкий лог без значения (§3.3.6); bord-детектор — вторая линия (§4) | `no_credential_material` |
| **I**nformation Disclosure | credential в URL | нормализация `base_url` (§3.3.6): query/fragment/userinfo всегда обдираются; unparsable — omit | `base_url_normalized` |
| **I**nformation Disclosure | harness-настроенный probe как канал к чужому/credentialed endpoint | ТОЛЬКО loopback; `auth: configured` → никогда не наблюдается; ≤8 целей; zero-redirect; один GET, quiet zero (§3.3.4; H3) | `mcp_names_only` n/a; ревью probe-правил (операционный контроль) |
| **S**poofing | чужой executor шлёт отчёт | executor-token + identity-match маршрута (наследуется; agent-discovery §3.1) | интеграционные тесты маршрута (операционный контроль) |
| **E**levation of Privilege | discovery-факт выдаёт себе полномочия | advisory, never authority: поле не создаёт строк, не расширяет словарей (agent-discovery §3.1, §3.11) | конформанс борды (операционный контроль) |
| **D**enial of Service | раздутый отчёт (frontmatter ≤64 файлов × legs) душит борду | shrink-to-fit (§3.3.5); honest 422 семейства (§4); часовая cadence без собственного таймера | `row_caps`, `mcp_names_cap30` |
| **R**epudiation | «кто отбросил строку / кто прислал credential?» | drop'ы аудируются, инциденты называются, локальный лог громкий (§3.3.6, §4) | операционный контроль (audit trail борды) |
| **T**ampering | рендер прозрачности врёт о поверхности (catalog drift между версией контракта у борды и у агента) | version handshake агент↔контракт (§3.6); карта поле → FC полная (§3.2); поле без FC-id = дефект | операционный контроль (handshake-тесты) |

Осознанные остаточные риски: харнес читает СВОИ конфиги — threat model
харнеса, не флота (gate 2 §6); компрометация борд-хоста — вне провода
агента; имена MCP-серверов на борде — advisory-метаданные той же
чувствительности, что имена провайдеров.

## 9. Миграция и статус реализации

Легаси-leg: v6 (AGW-25) ходит по проводу — его standalone-таблица
superseded, но поле совместимо (§7). Статус ног — честно:

| Нога | Статус | Где живёт |
|---|---|---|
| Агентная v6 (standalone `models`) | **ходила** (AGW-25, влита 2026-10-28) — SUPERSEDED правилами населения этого контракта; ноль строк на реальном флоте (проверено живьём 2026-10-28 на core-51: четыре v6 конфиг-файла отсутствуют; реальные харнесы fleet — zcode/copilot — несут каталоги в frontmatter определений) | vesmaro/vesma-agent, main (merge b98960e); `docs/PROTOCOL.md` §3 |
| Агентная v7 (per-harness re-key + FC-7) | **в полёте** — ветка `feat/host-intake-contract`, AGW-26; драфт контракта — `docs/design/host-intake-contract-draft.md` (этой спеки источник) | vesmaro/vesma-agent |
| Борд-зеркало новых полей (ingest `models` per-harness, `mcp_servers`; рендер прозрачности §3.6) | **не влита** — отдельная волна vesma-eyes (pending; contract §9) | vesma-eyes |
| FC-8 / FC-9 | **DEFERRED (v2)** — решение владельца на гейте драфта; активация = минор этого контракта с гейтом | — |

`sessions[]` — вне поверхности сбора агента (проверено 2026-10-28):
поле существует в `ExecutorDiscoveryBody` борды (аддитивная нога
ME-062: task-linked session-факты, стор task-session-fact, drop'ы
аудитируются как `sessions.rejected`), но наполняется eyes-сканером
борды (kora-scan ingest `POST /api/executors/{id}/kora-scan`; кластерные
сессии — синтетический executor id `hermes`), а не агентом: в Go-коде
агента (`internal/discovery`, `internal/board`) session-факты не
конструируются — слово «sessions» встречается только как имя
directory-стора в fingerprint-маркерах FC-2 (store name + count, v3
дисциплина). Для агента поле отсутствует; честное отсутствие (P4).

Порядок ввода: (1) спека (этот документ) — да; (2) агентная волна v7
(AGW-26): re-key + FC-7, фикстуры на GROUNDED формах, гейты + cascade,
release v0.11.0, fleet update — стоящая волновая дисциплина (contract
§10); (3) борд-зеркальная волна — ingest + рендер прозрачности;
(4) ратификация stable — конформанс обеих сторон зелёный. Промежуточные
состояния конформны по аддитивности (§7).

## 10. Ссылки

- Директива владельца 2026-10-28 — два пункта (per-harness re-key;
  явный контракт поверхности сбора): полномочия этого контракта;
  продублирована в шапке и в [CHANGELOG](CHANGELOG.md).
- Агентный драфт контракта —
  `docs/design/host-intake-contract-draft.md` (vesmaro/vesma-agent,
  ветка `feat/host-intake-contract`): источник каталога, принципов
  P1–P6, per-harness таблицы, красных линий; гейты драфта (OQ-1…OQ-5)
  утверждены владельцем.
- Gate 2 — `docs/design/models-fleet/security-verdict.md`
  (vesmaro/vesma-eyes, ветка `feat/models-fleet-blueprint`, 832cd7a):
  перенесённые красные линии (names-only, нормализация URL, auth из
  presence, анонимный probe H3, борд-сторонний детектор).
- [specs/agent-discovery/v0/spec.md](../../agent-discovery/v0/spec.md)
  (0.1.0-draft.2) — проводная дисциплина поля `models` (форма строки,
  snapshot/no-wipe, обязанности борды на ingest, коды маршрута §4);
  этот контракт её не переигрывает, а населяет.
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) —
  структура и governance слоя; форма контракта.
- [ADR-0002](../../../adrs/0002-agent-discovery-contract.md) —
  кодификация agent-discovery (предшественник).
- [ADR-0003](../../../adrs/0003-host-intake-catalog.md) — решение об
  явном каталоге сбора (authority trail этой спеки).
- Brief TL спека-фазы 2026-10-28 — спека-фазовые бюджеты волны поверх
  утверждённых гейтов: ≤64 файлов frontmatter-read, ≤8
  harness-настроенных probe-целей, knob `discovery_models` для FC-7,
  `count` = полный итог, pi-строка provider `pi` с пустым `models[]`,
  per-row note как OQ-5 wire-форма.
- [Глоссарий](../../../GLOSSARY.md), [карта
  экосистемы](../../../ECOSYSTEM.md), [roadmap](../../../docs/roadmap.md).
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — интерпретация
  ключевых слов.
