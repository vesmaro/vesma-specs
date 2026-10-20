# Changelog — layout

Формат версий: SemVer; статус контракта и дисциплина ломающих изменений —
в `spec.md` §7 и README репозитория.

## 2.0.0-draft.1 — 2026-10-21

Dual-profile лэйаут — кодификация вердикта АрхКома VESMA 2026-10-21
([ADR-0045](https://github.com/vesmaro/vesma/blob/main/docs/project/adr/0045-dual-profile-fhs-layout.md)
в репо движка, волна 1 — документы) с дополнением владельца о
самодостаточности user-профиля, вложенным в вердикт до публикации.
Статус draft до первой конформной реализации (волновой план ADR-0045).

- **Dual-profile**: user — канон/дефолт, system — FHS opt-in; выбор
  профиля — продуктовое решение первого класса при установке;
  `sudo vesma service install --system` — канонический установщик
  system-профиля.
- **User-профиль v2 — самодостаточный `~/.vesma/**`** (прецеденты
  `~/.vscode`, `~/.nvm`): venv движка `~/.vesma/venv/`, venvs
  `~/.vesma/venvs/<name>/`, кэш `~/.vesma/cache/<name>/`, данные
  `~/.vesma/components/<name>/`, `components.d/`, `env.d/<name>.env`,
  `history/`, fallback `run/`; store-дом движка (vesma.db, data/, vault/,
  config.yaml) не переигрывается. Явный список исключений, мандатированных
  ОС: systemd user unit dir (канон-хранение `~/.vesma/systemd/user/` +
  линковка при установке), `${XDG_RUNTIME_DIR}/vesma/` (сокеты),
  shell rc-строки (external), journald.
- **Legacy-генерация v1.5** (XDG-россыпь v1) нормативна для существующих
  установок: резолв по метке генерации, zero-regression, pin-тесты обеих
  генераций; новые user-инсталляции — только v2.
- **System-профиль (FHS)**: `/etc/vesma` (`config.yaml` + `components.d/`
  `0640 root:vesma`, conffile-зона; `env.d/` `0600` — doctor FAIL-гейт),
  данные `/var/lib/vesma` (vesma:vesma 0750, БД 0600, install-state.yaml),
  venv `/usr/lib/vesma/venv|venvs/<name>` (root-owned, symlink-ревизии с
  атомарным swap), статика `/usr/share/vesma`, кэш `/var/cache/vesma`
  0750, логи — journald primary + `/var/log/vesma` opt-in, IPC
  `/run/vesma` (`RuntimeDirectoryMode=0750`); sysusers.d создаёт
  vesma:vesma.
- **Юниты user/system сосуществуют без префиксов** (`vesma.service` в
  своих областях systemd); IPC производен профиля.
- **Экосистемная таблица размещения**: движок, MCP-сервер/entrypoint,
  агенты-дети, board, metrics, mesh, таймеры — единая структура обоих
  профилей; mcp.json чужих харнесов и shell rc — external surfaces.
- **Один декларативный FHS-манифест** (роль, пути обоих профилей, права,
  владельцы, флаги) — источник истины для инсталлятора, сборки
  контейнера и будущих deb/rpm; резолвер — единственный читатель путей в
  коде; override базы (например `/opt/vesma`) — MAY, с валидацией.
- **Механика system-профиля**: идемпотентный install, sysusers-аккаунт,
  install-state → exact-inverse uninstall, mode-aware update через
  symlink-swap, venv материализует `uv venv` + wheel той же сборки
  (никогда pip-as-root).
- **Doctor v2**: DR-14 (изоляция data-root профилей — совмещение =
  FAIL/«ERROR»), DR-15 (права system + env.d FAIL-гейт), DR-16
  (venv-ревизии), DR-17 (install-state ↔ ФС), DR-18 (дрейф юнитов),
  DR-19 (генерация лэйаута, advisory консолидации).
- **Миграция**: консолидация user v1.5 → v2 — явный шаг без ломки
  (кандидат-носитель — update apply / service install); миграция прода в
  system — НЕ сейчас, `migrate-store --target=system` зарезервирован,
  precondition — round-trip soak.
- **SemVer 2.0.0** (MAJOR): перерисовка user-таблицы, `vesma.yaml` →
  `config.yaml` (выравнивание с каноном движка), `env/` → `env.d/`,
  system-таблица v1 §3.3 заменена (venvs → /usr/lib, `/var/log/vesma`
  opt-in, vesma-oper не вводится); непрерывность deployed-установок —
  через метку генерации.
- **Conformance**: гейт = LY-01…LY-14 (перецелены на §3.2) + LY-15/LY-16
  (генерации) + SY-01…SY-12 (system); LY-13 v1 superseded серией SY.
- **Артефакты**: примеры (дерево user v2, дерево system, FHS-манифест).
