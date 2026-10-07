from locales import t
from skills import get_skill


class Item:
    """Base item class"""
    
    def __init__(self, name, description, price):
        self.name = name
        self.description = description
        self.price = price
    
    def use(self, player):
        """Использовать предмет"""
        pass


class SkillBook(Item):
    """Книга, которая даёт уровень навыка при использовании.

    Если навык не изучен — изучает (уровень 1). Если изучен и не на макс уровне — повышает на 1.
    """
    def __init__(self, skill_id, name, description, price, levels=1):
        super().__init__(name, description, price)
        self.skill_id = skill_id
        self.levels = levels

    def use(self, player):
        meta = get_skill(self.skill_id)
        if not meta:
            print(t('unknown_skill'))
            return False

        # If not learned — learn
        if self.skill_id not in getattr(player, 'skills', {}):
            player.skills[self.skill_id] = 1
            # register ability entry
            player.abilities[self.skill_id] = (meta['name'], meta['description'], meta.get('base_cooldown', 3))
            player.ability_cooldowns[self.skill_id] = 0
            print(t('learned_skill', name=meta['name']))
            return True

        # Already learned — try to upgrade by levels
        cur = player.skills.get(self.skill_id, 0)
        maxl = meta.get('max_level', 1)
        if cur >= maxl:
            print(t('skill_at_max', name=meta['name']))
            return False

        # increase by one (or up to levels)
        new_level = min(maxl, cur + self.levels)
        player.skills[self.skill_id] = new_level
        print(t('skill_upgraded', name=meta['name'], level=new_level))
        return True


class Potion(Item):
    """Healing potion"""

    def __init__(self, name, heal_amount, price):
        super().__init__(name, t('potion_description', heal=heal_amount), price)
        self.heal_amount = heal_amount
    
    def use(self, player):
        """Использовать зелье"""
        if player.hp >= player.max_hp:
            print(t('already_max_hp'))
            return False
        
        player.heal(self.heal_amount)
        print(t('used_potion', item=self.name, hp=self.heal_amount, hp_now=player.hp, max_hp=player.max_hp))
        return True


class Weapon(Item):
    """Weapon"""

    def __init__(self, name, attack_bonus, price, quality='wooden', level=1, weapon_type='sword', requirements=None):
        super().__init__(name, t('weapon_description', val=attack_bonus), price)
        self.attack_bonus = attack_bonus
        self.quality = quality
        self.level = level
        self.weapon_type = weapon_type  # 'sword', 'spear', 'bow', 'staff', etc.
        self.requirements = requirements or {}  # {'attack': 10, 'intellect': 5, ...}
    
    def use(self, player):
        """Экипировать оружие"""
        if player.weapon:
            print(t('removed_item', name=player.weapon.name))
        player.weapon = self
        print(t('equipped_item', name=self.name, stat=player.get_total_attack()))
        return False  # Не удалять из инвентаря
    
    def get_effective_bonus(self, player):
        """Получить эффективный бонус атаки с учётом требований"""
        if not self.requirements:
            return self.attack_bonus
        
        bonus = self.attack_bonus
        scaling_multiplier = 1.0
        
        # Проверяем каждое требование и применяем бонус, если требование выполнено
        for stat, requirement in self.requirements.items():
            player_stat_value = getattr(player, stat, 0)
            if player_stat_value >= requirement:
                # За каждый пункт выше требования даём 2% бонуса к основному бонусу
                excess = player_stat_value - requirement
                scaling_multiplier += (excess * 0.02)
        
        return int(bonus * scaling_multiplier)


class Armor(Item):
    """Armor"""

    def __init__(self, name, defense_bonus, price, quality='wooden', level=1, armor_type='leather', requirements=None):
        super().__init__(name, t('armor_description', val=defense_bonus), price)
        self.defense_bonus = defense_bonus
        self.quality = quality
        self.level = level
        self.armor_type = armor_type  # 'leather', 'iron', 'cloth', 'robe', etc.
        self.requirements = requirements or {}  # {'attack': 10, 'intellect': 5, ...}
    
    def use(self, player):
        """Экипировать броню"""
        if player.armor:
            print(t('removed_item', name=player.armor.name))
        player.armor = self
        print(t('equipped_item_armor', name=self.name, stat=player.get_total_defense()))
        return False  # Не удалять из инвентаря
    
    def get_effective_bonus(self, player):
        """Получить эффективный бонус защиты с учётом требований"""
        if not self.requirements:
            return self.defense_bonus
        
        bonus = self.defense_bonus
        scaling_multiplier = 1.0
        
        # Для каждого требования даём дополнительный бонус, если он выполнен
        for stat, requirement in self.requirements.items():
            player_stat_value = getattr(player, stat, 0)
            if player_stat_value >= requirement:
                excess = player_stat_value - requirement
                # За каждый пункт выше требования даём 3% бонуса к защите (больше чем для оружия)
                scaling_multiplier += (excess * 0.03)
        
        return int(bonus * scaling_multiplier)


