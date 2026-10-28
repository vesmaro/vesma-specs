---
contract: agent-discovery
version: 0.1.0-draft.2
status: draft
decisions: [ADR-0001, ADR-0002, "AGW-25 — addendum «discovery v6, models fleet leg» в docs/PROTOCOL.md §3 (vesmaro/vesma-agent, main b98960e)", "gate 1 — discovery-contract-draft.md (vesmaro/vesma-eyes, feat/models-fleet-blueprint, daf969b)", "gate 2 — security-verdict.md (там же, 832cd7a)", "gate 3 — ux-blueprint.md (там же, cb166a8)", "директива владельца 2026-10-28 («контракты и документацию актуализировать» в vesma-specs)", "draft.2 — re-key per host-intake: [specs/host-intake/v0](../../host-intake/v0/spec.md) (0.1.0-draft, ADR-0003; агентный драфт docs/design/host-intake-contract-draft.md, vesma-agent feat/host-intake-contract, гейты утверждены владельцем)"]
ratified: |-
  Не ратифицирована (draft). Полномочия текста: агентная нога контракта
  уже влита как протокольная поправка AGW-25 в vesmaro/vesma-agent
  (main b98960e, аддендум «discovery v6» в §3
  docs/PROTOCOL.md); красные линии ратифицированы гейтом 2
  (security-verdict, 832cd7a, поправки 1–2 к OQ-4); форма провода
  ратифицирована гейтом 1 (discovery-contract-draft, daf969b); потребитель
  зеркала ратифицирован гейтом 3 (ux-blueprint, cb166a8 — MF1/MF2).
  Ратификация контракта как stable — первая конформная реализация обеих
  ног: агентной (влита) и борд-зеркала (ingest в `GET /api/models`,
  зона `discovered` — не влита; целевая схема `ModelsDiscoveredItem`
  бордой уже отдаётся, зона честно пуста).
---

# agent-discovery v0 — контракт discovery моделей (агент → борда)

> **Статус: draft (0.1.0-draft.2).** Контракт кодифицирует уже влитую
> агентную ногу — протокольную поправку AGW-25 «Models-fleet addendum —
> discovery v6» в `docs/PROTOCOL.md` §3 исходящего ЦУП-агента
> `vesmaro-agent` — как экосистемный контракт спек-слоя (директива
> владельца 2026-10-28). Борд-зеркало (ingest в `GET /api/models`)
> контрактом предусмотрено, но ещё не влито — см. §9. Изменения формы
> после ратификации — только через SemVer-процесс (ADR-0001 §2).
>
> **Поправка draft.2 (re-key per host-intake, 2026-10-28).** Правила
> НАСЕЛЕНИЯ поля `models` переключены на per-harness re-key: нормативный
> источник населения — [host-intake](../../host-intake/v0/spec.md) §3
> (per-harness layout-таблица: zcode/copilot frontmatter добавлены; pi —
> auth-маркерная строка; standalone-таблица §3.3 ниже superseded);
> новый аддитивный top-level элемент `mcp_servers` (FC-7) — дом
> host-intake §3.4; probe-нога расширена harness-настроенными loopback
> base_url (host-intake §3.3.4). Форма строки §3.2 и обязанности борды
> §3.11 не изменились.

Ключевые слова MUST / MUST NOT / SHOULD / MAY интерпретируются по
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Проза — русская;
идентификаторы, поля и enum-значения — EN. Нормативный источник каждого
требования — поправка AGW-25 либо гейты 1–2 флота моделей; в тексте они
помечены «(AGW-25)», «(gate 1 §…)», «(gate 2 §…)».

## 1. Scope

Контракт фиксирует **проводную дисциплину поля `models`** — аддитивного
top-level поля discovery-отчёта `POST /api/executors/{executor_id}/discovery`
исходящего ЦУП-агента: какие факты о провайдерах и моделях хоста агент
вправе читать, как нормализует, чем обязан жертвовать при утечке, что
борда делает с отчётом на ingest. Принцип: **только имена** —
provider/model имена и endpoint URL — факты; credential материал фактом
не является никогда.

**В скоупе:**

- форма аддитивного top-level поля `models` (`installations[]`, `notes`)
  и строки `installation` (§3.2);
- names-only чтение конфигов харнесов через built-in per-harness
  layout-таблицу (§3.3);
- нормализация `base_url` с обдиранием query/fragment/userinfo и
  credential-параметров (§3.4);
- `auth` — enum-факт из наличия поля, не из значения (§3.5);
- капы и shrink-to-fit: 64 строк, 50 моделей, 16 KiB объект, 8 KiB
  read-cap на файл (§3.6);
- анонимная probe-нога: loopback-only, фиксированная таблица портов
  (§3.7);
- leak-дисциплина: names-only валидатор, drop строки до marshal,
  громкий локальный лог с подавленным значением (§3.8);
- knob `discovery_models: auto|off` (§3.9);
- snapshot-семантика зеркала и различие «поле отсутствует» /
  «поле пустое» (§3.10);
