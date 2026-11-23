import random
from ui import cprint
from ui import progress_bar
from locales import t
from skills import get_skill

ROGUE_PASSIVE_EVADE_CAP = 0.95


class Player:
    """Класс игрока с характеристиками и системой прокачки"""

    def _clamp_passive_evade(self):
        """Keep rogue passive evade within [0, ROGUE_PASSIVE_EVADE_CAP]."""
        self.passive_evade_chance = max(
            0.0, min(ROGUE_PASSIVE_EVADE_CAP, float(self.passive_evade_chance or 0.0))
        )
    
    def __init__(self, name, class_id=None):
        self.name = name
        # Престиж
        self.prestige_level = 0
        # Класс персонажа
        from classes import get_class
        self.class_obj = get_class(class_id) if class_id else None
        self.class_name = self.class_obj.name if self.class_obj else 'Без класса'
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        
        # Базовые характеристики
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack = 10
        self.defense = 5
        # Очки для распределения
        self.stat_points = 0
        # Новые характеристики: сопротивления, удача, интеллект, ловкость
        self.fire_resist = 0
        self.cold_resist = 0
        self.luck = 0
        self.intellect = 0
        self.agility = 0

        # Применяем бонусы класса (если есть)
        if self.class_obj:
            self.max_hp += self.class_obj.hp_bonus
            self.hp = self.max_hp
            self.attack += self.class_obj.attack_bonus
            self.defense += self.class_obj.defense_bonus
            # Применяем бонусы к новым характеристикам, если они заданы
            self.fire_resist += getattr(self.class_obj, 'fire_resist_bonus', 0)
            self.cold_resist += getattr(self.class_obj, 'cold_resist_bonus', 0)
            self.luck += getattr(self.class_obj, 'luck_bonus', 0)
            self.intellect += getattr(self.class_obj, 'intellect_bonus', 0)
            self.agility += getattr(self.class_obj, 'agility_bonus', 0)
        self.gold = 50
        
        # Экипировка
        self.weapon = None
        self.armor = None
        self.artifact = None
        # Способности и состояния (например, уклонение)
        self.abilities = {}  # id -> (name, description, cooldown)
        self.ability_cooldowns = {}  # id -> remaining turns
        self.evade = False
        # Изученные навыки: id -> level
        self.skills = {}
        # Очки навыков, выдаются при повышении уровня
        self.skill_points = 0
        # Skip CD tick once after using an ability this turn
        self._skip_cd_tick_once = False
        if self.class_obj and getattr(self.class_obj, 'ability', None):
            aid, aname, adesc, acd = self.class_obj.ability
            self.abilities[aid] = (aname, adesc, acd)
            self.ability_cooldowns[aid] = 0
            self.skills[aid] = 1  # enable scaled skill path
        # Пассивные эффекты
        # Для Разбойника — шанс пассивного уклонения + ambush
        self.passive_evade_chance = 0.0
        self.ambush_ready = False
        self.fortune_active = False  # Lucky: +gold this fight
        if self.class_obj and self.class_obj.id == 'rogue':
            self.passive_evade_chance = 0.08  # 8% базово
            self._clamp_passive_evade()
        self.stunned_turns = 0
        # Messages collected for mobile/UI combat log (also still cprinted).
        self.combat_messages = []

        # Применяем базовые бонусы престижа (если есть)
        self.apply_prestige_base_bonuses()

    def clear_combat_messages(self):
        self.combat_messages = []

    def drain_combat_messages(self):
        msgs = list(self.combat_messages)
        self.combat_messages.clear()
        return msgs

    def _cm(self, msg, color=None):
        if not msg:
            return
        self.combat_messages.append(msg)
        try:
            if color is None:
                cprint(msg)
            else:
                cprint(msg, color)
        except Exception:
            pass

    def get_total_attack(self):
        """Возвращает общую атаку с учётом оружия, требований и артефакта"""
        total = self.attack
        if self.weapon:
            # Используем эффективный бонус, который учитывает требования
            if hasattr(self.weapon, 'get_effective_bonus'):
                total += self.weapon.get_effective_bonus(self)
            else:
                total += self.weapon.attack_bonus
        
        # Добавляем бонус атаки от артефакта
        artifact = getattr(self, 'artifact', None)
        if artifact:
            for slot in getattr(artifact, 'bonus_slots', []):
                if slot.get('type') == 'stat' and slot.get('stat') == 'attack':
                    total += slot.get('value', 0)
        
        return total
    
    def get_total_defense(self):
        """Возвращает общую защиту с учётом брони, требований и артефакта"""
        total = self.defense
        if self.armor:
            # Используем эффективный бонус, который учитывает требования
            if hasattr(self.armor, 'get_effective_bonus'):
                total += self.armor.get_effective_bonus(self)
            else:
                total += self.armor.defense_bonus
        
        # Добавляем бонус защиты от артефакта
        artifact = getattr(self, 'artifact', None)
        if artifact:
            for slot in getattr(artifact, 'bonus_slots', []):
                if slot.get('type') == 'stat' and slot.get('stat') == 'defense':
                    total += slot.get('value', 0)
        
        return total
    
    def get_total_luck(self):
        """Возвращает общую удачу с учётом артефакта"""
        total = self.luck
        
        # Добавляем бонус удачи от артефакта
        artifact = getattr(self, 'artifact', None)
        if artifact:
            for slot in getattr(artifact, 'bonus_slots', []):
                if slot.get('type') == 'stat' and slot.get('stat') == 'luck':
                    total += slot.get('value', 0)
        
        return total

    def get_total_agility(self):
        """Общая ловкость с учётом артефакта"""
        total = getattr(self, "agility", 0) or 0
        artifact = getattr(self, "artifact", None)
        if artifact:
            for slot in getattr(artifact, "bonus_slots", []):
                if slot.get("type") == "stat" and slot.get("stat") == "agility":
                    total += slot.get("value", 0)
        return total

    def begin_combat_passives(self):
        """Call when a fight starts — reset fortune; arm rogue ambush."""
        self.fortune_active = False
        if self.class_obj and self.class_obj.id == "rogue":
            self.ambush_ready = True
        else:
            self.ambush_ready = False

    def get_prestige_requirement(self):
        """Требуемый уровень для следующего престижа"""
        base = 50
        step = 15
        return base + self.prestige_level * step

    def can_prestige(self):
        """Проверить, доступен ли престиж"""
        return self.level >= self.get_prestige_requirement()

    def get_prestige_bonus(self, level=None):
        """Вернуть бонусы престижа для указанного уровня"""
        lvl = self.prestige_level if level is None else int(level)
        return {
            'hp': lvl * 20,
            'attack': lvl * 3,
            'defense': lvl * 2,
            'stat_points': lvl * 2,
            'exp_mult': 1.0 + lvl * 0.05,
            'gold_mult': 1.0 + lvl * 0.07,
            'loot_bonus': lvl * 0.02,
        }

    def get_prestige_exp_multiplier(self):
        return self.get_prestige_bonus().get('exp_mult', 1.0)

    def get_prestige_gold_multiplier(self):
        return self.get_prestige_bonus().get('gold_mult', 1.0)

    def get_prestige_loot_bonus(self):
        return self.get_prestige_bonus().get('loot_bonus', 0.0)

    def apply_prestige_base_bonuses(self):
        """Добавить базовые бонусы престижа к стартовым статам"""
        bonus = self.get_prestige_bonus()
        if bonus.get('hp', 0) > 0:
            self.max_hp += bonus['hp']
            self.hp = self.max_hp
        if bonus.get('attack', 0) > 0:
            self.attack += bonus['attack']
        if bonus.get('defense', 0) > 0:
            self.defense += bonus['defense']
        if bonus.get('stat_points', 0) > 0:
            self.stat_points += bonus['stat_points']

    def prestige_reset(self):
        """Сделать престиж и сбросить прогрессию"""
        self.prestige_level += 1

        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100

        # Базовые характеристики
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack = 10
        self.defense = 5
        self.stat_points = 0
        self.fire_resist = 0
        self.cold_resist = 0
        self.luck = 0
        self.intellect = 0
        self.agility = 0

        # Сбрасываем навыки и способности
        self.skills = {}
        self.skill_points = 0
        self.abilities = {}
        self.ability_cooldowns = {}

        # Экипировка и золото
        self.weapon = None
        self.armor = None
        self.artifact = None
        self.gold = 50

        # Пассивные эффекты
        self.passive_evade_chance = 0.0
        self.evade = False
        self.ambush_ready = False
        self.fortune_active = False

        # Применяем бонусы класса (если есть)
        if self.class_obj:
            self.max_hp += self.class_obj.hp_bonus
            self.hp = self.max_hp
            self.attack += self.class_obj.attack_bonus
            self.defense += self.class_obj.defense_bonus
            self.fire_resist += getattr(self.class_obj, 'fire_resist_bonus', 0)
            self.cold_resist += getattr(self.class_obj, 'cold_resist_bonus', 0)
            self.luck += getattr(self.class_obj, 'luck_bonus', 0)
            self.intellect += getattr(self.class_obj, 'intellect_bonus', 0)
            self.agility += getattr(self.class_obj, 'agility_bonus', 0)

        # Пассивные эффекты класса
        if self.class_obj and self.class_obj.id == 'rogue':
            self.passive_evade_chance = 0.08
            self._clamp_passive_evade()

        # Применить бонусы престижа к базовым статам
        self.apply_prestige_base_bonuses()

        # Восстановить классовую способность
        self._skip_cd_tick_once = False
        if self.class_obj and getattr(self.class_obj, 'ability', None):
            aid, aname, adesc, acd = self.class_obj.ability
            self.abilities[aid] = (aname, adesc, acd)
            self.ability_cooldowns[aid] = 0
            self.skills[aid] = 1

        return self.get_prestige_bonus()
    
    def get_evade_chance(self):
        """Уклонение от ловкости: 0.4% за пункт + бонус артефакта, softcap 40%."""
        agility = self.get_total_agility()
        base_evade = agility * 0.4  # %

        artifact_bonus = 0
        artifact = getattr(self, 'artifact', None)
        if artifact and hasattr(artifact, 'get_evade_bonus'):
            artifact_bonus = artifact.get_evade_bonus() * 100

        total_evade = base_evade + artifact_bonus
        return min(0.40, total_evade / 100.0)

    def consume_ambush_multiplier(self) -> float:
        """Rogue first-hit ambush; returns damage mult and clears flag."""
        if getattr(self, "ambush_ready", False):
            self.ambush_ready = False
            return 1.6
        return 1.0
    
    def get_crit_chance(self):
        """Получить шанс критического удара на основе удачи.

        1% за каждые 4 пункта удачи + бонус артефакта (без капа ниже 100%).
        """
        luck = self.get_total_luck()
        base_crit = luck / 4.0  # %

        artifact_bonus = 0
        artifact = getattr(self, 'artifact', None)
        if artifact and hasattr(artifact, 'get_crit_bonus'):
            artifact_bonus = artifact.get_crit_bonus() * 100

        total_crit = base_crit + artifact_bonus
        return total_crit / 100.0
    
    def check_evade(self):
        """Проверить, произойдет ли уклонение"""
        import random
        evade_chance = self.get_evade_chance()
        return random.random() < evade_chance
    
    def check_crit(self):
        """Проверить, произойдет ли критический удар
        
        Возвращает множитель урона:
        - < 100%: шанс на крит × 1.5
        - 100%+: гарантированный крит, каждые 100% добавляют +0.5×
        - 200%: всегда × 2.0
        - 300%: всегда × 2.5
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
        guaranteed_crits = int(crit_chance)  # Количество гарантированных критов
        remaining_chance = crit_chance - guaranteed_crits  # Дробная часть
        
        # Базовый множитель: 1.0 + 0.5 за каждый гарантированный крит
        multiplier = 1.0 + (0.5 * guaranteed_crits)
        
        # Шанс на дополнительный крит (если есть дробная часть)
        if remaining_chance > 0 and random.random() < remaining_chance:
            multiplier += 0.5
        
        return multiplier
    
    def take_damage(self, damage, element=None, defense_penetration: float = 0.0):
        """Получить урон. Поддерживает элементальный урон (fire/cold).

        defense_penetration: дробь (0.0-1.0) — доля брони противника, которую следует игнорировать.
        """
        if self.evade:
            self.evade = False
            self._cm(t('evade_success'), 'cyan')
            return 0
        
        # Уклонение зависит от ловкости
        if self.check_evade():
            self._cm(t('evade_chance_proc', pct=int(self.get_evade_chance() * 100)), 'cyan')
            return 0
        
        # Пассивное уклонение Разбойника (в дополнение к основному)
        if self.class_obj and self.class_obj.id == 'rogue' and self.passive_evade_chance > 0:
            self._clamp_passive_evade()
            if random.random() < self.passive_evade_chance:
                self._cm(t('passive_evade'), 'cyan')
                return 0

        # Воин: при низком HP входящий урон ×0.9
        if (
            self.class_obj
            and self.class_obj.id == "warrior"
            and self.max_hp > 0
            and self.hp < self.max_hp * 0.40
        ):
            damage = int(damage * 0.9)

        # Применяем сопротивления к элементальному урону до учёта брони
        if element == 'fire' and getattr(self, 'fire_resist', 0) > 0:
            reduction = max(0.0, min(100.0, self.fire_resist))
            damage = int(damage * max(0.0, 1.0 - reduction / 100.0))
            self._cm(t('resist_fire_reduce', pct=f"{reduction:.0f}"), 'cyan')
        elif element == 'cold' and getattr(self, 'cold_resist', 0) > 0:
            reduction = max(0.0, min(100.0, self.cold_resist))
            damage = int(damage * max(0.0, 1.0 - reduction / 100.0))
            self._cm(t('resist_cold_reduce', pct=f"{reduction:.0f}"), 'cyan')

        # Учитываем пробивание брони: уменьшаем эффективность защиты игрока
        total_def = self.get_total_defense()
        effective_def = int(total_def * max(0.0, 1.0 - float(defense_penetration)))
        actual_damage = max(1, damage - effective_def)
        if self.has_artifact('aegis_sigil'):
            actual_damage = max(1, int(actual_damage * 0.85))
        self.hp -= actual_damage
        return actual_damage

    def can_use_ability(self, ability_id):
        return ability_id in self.abilities and self.ability_cooldowns.get(ability_id, 0) == 0

    def use_ability(self, ability_id, enemy):
        """Использовать способность класса в бою. Возвращает описание эффекта"""
        if not self.can_use_ability(ability_id):
            print(t('ability_unavailable'))
            return False

        name, desc, cd = self.abilities[ability_id]
        skill_meta = get_skill(ability_id)
        skill_level = self.skills.get(ability_id, 0)
        if skill_meta and skill_level > 0:
            stat = skill_meta.get('stat')
            stat_val = getattr(self, stat, 0) if stat else 0
            base = skill_meta.get('base_multiplier', 1.0)
            stat_scale = skill_meta.get('stat_scale', 0.0)
            level_bonus = 1.0 + 0.1 * (skill_level - 1)
            multiplier = base * level_bonus * (1.0 + stat_val * stat_scale)

            if ability_id == 'warrior_rage':
                damage = int(self.get_total_attack() * multiplier)
                pen = max(0, (0.5 + 0.05 * (skill_level - 1)))
                effective_def = int(max(0, enemy.defense * (1.0 - pen)))
                actual = max(1, damage - effective_def)
                enemy.hp -= actual
                self.apply_artifact_on_hit(enemy, actual)
                self._cm(
                    t(
                        'ability_hit',
                        ability=name,
                        name=enemy.name,
                        damage=actual,
                        hp=max(0, enemy.hp),
                        max_hp=enemy.max_hp,
                    ),
                    'yellow',
                )
            elif ability_id == 'mage_lightning':
                damage = int(self.get_total_attack() * multiplier) + int(self.intellect * 0.5 * skill_level)
                actual = max(1, damage - enemy.defense)
                enemy.hp -= actual
                self.apply_artifact_on_hit(enemy, actual)
                enemy.stunned_turns = max(1, getattr(enemy, 'stunned_turns', 0) + 1 + (skill_level // 2))
                self._cm(
                    t(
                        'ability_hit',
                        ability=name,
                        name=enemy.name,
                        damage=actual,
                        hp=max(0, enemy.hp),
                        max_hp=enemy.max_hp,
                    )
                    + ' '
                    + t('enemy_stunned', name=enemy.name),
                    'magenta',
                )
            elif ability_id in ('rogue_backstab', 'rogue_evade'):
                damage = int(self.get_total_attack() * (1.6 + 0.15 * (skill_level - 1)))
                amb = self.consume_ambush_multiplier()
                if amb > 1.0:
                    damage = int(damage * amb)
                    self._cm(t("ambush_proc"), "cyan")
                effective_def = int(max(0, enemy.defense * 0.70))
                actual = max(1, damage - effective_def)
                enemy.hp -= actual
                self.apply_artifact_on_hit(enemy, actual)
                self._cm(
                    t(
                        "ability_hit",
                        ability=name,
                        name=enemy.name,
                        damage=actual,
                        hp=max(0, enemy.hp),
                        max_hp=enemy.max_hp,
                    ),
                    "yellow",
                )
            elif ability_id == 'lucky_fortune':
                self.fortune_active = True
                self._cm(t("fortune_active_msg", ability=name), "yellow")
            else:
                self._cm(t('ability_not_implemented'))
                return False
        else:
            if ability_id == 'warrior_rage':
                damage = int(self.get_total_attack() * 1.8)
                actual = max(1, damage - max(0, enemy.defense // 2))
                enemy.hp -= actual
                self.apply_artifact_on_hit(enemy, actual)
                self._cm(
                    t(
                        'ability_hit',
                        ability=name,
                        name=enemy.name,
                        damage=actual,
                        hp=max(0, enemy.hp),
                        max_hp=enemy.max_hp,
                    ),
                    'yellow',
                )
            elif ability_id == 'mage_lightning':
                damage = int(self.get_total_attack() * 1.5) + 5
                actual = max(1, damage - enemy.defense)
                enemy.hp -= actual
                self.apply_artifact_on_hit(enemy, actual)
                enemy.stunned_turns = max(1, getattr(enemy, 'stunned_turns', 0) + 1)
                self._cm(
                    t(
                        'ability_hit',
                        ability=name,
                        name=enemy.name,
                        damage=actual,
                        hp=max(0, enemy.hp),
                        max_hp=enemy.max_hp,
                    )
                    + ' '
                    + t('enemy_stunned', name=enemy.name),
                    'magenta',
                )
            elif ability_id == 'rogue_backstab':
                damage = int(self.get_total_attack() * 1.6)
                amb = self.consume_ambush_multiplier()
                if amb > 1.0:
                    damage = int(damage * amb)
                    self._cm(t("ambush_proc"), "cyan")
                actual = max(1, damage - int(max(0, enemy.defense * 0.70)))
                enemy.hp -= actual
                self.apply_artifact_on_hit(enemy, actual)
                self._cm(
                    t(
                        "ability_hit",
                        ability=name,
                        name=enemy.name,
                        damage=actual,
                        hp=max(0, enemy.hp),
                        max_hp=enemy.max_hp,
                    ),
                    "yellow",
                )
            elif ability_id == 'lucky_fortune':
                self.fortune_active = True
                self._cm(t("fortune_active_msg", ability=name), "yellow")
            else:
                self._cm(t('ability_not_implemented'))
                return False

        self.ability_cooldowns[ability_id] = cd
        # Do not tick this ability's CD down in the same turn's reduce_cooldowns()
        self._skip_cd_tick_once = True
        return True

    def learn_skill(self, skill_id):
        """Learn a new skill if requirements met and player has skill points."""
        meta = get_skill(skill_id)
        if not meta:
            return {'error': 'Unknown skill'}
        if skill_id in self.skills:
            return {'error': 'Already learned'}
        if self.level < 1:
            return {'error': 'Level too low'}
        cost = meta.get('learn_cost', 1)
        if self.skill_points < cost:
            return {'error': 'Not enough skill points'}
        # learn
        self.skill_points -= cost
        self.skills[skill_id] = 1
        # register in abilities so UI can use it
        self.abilities[skill_id] = (meta['name'], meta['description'], meta.get('base_cooldown', 3))
        self.ability_cooldowns[skill_id] = 0
        return {'ok': True, 'skill': skill_id}

    def upgrade_skill(self, skill_id):
        """Upgrade an already learned skill using skill points."""
        meta = get_skill(skill_id)
        if not meta:
            return {'error': 'Unknown skill'}
        if skill_id not in self.skills:
            return {'error': 'Skill not learned'}
        level = self.skills[skill_id]
        if level >= meta.get('max_level', 1):
            return {'error': 'Already at max level'}
        if self.skill_points < 1:
            return {'error': 'Not enough skill points'}
        # upgrade
        self.skill_points -= 1
        self.skills[skill_id] = level + 1
        return {'ok': True, 'skill': skill_id, 'level': self.skills[skill_id]}

    def reduce_cooldowns(self):
        if getattr(self, '_skip_cd_tick_once', False):
            self._skip_cd_tick_once = False
            return
        for aid in list(self.ability_cooldowns.keys()):
            if self.ability_cooldowns[aid] > 0:
                self.ability_cooldowns[aid] -= 1
                if self.has_artifact('chrono_shard') and self.ability_cooldowns[aid] > 0:
                    self.ability_cooldowns[aid] -= 1
    
    def heal(self, amount):
        """Восстановить здоровье"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def gain_exp(self, amount):
        """Получить опыт"""
        self.exp += amount
        cprint(t('xp_gained', xp=amount), 'green')
        
        while self.exp >= self.exp_to_next_level:
            self.level_up()
    
    def level_up(self):
        """Повышение уровня"""
        self.exp -= self.exp_to_next_level
        self.level += 1
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        # Повышение характеристик
        self.max_hp += 20
        self.hp = self.max_hp
        self.attack += 3
        self.defense += 2
        self.stat_points += 3
        # give skill point on level up
        self.skill_points += 1
        # Применить пассивные бонусы класса при повышении уровня
        self.apply_class_passive_on_levelup()

        cprint(f"\n{'='*40}", 'yellow')
        cprint(t('level_up_title', level=self.level), 'yellow')
        cprint(f"{'='*40}", 'yellow')
        cprint(t('hp_increase', max_hp=self.max_hp), 'green')
        cprint(t('attack_increase', attack=self.attack), 'green')
        cprint(t('defense_increase', defense=self.defense), 'green')
        cprint(t('stat_points_gained'), 'cyan')
        cprint(f"{'='*40}\n", 'yellow')

    def apply_class_passive_on_levelup(self):
        """Применить пассивные эффекты класса при повышении уровня"""
        if not self.class_obj:
            return
        cid = self.class_obj.id
        if cid == 'warrior':
            # Воин получает дополнительные +1 к защите при каждом уровне
            self.defense += 1
            cprint(t('ability') + ': ' + 'Warrior passive +1 defense', 'cyan')
        elif cid == 'mage':
            self.intellect += 1
            cprint(t('ability') + ': ' + 'Mage passive +1 intellect', 'magenta')
        elif cid == 'rogue':
            # Разбойник повышает пассивный шанс уклонения (кап 95%)
            self.passive_evade_chance += 0.01
            self._clamp_passive_evade()
            cprint(t('ability') + f": Rogue passive evade {self.passive_evade_chance:.2%}", 'cyan')
        elif cid == 'lucky':
            self.luck += 1
            cprint(t('ability') + ': ' + 'Lucky passive +1 luck', 'yellow')
    
    def apply_stat_spend(self, stat_id: str) -> bool:
        """Spend one available stat point on ``stat_id``. Shared by CLI/desktop/Android."""
        if self.stat_points <= 0:
            return False
        if stat_id == "hp":
            self.max_hp += 15
            self.hp += 15
        elif stat_id == "attack":
            self.attack += 2
        elif stat_id == "defense":
            self.defense += 2
        elif stat_id == "fire_resist":
            self.fire_resist += 2
        elif stat_id == "cold_resist":
            self.cold_resist += 2
        elif stat_id == "luck":
            self.luck += 1
        elif stat_id == "intellect":
            self.intellect += 1
        elif stat_id == "agility":
            self.agility += 1
        else:
            return False
        self.stat_points -= 1
        return True

    @staticmethod
    def stat_effect_preview(luck: int = 0, intellect: int = 0, agility: int = 0) -> dict:
        """Derived combat/economy percentages (evade=agility, crit=luck)."""
        evade = min(0.40, (agility or 0) * 0.4 / 100.0)
        crit = (luck or 0) / 4.0 / 100.0
        xp_bonus = (intellect or 0) * 0.05
        return {
            "evade": evade,
            "crit": crit,
            "xp_bonus": xp_bonus,
            "evade_pct": evade * 100.0,
            "crit_pct": crit * 100.0,
            "xp_bonus_pct": xp_bonus * 100.0,
        }

    def spend_stat_points(self):
        """Распределить очки характеристик (console)."""
        if self.stat_points <= 0:
            print(t('no_stat_points'))
            return

        print(f"\n{t('stat_points_available', pts=self.stat_points)}")
        print(f"1. {t('stat_option_hp')}")
        print(f"2. {t('stat_option_attack')}")
        print(f"3. {t('stat_option_defense')}")
        print(f"4. {t('stat_option_fire_resist')}")
        print(f"5. {t('stat_option_cold_resist')}")
        print(f"6. {t('stat_option_luck')}")
        print(f"7. {t('stat_option_intellect')}")
        print(f"8. {t('stat_option_agility')}")
        print("0. Back")

        choice = input("\n" + t('choose_action'))
        mapping = {
            '1': 'hp',
            '2': 'attack',
            '3': 'defense',
            '4': 'fire_resist',
            '5': 'cold_resist',
            '6': 'luck',
            '7': 'intellect',
            '8': 'agility',
        }
        stat_id = mapping.get(choice)
        if stat_id and self.apply_stat_spend(stat_id):
            print(t('stat_improved', pts=self.stat_points))
    
    def show_stats(self):
        """Показать характеристики"""
        cprint(f"\n{'='*40}", 'yellow')
        cprint(f"📊 ХАРАКТЕРИСТИКИ ПЕРСОНАЖА", 'yellow')
        cprint(f"{'='*40}", 'yellow')
        cprint(f"Имя: {self.name}", 'cyan')
        cprint(f"Класс: {self.class_name}", 'cyan')
        cprint(f"Уровень: {self.level}", 'cyan')
        cprint(f"Престиж: {getattr(self, 'prestige_level', 0)}", 'magenta')
        cprint(f"Опыт: {self.exp}/{self.exp_to_next_level}", 'cyan')

        # HP bar
        pct = self.hp / self.max_hp if self.max_hp > 0 else 0
        bar_color = 'green' if pct > 0.6 else ('yellow' if pct > 0.3 else 'red')
        bar = progress_bar(self.hp, self.max_hp, width=30, color=bar_color)
        cprint(f"Здоровье: {self.hp}/{self.max_hp} " + bar, None)
        cprint(f"Атака: {self.attack} (всего: {self.get_total_attack()})", 'magenta')
        cprint(f"Защита: {self.defense} (всего: {self.get_total_defense()})", 'blue')
        cprint(f"Сопротивление огню: {getattr(self, 'fire_resist', 0)}%", 'red')
        cprint(f"Сопротивление холоду: {getattr(self, 'cold_resist', 0)}%", 'blue')
        cprint(f"Удача: {getattr(self, 'luck', 0)}", 'yellow')
        cprint(f"Интеллект: {getattr(self, 'intellect', 0)}", 'magenta')
        cprint(f"Ловкость: {self.get_total_agility()}", 'cyan')
        cprint(f"Золото: {self.gold}", 'yellow')
        cprint(f"Очки характеристик: {self.stat_points}", 'cyan')
        cprint(f"Артефакт: {self.artifact.name if self.artifact else 'Нет'}", 'cyan')
        cprint(f"\nОружие: {self.weapon.name if self.weapon else 'Нет'}", 'white')
        cprint(f"Броня: {self.armor.name if self.armor else 'Нет'}", 'white')
        cprint(f"{'='*40}\n", 'yellow')
    
    def is_alive(self):
        """Проверить, жив ли игрок"""
        return self.hp > 0

    def get_artifact_effect_id(self):
        return getattr(getattr(self, 'artifact', None), 'effect_id', None)

    def has_artifact(self, effect_id):
        return self.get_artifact_effect_id() == effect_id

    def get_artifact_gold_multiplier(self):
        if self.has_artifact('greed_idol'):
            return 1.2
        return 1.0

    def get_artifact_loot_bonus(self):
        if self.has_artifact('greed_idol'):
            return 0.05
        return 0.0

    def apply_artifact_on_hit(self, enemy, damage):
        """Apply artifact effects when dealing damage."""
        if damage <= 0:
            return
        if self.has_artifact('blood_thorn'):
            heal = max(1, int(damage * 0.08))
            self.heal(heal)
            self._cm(t('artifact_lifesteal', heal=heal), 'magenta')
        if self.has_artifact('storm_lens') and enemy is not None and enemy.is_alive():
            if random.random() < 0.15:
                enemy.stunned_turns = max(1, getattr(enemy, 'stunned_turns', 0) + 1)
                self._cm(t('artifact_stun'), 'cyan')


def calc_rest_cost(prestige_level: int = 0, rotation: int = 0) -> int:
    """Cheap full heal between fights; grows with prestige and rotation.

    P0 R0 = 5; +3 per prestige; +2 per rotation.
    """
    return max(1, 5 + int(prestige_level or 0) * 3 + int(rotation or 0) * 2)