class Artifact(Item):
    """Artifact with bonus slots (each slot has a stat bonus or combat mechanic boost)"""

    def __init__(self, name, description, price, effect_id=None, bonus_slots=None):
        super().__init__(name, description, price)
        self.effect_id = effect_id  # Legacy support
        self.bonus_slots = bonus_slots or []  # List of {'type': 'stat', 'stat': 'attack', 'value': 15}

    def use(self, player):
        """Экипировать артефакт"""
        if getattr(player, 'artifact', None):
            try:
                player.artifact.equipped = False
            except Exception:
                pass
            print(t('artifact_unequipped', name=player.artifact.name))
        player.artifact = self
        try:
            self.equipped = True
        except Exception:
            pass
        print(t('artifact_equipped', name=self.name))
        return False  # Не удалять из инвентаря
    
    def get_slot_description(self):
        """Описание всех слотов артефакта"""
        if not self.bonus_slots:
            return "Нет бонусов"
        
        descriptions = []
        for slot in self.bonus_slots:
            if slot['type'] == 'stat':
                stat_name = slot['stat']
                value = slot['value']
                descriptions.append(f"+{value} {stat_name}")
            elif slot['type'] == 'crit':
                value = slot['value']
                descriptions.append(f"+{value}% крит")
            elif slot['type'] == 'evade':
                value = slot['value']
                descriptions.append(f"+{value}% уклонение")
        
        return ", ".join(descriptions)
    
    def apply_bonuses(self, player):
        """Применить все бонусы артефакта к игроку"""
        for slot in self.bonus_slots:
            if slot['type'] == 'stat':
                stat_name = slot['stat']
                value = slot['value']
                current = getattr(player, stat_name, 0)
                setattr(player, stat_name, current + value)
            elif slot['type'] == 'crit':
                # Крит бонус уже учитывается через get_crit_chance
                pass
            elif slot['type'] == 'evade':
                # Уклонение бонус уже учитывается через get_evade_chance
                pass
    
    def get_crit_bonus(self):
        """Получить бонус крита в процентах"""
        bonus = 0
        for slot in self.bonus_slots:
            if slot['type'] == 'crit':
                bonus += slot['value']
        return bonus / 100.0  # Вернуть как десятичное число
    
    def get_evade_bonus(self):
        """Получить бонус уклонения в процентах"""
        bonus = 0
        for slot in self.bonus_slots:
            if slot['type'] == 'evade':
                bonus += slot['value']
        return bonus / 100.0  # Вернуть как десятичное число


