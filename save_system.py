"""
Система сохранения и загрузки игры
"""
import json
import os
from player import Player
from inventory import Inventory
from items import Weapon, Armor, Potion, Item, Artifact
from locales import set_locale, get_locale, t
from version import VERSION


SAVE_FILE = "savegame.json"
SETTINGS_FILE = "settings.json"
SLOT_PREFIX = "save_slot_"
MAX_SLOTS = 5


def serialize_item(item):
    """Сериализовать предмет в словарь"""
    item_data = {
        'type': type(item).__name__,
        'name': item.name,
        'description': item.description,
        'price': item.price,
        'uid': getattr(item, 'uid', None),
        'equipped': getattr(item, 'equipped', False),
        'base_id': getattr(item, 'base_id', None),
    }
    
    if isinstance(item, Weapon):
        item_data.update({
            'attack_bonus': item.attack_bonus,
            'quality': getattr(item, 'quality', 'wooden'),
            'level': getattr(item, 'level', 1),
            'rotation': getattr(item, 'rotation', 0),
            'weapon_type': getattr(item, 'weapon_type', 'sword'),
            'requirements': getattr(item, 'requirements', {}),
        })
    elif isinstance(item, Armor):
        item_data.update({
            'defense_bonus': item.defense_bonus,
            'quality': getattr(item, 'quality', 'wooden'),
            'level': getattr(item, 'level', 1),
            'rotation': getattr(item, 'rotation', 0),
            'armor_type': getattr(item, 'armor_type', 'leather'),
            'requirements': getattr(item, 'requirements', {}),
        })
    elif isinstance(item, Potion):
        item_data.update({
            'heal_amount': item.heal_amount,
            'rotation': getattr(item, 'rotation', 0),
        })
    elif isinstance(item, Artifact):
        item_data.update({
            'effect_id': getattr(item, 'effect_id', None),
        })
    
    return item_data


def deserialize_item(item_data):
    """Восстановить предмет из словаря"""
    item_type = item_data.get('type')
    
    if item_type == 'Weapon':
        item = Weapon(
            item_data['name'],
            item_data['attack_bonus'],
            item_data['price'],
            quality=item_data.get('quality', 'wooden'),
            level=item_data.get('level', 1),
            weapon_type=item_data.get('weapon_type', 'sword'),
            requirements=item_data.get('requirements', {})
        )
        item.base_id = item_data.get('base_id')
        item.rotation = item_data.get('rotation', 0)
        item.description = item_data.get('description', '')
        # restore uid and equipped if present
        item.uid = item_data.get('uid', getattr(item, 'uid', None))
        item.equipped = item_data.get('equipped', getattr(item, 'equipped', False))
        return item
    
    elif item_type == 'Armor':
        item = Armor(
            item_data['name'],
            item_data['defense_bonus'],
            item_data['price'],
            quality=item_data.get('quality', 'wooden'),
            level=item_data.get('level', 1),
            armor_type=item_data.get('armor_type', 'leather'),
            requirements=item_data.get('requirements', {})
        )
        item.base_id = item_data.get('base_id')
        item.rotation = item_data.get('rotation', 0)
        item.description = item_data.get('description', '')
        item.uid = item_data.get('uid', getattr(item, 'uid', None))
        item.equipped = item_data.get('equipped', getattr(item, 'equipped', False))
        return item
    
    elif item_type == 'Potion':
        item = Potion(
            item_data['name'],
            item_data['heal_amount'],
            item_data['price']
        )
        item.base_id = item_data.get('base_id')
        item.rotation = item_data.get('rotation', 0)
        item.description = item_data.get('description', '')
        return item

    elif item_type == 'Artifact':
        item = Artifact(
            item_data['name'],
            item_data.get('description', ''),
            item_data['price'],
            item_data.get('effect_id')
        )
        item.base_id = item_data.get('base_id')
        item.uid = item_data.get('uid', getattr(item, 'uid', None))
        item.equipped = item_data.get('equipped', getattr(item, 'equipped', False))
        return item
    
    else:
        # Обычный предмет (например, материал)
        item = Item(
            item_data['name'],
            item_data['description'],
            item_data['price']
        )
        item.base_id = item_data.get('base_id')
        item.uid = item_data.get('uid', getattr(item, 'uid', None))
        item.equipped = item_data.get('equipped', getattr(item, 'equipped', False))
        return item


