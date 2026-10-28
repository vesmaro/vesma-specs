# Changelog — agent-discovery

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в [spec.md](spec.md) §7 и README репозитория.

## 0.1.0-draft — 2026-10-28

### Added

- [spec.md](spec.md) — нормативная спека провода discovery моделей
  (агент → борда): кодификация протокольной поправки AGW-25
  «Models-fleet addendum — discovery v6» (`docs/PROTOCOL.md` §3
  vesma-agent) как экосистемного контракта спек-слоя (директива
  владельца 2026-10-28). Внутри: аддитивное top-level поле `models`
  маршрута `POST /api/executors/{id}/discovery` (`installations[]` +
  `notes`); форма строки `{provider, base_url, auth, models[], harness,
  exec_env, source, note}`; красные линии names-only чтения
  (built-in per-harness layout-таблица на уровне JSON-pointer —
  гейт 2 поправка 1); нормализация `base_url` с обдиранием
  query/fragment/userinfo и credential-query-параметров (гейт 2
  поправка 2); `auth` — enum-факт из наличия поля; капы 64/50/16 KiB +
  read-cap 8 KiB и shrink-to-fit; анонимная loopback probe-нога с
  фиксированной таблицей портов; leak-дисциплина (drop строки до
  marshal, громкий локальный лог с подавленным значением;
  `models.credential_leak_suspected` — борд-сторона на ingest);
  knob `discovery_models: auto|off`; snapshot-семантика и no-wipe;
  обязанности борды на ingest (drop+audit `discovery.rejected`, честные
  422); коды ошибок §4; мини-STRIDE §8; честный статус реализации §9.
- [spec.en.md](spec.en.md) — информативное EN-зеркало (single-commit
  sync; норматив — русская версия).
- [README.md](README.md) — EN quickstart интегратора.
- [examples/](examples/) — пример-минимум (гейт мержа, ADR-0001 §1):
  config-строка, probe-строка, credential-redaction до/после.
- [conformance/](conformance/) — декларативный скелет сьюта
  (`cases.skeleton.yaml` — имя сознательное: раннер — одиночный профиль
  словаря CM, CI `run.py --all` остаётся зелёным; словарь проверок §6,
  фикстуры `fixtures/invalid/`) + чеклист интегратора.

### Decisions

- Полномочия текста (authority trail): агентная нога — AGW-25 (влита);
  красные линии — гейт 2 security-verdict (832cd7a, поправки 1–2 к
  OQ-4); форма провода — гейт 1 discovery-contract-draft (daf969b);
  потребитель зеркала — гейт 3 ux-blueprint (cb166a8, MF1/MF2).
  Запись решения — [ADR-0002](../../../adrs/0002-agent-discovery-contract.md).
- Скоуп контракта — только провод агент → борда: хранение credential'ов,
  гранты и pull-прокси остаются за вердиктом гейта 2 (vesma-eyes); UX
  ростера — за гейтом 3. Контракт остаётся корректным при ответе
  «никогда» на прокси (gate 1 §4.5).
- Контракт не вводит собственного номера протокола: поправки ног
  нумерует AGW-реестр vesma-agent (AGW-25 — эта волна).
- Машинная JSON-Schema формы `models` появится вместе с борд-зеркалом
  (прецедент decision-provider v1 / context-lifecycle v0: schema и
  executable-сьют — минорным изменением с первой конформной
  реализацией).

### Status

Draft, не ратифицирована. Агентная нога влита (AGW-25, ветка
`feat/models-discovery`); борд-зеркало (ingest в `GET /api/models`,
зона `discovered`) НЕ влито — целевая схема `ModelsDiscoveredItem`
бордой уже отдаётся, зона честно пуста. Ратификация stable — зелёный
конформанс обеих ног.
