"""
Примеры событий для игры
Это хранилище, которое легко расширять - просто добавляйте новые события в список ALL_EVENTS

ИНСТРУКЦИЯ ПО ДОБАВЛЕНИЮ СОБЫТИЯ:
==================================

1. Импортируйте нужные классы (Event, EventChoice, EventOutcome)
2. Используйте вспомогательные функции для проверок (stat_check, luck_check и т.д.)
3. Создайте выборы с исходами
4. Добавьте событие в список ALL_EVENTS в конце файла

ПРИМЕР ПРОСТОГО СОБЫТИЯ:
========================

forest_encounter = Event(
    event_id='forest_encounter',
    title='Встреча в лесу',
    description='Вы идёте через лес и видите странный предмет на земле.',
    
    choices=[
        EventChoice(
            text='Взять предмет',
            outcomes=[
                EventOutcome(
                    text='Вы нашли золотую монету!',
                    reward_gold=50,
                    reward_exp=10
                ),
            ]
        ),
        EventChoice(
            text='Пройти мимо',
            outcomes=[
                EventOutcome(
                    text='Вы решили не рисковать и пошли дальше.',
                    reward_exp=5
                ),
            ]
        ),
    ],
    location='Лес',
    difficulty='easy'
)

ПРИМЕР СОБЫТИЯ С УСЛОВИЯМИ:
=============================

dragon_encounter = Event(
    event_id='dragon_encounter',
    title='Встреча с драконом',
    description='На вас напал большой дракон!',
    
    choices=[
        EventChoice(
            text='Атаковать (требует атаку >= 20)',
            outcomes=[
                EventOutcome(
                    text='Вы победили дракона!',
                    effects={'hp': -10},  # Урон
                    reward_gold=200,
                    reward_exp=100,
                    condition_check=stat_check('attack', min_value=20)
                ),
            ],
            required_stat='attack',
            required_value=20
        ),
        EventChoice(
            text='Беежать',
            outcomes=[
                EventOutcome(
                    text='Вы убежали от дракона.',
                    reward_exp=5
                ),
            ]
        ),
    ],
    location='Горы',
    difficulty='hard'
)

СИСТЕМА ХАРАКТЕРИСТИК:
======================
Доступные для проверки характеристики:
- attack: Атака
- defense: Защита
- hp: Здоровье (текущее)
- max_hp: Максимальное здоровье
- luck: Удача
- intellect: Интеллект
- fire_resist: Огнестойкость
- cold_resist: Холодостойкость
- gold: Золото
- level: Уровень
"""

from events import (
    Event, EventChoice, EventOutcome, EventManager,
    stat_check, luck_check, combined_check, intellect_check, defense_check, attack_check
)


# ============================================================================
# ПРИМЕРЫ СОБЫТИЙ
# ============================================================================

# Событие 1: Простая встреча в деревне
village_merchant = Event(
    event_id='village_merchant',
    title='Встреча с торговцем',
    description='В деревне вы встречаете странного торговца с загадочным товаром.',
    choices=[
        EventChoice(
            text='Купить таинственное зелье (50 золотом)',
            outcomes=[
                EventOutcome(
                    text='Зелье подарило вам силу! +5 к атаке.',
                    effects={'attack': 5},
                    reward_exp=20
                ),
            ]
        ),
        EventChoice(
            text='Попробовать торговаться',
            outcomes=[
                EventOutcome(
                    text='Торговец согласился - 30 золотом!',
                    effects={'gold': -30, 'attack': 5},
                    reward_exp=25
                ),
                EventOutcome(
                    text='Торговец обиделся и ушёл.',
                    reward_exp=0
                ),
            ]
        ),
        EventChoice(
            text='Уйти без покупок',
            outcomes=[
                EventOutcome(
                    text='Вы спокойно прошли мимо.',
                    reward_exp=5
                ),
            ]
        ),
    ],
    location='Деревня',
    difficulty='easy'
)