- обязанности борды на ingest: drop+audit неизвестных словарных
  значений, честные 422 по капам, incident-детектор (§3.11);
- коды ошибок маршрута для этого поля (§4).

**Вне скоупа (домены соседних документов):**

- хранение provider credential'ов, sharing-гранты, pull-прокси — вердикт
  гейта 2 (`security-verdict.md` H1/H2, vesma-eyes); контракт сознательно
  остаётся корректным, если владелец скажет прокси «никогда» (gate 1 §4.5,
  gate 2 §4.10);
- UX ростера (`GET /api/models`, зоны `discovered`/`providers`/`board`,
  бейджи provenance) — гейт 3 (`ux-blueprint.md`, MF1/MF2);
- остальные поля discovery-отчёта (`harnesses`, `environments`,
  `k8s_*`) и ноги discovery v3/v4/v5 — норма `docs/PROTOCOL.md` §3
  vesma-agent, здесь не переигрываются;
- транспорт маршрута в целом: executor-token класс, identity-match,
  бюджет 60/60 с, 404-silence — унаследованы и зафиксированы в §3.1
  как есть (введены волной vesma-eyes 1.38.0, ME-015).

**Потребители:** агент `vesmaro-agent` (писатель поля), борда
`vesma-eyes` (читатель-ingest, зеркало и ростер), интеграторы
сторонних агентов, conformance-раннер слоя.

## 2. Терминология

Термины **provider**, **model**, **installation**, **discovery**
(нога агент → борда) определены в
[глоссарии](../../../GLOSSARY.md) и здесь не переопределяются:
provider флота моделей — внешний model-serving endpoint, который
подключает владелец; это не «decision provider» семейства
`specs/decision-provider/v1` (см. развеление в глоссарии).
Контрактные термины этого документа:

| Термин | Значение |
|---|---|
| `auth` | enum-факт наличия credential-маркера в конфиге: `configured` \| `anonymous` \| `unknown`. Значение credential никогда не читается и не уходит на провод (§3.5). |
| `source` | Происхождение строки установки: `config` (имена прочитаны из конфига харнеса) \| `probe` (локальный model-server ответил на models-list запрос). Третьих значений нет (AGW-25). |
| `exec_env` | Замороженный словарь поверхностей факта: `metal` \| `distrobox:<name>` \| `pod:<name>` (прецедент discovery v4). В этой волне строки `models` несут только `"metal"` (§3.2). |
| layout-таблица | Built-in per-harness таблица агента, которая называет — на уровне JSON-pointer / секционного пути — ровно те поля каждого конфига, которые агент вправе прочитать (§3.3). |
| quiet zero | Честное отсутствие факта, которое не является ошибкой: не логируется выше info, не ретраится, не всплывает в вердиктах (§3.6, §3.7). |
| shrink-to-fit | Дисциплина капов агента: объект ужимается ДО отправки, чтобы всегда уместиться; отправка не может переполнить капы (§3.6). |
| 404-silence | Fallback агента на борде без маршрута (pre-1.38): POST не удался — в лог ничего выше info (§3.1). |
| no-wipe | Различие «поле отсутствует» (= нога молчала, зеркало нетронуто) и «поле присутствует с пустым `installations`» (= реальный zero-and-ran, зеркало очищается) (§3.10). |
| names-only валидатор | Финальный фильтр перед marshal: длина-капы плюс credential-shape скан каждой эмитируемой строки (§3.8). |
| zero-and-ran | Отчёт «нога исполнялась и честно не нашла установок»: `models` присутствует, `installations` пуст (§3.10). |

## 3. Контракт

### 3.1 Транспорт: одно аддитивное поле на существующем маршруте

- **MUST**: факты о провайдерах и моделях едут ТОЛЬКО как аддитивное
  top-level поле `models` тела `POST /api/executors/{executor_id}/discovery`,
  рядом с `harnesses` (и другими аддитивными полями семейства). Нового
  маршрута, нового таймера, нового класса auth, нового event-канала
  контрактом не вводится (AGW-25; gate 1 §2).
- **MUST**: нога ездит на существующей cadence discovery (часовой проход +
  один POST на старте цикла) — собственного расписания у `models` нет
  (AGW-25; gate 1 §2.3).
- **MUST**: auth-класс и identity-match маршрута неизменны: токен этого
  executor'а; URL id ≠ token identity → `403`; revoked → `403`; pending
  MAY отчётить; аутентифицированный отчёт тикает `last_seen`
  (унаследовано из развёрнутой семантики маршрута, vesma-eyes 1.38.0).
- **MUST**: на борде без маршрута (pre-1.38) действует 404-silence —
  агент не логирует выше info и не ретраит вне обычного цикла (§2;
  AGW-25 подтверждает без изменений).
- **MUST**: борда, игнорирующая поле `models`, остаётся конформной:
  аддитивное unknown-поле принимается и игнорируется (правило
  аддитивности §5 vesma-agent; gate 1 §2.1).
