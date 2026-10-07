# Changelog — component-manifest

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в `spec.md` §7 и README репозитория.

## 1.1.0 — 2026-10-07

Аддитивное минорное: зависимости venv python-чилдов
(`launch.python`, §3.5.1; issue vesmaro/vesma#515 — инцидент живой
миграции 2026-10-06: кастомный python-чилд (8788 board face) не имел
поддержанного пути в v1 install-флоу). Плюс §3.12 — auth-injecting компоненты/прокси как trust boundary (ArchCom 2026-10-06, ADR-0042 движка: условие (а) — каскад-ревью обязательно). **Ratified 1.1.0 stable 2026-10-07** (ратификация — ТЛ по evidence первого конформанс-прогона
1.1.0; форма поля согласована с реализацией движка на feature-ветке).

- `launch.python` (опциональный блок, оба поля опциональны):
  `version` — ограничение интерпретатора venv (форма §3.6, семантика
  DR-05); `requirements[]` — ТОЧНЫЕ `==` пины, только PyPI (правила
  LY §3.8/LY-08: URL/file:/range/wildcard — reject; код
  `REQUIREMENTS_INVALID` — новый в реестре §4).
- `{engine_version}` — новая подстановка, допустимая ТОЛЬКО внутри
  requirements: расширяется install-флоу на версию движка в момент
  install (bundled-манифест metrics пинует `vesma=={engine_version}` —
  статичный пин в пак-манифесте дрейфовал бы с каждым релизом).
  Allowlist плейсхолдеров argv НЕ изменяется; супервайзер плейсхолдеров
  requirements не видит.
- Cross-field правило (§3.5.1): requirements без `{venv_bin}` в argv —
  мёртвая декларация; `{venv_bin}` без requirements — пины не объявлены;
  оба = reject (`REQUIREMENTS_INVALID`, проверка раннера
  `requirements_venv_consistency`).
- Venv наполняется ровно из requirements; lock = полный freeze (LY §3.8);
  ручной `pip install` = дрейф DR-02 → rebuild (CM-19).
- Схема (`schema/component-manifest.schema.json`): `launch.python`
  (additionalProperties: false; пин-паттерн в items). Пример
  `examples/python-child.yaml`; фикстуры `requirements-range.yaml`,
  `requirements-no-venv-bin.yaml`; сьют — 27 кейсов (было 24); чеклист
  интегратора CM-01…CM-19.
- Существующие манифесты 1.0.0 НЕ затронуты: блок опционален; валидация
  манифестов без `python` в `launch` идентична 1.0.0 байт-в-байт (§7).

## 1.0.0 — 2026-10-05

