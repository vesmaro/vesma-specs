# Changelog — agent-discovery

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в [spec.md](spec.md) §7 и README репозитория.

## 0.1.0-draft.3 — 2026-10-29

### Changed

- **Расширение класс-листа credential-shape детектора** (issue
  vesmaro/vesma-specs#10; паритет агент↔борда обязателен). §3.8 дополнен
  нормативной таблицей классов скана — единой для names-only валидатора
  агента и детектора борды. Два новых класса: **JWT-форма** (строка
  `eyJ…` с ≥ 1 точкой, форма `header.payload.…`; dot-split сегменты
  короче base64-порога 40 больше не спасают токен) и **длинный
  смешанный прогон** (непрерывные ≥ 32 из `[A-Za-z0-9_-]` — смешанные
  буквенно-цифровые секреты, недостающие до hex/b64-порогов).
  Сравнение токен-префиксов зафиксировано как БЕЗ УЧЁТА РЕГИСТРА:
  lowercase `akia` покрыт и прежде реализацией агента (проверка на
  lowercased строке), теперь это договор, а не случайность реализации.
- **Направление ложных срабатываний зафиксировано явно**: легитимная
  строка, похожая на credential (длинный hash-подобный model id), MAY
  дать громкий ложный drop — штатное безопасное направление (строка
  никогда не коверкается и никогда не эмитится; громкий ложный drop
  дешевле тихой утечки).
- §6 `no_credential_material`: порог hex выправлен на **≥ 20** по
  реализациям обеих ног (`[0-9a-fA-F]{20,}` у агента и борды; в строке
  стоял ошибочный «hex ≥ 40»), класс-лист приведён к ссылке на §3.8.

### Status

Draft (0.1.0-draft.3), не ратифицирована. Исполнительная синхронизация
класс-листа (валидатор агента `looksCredentialShaped`, детектор борды
`looks_like_credential`) — кодовая половина issue
vesmaro/vesma-specs#10, волны агента/борды; спек-половина закрыта этой
поправкой. Форма провода не менялась — для обеих ног аддитивно.

## 0.1.0-draft.2 — 2026-10-28

### Changed

- **Re-key: `models` keyed to discovered harnesses per host-intake
  contract** (пункт 1 директивы владельца 2026-10-28). Население поля
  `models` переключено со standalone-таблицы §3.3 на per-harness
  layout-таблицу контракта
  [host-intake](../../host-intake/v0/spec.md) §3 (0.1.0-draft,
  ADR-0003): таблица ATTACHED к fingerprint-inventory — строка модели
  возможна только для харнеса, который агент реально обнаружил.
  Standalone-таблица v6 (codex/continue/claude-code/aider detached) —
  **superseded**: её строки вошли в per-harness таблицу; добавлены
  zcode/copilot (agent frontmatter `model:`/`tier:` — grounded
  2026-10-28: v6 давала ноль строк на реальном флоте) и pi
  (auth-маркерная строка provider `pi` с пустым `models[]`);
  gemini/qwen строк нет. Дисциплины v6 (JSON-pointer layout-таблица,
  names-only, нормализация `base_url`, auth из presence, капы,
  shrink-to-fit, leak-дисциплина) перенесены verbatim — host-intake
  §3.3.6.
- **Probe through harness-configured loopback base_urls** (утверждённый
  гейт OQ-2): §3.7 дополнен расширением — `base_url` обнаруженного
  харнеса, резолвящийся loopback, MAY опрашиваться анонимно (≤8
  дополнительных целей; никогда non-loopback/credentialed — H3);
  норматив — host-intake §3.3.4.
- §9 (статус реализации): агентная нога v6 (AGW-25, влита) — superseded
  населением draft.2; исполнитель re-key — волна v7 (AGW-26), ветка
  `feat/host-intake-contract`; борд-зеркальная волна по-прежнему pending.

### Added

- Аддитивный top-level элемент `mcp_servers` (FC-7) — дом
  [host-intake §3.4](../../host-intake/v0/spec.md); knob
  `discovery_models` управляет им совместно с `models` (§3.9); форма
  строки `models` и обязанности борды (§3.2, §3.10, §3.11) не менялись —
  draft.2 не ломает ничего: провод аддитивен, старые борды конформны.

### Status

Draft (0.1.0-draft.2), не ратифицирована. Ратификация stable — зелёный
конформанс обеих ног (агент v7 + борд-зеркало), как и прежде.

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
main (merge b98960e)); борд-зеркало (ingest в `GET /api/models`,
зона `discovered`) НЕ влито — целевая схема `ModelsDiscoveredItem`
бордой уже отдаётся, зона честно пуста. Ратификация stable — зелёный
конформанс обеих ног.