# Предопределённые предметы
ITEMS_DATABASE = {
    # Зелья
    'small_potion': Potion(t('small_potion_name'), 30, 20),
    'medium_potion': Potion(t('medium_potion_name'), 60, 40),
    'large_potion': Potion(t('large_potion_name'), 100, 70),
    
    # Оружие для Воинов (на СИЛУ/ATTACK)
    'wooden_sword': Weapon(t('sword_name'), 5, 50),
    'iron_sword': Weapon(t('sword_name'), 12, 150),
    'steel_sword': Weapon(t('sword_name'), 20, 300),
    'short_sword': Weapon('Короткий меч', 8, 100),
    'battle_axe': Weapon('Боевой топор', 15, 250),
    'longsword': Weapon('Длинный меч', 18, 280),
    'legendary_sword': Weapon(t('sword_name'), 35, 1000),
    
    # Оружие для Рогов (на ЛОВКОСТЬ/LUCK)
    'wooden_bow': Weapon('Деревянный лук', 7, 80),
    'iron_bow': Weapon('Железный лук', 14, 200),
    'steel_bow': Weapon('Стальной лук', 22, 380),
    
    # Оружие для Магов (на ИНТЕЛЛЕКТ)
    'wooden_staff': Weapon('Деревянный посох', 6, 90),
    'crystal_staff': Weapon('Кристальный посох', 13, 210),
    'arcane_staff': Weapon('Магический посох', 21, 350),
    'ancient_staff': Weapon('Древний посох', 28, 600),
    
    # Броня для Воинов (на СИЛУ/ATTACK)
    'leather_armor': Armor(t('armor_name'), 3, 60),
    'iron_armor': Armor(t('armor_name'), 8, 180),
    'chainmail': Armor('Кольчуга', 11, 220),
    'steel_armor': Armor(t('armor_name'), 15, 350),
    'plate_armor': Armor('Пластинчатая броня', 19, 420),
    
    # Броня для Магов (на ИНТЕЛЛЕКТ)
    'cloth_armor': Armor('Тканевая броня', 4, 70),
    'silk_robe': Armor('Шёлковая роба', 7, 140),
    'mystic_robe': Armor('Мистическая роба', 12, 240),
    'enchanted_robe': Armor('Зачарованная роба', 16, 380),
    
    # Броня для Рогов (на ЛОВКОСТЬ/LUCK)
    'leather_armor_light': Armor('Лёгкая кожаная броня', 5, 90),
    'reinforced_leather': Armor('Укреплённая кожа', 10, 200),
    'shadow_leather': Armor('Теневая кожа', 14, 280),
    'legendary_armor': Armor(t('armor_name'), 25, 1200),
    
    # Материалы
    'upgrade_stone': Item(t('upgrade_stone_name'), t('upgrade_stone_desc'), 30),
    # Skill books
    'book_warrior_rage': SkillBook('warrior_rage', t('book_warrior_rage_name'), t('book_warrior_rage_desc'), 150),
    'book_mage_lightning': SkillBook('mage_lightning', t('book_mage_lightning_name'), t('book_mage_lightning_desc'), 160),
    'book_rogue_evade': SkillBook('rogue_evade', t('book_rogue_evade_name'), t('book_rogue_evade_desc'), 120),
    # Legendary artifacts
    'artifact_blood_thorn': Artifact(t('artifact_blood_thorn_name'), t('artifact_blood_thorn_desc'), 2500, 'blood_thorn'),
    'artifact_storm_lens': Artifact(t('artifact_storm_lens_name'), t('artifact_storm_lens_desc'), 2500, 'storm_lens'),
    'artifact_greed_idol': Artifact(t('artifact_greed_idol_name'), t('artifact_greed_idol_desc'), 2500, 'greed_idol'),
    'artifact_aegis_sigil': Artifact(t('artifact_aegis_sigil_name'), t('artifact_aegis_sigil_desc'), 2500, 'aegis_sigil'),
    'artifact_chrono_shard': Artifact(t('artifact_chrono_shard_name'), t('artifact_chrono_shard_desc'), 2500, 'chrono_shard'),
}

ARTIFACT_IDS = [
    'artifact_blood_thorn',
    'artifact_storm_lens',
    'artifact_greed_idol',
    'artifact_aegis_sigil',
    'artifact_chrono_shard',
]


# --- Типы снаряжения и требования ---
# Требования по типам экипировки
EQUIPMENT_REQUIREMENTS = {
    # === ОРУЖИЕ ===
    # Мечи (на СИЛУ/ATTACK - для Воинов)
    'weapon.sword': {
        'attack': 8,
    },
    
    # Боевые топоры (на СИЛУ/ATTACK - для Воинов)
    'weapon.axe': {
        'attack': 10,
    },
    
    # Луки (на ЛОВКОСТЬ/LUCK - для Рогов)
    'weapon.bow': {
        'luck': 7,
    },
    
    # Посохи (на ИНТЕЛЛЕКТ - для Магов)
    'weapon.staff': {
        'intellect': 10,
    },
    
    # === БРОНЯ ===
    # Тяжёлая броня для Воинов (на СИЛУ/ATTACK)
    'armor.iron_heavy': {
        'attack': 10,
    },
    'armor.plate': {
        'attack': 12,
    },
    
    # Лёгкая броня для Магов (на ИНТЕЛЛЕКТ)
    'armor.cloth': {
        'intellect': 8,
    },
    'armor.robe': {
        'intellect': 12,
    },
    
    # Кожаная броня для Рогов (на ЛОВКОСТЬ/LUCK)
    'armor.leather': {
        'luck': 6,
    },
    'armor.leather_heavy': {
        'luck': 10,
    },
}