- **MUST NOT**: поле `models` не создаёт registry-строк, не расширяет
  allowlist'ы, не меняет routing, не создаёт credential-записей —
  discovery зеркалит факт, а не выдаёт полномочия (gate 1 §4.3;
  «advisory, never authority» — первое предложение §3 vesma-agent).

### 3.2 Форма объекта `models` и строки `installation`

Форма (аддитивная; `notes` — omitempty):

```json
{"models": {"installations": [
  {"provider": "openrouter",
   "base_url": "https://openrouter.ai/api/v1",
   "auth": "configured",
   "models": ["z-ai/glm-4.6"],
   "harness": "codex",
   "exec_env": "metal",
   "source": "config",
   "note": "default model from harness settings"}],
 "notes": {"default_model": "z-ai/glm-4.6"}}}
```

- **MUST**: `installations[]` — строки формы
  `{provider, base_url, auth, models[], harness, exec_env, source,
  note}`; поле `note` — MAY, omitempty, свободный текст факта.
- **MUST**: `provider` — имя/slug, как его использует локальный конфиг,
  verbatim, ≤ 60 символов (AGW-25; gate 1 §2.1).
- **MUST**: `models[]` — отсортированный список model-id (строки,
  которые ожидает API провайдера, напр. `z-ai/glm-4.6`), ≤ 50 на строку
  (AGW-25; gate 1 §2.1).
- **MUST**: `harness` — для `source: config` строк — написание из
  словаря харнесов (владелец прочитанного конфига); для `source: probe`
  строк влитая AGW-25 нога несёт slug probe-источника (имя провайдера,
  напр. `ollama` — поведение влитого кода, `internal/discovery/models.go`);
  в обоих случаях локальные ad-hoc имена борда отбрасывает с аудитом по
  одному и тому же правилу §3.11 — особого carve-out для probe-строк
  влитый код не делает (gate 1 §2.4).
- **MUST**: `exec_env` — только `"metal"` в этой волне: конфиг-поверхности
  distrobox/pod НЕ читаются (honest absence; ноги v4/v5 контейнеров не
  трогаются). Остальные значения словаря — достояние будущих волн
  (AGW-25).
- **MUST**: `source` ∈ `config` | `probe` — третьих значений нет
  (AGW-25).
- **MUST**: `notes` — только факты, названные layout-таблицей; сегодня
  это указатель default model харнеса (`default_model`) (AGW-25).
- **MUST**: `top-level` поле `models` — одно на отчёт; атрибуция
  harness/exec_env живёт В строках (решение OQ-2: top-level с явной
  атрибуцией, не per-environment; gate 1 §5 OQ-2).

### 3.3 Names-only чтение конфигов: layout-таблица

> **Superseded (draft.2).** Население таблицы этой сборки (список
> «ровно» ниже) SUPERSEDED per-harness layout-таблицей контракта
> [host-intake §3.3.2](../../host-intake/v0/spec.md): таблица ATTACHED к
> fingerprint-inventory (per-harness секции), добавлены zcode/copilot
> (agent frontmatter `model:`/`tier:`) и pi (auth-маркерная строка
> provider `pi` с пустым `models[]`); gemini/qwen строк нет. Дисциплина
> чтения (MUST ниже: JSON-pointer-таблица, запрет scan-эвристик,
> built-in и версионируемость) НЕ изменилась — host-intake её
> подтверждает. Расширение таблицы — теперь дом host-intake (его §3.3.2
> и §7).

- **MUST**: чтение конфига харнеса выполняется ТОЛЬКО по built-in
  per-harness layout-таблице, которая называет — на уровне
  JSON-pointer / секционного пути (напр. `.providers.<name>.name`,
  ключи `models[]`) — ровно те поля, которые читаются; набор полей
  декода тождественен таблице (gate 2 §2, поправка 1; AGW-25).
- **MUST NOT**: parse-and-scan эвристики («прочитать файл, искать
  model-подобные строки») запрещены (gate 2 §2, поправка 1; AGW-25).
- **MUST**: таблица built-in и версионируется в агенте — прецедент
  fingerprint-таблицы v3 (gate 1 §2.2; gate 2 §2 п.3).
- **MUST**: набор таблицы этой сборки — ровно:
  - codex `~/.codex/config.toml`: `model`, `model_provider`,
    `model_providers.<name>.{name, base_url, env_key}`;
  - continue `~/.continue/config.json`:
    `models[].{provider, model, apiBase, apiKey}`;
  - claude-code `~/.claude/settings.json`: `model`; из `env` — ТОЛЬКО
    ИМЕНА ключей с префиксом `ANTHROPIC_`;
  - aider `~/.aider.conf.yml`: `model`, `openai-api-base`,
    `openai-api-key`;
  - zcode — намеренно ОТСУТСТВУЕТ: документированный path catalog
    моделей для этой сборки не определён (small-and-true beats
    broad-and-guessed) (AGW-25).
- **MUST**: расширение таблицы (новый харнес, новое поле) — изменение
  контракта по §7; молчаливое чтение неназванного поля = нарушение
  (gate 2 §2, поправка 1).

