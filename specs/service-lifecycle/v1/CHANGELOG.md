# Changelog — service-lifecycle

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в `spec.md` §6 и README репозитория.

## 1.0.0-draft.1 — 2026-10-04

Учредительная форма контракта супервайзера — кодификация ратифицированной
формы учредительного АрхКома VESMA (2026-10-04), без переигрывания решений.

- Модель процессов: setsid-сессии (pgid == pid), stop = `kill(-pgid, …)`,
  SIGCHLD → `waitpid(-1, WNOHANG)`, subreaper, PID1-режим.
- Изоляция: падение любого подмножества детей ≠ падение супервайзера и
  контрольного сокета; `env -i` семантика окружения ребёнка мандатна.
- FSM ребёнка: `stopped/starting/healthy/degraded/backoff/blocked` +
  нормативная таблица переходов T1–T14.
- Наблюдаемость: фиксированный формат структурных строк
  (`spawn/exit/health/degraded`), маркировка `SYSLOG_IDENTIFIER=vesma-<component>`.
- Рестарт-политики: core — бесконечно (backoff 1s ×2 cap 30s, jitter ±20%,
  сброс после 300s, crash-loop 10 попыток → глобальный degraded + алерт);
  optional — 5 попыток за 300s → degraded + ровно одна ERROR-строка +
  lazy-retry без спама; клампы override: base ≥ 500ms, max ≤ 5min, attempts ≥ 3.
- systemd: ровно один юнит над процессом vesma (systemd никогда не знает о
  детях), таблица MUST директив юнита, полный hardening-блок,
  `MemoryDenyWriteExecute` исключён осознанно, `SystemCallFilter` — Tier B.
- Threat model: полный мини-STRIDE (ассеты, границы, 14 угроз с митигациями,
  каждая закрыта conformance-чеком или помечена операционным контролем).
- Миграция с легаси: таблица «легаси-паттерн → контрактный ответ».
- Артефакты: примеры (юнит user-профиля, 8 структурных строк, status-ответ),
  conformance-чеклист SL-01…SL-18.