# Типизация оружия
WEAPON_TYPES = {
    # Мечи (на СИЛУ)
    'wooden_sword': 'sword',
    'short_sword': 'sword',
    'iron_sword': 'sword',
    'steel_sword': 'sword',
    'longsword': 'sword',
    'legendary_sword': 'staff',  # Легендарный меч магический
    
    # Боевые топоры (на СИЛУ)
    'battle_axe': 'axe',
    
    # Луки (на ЛОВКОСТЬ)
    'wooden_bow': 'bow',
    'iron_bow': 'bow',
    'steel_bow': 'bow',
    
    # Посохи (на ИНТЕЛЛЕКТ)
    'wooden_staff': 'staff',
    'crystal_staff': 'staff',
    'arcane_staff': 'staff',
    'ancient_staff': 'staff',
}

# Типизация брони
ARMOR_TYPES = {
    # Броня для Воинов (на СИЛУ)
    'leather_armor': 'iron_heavy',
    'chainmail': 'iron_heavy',
    'iron_armor': 'iron_heavy',
    'steel_armor': 'plate',
    'plate_armor': 'plate',
    
    # Броня для Магов (на ИНТЕЛЛЕКТ)
    'cloth_armor': 'cloth',
    'silk_robe': 'robe',
    'mystic_robe': 'robe',
    'enchanted_robe': 'robe',
    
    # Броня для Рогов (на ЛОВКОСТЬ)
    'leather_armor_light': 'leather',
    'reinforced_leather': 'leather_heavy',
    'shadow_leather': 'leather_heavy',
    'legendary_armor': 'robe',  # Легендарная броня магическая
}


def get_requirements_for_equipment(item_id):
    """Получить требования для предмета экипировки"""
    # Определяем тип, глядя на item_id
    armor_type = ARMOR_TYPES.get(item_id)
    weapon_type = WEAPON_TYPES.get(item_id)
    
    if armor_type:
        req_key = f'armor.{armor_type}'
    elif weapon_type:
        req_key = f'weapon.{weapon_type}'
    else:
        return {}
    
    return EQUIPMENT_REQUIREMENTS.get(req_key, {})


# Качества экипировки ---
QUALITY_ORDER = ['wooden', 'rusty', 'iron', 'silver', 'luxury', 'dragon']
QUALITY_DISPLAY = {
    'wooden': t('quality_wooden'),
    'rusty': t('quality_rusty'),
    'iron': t('quality_iron'),
    'silver': t('quality_silver'),
    'luxury': t('quality_luxury'),
    'dragon': t('quality_dragon'),
}
QUALITY_MULTIPLIER = {
    'wooden': 0.0,
    'rusty': 0.05,
    'iron': 0.15,
    'silver': 0.30,
    'luxury': 0.5,
    'dragon': 0.8,
}

# Иконки для качеств
QUALITY_ICONS = {
    'wooden': '▢',
    'rusty': '▫',
    'iron': '◆',
    'silver': '◇',
    'luxury': '✦',
    'dragon': '✶',
}

# RECIPES removed — crafting feature disabled per user request.
# If crafting is re-introduced later, recipes can be restored here.


def choose_quality_for_rotation(rotation=0):
    """Выбрать качество в зависимости от ротации."""
    # Более плавное усиление шансов верхних качеств с ростом ротации.
    # Начальные веса (для rotation=0)
    base_weights = [50.0, 30.0, 10.0, 7.0, 2.0, 1.0]
    weights = []
    # формируем веса так, чтобы верхним качествам давать экспоненциальный рост с rotation
    for idx, w in enumerate(base_weights):
        # фактор: небольшая экспонента для верхних индексов
        factor = 1.0 + (rotation * (idx / (len(base_weights) - 1))) * 0.25
        weights.append(max(0.1, w * factor))

    import random
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0.0
    for i, w in enumerate(weights):
        if upto + w >= r:
            return QUALITY_ORDER[i]
        upto += w
    return QUALITY_ORDER[-1]


