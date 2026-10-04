# Changelog — component-manifest

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в `spec.md` §7 и README репозитория.

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