### 3.4 Нормализация `base_url`

- **MUST**: `base_url` приводится к `scheme://authority[/base-path]`
  (AGW-25; gate 2 §2, поправка 2).
- **MUST**: query и fragment ОБДИРАЮТСЯ всегда (AGW-25; gate 2 §2,
  поправка 2).
- **MUST**: userinfo обдирается (AGW-25; gate 1 §2.1).
- **MUST**: credential-подобный query-параметр (`key=`, `api_key=`,
  `token=`, `access_token=`, … — детект по НАЛИЧИЮ имени параметра,
  никогда по значению) понижает факт до `scheme://authority`
  (host-only redaction) либо до omit — значение никогда не эхоится
  (AGW-25; gate 2 §2, поправка 2; gate 1 §2.1).
- **MUST**: unparsable или authority-less URL опускается (honest
  absence), никогда не угадывается (AGW-25; gate 1 §2.1).
- Правило борды зеркально: provider POST валидирует и обдирает
  credential-in-URL (userinfo или `?key=`) по той же поправке 2 —
  вне провода агента, для симметрии границы (gate 2 §4.5).

### 3.5 `auth` — enum-факт из наличия поля

- **MUST**: `auth` ∈ `configured` | `anonymous` | `unknown` и выводится
  ТОЛЬКО из НАЛИЧИЯ credential-маркерных полей, названных таблицей
  (§3.3); значения маркерных полей никогда не читаются в payload ни в
  какой кодировке (AGW-25; gate 2 §2 п.3).
- **MUST**: вывод по харнесам этой сборки — ровно (AGW-25):
  - codex: `env_key` непуст → `configured`; отсутствует → `anonymous`;
  - continue: поле `apiKey` присутствует → `configured`;
    null/отсутствует → `anonymous`;
  - claude-code: имя ключа `ANTHROPIC_*` в `env` → `configured`; нет
    ни одного → `unknown`;
  - aider: `openai-api-key` присутствует → `configured`; отсутствует →
    `unknown`.
- **MUST NOT**: агент не хэширует credential в отчёт, не эмитит его
  урезанным, не передаёт fingerprint — схема провода не содержит
  credential-подобного поля вообще (gate 1 §4.1; gate 2 §4.3).
- **MUST**: probe-нога анонимна: агент не принимает, не хранит и не
  запрашивает credential для discovery целей; «discovery master key»
  флота не изобретается (gate 2 §1 H3).

### 3.6 Капы и shrink-to-fit

- **MUST**: капы факта — `provider` ≤ 60 символов; `models[]`
  отсортирован, ≤ 50 на строку; `installations[]` ≤ 64 строк; весь
  объект `models` ≤ 16 KiB marshaled (AGW-25; gate 1 §2.1).
- **MUST**: объект ужимается ДО отправки (rows halve; терминальный
  всегда-умещающийся ответ — объект с пустым `installations` и
  `notes`) — отправка, превышающая капы, по построению невозможна
  (AGW-25).
- **MUST**: read-cap на файл конфига — жёсткие 8 KiB; файл сверх капа
  или unparsable в пределах капа = честное отсутствие факта, никогда
  не ошибка (AGW-25; gate 2 §2 п.3 — «8 KiB class» прецедента v3).
- **MUST**: усечение факта ездит в `note` затронутой строки
  («models truncated», «rows truncated») — молчаливой потери факта нет
  (AGW-25).
- Отсутствие конфига, мёртвый probe-порт, отсутствие маркерных полей —
  quiet zero (§2): info-факт, не ошибка, не ретрай (AGW-25; gate 1 §2.3).

### 3.7 Probe-нога: анонимный loopback

> **Расширение (draft.2).** Помимо фиксированной таблицы портов ниже,
> `base_url`, сконфигурированный ОБНАРУЖЕННЫМ харнесом и резолвящийся
> LOOPBACK, MAY опрашиваться анонимно (утверждённый гейт OQ-2; бюджет
> ≤8 дополнительных целей; никогда non-loopback, никогда credentialed —
> вердикт H3). Норматив — [host-intake
> §3.3.4](../../host-intake/v0/spec.md); дисциплины этого раздела
> (один GET, timeout, документированные формы ответа, quiet zero, без
> credentials) распространяются на расширение без изменений.

- **MUST**: probe работает ТОЛЬКО по loopback (`127.0.0.1`, `::1`,
  `localhost`) — сканирование внешних хостов конструкцией исключено
  (AGW-25; gate 2 §1 H3).
- **MUST**: цели — фиксированная built-in таблица портов: ollama 11434
  `GET /api/tags`; LM Studio 1234, llama.cpp server 8080, vLLM 8000 —
  `GET /v1/models` (AGW-25).
- **MUST**: один GET на сервер, timeout 2 с, без credentials —
  ни отправленных, ни принимаемых (AGW-25; gate 2 §1 H3).
