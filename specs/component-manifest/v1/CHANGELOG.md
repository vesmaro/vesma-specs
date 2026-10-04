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
- Плейсхолдеры argv: allowlist `{config_path} {state_dir} {runtime_dir}
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
  9 негативных случаев) и чеклист интегратора CM-01…CM-15.