# Событие 2: Встреча с бандитами (требует выбора тактики)
bandit_encounter = Event(
    event_id='bandit_encounter',
    title='Встреча с бандитами',
    description='На дороге вас окружили три бандита и требуют золото!',
    choices=[
        EventChoice(
            text='Атаковать',
            outcomes=[
                EventOutcome(
                    text='Вы победили бандитов в честном бою!',
                    effects={'hp': -15},
                    reward_gold=100,
                    reward_exp=75,
                    condition_check=stat_check('attack', min_value=20)
                ),
                EventOutcome(
                    text='Бой был тяжелым, но вы выжили.',
                    effects={'hp': -30},
                    reward_gold=50,
                    reward_exp=40,
                    condition_check=stat_check('attack', min_value=25)
                ),
            ],
            required_stat='attack',
            required_value=20
        ),
        EventChoice(
            text='Использовать интеллект для обмана',
            outcomes=[
                EventOutcome(
                    text='Вы обманули бандитов и убежали!',
                    reward_exp=50,
                    condition_check=intellect_check(10)
                ),
                EventOutcome(
                    text='Попытка обмана не сработала, пришлось платить.',
                    effects={'gold': -50},
                    reward_exp=20,
                    condition_check=intellect_check(10)
                ),
            ],
            required_stat='intellect',
            required_value=10
        ),
        EventChoice(
            text='Заплатить (50 золотом)',
            outcomes=[
                EventOutcome(
                    text='Бандиты довольны и отпустили вас.',
                    effects={'gold': -50},
                    reward_exp=10
                ),
            ]
        ),
        EventChoice(
            text='Попробовать убежать',
            outcomes=[
                EventOutcome(
                    text='Вы успешно убежали!',
                    effects={'hp': -10},
                    reward_exp=5,
                    condition_check=luck_check(0.5)
                ),
                EventOutcome(
                    text='Бандиты поймали вас!',
                    effects={'gold': -70, 'hp': -20},
                    reward_exp=0
                ),
            ]
        ),
    ],
    location='Дорога',
    difficulty='hard',
    can_ignore=False  # Нападение нельзя проигнорировать
)


# Событие 3: Загадка старого волшебника
wizard_riddle = Event(
    event_id='wizard_riddle',
    title='Загадка волшебника',
    description='Старый волшебник спрашивает: "Что может путешествовать по миру, оставаясь в углу?"',
    choices=[
        EventChoice(
            text='Ответить "Марка"',
            outcomes=[
                EventOutcome(
                    text='Волшебник поражён! Вы получили магический артефакт.',
                    effects={'intellect': 3},
                    reward_gold=100,
                    reward_exp=80,
                    condition_check=intellect_check(8)
                ),
            ],
            required_stat='intellect',
            required_value=8
        ),
        EventChoice(
            text='Угадывать наугад',
            outcomes=[
                EventOutcome(
                    text='Удача улыбнулась вам!',
                    reward_gold=50,
                    reward_exp=30,
                    condition_check=luck_check(0.4)
                ),
                EventOutcome(
                    text='Волшебник разочарован вашим ответом.',
                    reward_exp=5
                ),
            ]
        ),
        EventChoice(
            text='Отойти и уйти',
            outcomes=[
                EventOutcome(
                    text='Волшебник дал вам золото за хорошие манеры.',
                    reward_gold=20,
                    reward_exp=10
                ),
            ]
        ),
    ],
    location='Башня волшебника',
    difficulty='easy'
)


