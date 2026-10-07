# Руководство по системе событий

Краткое и аккуратное руководство по созданию событий для проекта. Примеры
готовы к копированию и вставке в модуль событий (обычно `events_data.py`).

## Быстрый старт — минимальный шаблон

Скопируйте этот блок в файл событий и добавьте объект в `ALL_EVENTS`.

```python
from events import Event, EventChoice, EventOutcome

my_simple_event = Event(
    event_id='my_simple_event',
    title='Моё простое событие',
    description='Вы наткнулись на интересный предмет на дороге.',
    choices=[
        EventChoice(
            text='Поднять предмет',
            outcomes=[EventOutcome(text='Вы получили немного золота.',
                                    reward_gold=50, reward_exp=5)]
        ),
        EventChoice(
            text='Оставить и уйти',
            outcomes=[EventOutcome(text='Вы ушли дальше без изменений.',
                                    reward_exp=1)]
        )
    ],
    location='Дорога',
    difficulty='easy'
)
```

Добавление в `ALL_EVENTS`:

```python
ALL_EVENTS = [
    (my_simple_event, 1),  # 1 = вес (вероятность появления)
]
```

## Типы событий — примеры

1. Простое событие (всегда одинаковый результат):

```python
simple_event = Event(
    event_id='simple_event',
    title='Сундук на дороге',
    description='Вы нашли сундук с золотом.',
    choices=[
        EventChoice(
            text='Взять золото',
            outcomes=[EventOutcome(text='Вы получили 100 золота!',
                                    reward_gold=100, reward_exp=10)]
        ),
    ],
    location='Дорога',
    difficulty='easy'
)
```

1. Событие со случайностью (несколько исходов для одного выбора):

```python
random_event = Event(
    event_id='random_event',
    title='Странник с предложением',
    description='Странник предлагает сделку.',
    choices=[
        EventChoice(
            text='Согласиться',
            outcomes=[
                EventOutcome(text='Вы получили редкое зелье!',
                             reward_gold=50, reward_exp=30),
                EventOutcome(text='Странник обманул вас!',
                             effects={'gold': -30}, reward_exp=10),
            ]
        ),
    ],
    location='Лес',
    difficulty='normal'
)
```

1. Событие с проверкой характеристики (кнопка доступна только при
    требуемой характеристике):

```python
stat_event = Event(
    event_id='stat_event',
    title='Вызов для сильных',
    description='Путь преграждает горгулья',
    choices=[
        EventChoice(
            text='Атаковать (требует attack >= 25)',
            outcomes=[EventOutcome(text='Вы победили!',
                                    reward_gold=100, reward_exp=30)],
            required_stat='attack',
            required_value=25
        ),
        EventChoice(
            text='Отступить',
            outcomes=[EventOutcome(text='Вы отошли в безопасности.',
                                    reward_exp=5)]
        )
    ],
    location='Развалины',
    difficulty='normal'
)
```

## Доступные характеристики

- `attack`, `defense`, `hp`, `max_hp`, `luck`, `intellect`, `gold`,
  `level`, `fire_resist`, `cold_resist`

## Функции проверок (шаблоны)

Примеры вспомогательных проверок (реализация — в `events.py`):

```python
# Атака >= value
stat_check('attack', min_value=20)

# Шанс удачи (0..1)
luck_check(0.5)

# Комбинация характеристики + удача
combined_check('defense', stat_weight=0.6, luck_weight=0.4,
               base_chance=0.5)
```

## Эффекты и исходы

В `EventOutcome` можно указывать:

- `text` — текст результата
- `reward_gold`, `reward_exp` — награды
- `effects` — словарь изменений характеристик, например
  `{'hp': -10, 'attack': 1}`

```python
EventOutcome(
    text='Вы получили силу!',
    effects={'attack': 5, 'hp': -10},
    reward_gold=100,
    reward_exp=50
)
```

## Советы по тестированию

- Для быстрой проверки увеличьте вес события в `ALL_EVENTS`.
- Вставляйте события в `events_data.py` (или куда у вас хранятся события)
  и перезапускайте игру.
- Используйте простые значения эффектов, чтобы увидеть поведение
  (hp, gold, exp).

## Где смотреть реализацию

Детали по условиям, функциям проверок и применению эффектов находятся в
исходном коде: `events.py`.

---

Если нужно, могу прогнать `markdownlint` и исправить оставшиеся
предупреждения или адаптировать стиль под ваш линтер.