def save_game(player, inventory, rotation, victories):
    """Сохранить игру в файл"""
    try:
        # Сериализация данных игрока
        player_data = {
            'name': player.name,
            'class_id': player.class_obj.id if player.class_obj else None,
            'level': player.level,
            'exp': player.exp,
            'exp_to_next_level': player.exp_to_next_level,
            'max_hp': player.max_hp,
            'hp': player.hp,
            'attack': player.attack,
            'defense': player.defense,
            'stat_points': player.stat_points,
            'prestige_level': getattr(player, 'prestige_level', 0),
            'fire_resist': getattr(player, 'fire_resist', 0),
            'cold_resist': getattr(player, 'cold_resist', 0),
            'luck': getattr(player, 'luck', 0),
            'intellect': getattr(player, 'intellect', 0),
            'gold': player.gold,
            'passive_evade_chance': getattr(player, 'passive_evade_chance', 0.0),
        }
        
        # Сериализация экипированных предметов
        weapon_data = serialize_item(player.weapon) if player.weapon else None
        armor_data = serialize_item(player.armor) if player.armor else None
        
        # Сериализация способностей и кулдаунов
        abilities_data = {}
        for aid, (name, desc, cd) in player.abilities.items():
            abilities_data[aid] = {
                'name': name,
                'description': desc,
                'cooldown': cd,
                'current_cooldown': player.ability_cooldowns.get(aid, 0)
            }
        
        # Сериализация инвентаря
        inventory_data = {
            'max_size': inventory.max_size,
            'items': [serialize_item(item) for item in inventory.items]
        }
        
        # Общая структура сохранения
        save_data = {
            'version': VERSION,
            'player': player_data,
            'weapon': weapon_data,
            'armor': armor_data,
            'abilities': abilities_data,
            'inventory': inventory_data,
            'rotation': rotation,
            'victories': victories,
            'locale': get_locale(),
        }
        
        # Запись в файл
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return True, t('save_success')
    
    except Exception as e:
        return False, t('save_error', error=str(e))


def save_settings(locale_code: str):
    """Сохранить простые настройки (например, язык) в отдельный файл"""
    try:
        data = {'locale': locale_code}
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def _slot_filename(slot: int) -> str:
    return f"{SLOT_PREFIX}{int(slot)}.json"


