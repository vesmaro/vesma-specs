# Changelog — context-lifecycle

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в [spec.en.md](spec.en.md) §1, §8 (норматив) и README репозитория.

## 0.1.0-draft — 2026-10-08

### Added

- [spec.en.md](spec.en.md) — нормативный скелет публичной спеки расширения
  `io.github.vesmaro/context-lifecycle` (волна 0 слайса
  nhi-8-universal-protocol): скоуп; терминология публичного глоссария
  (situation brief, advisory, turn budget policy/allocator, hypothesis
  record, blind spots, question charter); идентичность расширения (opt-in
  всегда, graceful degradation обязательна, серверный дедуп); операции v0
  (`context/assemble`, `tool-result/compress`, `context/rewrite`,
  `ambient/brief` с семантикой `state_id`, PULL в v1 — подписки v2,
  `lifecycle/signals`); нормативные security-требования S-1…S-8 (восемь
  условий волны-2 + разрешение конфликта императив); turn budget policy
  (рекомендуемый профиль `default`, `policy_id` = хеш, вето «nothing rides
  without a role»); конформанс (будущий pytest-набор, 10 ассертов);
  открытые вопросы OQ-1…OQ-4.
- [spec.md](spec.md) — русский мост (структура зеркальна, наполнение
  сокращённое; «EN governs; RU may lag ≤ 1 minor»).

### Decisions

- Языковая политика публичной спеки: норматив — EN (вердикт волны-2
  документации); репо-дефолт «RU-канон + EN-зеркало» для этой спеки
  инвертирован, механический bilingual-гейт остаётся зелёным; правка
  политики гейта — открытый вопрос OQ-4.
- Машинная schema и examples в v0 отсутствуют (прецедент
  decision-provider v1); появятся минорным изменением вместе с
  исполняемым сьютом.

### Status

Draft, не ратифицирована. Ратификация ждёт: ADR «vesma-specs как публичный
норматив», пример-минимум, конформанс-сьют (10 ассертов), кворум АрхКома.

Источник: вердикты волн 1–2 расширенного АрхКома («Владение обстановкой и
качественный вопрос», v1.0; слайс nhi-8, волна 0).