def generate_equipment(item_id, rotation=0, player_level=1, quality=None, item_level=1, force_quality=False):
    """Сгенерировать экипировку с учетом качества, уровня предмета и ротации."""
    base = ITEMS_DATABASE.get(item_id)
    if not base:
        return None

    if not quality:
        quality = choose_quality_for_rotation(rotation)

    # Запретить генерировать качество ниже, чем качество базового предмета,
    # если оно явно указано в item_id (например, 'iron_sword' не должно стать 'wooden').
    # Но если force_quality=True (для админ-панели), пропускаем эту проверку
    if not force_quality:
        base_min_index = 0
        for idx, q in enumerate(QUALITY_ORDER):
            if q in item_id:
                base_min_index = idx
                break
        else:
            if 'legend' in item_id or 'legendary' in item_id:
                base_min_index = len(QUALITY_ORDER) - 1

        try:
            sel_idx = QUALITY_ORDER.index(quality)
        except ValueError:
            sel_idx = 0
        if sel_idx < base_min_index:
            quality = QUALITY_ORDER[base_min_index]

    # Получаем требования для этого предмета
    requirements = get_requirements_for_equipment(item_id)

    # Случай: Оружие
    if isinstance(base, Weapon):
        base_bonus = base.attack_bonus
        extra = int(base_bonus * QUALITY_MULTIPLIER.get(quality, 0) + item_level * 1 + rotation * 2 + player_level // 2)
        weapon_type = WEAPON_TYPES.get(item_id, 'sword')
        item = Weapon(base.name, max(0, base_bonus + extra), base.price, quality=quality, level=item_level, weapon_type=weapon_type, requirements=requirements)
        item.base_id = item_id
        base_noun = base.name
        item.rotation = rotation
        item.name = f"{base_noun} | {QUALITY_DISPLAY.get(quality,quality)} | L{item_level} | +{extra} atk"
        return item

    # Случай: Броня
    if isinstance(base, Armor):
        base_bonus = base.defense_bonus
        extra = int(base_bonus * QUALITY_MULTIPLIER.get(quality, 0) + item_level * 1 + rotation * 2 + player_level // 3)
        armor_type = ARMOR_TYPES.get(item_id, 'leather')
        item = Armor(base.name, max(0, base_bonus + extra), base.price, quality=quality, level=item_level, armor_type=armor_type, requirements=requirements)
        item.base_id = item_id
        base_noun = base.name
        item.rotation = rotation
        item.name = f"{base_noun} | {QUALITY_DISPLAY.get(quality,quality)} | L{item_level} | +{extra} def"
        return item

    # Случай: Зелье
    if isinstance(base, Potion):
        extra = int(rotation * 5 + item_level * 2 + player_level // 2)
        item = Potion(base.name, max(1, base.heal_amount + extra), base.price)
        item.base_id = item_id
        item.rotation = rotation
        item.name = f"{base.name} (+{extra} heal) | R{rotation}" if rotation > 0 else f"{base.name} (+{extra} heal)"
        return item

    return None


def get_item(item_id):
    """Получить копию предмета по ID.

    Поддерживает ротацию и уровень: дополнительные бонусы будут добавлены
    в зависимости от `rotation` и `player_level`.
    """
    def _clone(item):
        if isinstance(item, Potion):
            ni = Potion(item.name, item.heal_amount, item.price)
            ni.base_id = item_id
            return ni
        if isinstance(item, Weapon):
            ni = Weapon(item.name, item.attack_bonus, item.price)
            ni.base_id = item_id
            return ni
        if isinstance(item, Armor):
            ni = Armor(item.name, item.defense_bonus, item.price)
            ni.base_id = item_id
            return ni
        if isinstance(item, SkillBook):
            ni = SkillBook(item.skill_id, item.name, item.description, item.price, levels=getattr(item, 'levels', 1))
            ni.base_id = item_id
            return ni
        if isinstance(item, Artifact):
            ni = Artifact(item.name, item.description, item.price, item.effect_id, bonus_slots=item.bonus_slots)
            ni.base_id = item_id
            return ni
        return None

    # backward-compatible simple call
    return _clone(ITEMS_DATABASE.get(item_id))


def get_item_scaled(item_id, rotation=0, player_level=1, quality=None, item_level=None, force_quality=False):
    """Вернуть предмет, масштабированный по ротации и уровню игрока.

    Можно явно указать `quality` и `item_level`, иначе они будут выбраны автоматически
    в зависимости от `rotation` и `player_level`.
    """
    # Если явно не указан уровень предмета, возьмём его как сочетание уровня игрока и ротации
    if item_level is None:
        item_level = max(1, player_level + rotation)

    # Генерируем предмет с помощью нового генератора
    gen = generate_equipment(item_id, rotation=rotation, player_level=player_level, quality=quality, item_level=item_level, force_quality=force_quality)
    if gen:
        return gen

    # Special-case: SkillBook scaling by rotation/level
    base = ITEMS_DATABASE.get(item_id)
    try:
        from skills import get_skill
    except Exception:
        get_skill = lambda x: None

    if isinstance(base, SkillBook):
        meta = get_skill(base.skill_id) or {}
        max_level = meta.get('max_level', getattr(base, 'levels', 1))
        # grant increases with rotation; every 3 rotations grant +1 extra level in the book
        grant = getattr(base, 'levels', 1) + (rotation // 3)
        grant = max(1, min(grant, max_level))
        price = int(base.price * (1 + rotation * 0.25) + player_level * 5)
        book = SkillBook(base.skill_id, base.name, base.description, price, levels=grant)
        book.base_id = item_id
        book.rotation = rotation
        if rotation > 0 and grant > getattr(base, 'levels', 1):
            book.name = f"{base.name} (+{grant})"
        return book

    if isinstance(base, Artifact):
        return get_item(item_id)

    # Фоллбек: если генератор не вернул (например, для простых материалов), вернём клонированный базовый предмет
    return get_item(item_id)


def get_random_artifact(rotation=0, player_luck=0):
    """Генерировать случайный артефакт с бонусами.
    
    Параметры:
    - rotation: текущая ротация игрока (влияет на значения бонусов)
    - player_luck: удача игрока (влияет на количество слотов: 1-5)
    """
    import random
    
    # Определяем количество слотов (1-5) на основе удачи и ротации
    base_slots = 1 + (rotation // 2)  # Ротация даёт слоты: 0=1, 2=2, 4=3 и т.д.
    luck_slots = max(0, (player_luck - 5) // 5)  # Удача даёт сдвиг: -5 слотов при luck<5, +1 при каждых 5 удачи выше 5
    total_slots = min(5, max(1, base_slots + luck_slots + random.randint(-1, 1)))  # Случайный +/- 1 слот
    
    # Генерируем бонусы для каждого слота
    bonus_slots = []
    bonus_types = ['stat', 'stat', 'stat', 'crit', 'evade']  # Больше вероятность получить stat
    
    for _ in range(total_slots):
        bonus_type = random.choice(bonus_types)
        
        # Базовые значения зависят от rotation и luck
        base_value = 5 + rotation * 2
        value_variance = random.randint(-3, 5)
        
        if bonus_type == 'stat':
            # Выбираем случайную характеристику
            stat_options = ['attack', 'defense', 'max_hp', 'intellect', 'luck', 'fire_resist', 'cold_resist']
            stat = random.choice(stat_options)
            
            # Разные значения для разных характеристик
            if stat == 'max_hp':
                value = max(5, 10 + base_value * 2 + value_variance)
            elif stat in ['fire_resist', 'cold_resist']:
                value = max(2, 5 + base_value + value_variance)
            else:
                value = max(1, base_value + value_variance)
            
            bonus_slots.append({
                'type': 'stat',
                'stat': stat,
                'value': value
            })
        
        elif bonus_type == 'crit':
            # Крит бонус в процентах
            value = max(2, 5 + rotation + random.randint(0, 3))
            bonus_slots.append({
                'type': 'crit',
                'value': value
            })
        
        elif bonus_type == 'evade':
            # Уклонение бонус в процентах
            value = max(2, 3 + rotation + random.randint(0, 3))
            bonus_slots.append({
                'type': 'evade',
                'value': value
            })
    
    # Создаём артефакт с бонусами
    artifact_names = [
        'Артефакт величия', 'Реликвия силы', 'Амулет доблести',
        'Орб мудрости', 'Камень удачи', 'Печать взумчатости',
        'Кольцо власти', 'Корона героя', 'Щит судьбы'
    ]
    name = random.choice(artifact_names)
    
    # Описание артефакта
    slots_desc = ', '.join([
        f"+{s['value']} {s.get('stat', s['type'])}" if s['type'] == 'stat' else f"+{s['value']}% {s['type']}"
        for s in bonus_slots
    ])
    description = f"Артефакт с {len(bonus_slots)} слотом(и): {slots_desc}"
    
    price = 1500 + rotation * 500 + len(bonus_slots) * 300
    
    artifact = Artifact(name, description, price, bonus_slots=bonus_slots)
    artifact.rotation = rotation
    return artifact
