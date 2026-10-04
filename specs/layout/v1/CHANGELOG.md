# Changelog — layout

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в `spec.md` §7 и README репозитория.

## 1.0.0-draft.1 — 2026-10-04

Учредительная форма контракта лэйаута — кодификация ратифицированной формы
учредительного АрхКома VESMA (2026-10-04), без переигрывания решений.

- Профили: user (v1, реализуемый) и system (таблица соответствия XDG 1:1;
  реализация отложена за миграцию прода — строго после 2026-10-16, B0-окно,
  горизонт v2); `/var/log/vesma` в v1 не создаётся.
- User-профиль: таблица MUST из 10 канонических путей с правами (конфиг,
  манифесты, env-секреты, data/cwd, venvs, логи, history, fallback runtime,
  canonical runtime, кэш).
- Канонизации, снимающие плейсхолдеры соседних контрактов: каталог
  манифестов = `~/.config/vesma/components.d/<name>.yaml` (drop-in;
  снимает `~/.config/vesma/manifests/` из component-manifest §2); имя
  сокета = `control.sock` (согласовано с control-socket §3); каноническое
  место env-файлов `env/<name>.env`; целевые пути плейсхолдеров
  `{config_path}/{state_dir}/{runtime_dir}/{venv_bin}`.
- Логи: канон — journald при systemd (`SYSLOG_IDENTIFIER=vesma-<component>`
  от супервайзера, `vesma service logs` = journalctl-фильтр); контейнер /
  ручной режим — files-under-state (`state/logs/<name>/`, ротация
  10 MB × 5); режим ровно один, никаких иных мест логов (закрывает
  инвентарный хаос «логи в 3 местах»).
- venv-дисциплина: один управляемый venv на python-юнит (движок+in-process
  = venv движка; python-ребёнок = `venvs/<name>/`); два компонента на одном
  venv = ошибка; `PYTHONNOUSERSITE=1` инжектируется безусловно; exact-pin
  (`==`) — v1, hash-pinning (`--require-hashes`) — дефолт v1, мандат v2
  (нужен тулинг); только PyPI.
- Кэш: регенерируемое, `0750`, никогда не секреты — enforcement на уровне
  API записи движка.
- Doctor (`vesma doctor --service`): MUST-список DR-01…DR-11 (права,
  venv integrity, user-site, уникальность venv, версия python, venv ≠
  движок, дрейф юнита, живость сокета, коллизии health-портов, свободное
  место, `Storage=persistent`); каждая находка — готовая команда
  исправления, doctor команды не исполняет.
- Threat model: мини-STRIDE по границе «файловая система лэйаута ↔
  супервайзер/загрузчик/doctor» (lax-права env/конфига, user-site утечка,
  tamper venv, секреты в кэше, переполнение диска); остальные границы —
  «trust boundaries: нет» (домены control-socket / service-lifecycle /
  component-manifest).
- Миграция с легаси (главная секция): таблица «легаси-путь → канонический
  путь» — `~/.config/mnemos-mesh/*.yaml`, `ops/*.log`, env-файл с токеном,
  данные `mnemos-prod/`, легаси `venv-5.1.1/venv-5.3.0`; helm-ревизии и
  nohup-лаунчер утилизируются; исполнение миграции — движок (карточка
  `cli-service-management`), спека фиксирует целевые пути.
- Артефакты: примеры (дерево user-профиля с правами, мок-отчёт doctor),
  conformance-чеклист LY-01…LY-14.
