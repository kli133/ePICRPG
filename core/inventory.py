from ui import cprint
from locales import t
import uuid


class Inventory:
    """Система инвентаря игрока"""
    
    def __init__(self, max_size=20):
        self.items = []
        self.max_size = max_size
    
    def add_item(self, item):
        """Добавить предмет в инвентарь"""
        if len(self.items) >= self.max_size:
            print(t('inventory_full'))
            return False
        # Ensure each item has a stable unique id for UI/equipment tracking
        try:
            if not getattr(item, 'uid', None):
                item.uid = uuid.uuid4().hex
        except Exception:
            pass
        # Mark as not equipped by default only if not already set (preserve loaded state)
        try:
            if not hasattr(item, 'equipped'):
                item.equipped = False
        except Exception:
            pass

        self.items.append(item)
        print(t('received_item', name=item.name))
        return True
    
    def remove_item(self, item):
        """Удалить предмет из инвентаря"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def evaluate_strength(self, item, player):
        """Оценить силу предмета относительно игрока.

        Возвращает 'stronger', 'weaker' или 'equal' для оружия и брони.
        Для остальных типов возвращает None.
        """
        try:
            if hasattr(item, 'attack_bonus'):
                # Сравним с текущим оружием игрока или с базовой атакой
                current = getattr(player, 'weapon', None)
                current_val = getattr(current, 'attack_bonus', None)
                if current_val is None:
                    current_val = getattr(player, 'attack', 0)
                if item.attack_bonus > current_val:
                    return 'stronger'
                if item.attack_bonus < current_val:
                    return 'weaker'
                return 'equal'
            if hasattr(item, 'defense_bonus'):
                current = getattr(player, 'armor', None)
                current_val = getattr(current, 'defense_bonus', None)
                if current_val is None:
                    current_val = getattr(player, 'defense', 0)
                if item.defense_bonus > current_val:
                    return 'stronger'
                if item.defense_bonus < current_val:
                    return 'weaker'
                return 'equal'
        except Exception:
            return None
        return None

    def show_inventory(self, player=None, filter_type='all', show_strength=False):
        """Показать содержимое инвентаря с возможностью фильтрации.

        filter_type: 'all','weapons','armor','potions','artifacts','materials','stronger','weaker'
        show_strength: если True, добавляет пометку силы рядом с экипировкой
        """
        if not self.items:
            print("\n" + t('inventory_empty'))
            return

        cprint(f"\n{'='*50}", 'yellow')
        cprint(f"🎒 ИНВЕНТАРЬ ({len(self.items)}/{self.max_size})", 'yellow')
        cprint(f"{'='*50}", 'yellow')

        def passes_filter(it):
            if filter_type == 'all':
                return True
            if filter_type == 'weapons' and hasattr(it, 'attack_bonus'):
                return True
            if filter_type == 'armor' and hasattr(it, 'defense_bonus'):
                return True
            if filter_type == 'potions' and hasattr(it, 'heal_amount'):
                return True
            if filter_type == 'artifacts' and hasattr(it, 'effect_id'):
                return True
            if filter_type == 'materials' and not (hasattr(it, 'attack_bonus') or hasattr(it, 'defense_bonus') or hasattr(it, 'heal_amount') or hasattr(it, 'effect_id')):
                return True
            if filter_type == 'stronger':
                s = self.evaluate_strength(it, player) if player else None
                return s == 'stronger'
            if filter_type == 'weaker':
                s = self.evaluate_strength(it, player) if player else None
                return s == 'weaker'
            return False

        # Группируем предметы по типам для удобного отображения
        groups = {
            'weapons': [],
            'armor': [],
            'potions': [],
            'artifacts': [],
            'materials': [],
            'other': []
        }

        for i, item in enumerate(self.items):
            if not passes_filter(item):
                continue
            if hasattr(item, 'attack_bonus'):
                groups['weapons'].append((i, item))
            elif hasattr(item, 'defense_bonus'):
                groups['armor'].append((i, item))
            elif hasattr(item, 'heal_amount'):
                groups['potions'].append((i, item))
            elif hasattr(item, 'effect_id'):
                groups['artifacts'].append((i, item))
            elif not (hasattr(item, 'attack_bonus') or hasattr(item, 'defense_bonus') or hasattr(item, 'heal_amount') or hasattr(item, 'effect_id')):
                groups['materials'].append((i, item))
            else:
                groups['other'].append((i, item))

        order = [
            ('weapons', t('filter_weapons')),
            ('armor', t('filter_armor')),
            ('potions', t('filter_potions')),
            ('artifacts', t('filter_artifacts')),
            ('materials', t('filter_materials')),
            ('other', t('section_other'))
        ]
        idx_count = 1
        for key, label in order:
            items = groups.get(key, [])
            if not items:
                continue
            cprint(f"--- {label} ---", 'magenta')
            for real_i, item in items:
                # Пометки об экипировке
                equipped = False
                if hasattr(item, 'attack_bonus'):
                    if player and getattr(player, 'weapon', None) is item:
                        equipped = True
                elif hasattr(item, 'defense_bonus'):
                    if player and getattr(player, 'armor', None) is item:
                        equipped = True
                elif hasattr(item, 'effect_id'):
                    if player and getattr(player, 'artifact', None) is item:
                        equipped = True

                strength_tag = ''
                if show_strength and player:
                    s = self.evaluate_strength(item, player)
                    if s == 'stronger':
                        strength_tag = t('stronger_tag')
                    elif s == 'weaker':
                        strength_tag = t('weaker_tag')
                    elif s == 'equal':
                        strength_tag = t('equal_tag')

                if hasattr(item, 'attack_bonus'):
                    from items import QUALITY_ICONS
                    icon = QUALITY_ICONS.get(getattr(item, 'quality', 'wooden'), '')
                    cprint(f"{idx_count}. {icon} {item.name}  | {getattr(item, 'quality', 'None')}  | L{getattr(item, 'level', 1)}  | {t('attack_label', val=item.attack_bonus)}" + (t('equipped_tag') if equipped else "") + strength_tag, 'green')
                elif hasattr(item, 'defense_bonus'):
                    from items import QUALITY_ICONS
                    icon = QUALITY_ICONS.get(getattr(item, 'quality', 'wooden'), '')
                    cprint(f"{idx_count}. {icon} {item.name}  | {getattr(item, 'quality', 'None')}  | L{getattr(item, 'level', 1)}  | {t('defense_label', val=item.defense_bonus)}" + (t('equipped_tag') if equipped else "") + strength_tag, 'green')
                elif hasattr(item, 'heal_amount'):
                    cprint(f"{idx_count}. {item.name} | {t('heal_label', val=item.heal_amount)}", 'green')
                elif hasattr(item, 'effect_id'):
                    cprint(f"{idx_count}. ✪ {item.name}" + (t('equipped_tag') if equipped else ""), 'magenta')
                else:
                    cprint(f"{idx_count}. {item.name} - {item.description}", 'white')
                idx_count += 1

        cprint(f"{'='*50}\n", 'yellow')

    def count_materials(self, material_base_id):
        """Посчитать количество материалов с данным base_id в инвентаре."""
        return sum(1 for it in self.items if getattr(it, 'base_id', None) == material_base_id)


    def show_item_details(self, index):
        """Показать детальную информацию по предмету"""
        if index < 0 or index >= len(self.items):
            cprint(t('invalid_index'), 'red')
            return

        item = self.items[index]
        cprint(f"\n{'-'*40}", 'yellow')
        from items import QUALITY_ICONS
        icon = QUALITY_ICONS.get(getattr(item, 'quality', 'wooden'), '')
        # Пометка об экипировке
        equipped_flag = ''
        try:
            # player isn't passed here; detect if item has attribute 'equipped' or rely on identity elsewhere
            pass
        except Exception:
            pass
        cprint(t('label_name', name=icon + ' ' + item.name), 'cyan')
        cprint(t('label_description', text=getattr(item, 'description', '')), 'white')
        cprint(t('label_base_id', id=getattr(item, 'base_id', 'None')), 'white')
        if hasattr(item, 'attack_bonus'):
            cprint(t('type_weapon', level=getattr(item, 'level', 1), quality=getattr(item, 'quality', 'None'), rotation=getattr(item, 'rotation', 0)), 'magenta')
            cprint(t('attack_label', val=item.attack_bonus), 'green')
        elif hasattr(item, 'defense_bonus'):
            cprint(t('type_armor', level=getattr(item, 'level', 1), quality=getattr(item, 'quality', 'None'), rotation=getattr(item, 'rotation', 0)), 'magenta')
            cprint(t('defense_label', val=item.defense_bonus), 'green')
        elif hasattr(item, 'heal_amount'):
            cprint(t('type_potion', heal=getattr(item, 'heal_amount', 0)), 'green')
        else:
            cprint(t('type_material'), 'white')
        cprint(t('price_in_shop', price=getattr(item, 'price', 'N/A')), 'yellow')
        cprint(f"{'-'*40}\n", 'yellow')
    
    def use_item(self, index, player):
        """Использовать предмет из инвентаря"""
        if index < 0 or index >= len(self.items):
            print(t('invalid_index'))
            return
        
        item = self.items[index]
        should_remove = item.use(player)
        
        if should_remove:
            self.remove_item(item)

    def sell_item(self, index, player, rotation=0):
        """Продать предмет из инвентаря. Добавляет золото игроку и удаляет предмет."""
        if index < 0 or index >= len(self.items):
            cprint("Неверный номер предмета!", 'red')
            return False

        item = self.items[index]
        # Определяем цену продажи
        try:
            from items import QUALITY_MULTIPLIER
        except Exception:
            QUALITY_MULTIPLIER = {}

        base_price = getattr(item, 'price', 0)
        level = getattr(item, 'level', 1)
        quality = getattr(item, 'quality', 'wooden')
        quality_mul = QUALITY_MULTIPLIER.get(quality, 0)

        # Формула: (base + level*50) * (1 + quality_mul) * 0.5, + небольшая премия за ротацию
        sell_price = int((base_price + level * 50) * (1 + quality_mul) * 0.5 + rotation * 10)
        # Учитываем удачу продавца (немного увеличивает выручку)
        sell_price = int(sell_price * (1 + getattr(player, 'luck', 0) * 0.02))

        cprint(t('sell_will_get', price=sell_price, name=item.name), 'yellow')
        confirm = input(t('sell_confirm_prompt'))
        if confirm.lower() not in ('y', 'yes'):
            cprint(t('sale_cancelled'), 'cyan')
            return False

        # Продажа
        player.gold += sell_price
        self.remove_item(item)
        cprint(t('item_sold_console', gold=sell_price), 'green')
        return True

    def upgrade_item(self, index, player, rotation=0):
        """Улучшить предмет - вызывает консольную версию для обратной совместимости"""
        return self.upgrade_item_console(index, player, rotation)

    def upgrade_item_console(self, index, player, rotation=0):
        """Улучшить предмет: повышает уровень предмета, взимая плату золотом и опционально материалами.

        Стоимость рассчитывается экспоненциально: base_cost * (multiplier ** current_level) * (1 + rotation_factor).
        Игрок может использовать `upgrade_stone` чтобы снизить стоимость (каждый камень уменьшает цену на 30%).
        """
        if index < 0 or index >= len(self.items):
            print(t('invalid_index'))
            return False

        item = self.items[index]
        from items import generate_equipment

        # Проверяем, есть ли у предмета base_id
        base_id = getattr(item, 'base_id', None)
        if not base_id:
            print(t('upgrade_not_upgradable'))
            return False

        current_level = getattr(item, 'level', 1)
        base_cost = 100
        multiplier = 1.6
        # экспоненциальная стоимость
        cost = int(base_cost * (multiplier ** current_level) * (1 + rotation * 0.15))

        # Материалы
        stones_available = self.count_materials('upgrade_stone')
        max_stones_use = min(stones_available, max(0, current_level // 2))

        print(t('upgrade_current_level', level=current_level))
        print(t('upgrade_base_cost', cost=cost))
        if stones_available > 0:
            print(t('upgrade_stones_available', count=stones_available))
            # also show max use
            print(t('upgrade_max_stones', max=max_stones_use))
        
        # Спросить, сколько камней использовать
        stones_to_use = 0
        if max_stones_use > 0:
            try:
                val = input(t('upgrade_how_many', max=max_stones_use) + ' ')
                stones_to_use = int(val)
                stones_to_use = max(0, min(max_stones_use, stones_to_use))
            except Exception:
                stones_to_use = 0

        final_cost = int(cost * (0.7 ** stones_to_use))

        # Подтверждение
        cprint(t('upgrade_confirm_cost', cost=final_cost), 'yellow')
        confirm = input(t('upgrade_confirm_title') + ' (y/n): ')
        if confirm.lower() not in ('y', 'yes'):
            cprint(t('upgrade_cancelled'), 'cyan')
            return False

        if player.gold < final_cost:
            cprint(t('need_gold', price=final_cost), 'red')
            return False

        # Списываем золото и материалы, затем генерируем новую версию предмета с повышенным уровнем
        player.gold -= final_cost
        # Удаляем использованные камни
        removed = 0
        if stones_to_use > 0:
            for it in list(self.items):
                if removed >= stones_to_use:
                    break
                if getattr(it, 'base_id', None) == 'upgrade_stone':
                    self.remove_item(it)
                    removed += 1

        new_item = generate_equipment(base_id, rotation=rotation, player_level=player.level, quality=getattr(item, 'quality', None), item_level=current_level + 1)
        if not new_item:
            print(t('upgrade_failed'))
            return False

        # Заменяем предмет в инвентаре (сохранить uid/equipped)
        try:
            old = self.items[index]
            # preserve uid and equipped flag if present
            try:
                new_item.uid = getattr(old, 'uid', None) or getattr(new_item, 'uid', None)
            except Exception:
                pass
            try:
                new_item.equipped = getattr(old, 'equipped', False)
            except Exception:
                pass
        except Exception:
            pass
        self.items[index] = new_item
        if getattr(player, 'weapon', None) is old:
            player.weapon = new_item
        if getattr(player, 'armor', None) is old:
            player.armor = new_item

        print(t('item_upgraded_text', level=current_level + 1, cost=cost))
        return True

    def upgrade_item_gui(self, index, player, rotation=0, stones_to_use=0):
        """Улучшить предмет для GUI версии (без интерактивных вопросов).
        
        Args:
            index: индекс предмета в инвентаре
            player: объект игрока
            rotation: текущая ротация игры
            stones_to_use: количество камней улучшения, которые нужно использовать
            
        Returns:
            dict с информацией об операции или False в случае ошибки
        """
        if index < 0 or index >= len(self.items):
            return {'error': t('invalid_index')}

        item = self.items[index]
        from items import generate_equipment

        # Проверяем, есть ли у предмета base_id
        base_id = getattr(item, 'base_id', None)
        if not base_id:
            return {'error': t('upgrade_not_upgradable')}

        current_level = getattr(item, 'level', 1)
        base_cost = 100
        multiplier = 1.6
        # экспоненциальная стоимость
        cost = int(base_cost * (multiplier ** current_level) * (1 + rotation * 0.15))

        # Материалы
        stones_available = self.count_materials('upgrade_stone')
        max_stones_use = min(stones_available, max(0, current_level // 2))

        # Информация для GUI (если stones_to_use = -1, вернуть только инфо)
        info = {
            'item_name': item.name,
            'current_level': current_level,
            'base_cost': cost,
            'stones_available': stones_available,
            'max_stones_use': max_stones_use
        }
        
        if stones_to_use == -1:
            return info

        # Проверка корректности количества камней
        stones_to_use = max(0, min(max_stones_use, stones_to_use))
        final_cost = int(cost * (0.7 ** stones_to_use))

        if player.gold < final_cost:
            return {'error': t('need_gold', price=final_cost)}

        # Списываем золото и материалы, затем генерируем новую версию предмета с повышенным уровнем
        player.gold -= final_cost
        # Удаляем использованные камни
        removed = 0
        if stones_to_use > 0:
            for it in list(self.items):
                if removed >= stones_to_use:
                    break
                if getattr(it, 'base_id', None) == 'upgrade_stone':
                    self.remove_item(it)
                    removed += 1

        new_item = generate_equipment(base_id, rotation=rotation, player_level=player.level, quality=getattr(item, 'quality', None), item_level=current_level + 1)
        if not new_item:
            return {'error': t('upgrade_failed')}

        # Заменяем предмет в инвентаре (сохранить uid/equipped)
        try:
            old = self.items[index]
            try:
                new_item.uid = getattr(old, 'uid', None) or getattr(new_item, 'uid', None)
            except Exception:
                pass
            try:
                new_item.equipped = getattr(old, 'equipped', False)
            except Exception:
                pass
        except Exception:
            old = None
        self.items[index] = new_item
        if old is not None and getattr(player, 'weapon', None) is old:
            player.weapon = new_item
        if old is not None and getattr(player, 'armor', None) is old:
            player.armor = new_item

        return {
            'success': True,
            'new_level': current_level + 1,
            'cost': final_cost,
            'stones_used': stones_to_use
        }
    
    def has_potions(self):
        """Проверить наличие зелий в инвентаре"""
        from items import Potion
        return any(isinstance(item, Potion) for item in self.items)
    
    def get_item_by_index(self, index):
        """Получить предмет по индексу"""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
