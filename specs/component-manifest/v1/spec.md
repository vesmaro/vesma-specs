---
contract: component-manifest
version: 1.1.0-draft
status: draft — ratification pending conformance run
decisions: [ADR-0001]
ratified: |-
  1.0.0 — учредительный АрхКом VESMA, 2026-10-04; ратифицирован первой конформной реализацией — движок vesmaro/vesma, main 4a2da5a, 2026-10-05 (конформанс — docs/project/reports/service-conformance-2026-10-06.md в репо движка; раннер 24/24; чеклист интегратора CM-01…CM-17 green).
  1.1.0-draft — python-чилд зависимости venv (CM §3.5.1; issue vesmaro/vesma#515, окно миграции 2026-10-06): Draft — ratification pending conformance run. Ратификация — ТЛ по evidence первого конформанс-прогона 1.1.0 (раннер + движок-реализация requirements на feature-ветке).
---

# component-manifest v1 — контракт манифеста компонента

Ключевые слова MUST / MUST NOT / SHOULD / MAY интерпретируются по RFC 2119.
Проза — русская; идентификаторы, поля и enum-значения — EN; свободный текст
(`description`) — язык компонента.

## 1. Scope

Манифест — декларативное YAML-описание компонента: единственный источник
знаний CLI и супервайзера о том, как компонент исполняется, чем судить о его
живости, как его останавливать и от кого он зависит. Принцип «CLI-first»
(директива владельца 2026-10-04): CLI не дописывается под компонент —
компонент заявляет себя манифестом и управляется по общим правилам.

**В скоупе:**

- форма манифеста: `apiVersion`, `kind`, `metadata`, `launch` / `in_process`,
  `health`, `stop`, `config`, `restart`, `depends_on`;
- strict validation: неизвестное поле = reject (эволюция только через
  `apiVersion`; аддитивные поля = минорная версия контракта);
- политика секретов манифеста (секреты — только через `env_file`);
- право записи на манифест (кто его создаёт и меняет);
- машинная схема (`schema/`), примеры-минимум (`examples/`) и
  conformance-сьют (`conformance/`);
- коды ошибок валидации (§4).

**Вне скоупа (домены соседних контрактов):**

- поведение супервайзера: FSM, рестарт-политики по тирам, модель процессов,
  systemd-юнит — `specs/service-lifecycle/v1`;
- канонические пути лэйаута (конфиги, state, cache, data, каталог манифестов)
  — `specs/layout/v1`;
- протокол CLI ↔ живой супервайзер — `specs/control-socket/v1`;
- содержимое конфига компонента — манифест фиксирует только схему его
  валидации;
- capabilities/permissions, resource limits, replicas, декларация
  metrics/alerts-webhook — осознанно отложены за пределы v1 (§7).

**Потребители:** install-флоу CLI (единственный писатель манифеста),
супервайзер движка `vesma` (читатель-исполнитель), `doctor`, conformance-раннер
`tools/conformance`, внешние интеграторы.

## 2. Терминология

Термины Component, In-process module, Child-process, Supervisor, Manifest,
Tier, Health check, Grace period, Canonical layout определены в
[глоссарии](../../../GLOSSARY.md) и здесь не переопределяются. Контрактные
термины этого документа:

| Термин | Значение |
|---|---|
| установка (installation) | множество манифестов компонентов на одной машине под одним супервайзером; имена манифестов уникальны в установке |
| каталог манифестов | каталог лэйаута, в который install-флоу пишет манифесты; канонизирован `specs/layout/v1` как `~/.config/vesma/components.d/` (drop-in: install кладёт, uninstall убирает) |
| плейсхолдер | токен вида `{name}` в элементе `argv`, который расширяет супервайзер при spawn по фиксированному allowlist |
| allowlist плейсхолдеров | `{config_path}` (файл конфига компонента в каноническом лэйауте), `{data_dir}` (data-каталог компонента), `{runtime_dir}`, `{venv_bin}` (каталог bin venv компонента) |
| fail-closed загрузчик | загрузчик `env_file`: любое нарушение условий (файл отсутствует, права не 0600, чужой владелец) = отказ старта, а не предупреждение |
| health-проход | один успешный результат health-проверки (`specs/service-lifecycle/v1` §2) |
| strict validation | дисциплина валидации: `additionalProperties: false` на каждом объекте схемы; неизвестное поле = reject |

## 3. Контракт

### 3.1 Владение и право записи

- **MUST**: манифест создаёт и изменяет **только install-флоу CLI**
  (`vesma service install`).
- **MUST NOT**: компонент пишет собственный манифест — иначе ребёнок
  переписывает свой `env`/`argv`, что является эскалацией привилегий по
  построению.
- **MUST**: каталог манифестов недоступен компонентам на запись; юнит
  супервайзера держит запись только за state/cache/data лэйаута
  (`ProtectSystem=strict`, `ReadWritePaths=` — specs/service-lifecycle/v1
  §3.6, SL-18).
- **SHOULD**: `doctor` сверяет манифесты с фактической установкой
  (файлы, права, пути); расхождение — громкое диагностируемое сообщение,
  не тихая починка.

### 3.2 Общая форма и strict validation

- **MUST**: `apiVersion` равен `vesma.component/v1`. Неподдерживаемая версия
  = reject; сообщение об ошибке **MUST** содержать массив поддерживаемых
  загрузчиком версий.
- **MUST**: strict validation — `additionalProperties: false` на каждом
  объекте схемы (`schema/component-manifest.schema.json`); неизвестное поле
  = reject, не протаскивается. Эволюция — через `apiVersion`; аддитивные
  (не ломающие) поля = минорная версия контракта (ADR-0001 §2).
- **MUST**: длительности — строки по шаблону `^[0-9]+(ms|s|m|h)$`
  (`500ms`, `10s`, `5m`, `1h`); составные значения (`1h30m`) и числа без
  единиц запрещены.
- **MUST**: манифест валиден по `schema/component-manifest.schema.json`
  (JSON-Schema 2020-12).

### 3.3 metadata

- **MUST**: `name` — по шаблону `^[a-z][a-z0-9-]{0,62}$`; уникален в
  установке.
- **MUST**: `name` не входит в множество зарезервированных имён
  {`venv`, `venvs`} — коллизия с venv-каталогами лэйаута
  (specs/layout/v1 §3.8); валидатор манифестов обязан отвергать.
- **MUST**: `version` — SemVer 2.0.0 самого компонента.
- **MUST**: `tier` — `core` \| `optional`. Манифест кодирует тир;
  рестарт-политику по тиру применяет супервайзер
  (specs/service-lifecycle/v1 §3.5) — манифест поведение рестарта по тиру
  не описывает.
- **MUST**: `description` — не длиннее 200 символов.
- **MUST**: `provenance.repo` — https-URL публичного репозитория компонента.
- **MUST**: `provenance.license` — SPDX-идентификатор лицензии
  (экосистемный дефолт — `Apache-2.0`).
- **MAY**: `provenance.artifact_sha256` — hex64. Если задан, супервайзер
  проверяет хэш артефакта запуска **при каждом старте** — ловит tamper и
  drift между install и spawn. Подписи артефактов — v2 (нужен корневой ключ).
- **MUST**: при `tier: core` артефакт-хэш (`provenance.artifact_sha256`)
  обязателен; при `tier: optional` — опционален, отсутствие = `doctor`
  WARN (молчаливый приём подмены не оговорён контрактом — см. threat
  model, §8).

### 3.4 kind и секции исполнения

- **MUST**: `kind` ∈ `in-process` \| `child-process`; выбор взаимоисключающий
  с секциями: `launch` обязателен и `in_process` запрещён при
  `kind: child-process`; `in_process` обязателен и `launch` запрещён при
  `kind: in-process`.

### 3.5 launch (child-process)

- **MUST**: `argv` — строго массив строк (`minItems: 1`); никаких
  shell-строк. Элементы **MUST NOT** содержать shell-метасимволы
  (``| & ; < > ( ) $ ` \ " ' * ?``) и whitespace; запрещена shell-инвокация:
  первый элемент с базовым именем шелла (`sh`, `bash`, `dash`, `ash`, `zsh`,
  `ksh`, `busybox`, `cmd`, `powershell`) и любой элемент `-c` / `-lc`.
  Следствие по построению: инъекция через shell невозможна, `ExecStart`
  юнита генерируется одной строкой (SL-17).
- **MUST**: плейсхолдеры в элементах `argv` — только из allowlist
  (`{config_path}`, `{data_dir}`, `{runtime_dir}`, `{venv_bin}`); расширяет
  их супервайзер при spawn; **других подстановок нет** — никакой
  интерполяции переменных окружения и никакого shell.
- **MUST**: `cwd` — строка (рабочая директория; канонические пути —
  `specs/layout/v1`).
- **MUST**: `env.vars` — только не-секреты. Ключ, чьё имя содержит
  (без учёта регистра) `token`, `secret`, `password`, `passwd`, `api_key`,
  `apikey`, `private_key`, `credential` — reject (проверка
  `no_secret_in_vars`).
- **MUST**: `env.env_file` — единственное место секретов. Файл **MUST**
  лежать вне каталога манифестов, иметь права `0600` и владельца —
  пользователя супервайзера. Загрузчик fail-closed: нарушение любого
  условия = отказ старта с готовой командой исправления (`chmod 600`,
  `chown`, перенос файла) — предупреждением это не лечится.
- Примечание (юнит и spawn): argv компонентов никогда не попадает в строки
  юнита — `ExecStart` юнита статичен (`vesma service run`); spawn
  выполняется execve-массивом, поэтому гарантия «без shell» сохраняется
  при любых пробелах в путях.
- Семантика окружения ребёнка (конструирует супервайзер): конструируемый
  PATH + `env.vars` + содержимое `env_file`; семантика `env -i` мандатна
  (specs/service-lifecycle/v1 §3.2, SL-13).
- Примечание (остаточный риск): значения `env_file` передаются в окружение
  ребёнка; процесс с тем же uid может читать `/proc/<pid>/environ` —
  осознанный остаточный риск v1 (единый trust-domain,
  specs/service-lifecycle/v1 §3.2); v2-горизонт — fd-passing или
  альтернативная передача секретов.

### 3.5.1 launch.python — зависимости venv python-чилда (1.1.0)

Опциональный блок декларирует зависимости компонентного venv. Введён в
1.1.0 (аддитивно, не ломает существующие манифесты — §7); до 1.1.0
содержимое venv наполнял только install-флоу bundled-пака, кастомный
python-чилд был не поддержан (issue vesmaro/vesma#515).

- **MUST**: `python.version` (опционально) — ограничение версии
  интерпретатора venv в форме §3.6 (`>=3.11`); семантика проверки —
  `doctor` DR-05 (интерпретатор venv наследуется от движка).
- **MUST**: `python.requirements` (опционально) — массив строк, каждый —
  ТОЧНЫЙ пин `name==version`: URL, `file:`, range- и wildcard-спеки
  запрещены; источники пакетов — только PyPI (правила идентичны LY §3.8 /
  LY-08 применённо к декларации, reject на load-валидации, код
  `REQUIREMENTS_INVALID` с JSON-path элемента и готовой формой исправления).
- **MUST**: единственная подстановка внутри requirements —
  `{engine_version}` (заменяется на версию движка в момент install;
  предназначена для bundled-манифестов, чей пин движка отслеживает
  релизный поезд). Вне requirements (argv, поля версий) токен
  неизвестен — `argv_placeholder_allowlist` не изменяется, супервайзер
  плейсхолдеров requirements никогда не видит.
- **MUST**: requirements при отсутствии `{venv_bin}` в `launch.argv` —
  мёртвая декларация (venv не создаётся, пины не устанавливаются) —
  reject (`REQUIREMENTS_INVALID`). Симметрично: `{venv_bin}` в argv без
  requirements — reject (`REQUIREMENTS_INVALID`, load-валидация; защита
  в глубину — инсталлер повторяет проверку: venv без пинов всегда
  ошибка конфигурации, never silent-empty).
- **MUST**: install-флоу наполняет venv python-чилда ровно из
  `python.requirements` и пишет полный freeze venv в lock-файл (LY §3.8);
  ручной `pip install` внутрь `venvs/<name>/` манифест не меняет —
  freeze-дрейф против lock = находка `doctor` DR-02 и rebuild при
  следующем install: ручное наполнение venv = объявленный дрейф (DR-02,
  specs/layout/v1 §3.8; CM-19).
- In-process компоненты блок `python.requirements` не имеют: они живут на
  venv движка; попытка декларировать requirements вне `launch` отвергается
  схемой (strict validation, §3.2).

### 3.6 in_process

- **MUST**: `module` — импортируемый python-модуль; `entrypoint` — фабрика
  без аргументов `() -> Component`, вызываемая супервайзером.
- **MUST**: `python.version` — ограничение версии интерпретатора в форме
  `>=3.11` (операторы `>=`, `>`, `<=`, `<`, `==`, `^`, `~` + `MAJOR.MINOR[.PATCH]`).
- In-process компонент живёт в процессе супервайзера: смерть in-process
  ядра = смерть супервайзера → рестарт юнита systemd
  (specs/service-lifecycle/v1 §3.1); отдельный механизм рестарта ядра
  не вводится.

### 3.7 health

- **MAY**: секция `health` опциональна; без неё `checker = liveness`
  (процесс жив / модуль загружен).
- **MUST**: `checker` ∈ `http` \| `tcp` \| `exec` \| `liveness` \| `callback`.
  Блок, соответствующий `checker`, обязателен; остальные пробные блоки
  запрещены (мёртвая конфигурация недопустима).
- **MUST**: пробные блоки (`http` / `tcp` / `exec`) несут `interval`,
  `timeout`, `unhealthy_threshold` (порог деградации: подряд неуспешных
  проб → переход FSM в `degraded`, T7 в specs/service-lifecycle/v1 §3.3).
- **MUST**: `callback` — только для in-process; формат `module:attr`;
  сигнатура `() -> {state, detail?}`, `state` ∈ `healthy` \| `degraded` \|
  `failed`. Супервайзер вызывает callback **в изолированной границе**:
  try/except + timeout; **любое** исключение или таймаут = результат
  `state: failed`. Падение callback никогда не роняет супервайзер.
- **MAY**: `startup` — параметры стартового окна: `grace` (сколько ждать
  первого успешного health-прохода), `interval`, `timeout` проб в стартовом
  окне.
- `liveness` без проб: для child-process — «процесс жив»; для in-process —
  «модуль импортирован и фабрика отработала».

### 3.8 stop

- **MUST**: при `kind: in-process` секция `stop` **запрещена** — мёртвая
  конфигурация; остановка in-process = остановка супервайзера (§3.6).
- **MUST**: `signal` ∈ `SIGTERM` \| `SIGINT` — graceful-сигнал остановки.
- **MUST**: `grace_period` — длительность; по истечении супервайзер шлёт
  SIGKILL всей процесс-группе ребёнка (`kill(-pgid, …)` —
  specs/service-lifecycle/v1 §3.1, §3.5).
- Компонент **MUST** завершаться по graceful-сигналу в пределах
  `grace_period` — это обязательство кода компонента, проверяемое на
  конформансе.

### 3.9 config

- **MUST**: `schema_file` XOR `schema_inline` — ровно один способ объявления
  схемы; схема — JSON-Schema 2020-12. `schema_file` — путь к файлу схемы;
  относительный путь резолвится от data-каталога компонента (см.
  `specs/layout/v1`, `~/.local/share/vesma/<name>/`); в канонической установке
  install-флоу кладёт схему туда же.
- **MUST**: конфиг компонента = секция общего конфига экосистемы;
  валидация секции — по схеме из манифеста; **инвалидная конфигурация =
  отказ старта (fail-fast)**, не запуск с дефолтами.
- **SHOULD**: схема конфига сама выдерживает дисциплину строгости
  (`additionalProperties: false`).

### 3.10 restart

- **MAY**: секция опциональна; без неё действуют тировые дефолты
  супервайзера (specs/service-lifecycle/v1 §3.5).
- **MUST** (клампы install-валидации): `backoff.base` ≥ `500ms`;
  `backoff.max` ≤ `5min`; `window.attempts` ≥ `3`. Значение вне клапмов =
  reject (SL-18).
- Семантика полей: `backoff` — экспоненциальный backoff от `base` до капа
  `max`; счётчик сбрасывается после `reset_after` непрерывного uptime;
  `window` — бюджет `attempts` попыток за окно `per`. Поведение по тирам
  (core — бесконечно, optional — бюджет + деградация) применяет супервайзер.

### 3.11 depends_on

- **MAY**: секция опциональна.
- **MUST**: элементы — имена других манифестов установки (по шаблону имени);
  граф зависимостей **ацикличен** — цикл = ошибка install-валидации.
- **MUST**: зависимость считается поднятой («up») по первому успешному
  health-проходу зависимого компонента (T4 в specs/service-lifecycle/v1);
  порядок старта — топологический, остановки — реверс-топологический.

## 4. Коды ошибок

Единый реестр кодов валидации и старта. Источник — install-валидация /
загрузчик супервайзера; получатель (CLI, оператор) получает код + путь к
полю + готовую команду исправления там, где применимо.

| Код | Смысл | Источник | Реакция получателя |
|---|---|---|---|
| `APIVERSION_UNSUPPORTED` | `apiVersion` ≠ поддерживаемой версии | загрузчик | reject; ошибка содержит массив поддерживаемых версий |
| `MANIFEST_SCHEMA_INVALID` | манифест не проходит JSON-Schema (тип, формат, неизвестное поле) | install-валидация / загрузчик | reject; показать JSON-path поля и ожидание схемы |
| `NAME_DUPLICATED` | имя уже занято другим манифестом установки | install-валидация | reject; показать конфликтующий манифест |
| `SHELL_IN_ARGV` | shell-метасимволы / whitespace / shell-инвокация в `argv` | install-валидация | reject; показать элемент и позицию |
| `PLACEHOLDER_UNKNOWN` | плейсхолдер вне allowlist | install-валидация | reject; показать allowlist |
| `REQUIREMENTS_INVALID` | запись `launch.python.requirements` не является точным пином `name==version` (URL/file:/range/wildcard); requirements без `{venv_bin}` в argv либо `{venv_bin}` без requirements | install-валидация | reject; показать JSON-path элемента и форму пина (или инсталлер-сообщение о пустом venv) |
| `SECRET_IN_VARS` | секретное имя ключа в `env.vars` | install-валидация | reject; ключ удалить, значение перенести в `env_file` |
| `ENV_FILE_UNSAFE` | `env_file` отсутствует / права не 0600 / чужой владелец / лежит в каталоге манифестов | загрузчик (fail-closed) | отказ старта + готовая команда исправления (`chmod 600`, `chown`, перенос) |
| `DURATION_INVALID` | длительность не по шаблону | install-валидация | reject |
| `CLAMP_VIOLATION` | restart-числа вне клапмов (base < 500ms, max > 5min, attempts < 3) | install-валидация | reject |
| `DEPENDS_CYCLE` | цикл в графе `depends_on` | install-валидация | reject; показать цикл |
| `DEPENDS_MISSING` | ссылка на несуществующий манифест установки | install-валидация | reject |
| `CONFIG_INVALID` | секция конфига компонента не проходит его схему | загрузчик (fail-fast) | отказ старта; показать ошибку схемы |
| `ARTIFACT_HASH_MISMATCH` | хэш артефакта не совпал с `artifact_sha256` | супервайзер при старте | отказ старта; сигнал tamper/drift, требует reinstall |
| `CALLBACK_FAILED` | исключение/таймаут в health-callback | супервайзер | state failed компонента; супервайзер жив |

## 5. Примеры

Пример-минимум обязателен к мержу (ADR-0001 §1); в примерах — только
канонические пути лэйаута и плейсхолдеры, никаких реальных путей машин и
секретов (ADR-0001 §6).

| Файл | Что показывает |
|---|---|
| `examples/python-inprocess.yaml` | in-process python-компонент (`board`): `in_process` с фабрикой, `health.callback`, `config.schema_inline` (JSON-Schema с 2-3 свойствами) |
| `examples/go-child.yaml` | child-process Go-бинарь (`mesh`): `launch.argv` с плейсхолдером `{config_path}`, `health.http`, `provenance.artifact_sha256` |
| `examples/node-runtime.yaml` | child-process Node-раннтайм (`eyes`): `health.tcp`, `depends_on: [server]` |
| `examples/python-child.yaml` | child-process python-чилд (`reporter`): `launch.python.requirements` с точными пинами + `{venv_bin}` в argv (§3.5.1, 1.1.0) |

## 6. Conformance

Сьют — `conformance/cases.yaml`; человеческий чеклист интегратора —
`conformance/checklist.md`. Исполняется раннером `tools/conformance`
(stdlib + `jsonschema`; валидирует только декларации и не исполняет
компоненты — ADR-0001 §4). Зелёный MUST-прогон сьюта = гейт интеграции
компонента в экосистему.

**Семантика проверки `schema_invalid`:** манифест отвергнут валидацией
контракта — JSON-Schema (`schema/`) плюс нормативные правила §3, реализуемые
раннером (секретность `env.vars`, размещение `env_file`, граф `depends_on`).
Декомпозицию причины дают статические проверки из словаря.

**Фикстуры.** Каталог `conformance/fixtures/invalid/` для set-проверок
(`name_kebab_unique`, `depends_on_acyclic`) рассматривается как одна
установка; каждый кейс таргетит свой файл.

Словарь проверок (исполнитель — `tools/conformance/run.py`, отдельная задача):

| Проверка | Что делает |
|---|---|
| `schema_valid` | документ валиден по `schema/component-manifest.schema.json` |
| `schema_invalid` | документ отвергнут валидацией контракта (см. семантику выше) |
| `api_version_present` | `apiVersion` присутствует и соответствует `^vesma\.component/v[0-9]+$` |
| `name_kebab_unique` | `metadata.name` по шаблону и уникален в установке |
| `name_not_reserved` | `metadata.name` ∉ зарезервированного множества {`venv`, `venvs`} (§3.3; коллизия с venv-каталогами лэйаута — specs/layout/v1 §3.8) |
| `tier_enum` | `metadata.tier` ∈ `core` \| `optional` |
| `duration_format` | все поля-длительности по шаблону `^[0-9]+(ms\|s\|m\|h)$` |
| `no_secret_in_vars` | секретов в манифесте нет: (а) имена ключей `launch.env.vars` проверяются на секретоподобные (`token`, `secret`, `password`, `passwd`, `api_key`, `apikey`, `private_key`, `credential`; case-insensitive); (б) значения всех строковых скаляров документа проверяются на 5 секретоподобных паттернов (openai-style `sk-…`, github PAT `ghp_…`, PEM private key, длинный hex ≥ 40, длинный base64 ≥ 40). Исключения value-scan: поддерево `config` (`schema_inline` содержит легитимные паттерны и дефолты), `metadata.description`, `metadata.provenance.artifact_sha256` (hex64 по контракту), значения-плейсхолдеры `<...>`; в диагностике значения маскируются |
| `no_shell_metacharacters` | `argv` (launch и health.exec) без shell-метасимволов, whitespace и shell-инвокации |
| `argv_placeholder_allowlist` | плейсхолдеры argv (`launch.argv`, `health.exec.argv`) только из allowlist §2; флагуются только well-formed плейсхолдеры вида `{[a-z_]+}` вне allowlist — литеральные `{}`, `{a` и т.п. плейсхолдерами не являются и не флагуются |
| `checker_block_consistency` | `health.checker` ↔ соответствующий блок (иф-связка §3.7); `callback` только при in-process |
| `kind_launch_consistency` | kind ↔ launch/in_process XOR (§3.4) |
| `requirements_venv_consistency` | `launch.python.requirements` ↔ `{venv_bin}` в `launch.argv` (§3.5.1, 1.1.0): requirements без вени-ссылки — мёртвая декларация; `{venv_bin}` без requirements — пины не объявлены; cross-field правило, JSON-Schema не выразимо |
| `env_file_outside_manifests_dir` | `env.env_file` вне каталога манифестов |
| `depends_on_acyclic` | граф `depends_on` установки ацикличен |
| `license_spdx` | `provenance.license` — форма SPDX-идентификатора (regex `^[A-Za-z0-9.-]+(\+[A-Za-z0-9.-]+)?$`), не реестр |

Кейсы: четыре позитивных (примеры, `expect: pass`, полный набор уместных
проверок, все `severity: must`; с 1.1.0 — `examples/python-child.yaml`) и
негативные по `conformance/fixtures/invalid/` (все `severity: must`,
`expect: fail`). Проверки `depends_on_acyclic`, `no_shell_metacharacters`,
`env_file_outside_manifests_dir`, `no_secret_in_vars`,
`requirements_venv_consistency` (у python-чилда) входят и в позитивные кейсы.

## 7. Совместимость

- **SemVer**: ратифицирован 2026-10-05 первой конформной реализацией
  в движке vesma (main `4a2da5a`): `1.0.0-draft.2` → `1.0.0`.
  Ломающее изменение = MAJOR + deprecation-окно
  `max(90 дней, 2 минорных релиза)` с dual-поддержкой (ADR-0001 §2).
- **Аддитивные поля** (новые опциональные поля, не ломающие существующие
  манифесты) = минорная версия контракта; строгая схема с
  `additionalProperties: false` делает их детектируемыми breaking-детектором
  CI (сравнение схем соседних версий).
- **Потребители контракта**: супервайзер читает `name/kind/tier/metadata/
  launch/in_process/health/stop/config/restart/depends_on` (требования к
  чтению — specs/service-lifecycle/v1 §6); пути манифестов и env-файлов —
  `specs/layout/v1`; управление живым супервайзером —
  `specs/control-socket/v1`.
- **Отложено за пределы v1 (осознанно, кандидаты v2):**
  capabilities/permissions; resource limits; replicas; декларация
  metrics/alerts-webhook; подписи артефактов (v1 даёт только
  `artifact_sha256` — подписи требуют корневого ключа).
- **1.1.0 (аддитивно, 2026-10-06, issue vesmaro/vesma#515)**:
  `launch.python` — опциональный блок декларации python-чилда
  (`version`, `requirements[]` — точные == пины, PyPI-only; §3.5.1).
  Не ломает существующие манифесты: блок опционален, у манифестов без
  `python` в `launch` вся валидация 1.0.0 проходит байт-в-байт.
  Ратификация — первый конформанс-прогон 1.1.0 (Draft — ratification
  pending conformance run). Для вендоров v1-манифестов блок остаётся
  необязательным; `{engine_version}` — плейсхолдер только внутри
  requirements.
- Шаблон `templates/manifest-template.yaml` — производный от этой спеки;
  при расхождении нормативны спека и `schema/`.

## 8. Threat model (мини-STRIDE)

Манифест — **локальный доверенный файл без привилегий**: он не исполняется,
его читают install-флоу и супервайзер. Доверие границей не делегируется:
компонент не является доверенным писателем собственного манифеста.

**Ассеты:** `env`/`argv` детей (через манифест), секреты в `env_file`,
граф зависимостей, процесс супервайзера.

**Граница:** файл манифеста ↔ загрузчик/супервайзер; компонент ↔ каталог
манифестов.

| Категория | Угроза | Митигация | Проверка |
|---|---|---|---|
| **T**ampering | компонент/сторонний процесс правит свой манифест (переписывает свой `env`/`argv`) | право записи: манифест пишет только install-флоу (§3.1); каталог манифестов вне `ReadWritePaths` компонентов (hardening, SL-18) | операционный контроль (права каталога) + CM-чеклист |
| **T**ampering | подмена артефакта запуска между install и spawn | `artifact_sha256` проверяется супервайзером при каждом старте → `ARTIFACT_HASH_MISMATCH` | §3.3; старт-проверка движка |
| **T**ampering | протаскивание мусора через неизвестные поля | strict validation: `additionalProperties: false`, неизвестное поле = reject | `fix-unknown-field` (`schema_invalid`) |
| **I**nformation Disclosure | секрет в `env.vars` манифеста | секреты в манифесте запрещены; секретное имя ключа = reject | `fix-secret-in-vars` (`no_secret_in_vars`) |
| **I**nformation Disclosure | `env_file` с ослабленными правами или в каталоге манифестов | fail-closed загрузчик: вне каталога манифестов, `0600`, владелец — пользователь супервайзера, иначе отказ старта с командой исправления | `fix-env-file-inside-manifest-dir` + операционный контроль |
| **E**levation of Privilege | shell-инъекция через `argv` | argv — массив строк без shell по построению; метасимволы и `sh -c` запрещены; плейсхолдеры расширяет супервайзер по allowlist, интерполяции нет | `fix-argv-string` + `no_shell_metacharacters` / `argv_placeholder_allowlist` |
| **E**levation of Privilege | ребёнок переписывает граф зависимостей/тир через манифест | то же право записи (§3.1): единственный писатель — install-флоу | операционный контроль |
| **D**enial of Service | health-callback роняет супервайзер исключением | изолированная граница вызова: try/except + timeout; любое исключение = `state: failed` | §3.7 (движок) + `checker_block_consistency` |
| **D**enial of Service | манифест вынуждает рестарт-шторм | клампы restart-чисел (§3.10) + тировые политики супервайзера (SL §3.5) | `fix-bad-duration` / `CLAMP_VIOLATION` + SL-18 |
| **D**enial of Service | цикл зависимостей подвешивает старт | граф `depends_on` ацикличен: цикл = ошибка install-валидации | `fix-cyclic-dependson-*` (`depends_on_acyclic`) |
| **S/R**poofing / **R**epudiation | «кто изменил манифест?» | единственный писатель — install-флоу через CLI; изменения супервайзера видны структурными строками журнала (SL §3.4); journald append-only | операционный контроль |

Каждая митигация закрыта conformance-чеком либо помечена «операционный
контроль» — тихих непроверяемых обещаний нет.

## 9. Миграция с легаси

Легаси-юниты с `env -i` в sh-обёртках и `pkill`-паттернами заменяются
манифестами; перенос ручной, точка миграции одна — install-флоу. `doctor`
сверяет манифесты с фактической установкой и подсвечивает легаси-остатки.

| Легаси-паттерн (инвентарь 2026-10-04) | Контрактный ответ |
|---|---|
| sh-обёртка с `env -i` (ручная гигиена окружения на каждый компонент) | `launch.env.vars` + `env.env_file`; env-семантику строит супервайзер централизованно (SL-13) |
| `pkill`-паттерны в ExecStop (инвентаризация по имени) | `stop.signal` + `stop.grace_period`; остановку делает супервайзер по процесс-группе (SL-04); pkill исчезает |
| `ExecStart` с `sh -c` и конкатенацией | `launch.argv` списком строк; `ExecStart` генерируется одной строкой без shell (SL-17) |
| конфиги в легаси-именах, разбросанные по дому | секция общего конфига, валидируемая `config.schema_file`/`schema_inline`; канонические пути — `specs/layout/v1` |
| venv-перекрытия, ручные симлинки на интерпретатор | плейсхолдер `{venv_bin}`; venv-дисциплина одного venv на компонент — `specs/layout/v1` |
| правки «живых» скриптов запуска руками | манифест пишет только install-флоу (§3.1); `doctor` сверяет манифест ↔ установку |

Порядок: инвентарь `doctor` → install-флоу генерирует манифесты → зелёный
MUST-прогон сьюта компонента → старые механизмы запуска выводятся из
оборота. Миграция легаси-развёртывания — не ранее закрытия первого окна
наблюдения учредительного трека (founding context — см. `docs/`; roadmap
фаза 3, трек движка); спеки и код CLI окну не подчиняются (как в
specs/service-lifecycle/v1 §8).

**Историческая справка.** Спека намеренно генерифицирована (решение
владельца 2026-10-04): конкретика учредительного окружения — легаси-имена,
целевая машина, детали первого окна наблюдения — сохранена в founding-паке
`docs/` (в частности, бриф директивы
`docs/brief-2026-10-04-archcom-founding.md`) и в истории репы; для
связности истории читай их вместе с этой спекой.

## 10. Ссылки

- `specs/service-lifecycle/v1` — супервайзер: потребляет манифест, определяет FSM, рестарт-политики, systemd-юнит
- `specs/control-socket/v1` — управление живым супервайзером
- `specs/layout/v1` — канонические пути: каталог манифестов, env-файлы, state/runtime/config
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — структура и governance слоя; форма этого контракта ратифицирована учредительным АрхКомом 2026-10-04
- [Бриф учредительного АрхКома](../../../docs/brief-2026-10-04-archcom-founding.md) — директивы CLI-first, супервайзер-архитектура, контрактный интерфейс
- [Глоссарий](../../../GLOSSARY.md), [карта экосистемы](../../../ECOSYSTEM.md)
- [Шаблон манифеста](../../../templates/manifest-template.yaml) — производный от этой спеки
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — интерпретация ключевых слов
- [JSON Schema 2020-12](https://json-schema.org/specification-links#2020-12) — формат `schema/` и `config.schema_inline`
- [Semantic Versioning 2.0.0](https://semver.org/) — формат `metadata.version`
- [SPDX License List](https://spdx.org/licenses/) — формат `provenance.license`