def list_save_slots():
    """Вернуть словарь статусов слотов: {slot: {'exists': bool, 'mtime': float or None}}"""
    res = {}
    for i in range(1, MAX_SLOTS + 1):
        fn = _slot_filename(i)
        if os.path.exists(fn):
            info = {'exists': True, 'mtime': os.path.getmtime(fn)}
            # try to read player snapshot for display (name, class_id, level)
            try:
                with open(fn, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                player = data.get('player', {})
                info['player_name'] = player.get('name')
                info['class_id'] = player.get('class_id')
                info['level'] = player.get('level')
            except Exception:
                info['player_name'] = None
                info['class_id'] = None
                info['level'] = None
            res[i] = info
        else:
            res[i] = {'exists': False, 'mtime': None, 'player_name': None, 'class_id': None, 'level': None}
    return res


def save_game_slot(player, inventory, rotation, victories, slot: int = 1):
    """Сохранить игру в указанном слоте"""
    try:
        fn = _slot_filename(slot)
        # Reuse save_game logic but write to slot file
        player_data = {
            'name': player.name,
            'class_id': player.class_obj.id if player.class_obj else None,
            'level': player.level,
            'exp': player.exp,
            'exp_to_next_level': player.exp_to_next_level,
            'max_hp': player.max_hp,
            'hp': player.hp,
            'attack': player.attack,
            'defense': player.defense,
            'stat_points': player.stat_points,
            'prestige_level': getattr(player, 'prestige_level', 0),
            'fire_resist': getattr(player, 'fire_resist', 0),
            'cold_resist': getattr(player, 'cold_resist', 0),
            'luck': getattr(player, 'luck', 0),
            'intellect': getattr(player, 'intellect', 0),
            'gold': player.gold,
            'passive_evade_chance': getattr(player, 'passive_evade_chance', 0.0),
        }

        weapon_data = serialize_item(player.weapon) if player.weapon else None
        armor_data = serialize_item(player.armor) if player.armor else None

        abilities_data = {}
        for aid, (name, desc, cd) in player.abilities.items():
            abilities_data[aid] = {
                'name': name,
                'description': desc,
                'cooldown': cd,
                'current_cooldown': player.ability_cooldowns.get(aid, 0)
            }

        inventory_data = {
            'max_size': inventory.max_size,
            'items': [serialize_item(item) for item in inventory.items]
        }

        save_data = {
            'version': VERSION,
            'player': player_data,
            'weapon': weapon_data,
            'armor': armor_data,
            'abilities': abilities_data,
            'inventory': inventory_data,
            'rotation': rotation,
            'victories': victories,
            'locale': get_locale(),
        }

        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        return True, t('save_success')

    except Exception as e:
        return False, t('save_error', error=str(e))


def load_game_slot(slot: int = 1):
    """Загрузить игру из указанного слота"""
    try:
        fn = _slot_filename(slot)
        if not os.path.exists(fn):
            return None, t('save_file_not_found')

        with open(fn, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        # Reuse existing load logic: build player/inventory
        player_data = save_data['player']
        player = Player(player_data['name'], class_id=player_data.get('class_id'))

        player.level = player_data['level']
        player.exp = player_data['exp']
        player.exp_to_next_level = player_data['exp_to_next_level']
        player.max_hp = player_data['max_hp']
        player.hp = player_data['hp']
        player.attack = player_data['attack']
        player.defense = player_data['defense']
        player.stat_points = player_data['stat_points']
        player.prestige_level = player_data.get('prestige_level', 0)
        player.fire_resist = player_data.get('fire_resist', 0)
        player.cold_resist = player_data.get('cold_resist', 0)
        player.luck = player_data.get('luck', 0)
        player.intellect = player_data.get('intellect', 0)
        player.gold = player_data['gold']
        player.passive_evade_chance = player_data.get('passive_evade_chance', 0.0)

        abilities_data = save_data.get('abilities', {})
        player.abilities = {}
        player.ability_cooldowns = {}
        for aid, adata in abilities_data.items():
            player.abilities[aid] = (adata['name'], adata['description'], adata['cooldown'])
            player.ability_cooldowns[aid] = adata.get('current_cooldown', 0)

        inventory_data = save_data['inventory']
        inventory = Inventory(max_size=inventory_data['max_size'])
        for item_data in inventory_data['items']:
            item = deserialize_item(item_data)
            if item:
                inventory.add_item(item)

        # Restore equipped by flags or uid/back-compat
        player.weapon = None
        player.armor = None
        for item in inventory.items:
            if getattr(item, 'equipped', False):
                if hasattr(item, 'attack_bonus') and player.weapon is None:
                    player.weapon = item
                elif hasattr(item, 'defense_bonus') and player.armor is None:
                    player.armor = item
                elif hasattr(item, 'effect_id') and getattr(player, 'artifact', None) is None:
                    player.artifact = item

        if not player.weapon and save_data.get('weapon'):
            weapon_data = save_data['weapon']
            for item in inventory.items:
                if (hasattr(item, 'attack_bonus') and getattr(item, 'uid', None) == weapon_data.get('uid')):
                    player.weapon = item
                    break
            else:
                player.weapon = deserialize_item(weapon_data)

        if not player.armor and save_data.get('armor'):
            armor_data = save_data['armor']
            for item in inventory.items:
                if (hasattr(item, 'defense_bonus') and getattr(item, 'uid', None) == armor_data.get('uid')):
                    player.armor = item
                    break
            else:
                player.armor = deserialize_item(armor_data)

        rotation = save_data.get('rotation', 0)
        victories = save_data.get('victories', 0)

        return (player, inventory, rotation, victories), t('load_success')

    except Exception as e:
        return None, t('load_error', error=str(e))


def load_settings():
    """Загрузить настройки из файла, вернуть словарь или None"""
    try:
        if not os.path.exists(SETTINGS_FILE):
            return None
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Если в файле указана локаль — применим
        if 'locale' in data:
            set_locale(data['locale'])
        return data
    except Exception:
        return None


def load_game():
    """Загрузить игру из файла"""
    try:
        if not os.path.exists(SAVE_FILE):
            return None, t('save_file_not_found')
        
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # Восстановление игрока
        player_data = save_data['player']
        player = Player(player_data['name'], class_id=player_data.get('class_id'))
        
        # Восстанавливаем все характеристики
        player.level = player_data['level']
        player.exp = player_data['exp']
        player.exp_to_next_level = player_data['exp_to_next_level']
        player.max_hp = player_data['max_hp']
        player.hp = player_data['hp']
        player.attack = player_data['attack']
        player.defense = player_data['defense']
        player.stat_points = player_data['stat_points']
        player.prestige_level = player_data.get('prestige_level', 0)
        player.fire_resist = player_data.get('fire_resist', 0)
        player.cold_resist = player_data.get('cold_resist', 0)
        player.luck = player_data.get('luck', 0)
        player.intellect = player_data.get('intellect', 0)
        player.gold = player_data['gold']
        player.passive_evade_chance = player_data.get('passive_evade_chance', 0.0)
        
        # Восстанавливаем способности
        abilities_data = save_data.get('abilities', {})
        player.abilities = {}
        player.ability_cooldowns = {}
        for aid, adata in abilities_data.items():
            player.abilities[aid] = (adata['name'], adata['description'], adata['cooldown'])
            player.ability_cooldowns[aid] = adata.get('current_cooldown', 0)
        
        # Восстанавливаем инвентарь
        inventory_data = save_data['inventory']
        inventory = Inventory(max_size=inventory_data['max_size'])
        for item_data in inventory_data['items']:
            item = deserialize_item(item_data)
            if item:
                # Use add_item which will preserve existing uid/equipped if present
                inventory.add_item(item)
        
        # Восстанавливаем экипировку - сначала пробуем по флагам equipped в инвентаре
        player.weapon = None
        player.armor = None
        for item in inventory.items:
            if getattr(item, 'equipped', False):
                if hasattr(item, 'attack_bonus') and player.weapon is None:
                    player.weapon = item
                elif hasattr(item, 'defense_bonus') and player.armor is None:
                    player.armor = item
                elif hasattr(item, 'effect_id') and getattr(player, 'artifact', None) is None:
                    player.artifact = item

        # Если в save_data есть отдельные записи weapon/armor и мы не нашли предметы по флагам,
        # попытаемся восстановить их по полям (backward-compatibility)
        if not player.weapon and save_data.get('weapon'):
            weapon_data = save_data['weapon']
            for item in inventory.items:
                if (hasattr(item, 'attack_bonus') and
                    getattr(item, 'uid', None) == weapon_data.get('uid')):
                    player.weapon = item
                    break
            else:
                player.weapon = deserialize_item(weapon_data)

        if not player.armor and save_data.get('armor'):
            armor_data = save_data['armor']
            for item in inventory.items:
                if (hasattr(item, 'defense_bonus') and
                    getattr(item, 'uid', None) == armor_data.get('uid')):
                    player.armor = item
                    break
            else:
                player.armor = deserialize_item(armor_data)
        
        # Остальные параметры игры
        rotation = save_data.get('rotation', 0)
        victories = save_data.get('victories', 0)
        
        return (player, inventory, rotation, victories), t('load_success')
    
    except Exception as e:
        return None, t('load_error', error=str(e))


def has_save_file():
    """Проверить наличие файла сохранения"""
    return os.path.exists(SAVE_FILE)
