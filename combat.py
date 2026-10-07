import random
from ui import cprint
from locales import t


# Enemy skill implementations (simple, deterministic effects)
def _skill_fire_breath(enemy, player):
    attack_type = 'fire'
    dmg = random.randint(int(enemy.attack * 1.0), int(enemy.attack * 1.6))
    cprint(f"{enemy.name} использует огненное дыхание!", 'red')
    actual = player.take_damage(dmg, element=attack_type, defense_penetration=getattr(enemy, 'penetration', 0.0))
    return actual


def _skill_shield_bash(enemy, player):
    attack_type = 'physical'
    dmg = random.randint(int(enemy.attack * 0.8), int(enemy.attack * 1.1))
    cprint(f"{enemy.name} использует Удар щитом! (оглушение)", 'red')
    actual = player.take_damage(dmg, element=attack_type, defense_penetration=getattr(enemy, 'penetration', 0.0))
    # apply 1-turn stun to player
    try:
        player.stunned_turns = max(0, getattr(player, 'stunned_turns', 0)) + 1
    except Exception:
        setattr(player, 'stunned_turns', 1)
    return actual


def _skill_life_drain(enemy, player):
    attack_type = 'physical'
    dmg = random.randint(int(enemy.attack * 0.7), int(enemy.attack * 1.2))
    cprint(f"{enemy.name} использует Похищение жизни!", 'red')
    actual = player.take_damage(dmg, element=attack_type, defense_penetration=getattr(enemy, 'penetration', 0.0))
    heal = max(1, actual // 2)
    enemy.hp = min(enemy.max_hp, enemy.hp + heal)
    cprint(f"{enemy.name} восстанавливает {heal} HP.", 'red')
    return actual


_ENEMY_SKILL_MAP = {
    'fire_breath': _skill_fire_breath,
    'shield_bash': _skill_shield_bash,
    'life_drain': _skill_life_drain,
}

# Враги, которые не могут использовать магические атаки (животные и глупые существа)
ANIMAL_ENEMIES = {
    'Крыса', 'Волк', 'Паук', 'Слизень', 'Ящерица', 'Гоблин',
    'Орк', 'Минотавр', 'Тролль', 'Боров', 'Кабан', 'Гиена',
    'Циклоп', 'Бестия', 'Хищник', 'Маньяк', 'Странник'
}

def can_use_magic(enemy):
    """Проверить, может ли враг использовать магические атаки"""
    enemy_name = enemy.name
    # Проверяем, является ли враг животным
    for animal in ANIMAL_ENEMIES:
        if animal in enemy_name:
            return False
    # Враги с магическими умениями могут использовать магию
    if hasattr(enemy, 'skills') and enemy.skills:
        return True
    # Остальные враги не используют магию
    return False


def enemy_take_action(enemy, player):
    """Enemy chooses to use a skill (if available) or perform a normal attack.

    Returns actual damage dealt to player.
    """
    # Try skills first
    skills = getattr(enemy, 'skills', []) or []
    if skills:
        for sid, chance in skills:
            if random.random() < chance:
                fn = _ENEMY_SKILL_MAP.get(sid)
                if fn:
                    return fn(enemy, player)

    # Default physical/elemental attack
    attack_type = 'physical'
    # Только враги, которые могут использовать магию, используют элементальные атаки
    if can_use_magic(enemy) and random.random() < 0.15:
        attack_type = random.choice(['fire', 'cold'])
    enemy_damage = random.randint(int(enemy.attack * 0.8), int(enemy.attack * 1.2))
    if attack_type != 'physical':
        cprint(t('enemy_elemental', name=enemy.name, element=attack_type), 'red')
    actual_damage = player.take_damage(enemy_damage, element=attack_type,
                                       defense_penetration=getattr(enemy, 'penetration', 0.0))
    return actual_damage


class Enemy:
    """Класс врага"""

    def __init__(self, name, level, hp, attack, defense, exp_reward, gold_reward):
        self.name = name
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.stunned_turns = 0
        # Враги имеют меньший шанс уклонения/крита
        self.luck = max(0, level // 2)

    def get_evade_chance(self):
        """Получить шанс уклонения (меньше чем у игрока)"""
        return min(0.25, self.luck * 0.3 / 100.0)  # Максимум 25% для врагов
    
    def get_crit_chance(self):
        """Получить шанс критического удара"""
        return self.luck / 4.0 / 100.0  # Без ограничения
    
    def check_evade(self):
        """Проверить, произойдет ли уклонение"""
        import random
        return random.random() < self.get_evade_chance()
    
    def check_crit(self):
        """Проверить, произойдет ли критический удар
        
        Возвращает множитель урона:
        - < 100%: шанс на крит × 1.5
        - 100%+: гарантированный крит, каждые 100% добавляют +0.5×
        """
        import random
        crit_chance = self.get_crit_chance()
        
        # Если крит < 100%, обычная проверка
        if crit_chance < 1.0:
            if random.random() < crit_chance:
                return 1.5  # Обычный крит
            else:
                return 1.0  # Нет крита
        
        # Крит ≥ 100% - система множественных критов
        guaranteed_crits = int(crit_chance)
        remaining_chance = crit_chance - guaranteed_crits
        
        multiplier = 1.0 + (0.5 * guaranteed_crits)
        
        if remaining_chance > 0 and random.random() < remaining_chance:
            multiplier += 0.5
        
        return multiplier

    def take_damage(self, damage):
        """Получить урон"""
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage

    def is_alive(self):
        """Проверить, жив ли враг"""
        return self.hp > 0


# Враги по уровням
ENEMY_TEMPLATES = {
    1: [
        ("Гоблин", 1, 30, 8, 2, 25, 10),
        ("Крыса", 1, 20, 6, 1, 20, 5),
        ("Слизень", 1, 25, 5, 3, 22, 8),
        ("Гоблин-Шаман", 1, 22, 7, 1, 18, 6, [('fire_breath', 0.12)]),
    ],
    2: [
        ("Орк", 2, 50, 12, 4, 40, 20),
        ("Волк", 2, 40, 14, 3, 35, 15),
        ("Скелет", 2, 45, 10, 5, 38, 18),
        ("Капитан бандитов", 2, 48, 15, 6, 45, 22, [('shield_bash', 0.18)]),
    ],
    3: [
        ("Тролль", 3, 80, 18, 7, 60, 35),
        ("Темный рыцарь", 3, 70, 20, 8, 65, 40),
        ("Огр", 3, 90, 16, 9, 58, 32),
        ("Скелет-маг", 3, 60, 14, 6, 55, 30, [('life_drain', 0.12)]),
    ],
    4: [
        ("Дракон", 4, 120, 25, 12, 100, 60),
        ("Демон", 4, 100, 28, 10, 95, 55),
        ("Минотавр", 4, 110, 22, 14, 90, 50),
        ("Некромант", 4, 85, 18, 8, 120, 60, [('life_drain', 0.20)]),
    ],
    5: [
        ("Архидемон", 5, 150, 32, 15, 150, 100),
        ("Древний дракон", 5, 180, 30, 18, 160, 110),
        ("Повелитель тьмы", 5, 200, 35, 20, 200, 150),
        ("Виверна", 5, 140, 34, 14, 180, 120, [('fire_breath', 0.25)]),
    ],
}


def create_enemy(player_level, rotation=0):
    """Создать врага подходящего уровня и масштабировать его по ротации."""
    enemy_level = max(1, min(5, player_level + random.randint(-1, 1)))
    enemy_data = random.choice(ENEMY_TEMPLATES[enemy_level])
    # enemy_data may optionally include a skills list as 8th element
    enemy = Enemy(*enemy_data[:7])
    if len(enemy_data) > 7:
        enemy.skills = enemy_data[7]
    else:
        enemy.skills = []

    # Увеличенный масштаб по ротациям: даём больше атаки/HP/защиты
    hp_extra = rotation * 30 + player_level * 5
    atk_extra = rotation * 4 + player_level // 2
    def_extra = rotation * 2 + player_level // 3

    enemy.max_hp += hp_extra
    enemy.hp = enemy.max_hp
    enemy.attack += atk_extra
    enemy.defense += def_extra

    # Процент пробивания брони — растёт с ротацией (максимум 50%)
    enemy.penetration = min(0.5, rotation * 0.05)

    enemy.exp_reward += rotation * 20 + player_level * 5
    enemy.gold_reward += rotation * 15 + player_level * 3

    if rotation > 0:
        enemy.name = f"{enemy.name} [R{rotation}]"

    return enemy


def combat(player, inventory, rotation=0):
    """Боевая система"""
    enemy = create_enemy(player.level, rotation=rotation)

    cprint(f"\n{'='*50}", 'yellow')
    cprint(t('combat_begin'), 'yellow')
    cprint(f"{'='*50}", 'yellow')
    cprint(t('encountered', name=enemy.name, level=enemy.level), 'cyan')
    cprint(t('enemy_hp', hp=enemy.hp, max_hp=enemy.max_hp), 'red')
    cprint(f"{'='*50}\n", 'yellow')

    turn = 1

    while player.is_alive() and enemy.is_alive():
        print(t('round_header', n=turn))
        print(t('your_hp', hp=player.hp, max_hp=player.max_hp))
        print(t('enemy_hp', hp=enemy.hp, max_hp=enemy.max_hp))

        available_abilities = []
        for aid, data in player.abilities.items():
            name, desc, cd = data
            rc = player.ability_cooldowns.get(aid, 0)
            available_abilities.append((aid, name, desc, cd, rc))

        print("\n1.", t('attack'))
        print("2.", t('use_potion'))
        print("3.", t('ability'))
        print("4.", t('run'))

        choice = input("\n" + t('choose_action'))

        if choice == '1':
            damage = random.randint(int(player.get_total_attack() * 0.8), int(player.get_total_attack() * 1.2))
            actual_damage = enemy.take_damage(damage)
            try:
                player.apply_artifact_on_hit(enemy, actual_damage)
            except Exception:
                pass
            print(t('you_attack', name=enemy.name, damage=actual_damage))

            if not enemy.is_alive():
                print(f"\n{'='*50}")
                cprint(t('victory', name=enemy.name), 'green')
                print(f"{'='*50}")
                prestige_exp_mult = 1.0
                prestige_gold_mult = 1.0
                artifact_gold_mult = 1.0
                try:
                    prestige_exp_mult = player.get_prestige_exp_multiplier()
                    prestige_gold_mult = player.get_prestige_gold_multiplier()
                except Exception:
                    pass
                try:
                    artifact_gold_mult = player.get_artifact_gold_multiplier()
                except Exception:
                    pass

                xp_gain = int(
                    enemy.exp_reward * (1 + getattr(player, 'intellect', 0) * 0.05 + rotation * 0.10)
                    * prestige_exp_mult
                )
                gold_gain = int(
                    enemy.gold_reward * (1 + getattr(player, 'luck', 0) * 0.05 + rotation * 0.12)
                    * prestige_gold_mult
                    * artifact_gold_mult
                )
                player.gain_exp(xp_gain)
                player.gold += gold_gain
                print(t('gold_gained', gold=gold_gain))
                print(f"{'='*50}\n")

                loot_bonus = 0.0
                try:
                    loot_bonus = player.get_prestige_loot_bonus()
                except Exception:
                    pass
                try:
                    loot_bonus += player.get_artifact_loot_bonus()
                except Exception:
                    pass

                loot_chance = min(
                    0.95,
                    0.35 + rotation * 0.05 + getattr(player, 'luck', 0) * 0.04
                    + player.level * 0.01 + loot_bonus
                )
                if random.random() < loot_chance:
                    from items import get_item_scaled
                    loot_items = ['small_potion', 'medium_potion']
                    if player.level >= 2 or rotation >= 1:
                        loot_items.extend(['wooden_sword', 'leather_armor'])
                    if player.level >= 3 or rotation >= 2:
                        loot_items.extend(['iron_sword', 'iron_armor'])
                    if player.level >= 4 or rotation >= 3:
                        loot_items.extend(['steel_sword', 'steel_armor'])
                    if rotation >= 4:
                        loot_items.extend(['legendary_sword', 'legendary_armor'])

                    extra_drop = random.random() < min(0.35, getattr(player, 'luck', 0) * 0.03 + rotation * 0.02)
                    choice_id = random.choice(loot_items)
                    loot = get_item_scaled(choice_id, rotation=rotation, player_level=player.level)
                    if loot:
                        inventory.add_item(loot)
                    if extra_drop:
                        choice_id = random.choice(loot_items)
                        loot2 = get_item_scaled(choice_id, rotation=rotation, player_level=player.level)
                        if loot2:
                            inventory.add_item(loot2)

                # Rare artifact drop
                try:
                    from items import get_random_artifact
                    artifact_chance = min(0.20, 0.02 + rotation * 0.01 + getattr(player, 'luck', 0) * 0.002)
                    if random.random() < artifact_chance:
                        artifact = get_random_artifact()
                        if artifact:
                            inventory.add_item(artifact)
                            print(t('artifact_found', name=artifact.name))
                except Exception:
                    pass

                return True

            if getattr(enemy, 'stunned_turns', 0) > 0:
                print(t('enemy_stunned', name=enemy.name))
                enemy.stunned_turns -= 1
            else:
                actual_damage = enemy_take_action(enemy, player)
                try:
                    print(t('enemy_hits', name=enemy.name, damage=actual_damage))
                except Exception:
                    pass

            if not player.is_alive():
                print(f"\n{'='*50}")
                cprint(t('defeat'), 'red')
                print(t('defeated_by', name=enemy.name))
                print(f"{'='*50}\n")
                return False

        elif choice == '2':
            from items import Potion
            potions = [(i, item) for i, item in enumerate(inventory.items) if isinstance(item, Potion)]
            if not potions:
                print(t('no_potions'))
                continue

            for idx, (i, potion) in enumerate(potions, 1):
                print(f"{idx}. {potion.name} ({potion.description})")

            try:
                potion_choice = int(input("\n" + t('choose_potion_prompt'))) - 1
                if 0 <= potion_choice < len(potions):
                    inventory_index = potions[potion_choice][0]
                    inventory.use_item(inventory_index, player)
                else:
                    continue
            except ValueError:
                print(t('invalid_input'))
                continue

            if getattr(enemy, 'stunned_turns', 0) > 0:
                print(t('enemy_stunned', name=enemy.name))
                enemy.stunned_turns -= 1
            else:
                actual_damage = enemy_take_action(enemy, player)
                try:
                    print(t('enemy_hits', name=enemy.name, damage=actual_damage))
                except Exception:
                    pass

                if enemy.is_alive():
                    if getattr(enemy, 'stunned_turns', 0) > 0:
                        print(t('enemy_stunned', name=enemy.name))
                        enemy.stunned_turns -= 1
                    else:
                        actual_damage = enemy_take_action(enemy, player)
                        try:
                            print(t('enemy_hits', name=enemy.name, damage=actual_damage))
                        except Exception:
                            pass
        elif choice == '3':
            # Use ability
            if not available_abilities:
                print(t('no_abilities'))
                continue
            print("\n" + t('ability_title'))
            for idx, (aid, name, desc, cd, rc) in enumerate(available_abilities, 1):
                status = t('status_ready') if rc == 0 else t('status_cd', rc=rc)
                print(f"{idx}. {name} - {desc} ({status})")
            try:
                achoice = int(input("\n" + t('choose_action'))) - 1
                if achoice == -1:
                    continue
                if 0 <= achoice < len(available_abilities):
                    aid = available_abilities[achoice][0]
                    if player.can_use_ability(aid):
                        player.use_ability(aid, enemy)
                        print(t('ability_on_cd'))
                else:
                    print(t('invalid_choice'))
                    continue
            except ValueError:
                print(t('invalid_input'))
                continue

            # Enemy response
            if enemy.is_alive():
                if getattr(enemy, 'stunned_turns', 0) > 0:
                    print(t('enemy_stunned', name=enemy.name))
                    enemy.stunned_turns -= 1
                else:
                    actual_damage = enemy_take_action(enemy, player)
                    try:
                        print(t('enemy_hits', name=enemy.name, damage=actual_damage))
                    except Exception:
                        pass

        elif choice == '4':
            # Try to flee
            if random.random() < 0.5:
                print(t('you_fled'))
                return False
            else:
                print(t('flee_failed'))
                actual_damage = enemy_take_action(enemy, player)
                try:
                    print(t('enemy_hits', name=enemy.name, damage=actual_damage))
                except Exception:
                    pass

        else:
            print(t('invalid_choice'))
            continue

        # Reduce cooldowns and next turn
        player.reduce_cooldowns()
        turn += 1

    return player.is_alive()