# Событие 4: Пещера с сокровищами (опасное событие)
treasure_cave = Event(
    event_id='treasure_cave',
    title='Пещера с сокровищами',
    description='Вы нашли пещеру с блеском золота, но там опасно!',
    choices=[
        EventChoice(
            text='Смело войти',
            outcomes=[
                EventOutcome(
                    text='Вы обошли все ловушки и собрали сокровища!',
                    effects={'hp': -5},
                    reward_gold=300,
                    reward_exp=150,
                    condition_check=stat_check('defense', min_value=15)
                ),
                EventOutcome(
                    text='Вы попались в одну из ловушек!',
                    effects={'hp': -40},
                    reward_gold=150,
                    reward_exp=50,
                    condition_check=stat_check('defense', min_value=15)
                ),
            ],
            required_stat='defense',
            required_value=15
        ),
        EventChoice(
            text='Осторожно исследовать',
            outcomes=[
                EventOutcome(
                    text='Ваша осторожность окупилась! Нашли скрытый проход с ещё большим сокровищем!',
                    effects={'hp': 0},
                    reward_gold=400,
                    reward_exp=200,
                    condition_check=intellect_check(12)
                ),
                EventOutcome(
                    text='Вы нашли немного золота.',
                    reward_gold=100,
                    reward_exp=30
                ),
            ],
            required_stat='intellect',
            required_value=12
        ),
        EventChoice(
            text='Попросить помощи у мага',
            outcomes=[
                EventOutcome(
                    text='Маг помог магией. Вы получили награду!',
                    reward_gold=200,
                    reward_exp=100
                ),
            ],
            required_stat='level',
            required_value=5
        ),
        EventChoice(
            text='Пройти мимо',
            outcomes=[
                EventOutcome(
                    text='Вы решили не рисковать.',
                    reward_exp=10
                ),
            ]
        ),
    ],
    location='Горы',
    difficulty='hard'
)


# Событие 5: Драматичное событие с удачей
lucky_escape = Event(
    event_id='lucky_escape',
    title='Чудесное спасение',
    description='Вы падаете в ущелье! Надежда на чудо...',
    choices=[
        EventChoice(
            text='Попытаться поймать выступ скалы',
            outcomes=[
                EventOutcome(
                    text='Вам удалось! Вы спасены!',
                    effects={'hp': -10},
                    reward_exp=40,
                    condition_check=combined_check('defense', stat_weight=0.6, luck_weight=0.4, base_chance=0.5)
                ),
                EventOutcome(
                    text='Вы упали дальше...',
                    effects={'hp': -60},
                    reward_exp=10
                ),
            ]
        ),
        EventChoice(
            text='Вскрикнуть о помощи',
            outcomes=[
                EventOutcome(
                    text='Кто-то услышал! Вас спасли!',
                    reward_exp=50,
                    condition_check=luck_check(0.6)
                ),
                EventOutcome(
                    text='Никто не услышал...',
                    effects={'hp': -70},
                    reward_exp=5
                ),
            ]
        ),
        EventChoice(
            text='Использовать зелье восстановления',
            outcomes=[
                EventOutcome(
                    text='Зелье сработало! Вы вернулись на верх!',
                    effects={'gold': -30},
                    reward_exp=60
                ),
            ]
        ),
    ],
    location='Ущелье',
    difficulty='deadly',
    can_ignore=False  # Падение в ущелье нельзя проигнорировать
)


# Событие 6: Встреча с древним существом
ancient_being = Event(
    event_id='ancient_being',
    title='Встреча с древним существом',
    description='Вы встретили загадочное древнее существо. Оно смотрит на вас с интересом...',
    choices=[
        EventChoice(
            text='Говорить с уважением',
            outcomes=[
                EventOutcome(
                    text='Существо одобрило вашу мудрость. Оно научило вас древней магии!',
                    effects={'intellect': 5, 'fire_resist': 10},
                    reward_exp=150,
                    condition_check=intellect_check(10)
                ),
            ],
            required_stat='intellect',
            required_value=10
        ),
        EventChoice(
            text='Атаковать',
            outcomes=[
                EventOutcome(
                    text='Существо было слишком сильным. Вы еле выжили.',
                    effects={'hp': -80},
                    reward_exp=50
                ),
            ]
        ),
        EventChoice(
            text='Поклониться и просить благословения',
            outcomes=[
                EventOutcome(
                    text='Существо благословило вас!',
                    effects={'hp': 20, 'attack': 3, 'defense': 3},
                    reward_exp=100
                ),
            ]
        ),
        EventChoice(
            text='Бежать в панике',
            outcomes=[
                EventOutcome(
                    text='Вы убежали, но остались в страхе. Ничего ценного.',
                    reward_exp=5
                ),
            ]
        ),
    ],
    location='Древний храм',
    difficulty='deadly'
)