Ратификация реализацией (SemVer: `1.0.0-draft.2` → `1.0.0`, статус
draft → stable). Первая конформная реализация — движок
[vesmaro/vesma](https://github.com/vesmaro/vesma), main `4a2da5a`
(волны W1–W7, PR #486/#491/#494/#492/#496/#497): раннер
`tools/conformance` — 24/24, чеклист интегратора CM-01…CM-17 green.

## 1.0.0-draft.2 — 2026-10-05

Нормативные поправки глубокого ревью №2 (до первой реализации):

- Зарезервированные имена: `metadata.name` ∉ {`venv`, `venvs`} — коллизия
  с venv-каталогами лэйаута (P1-2; детали — fix-слайс B ниже).
- `artifact_sha256` обязателен при `tier: core`; при `tier: optional` —
  опционален, отсутствие = `doctor` WARN (F-11; детали — fix-слайс B ниже).

Форма контракта не менялась (draft до ратификации реализацией).

## 1.0.0-draft.1 — 2026-10-04

Учредительная форма контракта манифеста компонента — кодификация
ратифицированной формы учредительного АрхКома VESMA (2026-10-04), без
переигрывания решений.

- Форма манифеста: `apiVersion` (`vesma.component/v1`), `kind`
  (in-process | child-process, XOR секций исполнения), `metadata`
  (name/version/tier/description/provenance), `launch` (argv без shell,
  cwd, env.vars + env_file), `in_process` (module/entrypoint/python),
  `health` (http | tcp | exec | liveness | callback), `stop`
  (signal + grace_period), `config` (schema_file XOR schema_inline),
  `restart` (клампы), `depends_on` (ациклично).
- Strict validation: `additionalProperties: false` на каждом объекте;
  неизвестное поле = reject; эволюция через `apiVersion` (аддитивные поля
  = минор контракта).
- Секреты: в манифесте запрещены; только `env_file` вне каталога
  манифестов, `0600`, владелец — пользователь супервайзера; загрузчик
  fail-closed с готовой командой исправления.
- Плейсхолдеры argv: allowlist `{config_path} {data_dir} {runtime_dir}
  {venv_bin}`; расширяет супервайзер, других подстановок нет.
- `artifact_sha256`: опциональная проверка хэша артефакта при каждом
  старте (tamper/drift); подписи артефактов — v2 (нужен корневой ключ).
- In-process health: liveness по умолчанию; `callback` — вызов в
  изолированной границе (try/except + timeout), любое исключение = state
  failed, супервайзер не роняется никогда.
- Право записи: манифест пишет только install-флоу CLI; компонент
  собственный манифест не пишет.
- Отложено за пределы v1 (кандидаты v2): capabilities/permissions,
  resource limits, replicas, декларация metrics/alerts-webhook, подписи
  артефактов.
- Артефакты: JSON-Schema 2020-12, три примера-минимума (in-process python,
  Go child-process, Node child-process), conformance-сьют (3 позитивных +
  19 негативных случаев) и чеклист интегратора CM-01…CM-15.

Поправки глубокого ревью (fix-слайс A, 2026-10-04; chair-решения, до
ратификации реализацией):

- `config.schema_file` резолвится от data-каталога компонента
  (`~/.local/share/vesma/<name>/`, specs/layout/v1), не от каталога
  манифеста; install-флоу кладёт схему туда же.
- Плейсхолдер `{state_dir}` переименован в `{data_dir}` (allowlist §2,
  раннер, примеры, шаблон).
- §6: value-scan секретов кодифицирован — 5 паттернов значений с
  исключениями (поддерево `config`, `metadata.description`,
  `artifact_sha256`, `<…>`-плейсхолдеры), маскирование в диагностике;
  плейсхолдеры argv флагуются только well-formed `{[a-z_]+}` вне allowlist.
- `stop` запрещён при `kind: in-process` (мёртвая конфигурация); при
  `child-process` обязателен (перенос глобального required в if/then).
- Кламп `window.attempts >= 3` закодирован в схеме (minimum).
- Словарь §6 выровнен с раннером: `api_version_present` — regex
  `^vesma.component/v[0-9]+$`; `license_spdx` — форма SPDX, не реестр.
- Негативные фикстуры уникализированы по именам (`mesh-<дефект>`, dup-пара
  `dupcomp`); добавлены 10 фикстур под непокрытые проверки (имя/дубликат,
  плейсхолдер, метасимволы, checker/kind-несоответствия, лицензия, кламп,
  stop при in-process); сьют — 22 кейса.

Поправки ревью волны №2 (fix-слайс B, 2026-10-05; chair-решения, до
ратификации реализацией):

- Зарезервированные имена (P1-2): `metadata.name` ∉ {`venv`, `venvs`} —
  коллизия с venv-каталогами лэйаута (specs/layout/v1 §3.8); MUST §3.3,
  `not.enum` в схеме, проверка раннера `name_not_reserved`, фикстура
  `reserved-name.yaml`.
- Политика `artifact_sha256` по тирам (F-11): при `tier: core` хэш
  обязателен (if/then по `metadata.tier` в схеме), при `optional` —
  опционален, отсутствие = `doctor` WARN; фикстура `core-no-sha.yaml`.
- §3.5, примечание об остаточном риске env (F-12): значения `env_file`
  живут в окружении ребёнка и читаемы same-uid процессом через
  `/proc/<pid>/environ` (единый trust-domain, SL §3.2); v2-горизонт —
  fd-passing/альтернативная передача.
- §3.5, примечание о статичном `ExecStart` (F-13): argv компонентов не
  попадает в строки юнита — юнит статичен (`vesma service run`), spawn
  выполняется execve-массивом («без shell» при любых пробелах в путях).
- Сьют — 24 кейса; чеклист интегратора — CM-01…CM-17.
