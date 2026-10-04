# Conformance-раннер v0 (`tools/conformance`)

`run.py` исполняет conformance-сьюты контрактов VESMA: читает
`<spec-dir>/conformance/cases.yaml`, применяет к каждому таргету проверки из
словаря контракта и сверяет факт с ожиданием (`expect`).

**Раннер валидирует только декларации и никогда не исполняет код компонентов**
(ADR-0001 §4). Исполнение кода компонентов — граница доверия v2 (супервайзер
движка), сюда она не входит.

## Запуск

```bash
python3 tools/conformance/run.py specs/component-manifest/v1                 # один сьют, text
python3 tools/conformance/run.py specs/component-manifest/v1 --format=json   # машинный отчёт
python3 tools/conformance/run.py --all specs                                 # все сьюты specs/*/v1/
```

В режиме `--all` обходятся все каталоги вида `specs/*/*/`, где есть
`conformance/cases.yaml`; JSON-отчёт содержит `suites: [...]` и агрегированный
`summary`.

## Exit-коды

| Код | Значение |
|---|---|
| `0` | все `must`-кейсы зелёные |
| `1` | провал хотя бы одного `must`-кейса (в т.ч. любое расхождение expect/факт) |
| `2` | инфраструктурная ошибка: сьют не прочитан, схема не найдена, нет `jsonschema`, таргет отсутствует, неверные аргументы |

Провал `should`-кейса = `WARN` — в сводку попадает, на exit-код не влияет.

## Словарь проверок (component-manifest v1 — spec.md §6)

| Проверка | Что делает |
|---|---|
| `schema_valid` | документ валиден по `schema/*.schema.json` (JSON-Schema Draft 2020-12; в spec-dir ожидается ровно один файл схемы) |
| `schema_invalid` | документ **отвергнут валидацией контракта** = провал JSON-Schema **или** любого нормативного правила раннера (секретность `env.vars`, размещение `env_file`, граф `depends_on` и остальные правила §3 не выражаемы JSON-Schema) |
| `api_version_present` | `apiVersion` соответствует `^vesma\.component/v[0-9]+$` |
| `name_kebab_unique` | `metadata.name` по шаблону `^[a-z][a-z0-9-]{0,62}$` и уникален среди `*.yaml` каталога таргета |
| `tier_enum` | `metadata.tier` ∈ {`core`, `optional`} |
| `duration_format` | поля-длительности (`health.*.interval/timeout/grace`, `stop.grace_period`, `restart.*.*`) по шаблону `^[0-9]+(ms\|s\|m\|h)$` |
| `no_secret_in_vars` | в `launch.env.vars` нет ключей с секретными именами (`token`, `secret`, `password`, `passwd`, `api_key`, `apikey`, `private_key`, `credential`, case-insensitive); дополнительно — скан всех строковых скаляров на секретоподобные значения (`sk-…`, `ghp_…`, PEM, hex/base64 ≥ 40 символов); исключения: поле `metadata.provenance.artifact_sha256` (контрактный хэш, не секрет) и плейсхолдеры `<…>` |
| `no_shell_metacharacters` | `launch.argv` и `health.exec.argv` — массивы строк без shell-метасимволов (`;`, `\|`, `&`, `$`, `<`, `>`, скобок, кавычек, бэктика, `\`, `*`, `?`), без whitespace и shell-инвокации (`sh`/`bash`/… первым элементом, флаги `-c`/`-lc`) — spec.md §3.5 |
| `argv_placeholder_allowlist` | плейсхолдеры `{…}` в argv только из allowlist: `{config_path}`, `{state_dir}`, `{runtime_dir}`, `{venv_bin}` |
| `checker_block_consistency` | `health.checker` ↔ соответствующий блок (`http`/`tcp`/`exec`/`callback`); лишние пробные блоки запрещены; `callback` — только при `kind: in-process` |
| `kind_launch_consistency` | `kind: child-process` ⇒ есть `launch`, нет `in_process`; `kind: in-process` ⇒ наоборот |
| `env_file_outside_manifests_dir` | `launch.env.env_file` резолвится вне каталога манифестов — каталога таргета и канонизированного `specs/layout/v1` каталога `~/.config/vesma/components.d/` |
| `depends_on_acyclic` | граф `depends_on` по манифестам каталога таргета ацикличен; ребро берётся только к имени из той же директории (ссылка на отсутствующее имя — install-time concern, не цикл) |
| `license_spdx` | `metadata.provenance.license` — форма SPDX-идентификатора `^[A-Za-z0-9.-]+(\+[A-Za-z0-9.-]+)?$` (форма, не реестр) |

Для негативных кейсов (`expect: fail`) кейс зелёный, когда документ отвергнут
хотя бы одной проверкой; если отвергнут только через `schema_invalid`, а
диагностические проверки кейса ничего не поймали — `WARN` (фикстура, возможно,
больше не ловит свой дефект).

## Формат `cases.yaml`

```yaml
suite: <имя-сьюта>
contract: <имя-контракта>        # = каталог specs/<name>/
version: <версия контракта>      # SemVer-стиль, как во front-matter спеки
cases:
  - id: <kebab-case-id>          # стабильный идентификатор кейса
    severity: must | should      # must образует MUST-гейт интеграции
    target: <путь от spec-dir>   # YAML-файл (пример или фикстура)
    checks: [<имена из словаря §6>]
    expect: pass | fail          # pass = все проверки проходят; fail = документ отвергнут
```

Шаблон нового сьюта — `templates/cases-template.yaml`. Фикстуры
`conformance/fixtures/invalid/` для set-проверок (`name_kebab_unique`,
`depends_on_acyclic`) рассматриваются как одна установка (spec.md §6).

## Зависимости

- **Обязательно:** Python 3.9+ (stdlib) и `jsonschema` (JSON-Schema Draft
  2020-12) — нужны, когда сьют использует `schema_valid`/`schema_invalid`;
  без них раннер деградирует с понятной ошибкой и exit 2.
- **Опционально:** PyYAML. Если он установлен — парсится весь YAML; если нет —
  встроенный мини-парсер подмножества (вложенные мапы/списки/скаляры, кавычки,
  комментарии, inline-мапы `{a: b}` и inline-списки `[a, b]`). Block scalars
  (`|`, `>`), анкеры и теги подмножеством не поддерживаются — раннер скажет об
  этом явно. «Голая машина» без PyYAML — штатный режим (решение АрхКома
  2026-10-04: stdlib + jsonschema).

## Формат отчёта

- **text:** построчно `[PASS|FAIL|WARN] case-id (severity) expect=…`, под ним
  статус каждой проверки с путём и конкретикой; в конце —
  `N passed / M failed / K warned`.
- **json:** `{suite, contract, version, spec_dir, results: [{case, severity,
  target, expect, checks: [{check, ok, detail}], verdict}], summary: {passed,
  failed, warned}, suite_sha256}` — `suite_sha256` (sha256 содержимого
  `cases.yaml`) предназначен для фиксации вердиктов интеграции.