# Событие 7: Помощь путнику
help_traveler = Event(
    event_id='help_traveler',
    title='Помощь путнику',
    description='Раненый путник лежит на дороге. Он просит о помощи.',
    choices=[
        EventChoice(
            text='Помочь ему полностью',
            outcomes=[
                EventOutcome(
                    text='Путник благодарен. Он дал вам редкое зелье!',
                    effects={'gold': -20},
                    reward_exp=80,
                    reward_gold=30
                ),
            ]
        ),
        EventChoice(
            text='Помочь, но не тратить зелье',
            outcomes=[
                EventOutcome(
                    text='Вы перевязали его раны собственноручно.',
                    effects={'defense': 2},
                    reward_exp=60,
                    condition_check=stat_check('defense', min_value=10)
                ),
                EventOutcome(
                    text='Ваша помощь была не достаточной.',
                    reward_exp=20
                ),
            ],
            required_stat='defense',
            required_value=10
        ),
        EventChoice(
            text='Отобрать его золото',
            outcomes=[
                EventOutcome(
                    text='Путник был слаб. Вы получили золото.',
                    effects={'gold': 50},
                    reward_exp=-10  # Штраф за жестокость (можно убрать)
                ),
            ]
        ),
        EventChoice(
            text='Пройти мимо',
            outcomes=[
                EventOutcome(
                    text='Вы ушли, но помните его взгляд...',
                    reward_exp=0
                ),
            ]
        ),
    ],
    location='Дорога',
    difficulty='easy'
)


# ============================================================================
# РЕГИСТРАЦИЯ ВСЕХ СОБЫТИЙ
# ============================================================================

# Список всех событий с их весами (вероятность появления)
# Большой вес = чаще появляется
ALL_EVENTS = [
    (village_merchant, 2),          # 2x вес - появляется чаще
    (bandit_encounter, 2),
    (wizard_riddle, 1),
    (treasure_cave, 1),
    (lucky_escape, 1),
    (ancient_being, 1),
    (help_traveler, 2),
]


def create_event_manager() -> 'EventManager':
    """Создать и инициализировать менеджер событий"""
    manager = EventManager()
    manager.register_events(ALL_EVENTS)
    return manager


# ============================================================================
# БЫСТРАЯ ИНСТРУКЦИЯ ДЛЯ ДОБАВЛЕНИЯ НОВЫХ СОБЫТИЙ
# ============================================================================

"""
ДЛЯ ДОБАВЛЕНИЯ НОВОГО СОБЫТИЯ:

1. Создайте событие в этом файле, используя класс Event:

my_event = Event(
    event_id='unique_id',  # Уникальный идентификатор
    title='Название события',
    description='Описание события',
    choices=[
        EventChoice(
            text='Вариант 1',
            outcomes=[
                EventOutcome(
                    text='Результат 1',
                    reward_gold=50,
                    reward_exp=25
                ),
            ]
        ),
        EventChoice(
            text='Вариант 2 (требует характеристику)',
            outcomes=[
                EventOutcome(
                    text='Результат 2',
                    effects={'attack': 5},
                    reward_gold=100,
                    condition_check=stat_check('attack', min_value=20)
                ),
            ],
            required_stat='attack',
            required_value=20
        ),
    ],
    location='Место события',
    difficulty='normal'  # easy, normal, hard, deadly
)

2. Добавьте событие в список ALL_EVENTS в конце файла:

ALL_EVENTS = [
    ...
    (my_event, 1),  # 1 - вес (вероятность появления)
    ...
]

ГОТОВО! Ваше событие теперь появляется в игре.

ДОСТУПНЫЕ ФУНКЦИИ ПРОВЕРОК:
- stat_check('stat_name', min_value=X)
- luck_check(chance=0.5)
- intellect_check(min_intellect=X)
- defense_check(min_defense=X)
- attack_check(min_attack=X)
- combined_check('stat_name', stat_weight=0.7, luck_weight=0.3, base_chance=0.5)
"""