- **MUST**: разобраются ТОЛЬКО документированные формы ответа:
  `{"models":[{"name":…}]}` (ollama) и `{"data":[{"id":…}]}` (серверы
  OpenAI-формы); всё остальное = отсутствие факта (AGW-25).
- **MUST**: неудача/мёртвый порт — quiet zero: info-факт, не ошибка, не
  retry-цикл (AGW-25; gate 1 §2.3).
- **MUST NOT**: probe не отправляет и не принимает credential-заголовки
  и параметры (§3.5; gate 2 §1 H3).

### 3.8 Leak-дисциплина

- **MUST**: каждая эмитируемая строка (provider slug, model id,
  base_url, note) проходит names-only валидатор: длина-капы §3.6 плюс
  credential-shape скан (token-префиксы `sk-`/`ghp_`/`xox`-…, длинные
  hex или base64-подобные раны, key-shaped assignments) (AGW-25).
- **MUST**: credential-подобная строка в неожиданном поле роняет ВСЮ
  строку installation ДО marshal (AGW-25).
- **MUST**: drop сопровождается ГРОМКИМ локальным логом, reason
  которого НИКОГДА не несёт самого значения (mask-first: маскировать
  до truncate) (AGW-25).
- **MUST**: агент НЕ эмитит событий: инцидент-детектор
  `models.credential_leak_suspected` — БОРД-СТОРОННИЙ, на ingest;
  обязанности агента исчерпываются drop'ом и локальным логом (AGW-25;
  gate 2 §1 H4).
- **MUST**: credential материал никогда не читается в память для
  целей отчёта и никогда не эмитится ни в какой кодировке (gate 1
  §2.2; gate 2 §2 п.3, §4.1).

### 3.9 Knob `discovery_models`

