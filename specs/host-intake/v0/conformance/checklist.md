# Чеклист интегратора — host-intake v0

Человеческая проверка соответствия контракту (дополнение к сьюту
`cases.yaml` после волны runner-profile). Маркеры MUST/SHOULD — по
spec.md §3; ссылки HI-nn — для отчётов конформанса.

## Агент (соблюдение каталога)

- [ ] **HI-01** Собираются ТОЛЬКО классы каталога §3.2; в коде агента нет
      ног чтения, не названных каталогом; FC-8/FC-9 не собираются до
      активации v2 (P1).
- [ ] **HI-02** Граница §3.5 соблюдена: в payload нет содержимого файлов
      (вне названных исключений), имён проектов/workspace'ов, промптов и
      содержимого сессий, значений env-переменных, трафика,
      credential-материала (P2/P3).
- [ ] **HI-03** Атрибуция FC-6/FC-7 структурная: скан исполняется поверх
      результатов inventory; строк необнаруженных харнесов нет (§3.3.1).
- [ ] **HI-04** Чтение конфигов — только по per-harness layout-таблице
      §3.3.2 (zcode/copilot frontmatter ≤64 файлов × 8 KiB read-cap;
      codex; continue; claude-code — только ИМЕНА env-ключей `ANTHROPIC_`;
      aider; pi — existence `auth.json`); scan-эвристик нет; gemini/qwen
      строк не эмитят (§3.3.2).
- [ ] **HI-05** Dual-form emission: `models[]` — сырые строки verbatim;
      provider — только из документированной формы (суффикс/префикс/
      `copilot` vendor) либо harness bucket с note-причиной; угаданных
      провайдеров нет (§3.3.3).
- [ ] **HI-06** `base_url` omitempty только у endpoint-less источников;
      присутствующий `base_url` нормализован (`scheme://authority[/base-
      path]`, query/fragment/userinfo обдраны; credential-подобный query
      → host-only/omit) (§3.3.2, §3.3.6).
- [ ] **HI-07** `auth` — только из наличия маркерных полей; значений
      маркеров нет в payload ни в какой кодировке; pi-строка — provider
      `pi`, поле `models` опущено (omitempty), `auth` из existence
      `auth.json`; frontmatter-строки (zcode/copilot) note не несут
      (§3.3.2, §3.3.3, §3.3.6).
- [ ] **HI-08** Probe: фиксированная loopback-таблица + ≤8
      harness-настроенных base_url — только loopback, только анонимно
      (credentialed — никогда), zero-redirect, один GET, quiet zero
      (§3.3.4).
- [ ] **HI-09** Капы и shrink-to-fit: provider ≤ 60; models[] ≤ 50 sorted;
      installations ≤ 64; объект ≤ 16 KiB; файл-кап 8 KiB; усечение — в
      `note`; `count` FC-7 — полный итог (§3.3.5, §3.4).
- [ ] **HI-10** Красные линии v6: names-only валидатор (drop, never
      mangle); credential-подобная строка в неожиданном поле → drop всей
      строки до marshal + громкий лог без значения; агент событий не
      эмитит; `exec_env` = `"metal"` (§3.3.6).
- [ ] **HI-11** FC-7: `mcp_servers` — аддитивный top-level; pi
      `mcp-cache.json` — только имена (dict-KEYS), значения не
      декодируются; argv/env/URL нет; knob `discovery_models: auto|off`
      управляет FC-6 и FC-7 совместно (§3.4).

## Борда (ingest + прозрачность)

- [ ] **HI-12** Неизвестный `harness`/`exec_env` в новых полях → drop +
      аудит; сверх-кап объект → честный `422`, не тихий trim
      (agent-discovery §3.11 семья; §4).
- [ ] **HI-13** Рендер «что агенты собирают» построен ИЗ текста контракта,
      по карточке на FC-id, привязан к версии контракта через version
      handshake; поле без FC-id = дефект реализации (§3.6).
- [ ] **HI-14** `sessions[]` трактуется как scanner-owned (eyes-сканер,
      kora-scan / синтетический `hermes`); в рендере поверхности агента
      поле отсутствует (§1, §9).

## Фикстуры и примеры

- [ ] **HI-15** В `examples/` и документе нет реальных токенов и путей
      машин владельца — только плейсхолдеры и публичные endpoint'ы
      (ADR-0001 §6).
- [ ] **HI-16** Негативные фикстуры используют zero-entropy fake-формы
      (префикс+длина), чтобы триггерить shape-скан, но не gitleaks
      (прецедент agent-discovery AD-18).
