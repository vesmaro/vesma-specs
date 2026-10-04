# CHANGELOG — `control-socket`

Формат: SemVer по «Дисциплине контрактов» репозитория (README): MAJOR —
ломающее, MINOR — аддитивное, PATCH — редакционное.

## [1.0.0-draft.1] — 2026-10-04

### Added

- Учредительная форма контракта, ратифицированная учредительным АрхКомом
  VESMA 2026-10-04 (ADR-0001), кодифицирована в [spec.md](spec.md):
  пути и права профилей (user, user fallback, system-горизонт v2);
  TOCTOU/SYMLINK-процедура bind-стороны; протокол JSON Lines; методы
  `hello` / `status` / `start` / `stop` / `restart` / `logs` / `health`;
  коды ошибок с диапазонами; лимиты; мини-STRIDE threat model; политика
  совместимости; миграция с легаси.
- [examples/example-session.txt](examples/example-session.txt) — пример-минимум
  (hello → status → start → status → logs → stop → идемпотентный повтор +
  ошибка `unknown_component`).
- [conformance/checklist.md](conformance/checklist.md) — 15 исполняемых
  пунктов соответствия.

### Decisions (ратифицировано, зафиксировано)

- **Socket activation отклонён** владельцем 2026-10-04: это сокет
  управления, не activation; вернуться при появлении реального сценария.
- **JSON-RPC 2.0 отклонён** комитетом (notifications/batch/коды не нужны);
  envelope сознательно совместим по форме — будущий мост дёшев.
- **TCP control plane запрещён** by construction; его появление = MAJOR +
  полный threat model.
- **Группа `vesma-oper` инсталлятором по умолчанию не создаётся** (группа =
  оператор-эквивалент; урок docker-сокета) — только документируется.
- **Linux-only в v1** (BSD/mac `getpeereid` — отдельное решение).
- **Ранние запросы без `hello` → error 4 `version_unsupported`**
  (`data.reason="hello_required"`, `data.supported` обязателен): до `hello`
  версия протокола не согласована — отказ по той же ветке, что и при
  несовпадении major; единый путь восстановления (отправить `hello`); код 3
  остаётся только для params. Выбор из двух вариантов, предложенных
  ратифицированным текстом (4 или 3), зафиксирован кодификатором 2026-10-04.

### Status

`draft` — ратифицируется первой конформанной реализацией в движке `vesma`
(карточка `cli-service-management`).

[1.0.0-draft.1]: ./spec.md