- **MUST**: нога управляется knob'ом `discovery_models: auto|off`
  (дефолт `auto`; неизвестные значения отвергаются на старте —
  прецедент knob'а) (AGW-25; PROTOCOL §7.1).
- **MUST**: `off` = поле `models` отсутствует целиком; `auto` и ran =
  поле присутствует, даже если `installations` пуст (реальный
  zero-and-ran) (AGW-25).
- Это единственный knob ноги; отдельных расписаний, портов и
  credendentials у ноги нет (AGW-25). С draft.2 knob управляет И аддитивным
  элементом `mcp_servers` (FC-7) совместно — [host-intake
  §3.4](../../host-intake/v0/spec.md).

### 3.10 Snapshot-семантика и no-wipe

- **MUST**: зеркало `models` на борде — snapshot: хранится ПОСЛЕДНИЙ
  отчёт; идентичный повторный отчёт — тихий no-op (наследуется verbatim
  из семантики §3 маршрута; gate 1 §2.3).
- **MUST**: отсутствующее поле ≠ пустое: `models` отсутствует = нога не
  отчётила (старый агент / knob off) — зеркало НЕТРОНУТО; `models`
  присутствует с пустым `installations` = реальный zero-and-ran —
  зеркало ОЧИЩАЕТСЯ. no-wipe различие переносится без изменений
  (gate 1 §2.3).
- **MUST**: wire-диффов нет; диффы против предыдущего snapshot
  считает борда (для SSE-событий роста) — на проводе всегда полный
  snapshot (gate 1 §2.3).

### 3.11 Обязанности борды на ingest

- **MUST**: неизвестная атрибуция `harness` → строка отброшена +
  аудит (`discovery.rejected` семейство); словарь никогда не
  расширяется discovery-отчётом (gate 1 §2.4; прецедент волны 3C).
  Правило применяется к обеим классам строк одинаково, включая
  `source: probe` строки (чья `harness` несёт slug probe-источника,
  §3.2) — зеркальная волна ДОЛЖНА решить вопрос словарной принадлежности
  probe-slug'ов осознанно, не тихим carve-out'ом.
- **MUST**: неизвестное значение `exec_env` → строка отброшена + аудит
  — словарь поверхностей закрытый (gate 1 §2.4).
- **MUST**: неизвестные имена `provider` хранятся как advisory-факты
  (OQ-3: словарь провайдеров не заводится на этом драфте; дубликаты не
  страшны — dedup по (provider, base_url)) (gate 1 §2.4, §5 OQ-3).
- **MUST**: credential-подобная строка в любом неожиданном поле
  `models` = drop + инцидент-событие аудита `models.credential_leak_suspected`
  — это данные-инцидент, а не данные (gate 1 §2.4; gate 2 §1 H4).
- **MUST**: капы §3.6 борда проверяет по family честного 422:
  nameless-строка или объект сверх капа → `422`, никогда не тихий trim
  — счётчики остаются честным отчётом агента (gate 1 §2.1; §4).
- **MUST**: аутентифицированный отчёт тикает `last_seen` как сегодня
  (§3.1).

## 4. Коды ошибок

Единый реестр исходов маршрута, значимых для поля `models`. База —
развёрнутая семантика маршрута (vesma-eyes 1.38.0, §3 PROTOCOL.md);
капы поля добавлены gate 1 §2.1. Реакция агента на каждый исход — в
третьей колонке.

| Код | Смысл | Источник | Реакция получателя |
|---|---|---|---|
| `200` | отчёт принят; `last_seen` тикнут | борда | обычный цикл; идентичный повтор — тихий no-op (§3.10) |
| `401` | executor token отсутствует/невалиден | борда | retry в обычном цикле; не выше info |
| `403` | URL id ≠ token identity, либо executor revoked | борда | не ретраить как 4xx-навсегда: identity — конфигурационная ошибка; revoked — kill-switch, присутствие должно угаснуть |
| `404` | маршрута нет (pre-1.38 борда) | борда | 404-silence: ничего выше info (§3.1) |
| `422` | валидация: `harnesses` > 32; объект `models` сверх 16 KiB marshaled; `installations[]` > 64; строка без `provider` или с `models[]` > 50; неизвестное enum-значение формы | борда | честный отказ, никогда тихий trim (gate 1 §2.1); агент не должен уметь послать сверх капа (shrink-to-fit §3.6) — 422 сверх капа = дефект агента |
| `429` | rate (бюджет 60/60 с, общий с heartbeat) | борда | retry на следующем бите цикла; never fatal |

События аудита/инцидентов борды (не HTTP-коды, для полноты реестра):

| Событие | Смысл | Источник |
|---|---|---|
| `discovery.rejected` | отброшена строка с неизвестным `harness` или `exec_env` | борда, ingest (§3.11) |
| `models.credential_leak_suspected` | credential-подобная строка в неожиданном поле `models` — drop + инцидент | борда, ingest (§3.11); агент НЕ эмитит (§3.8) |

## 5. Примеры

Пример-минимум обязателен к мержу (ADR-0001 §1). Файлы лежат в
`examples/` рядом со спекой; в примерах — только плейсхолдеры и
публичные документированные endpoint'ы, никаких реальных токенов,
путей и hostname'ов машин владельца (ADR-0001 §6).

| Файл | Что показывает |
|---|---|
| `examples/config-source-installation.json` | отчёт с одной `config`-строкой (codex): openrouter через `model_providers`, `auth: configured` из непустого `env_key`, `notes.default_model` |
| `examples/probe-source-installation.json` | отчёт с одной `probe`-строкой: локальный ollama ответил `GET /api/tags` на 11434, `auth: anonymous`, `exec_env: metal` |
| `examples/credential-redaction.json` | до/после нормализации `base_url`: query+fragment обдраны; credential-подобный query-параметр → host-only; credential-строка в неожиданном поле → строка dropped, на провод не попала |

## 6. Conformance

Сьют — `conformance/cases.skeleton.yaml`; человеческий чеклист
интегратора — `conformance/checklist.md`. Исполняется раннером
`tools/conformance` (stdlib + `jsonschema`; валидирует только
декларации — ADR-0001 §4). **Статус исполнения — честно:** раннер —
одиночный профиль словаря component-manifest, поэтому скелет лежит под
именем `cases.skeleton.yaml` (CI-гейт `run.py --all` остаётся зелёным);
исполнение проверок этого словаря — волна runner-profile (изменение
`tools/` — через TL-ревью). Машинная JSON-Schema формы `models`
появится вместе с борд-зеркалом (§9). Словарь проверок и таргеты
(`examples/`, `conformance/fixtures/invalid/`) зафиксированы; зелёный
MUST-прогон сьюта после заведения runner-profile = гейт интеграции
агента и борды по этому контракту.

Словарь проверок (исполнитель — будущий профиль раннера):

| Проверка | Что делает |
|---|---|
| `models_object_shape` | top-level `models` несёт ровно `installations` (массив) и MAY `notes` (объект); строка — ровно поля §3.2, `note` — MAY |
| `row_required_fields` | у каждой строки присутствуют `provider`, `base_url`, `auth`, `models`, `harness`, `exec_env`, `source` |
| `auth_enum` | `auth` ∈ `configured` \| `anonymous` \| `unknown` |
| `source_enum` | `source` ∈ `config` \| `probe` |
| `exec_env_metal_only` | `exec_env` = `"metal"` в этой волне |
| `provider_length_cap` | `provider` ≤ 60 символов |
| `models_sorted_cap50` | `models[]` отсортирован и ≤ 50 элементов |
| `installations_cap64` | `installations[]` ≤ 64 строк |
| `base_url_normalized` | `base_url` = `scheme://authority[/base-path]`; query/fragment/userinfo отсутствуют |
| `no_credential_material` | ни одна строка документа не проходит credential-shape скан (`sk-`/`ghp_`/`xox`- префиксы, hex ≥ 40, base64 ≥ 40, key-shaped assignment) — names-only валидатор §3.8 как статическая проверка примеров. Исключение value-scan (прецедент CM `no_secret_in_vars`): пояснительный документ `credential-redaction.json` — его «до»-строки намеренно показывают, что обдирается; скану подлежат только wire-shape документы |
| `harness_dictionary_spelling` | `source: config` строки несут написание из словаря харнесов (с draft.2 словарь населения — per host-intake §3.3.2: zcode, copilot, codex, continue, claude-code, aider, pi); `source: probe` строки несут slug probe-источника (§3.2) |
| `knob_values` | декларация knob'а — только `auto` \| `off` (исполнительный таргет — декларация конфига агента; кейс заводится вместе с борд-зеркалом) |

Кейсы: позитивные — wire-примеры §5 (`examples/config-source-installation.json`,
`examples/probe-source-installation.json`; `expect: pass`, все
`severity: must`; пояснительный `credential-redaction.json` — вне
кейсов, см. исключение выше); негативные — фикстуры
`conformance/fixtures/invalid/` (`expect: fail`).

## 7. Совместимость

- **SemVer**: `0.1.0-draft`; ратификация stable — первая конформная
  реализация ОБЕИХ ног (§9). Ломающее изменение = MAJOR + окно
  `max(90 дней, 2 минорных релиза)` с dual-поддержкой (ADR-0001 §2);
  для версий до 1.0 окно — 14 дней.
- **Аддитивность — правило неизвестного поля** (унаследовано из §5
  PROTOCOL.md, AGW-25 подтверждает): неизвестные JSON-поля аддитивны и
  игнорируются; борда, игнорирующая `models`, конформна; старый агент,
  не знающий `models`, конформен (поля просто нет).
- **REMOVING именованного поля = протокольный MAJOR**: удаление любого
  поля строки §3.2 или top-level `notes` — ломающее изменение.
  Ужесточение капа вниз — ломающее (сужает допустимое); вверх —
  минорное.
- **Расширение layout-таблицы** (новый харнес, новые поля чтения) —
  минорное изменение контракта с уведомлением комитета; расширение
  словаря `auth`/`source` — MAJOR (замкнутые enum'ы).
- **Нумерация**: контракт не вводит собственного номера протокола —
  поправки ног нумеруются AGW-реестром vesma-agent (AGW-25 — эта волна);
  контракту принадлежит форма провода, а не журнал поправок агента.
- **Потребители контракта**: агент пишет поле по §3; борда ingest'ит по
  §3.11 и отдаёт зеркало/ростер по контракту `GET /api/models`
  (`ModelsDiscoveredItem`, vesma-eyes — зона `discovered`, см. §9);
  FE рендер — гейт 3 (ux-blueprint MF1/MF2).

## 8. Threat model (мини-STRIDE)

Ассет контракта — **отсутствие credential материала на проводе**.
Границы: (а) конфиги харнесов ↔ reader агента; (б) агент ↔ борда
(аутентифицированный POST); (в) ingest борды ↔ зеркало/ростер.
Names-only дисциплина — центральный контроль; каждая митигация ниже —
ссылка на MUST §3 либо «операционный контроль».

| Категория | Угроза | Митигация | Проверка |
|---|---|---|---|
| **I**nformation Disclosure | credential материал из конфига попадает в payload (значение `apiKey`, `env_key`, токен в query) | маркерные поля не читаются в память для отчёта — только НАЛИЧИЕ → `auth` (§3.5); credential в query → host-only/omit (§3.4); read-cap 8 KiB сужает поверхность чтения (§3.6) | `no_credential_material`, `base_url_normalized` |
| **I**nformation Disclosure | агент затянут в «прочитать всё и найти model-строки» | layout-таблица на уровне JSON-pointer, scan-эвристики запрещены (§3.3) | `models_object_shape` + ревью таблицы (операционный контроль) |
| **I**nformation Disclosure | credential-подобная строка просочилась в свободное поле (`note`) | names-only валидатор перед marshal: роняет ВСЮ строку, громкий локальный лог с подавленным значением (§3.8) | `no_credential_material`; борд-детектор `models.credential_leak_suspected` (§3.11) — вторая линия |
| **I**nformation Disclosure | credential в URL (`user:pass@host`, `?key=`) | userinfo/query/fragment обдираются всегда; unparsable — omit, не угадывание (§3.4) | `base_url_normalized` |
| **S**poofing | чужой executor шлёт отчёт от чужого id | executor-token класс + identity-match маршрута: id ≠ token → 403 (§3.1, унаследовано) | интеграционные тесты маршрута (операционный контроль) |
| **E**levation of Privilege | discovery-факт выдаёт себе полномочия: роутинг, allowlist, credential-запись | advisory, never authority: поле не создаёт строк, не расширяет словарей и allowlist'ов (§3.1, §3.11) | конформанс борды (drop+audit-тесты, операционный контроль) |
| **D**enial of Service | раздутый отчёт душит борду | shrink-to-fit агента (§3.6) — сверх-кап провод невозможен; борд-капы честным 422 (§4); часовая cadence без собственного таймера (§3.1) | `installations_cap64`, `models_sorted_cap50` |
| **D**enial of Service | probe-нога как SSRF-пушка или сканер | loopback-only, фиксированная таблица портов, один GET, 2 с, без credentials, тихий ноль без ретраев (§3.7) — прицел на произвольный хост конструкцией исключён | `exec_env_metal_only` + ревью таблицы портов (операционный контроль) |
| **R**epudiation | «кто отбросил строку / кто прислал credential?» | drop'ы аудируются (`discovery.rejected`), инциденты называются (`models.credential_leak_suspected`), локальный лог агента громкий (§3.8, §3.11) | операционный контроль (audit trail борды) |
| **T**ampering | подмена словарей (`exec_env`, харнесы) через отчёт | неизвестные значения drop+audit, словари закрытые, рост — owner act (§3.11) | операционный контроль |

Осознанные остаточные риски (за границей контракта): владелец-харнес
читает СВОИ конфиги — это threat model харнеса, не флота (gate 2 §6);
компрометация борд-хоста — вне провода агента; злоупотребление зеркалом
после ingest — дом контрактов ростера и грантов (gate 2).

## 9. Миграция и статус реализации

Легаси нет: поле вводится впервые. Статус реализации ног — честно:

| Нога | Статус | Где живёт |
|---|---|---|
| Агентная (писатель поля) | v6 **влита** — AGW-25 «discovery v6», 2026-10-28 — и **SUPERSEDED** правилами населения draft.2 (per-harness re-key, [host-intake](../../host-intake/v0/spec.md) §3): v6 standalone-таблица давала ноль строк на реальном флоте (проверено живьём 2026-10-28 на core-51); исполнитель re-key — волна v7 (AGW-26), ветка `feat/host-intake-contract` | vesmaro/vesma-agent; норма населения — host-intake §3; норма провода — эта спека §3.2 |
| Борд-зеркало (ingest в `GET /api/models`) | **не влита** — следующая волна vesma-eyes | целевая схема ingest'а уже отдаётся бордой: `ModelsDiscoveredItem` в `ModelsRosterOut.discovered` (зона «discovered», MF2 cut) — поле существует, чтобы FE-контракт встал при landing'е ноги; зона честно пуста, пока на проводе нет slice'а `models` |
| UX ростера (рендер зеркала) | ратифицирован гейтом 3 | `ux-blueprint.md` MF1 «Ростер» (cb166a8), `GET /api/models` — единая точка агрегации (OQ-1) |

Порядок ввода: (1) агентная нога v6 — сделано (AGW-25) и superseded
населением draft.2; (2) агентная волна v7 (AGW-26): per-harness re-key +
FC-7 — в полёте на `feat/host-intake-contract`; (3) борды без зеркала
остаются конформными — поле аддитивно и игнорируется (§3.1, §7);
(4) борд-зеркало — ingest по §3.11, no-wipe семантика §3.10, честные
422 §4; (5) ратификация stable — конформанс обеих ног зелёный.
Промежуточные состояния (зеркало есть, поле не ходит; поле ходит,
зеркала нет) — допустимы и честны: обе стороны читают/пишут аддитивно.

Реализация обязана НЕ опираться на порядок волн: агент не ждёт зеркала,
зеркало не ждёт UX — единственная зависимость «кто кого ломает»
отсутствует по построению аддитивности.

## 10. Ссылки

- [specs/host-intake/v0/spec.md](../../host-intake/v0/spec.md)
  (0.1.0-draft, ADR-0003) — с draft.2 НОРМАТИВНЫЙ ИСТОЧНИК НАСЕЛЕНИЯ
  этого поля: per-harness layout-таблица (FC-6), провайдерные формы
  строк, probe-расширение, аддитивный элемент `mcp_servers` (FC-7);
  форма строки и обязанности борды остаются здесь (§3.2, §3.10, §3.11).
- `docs/PROTOCOL.md` §3 (аддендум «Models-fleet addendum — discovery
  v6», AGW-25, 2026-10-28) и §7.1 (`discovery_models`) — нормативный
  источник агентной ноги; vesmaro/vesma-agent, ветка
  main (merge b98960e).
- Gate 1 — `docs/design/models-fleet/discovery-contract-draft.md`
  (vesmaro/vesma-eyes, ветка `feat/models-fleet-blueprint`, daf969b):
  wire shape §2, red lines §2.2, trust boundaries §4.
- Gate 2 — `docs/design/models-fleet/security-verdict.md` (там же,
  832cd7a): вердикт OQ-4 с поправками 1–2 §2, финальные red lines §4,
  вердикты H1–H4 §1.
- Gate 3 — `docs/design/models-fleet/ux-blueprint.md` (там же,
  cb166a8): MF1/MF2 — потребители зеркала.
- `specs/decision-provider/v1` — «decision provider» семейства решений;
  не путать с provider флота моделей (§2, глоссарий).
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) —
  структура и governance слоя; форма контракта.
- [ADR-0002](../../../adrs/0002-agent-discovery-contract.md) — решение
  о кодификации контракта (authority trail).
- [Глоссарий](../../../GLOSSARY.md), [карта
  экосистемы](../../../ECOSYSTEM.md).
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — интерпретация
  ключевых слов.
