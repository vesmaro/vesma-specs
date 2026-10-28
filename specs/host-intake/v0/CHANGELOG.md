# Changelog — host-intake

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в [spec.md](spec.md) §7 и README репозитория.

## 0.1.0-draft — 2026-10-28

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
