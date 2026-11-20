class CharacterClass:
    """Описание класса персонажа"""

    def __init__(self, id_, name, description, hp_bonus=0, attack_bonus=0, defense_bonus=0,
                 fire_resist_bonus=0, cold_resist_bonus=0, luck_bonus=0, intellect_bonus=0):
        self.id = id_
        self.name = name
        self.description = description
        self.hp_bonus = hp_bonus
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        # Новые бонусы к характеристикам
        self.fire_resist_bonus = fire_resist_bonus
        self.cold_resist_bonus = cold_resist_bonus
        self.luck_bonus = luck_bonus
        self.intellect_bonus = intellect_bonus
        # Активная способность класса: (id, name, description, cooldown_turns)
        self.ability = None


# Предопределённые классы
CLASSES = {
    'warrior': CharacterClass(
        'warrior',
        'Воин',
        'Хороший в ближнем бою. Повышенное здоровье и защита.',
        hp_bonus=30,
        attack_bonus=5,
        defense_bonus=3,
        fire_resist_bonus=5,
        cold_resist_bonus=5,
    ),
    'mage': CharacterClass(
        'mage',
        'Маг',
        'Использует магию. Высокая сила атаки, но меньше защиты.',
        hp_bonus=10,
        attack_bonus=8,
        defense_bonus=-1,
        intellect_bonus=2,
    ),
    'rogue': CharacterClass(
        'rogue',
        'Разбойник',
        'Быстрый и ловкий. Сбалансированные бонусы.',
        hp_bonus=15,
        attack_bonus=4,
        defense_bonus=3,
    ),
    'lucky': CharacterClass(
        'lucky',
        'Удачливый',
        'Обладает природной удачей — повышенный шанс на лут и золото.',
        luck_bonus=5,
    ),
}

# Назначаем простые способности
CLASSES['warrior'].ability = ('warrior_rage', 'Удар ярости', 'Мощный удар: игнорирует часть защиты врага.', 3)
CLASSES['mage'].ability = ('mage_lightning', 'Молния', 'Наносит сильный урон и оглушает врага на 1 ход.', 4)
CLASSES['rogue'].ability = ('rogue_evade', 'Уклонение', 'Полное уклонение от следующей атаки врага.', 3)


def get_class(class_id):
    """Вернуть класс по id или None"""
    return CLASSES.get(class_id)
