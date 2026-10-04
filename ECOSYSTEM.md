# Карта экосистемы VESMA

Кто есть кто в экосистеме: тир критичности, способ исполнения, реализуемый
контракт и дом кода. Код компонентов живёт в своих репозиториях; здесь —
только контракты и их статусы. Компонент появляется в этой карте манифестом
(приём по контракту — [ADR-0001](adrs/0001-repo-structure-and-governance.md);
усыновление компонентов — фаза 4 [roadmap](docs/roadmap.md)).

Терминология — [GLOSSARY.md](GLOSSARY.md).

| Компонент | Тип | Тир | Реализуемый контракт | Статус | Репа |
|---|---|---|---|---|---|
| vesma server | in-process | core | component-manifest, service-lifecycle, control-socket (реализует как супервайзер) | супервайзер движка; реализация контрактов — фаза 3 | [vesma](https://github.com/vesmaro/vesma) |
| vesma board | in-process (python) | optional | component-manifest | манифест не заявлен (фаза 4) | [vesma](https://github.com/vesmaro/vesma) |
| vesma mesh | child-process (Go) | optional | component-manifest, service-lifecycle | манифест не заявлен (фаза 4) | [vesma-mesh](https://github.com/vesmaro/vesma-mesh) |
| vesma eyes | child-process (Node) | optional | component-manifest, service-lifecycle | манифест не заявлен (фаза 4) | [vesma-eyes](https://github.com/vesmaro/vesma-eyes) |
| vesma agent | child-process (Go) | optional | component-manifest, service-lifecycle | манифест не заявлен (фаза 4) | [vesma-agent](https://github.com/vesmaro/vesma-agent) |
| vesma cortex-metrics | child-process (python / скрипт) | optional | component-manifest, service-lifecycle | манифест не заявлен (фаза 4) | [vesma-cortex](https://github.com/vesmaro/vesma-cortex) |

Примечания:

- `vesma board` и `vesma cortex-metrics` живут внутри реп `vesma` и
  `vesma-cortex` соответственно; отдельных репозиториев у них нет.
- Контракты `component-manifest`, `service-lifecycle`, `control-socket`,
  `layout` создаются в фазе 1 [roadmap](docs/roadmap.md); до тех пор
  «реализуемый контракт» — план, а не обязательство.
- Статус «манифест не заявлен» снимается появлением манифеста компонента и
  зелёным MUST-прогоном его conformance-сьюта (гейт интеграции).

## Слой specs vs canon

Правило границы: **«КАК соединяются → specs; ЧТО обещано до измерения →
canon»**. Здесь живут живущие интеграционные контракты, манифесты, примеры и
конформанс; запечатанные обещания (препреги, аддендумы, вердикты
экспериментов, протоколы калибровок) — в append-only
[vesma-canon](https://github.com/vesmaro/vesma-canon). История canon не
переписывается; перенос living-контрактов сюда — с указателями (фаза 2).

## Ссылки

- [ADR-0001: структура репозитория и governance](adrs/0001-repo-structure-and-governance.md) — откуда взяты правила карты.
- [docs/roadmap.md](docs/roadmap.md) — фазы появления контрактов и усыновления компонентов.
- [docs/concept.md](docs/concept.md) — концепция спек-слоя.
