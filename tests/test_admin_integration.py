"""
Тест интеграции новых механик и вещей с Админ модом
Проверяет корректность работы dodge, crit, equipment scaling в админ режиме
"""

import sys
sys.path.insert(0, '/Users/user/Desktop/rpg')

from items import get_item_scaled, ITEMS_DATABASE, get_requirements_for_equipment
from player import Player
from combat import create_enemy

def test_admin_equipment_with_requirements():
    """Проверить что оборудование с requirements корректно создается в админ режиме"""
    print("=" * 60)
    print("ТЕСТ 1: Лоад оборудования с требованиями в админ режиме")
    print("=" * 60)
    
    # Создаем персонажа - воина
    player = Player("TestWarrior", "warrior")
    player.attack = 15
    player.strength = 20  # Для требований оружия
    
    # Пытаемся создать equipment dengan requirements через админ функцию
    test_weapons = [
        'iron_sword',      # warrior weapon
        'steel_sword',     # warrior weapon  
        'wooden_sword',    # basic weapon
    ]
    
    for weapon_id in test_weapons:
        print(f"\n🔍 Проверка {weapon_id}:")
        item = get_item_scaled(weapon_id, rotation=0, player_level=1, force_quality=True)
        
        if item:
            print(f"  ✓ Предмет создан: {item.name}")
            print(f"    - Атака: {getattr(item, 'attack_bonus', 'N/A')}")
            
            # Проверь requirements
            if hasattr(item, 'requirements'):
                print(f"    - Требования: {item.requirements}")
                
                # Провери effective bonus
                if hasattr(item, 'get_effective_bonus'):
                    effective = item.get_effective_bonus(player)
                    base = item.attack_bonus
                    print(f"    - Базовая атака: {base}")
                    print(f"    - Эффективная атака: {effective}")
                    print(f"    - Бонус скейлинга: +{effective - base}")
            else:
                print(f"    ⚠ Требования не установлены")
        else:
            print(f"  ✗ Ошибка: не удалось создать предмет {weapon_id}")

def test_admin_enemy_with_combat_mechanics():
    """Проверить что враги создаются с dodge и crit в админ режиме"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Враги с dodge/crit механиками в админ режиме")
    print("=" * 60)
    
    for level in [1, 5, 10, 20]:
        print(f"\n⚔️ Враг уровня {level}:")
        enemy = create_enemy(level, rotation=0)
        
        print(f"  - Name: {enemy.name}")
        print(f"  - HP: {enemy.max_hp}")
        print(f"  - Attack: {enemy.attack}")
        print(f"  - Luck: {getattr(enemy, 'luck', 'N/A')}")
        
        # Проверь методы dodge/crit
        if hasattr(enemy, 'get_evade_chance'):
            evade_chance = enemy.get_evade_chance()
            print(f"  - Evade Chance: {evade_chance * 100:.1f}%")
        else:
            print(f"  ⚠ Нет метода get_evade_chance")
            
        if hasattr(enemy, 'get_crit_chance'):
            crit_chance = enemy.get_crit_chance()
            print(f"  - Crit Chance: {crit_chance * 100:.1f}%")
        else:
            print(f"  ⚠ Нет метода get_crit_chance")
            
        # Проверь методы check
        if hasattr(enemy, 'check_evade'):
            print(f"  ✓ Есть метод check_evade")
        else:
            print(f"  ✗ Нет метода check_evade")
            
        if hasattr(enemy, 'check_crit'):
            print(f"  ✓ Есть метод check_crit")
        else:
            print(f"  ✗ Нет метода check_crit")

def test_admin_player_dodge_crit():
    """Проверить dodge/crit механики на игроке"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Dodge/Crit механики игрока")
    print("=" * 60)
    
    for player_class in ['warrior', 'mage', 'rogue']:
        print(f"\n👤 Класс: {player_class}")
        player = Player("TestChar", player_class)
        
        # Установи разные значения удачи
        for luck_val in [0, 10, 20, 30]:
            player.luck = luck_val
            
            if hasattr(player, 'get_evade_chance'):
                evade = player.get_evade_chance()
                print(f"  Luck {luck_val}: Evade {evade * 100:.1f}%", end="")
            else:
                print(f"  ⚠ Нет метода get_evade_chance")
                break
                
            if hasattr(player, 'get_crit_chance'):
                crit = player.get_crit_chance()
                print(f", Crit {crit * 100:.1f}%")
            else:
                print(f"  ⚠ Нет метода get_crit_chance")
                break

def test_admin_add_item_with_requirements():
    """Проверить добавление предмета через админ в инвентарь"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Добавление предметов с requirements через админ")
    print("=" * 60)
    
    player = Player("TestWarrior", "warrior")
    
    # Проверь что требования установлены правильно
    print("\n📋 Требования для разного оборудования:")
    
    equipment_ids = ['iron_sword', 'leather_armor', 'steel_sword', 'mage_robe']
    for eq_id in equipment_ids:
        reqs = get_requirements_for_equipment(eq_id)
        print(f"  {eq_id}: {reqs}")

def test_serialization_with_new_fields():
    """Проверить что новые поля сохраняются/загружаются"""
    print("\n" + "=" * 60)
    print("ТЕСТ 5: Сериализация новых полей equipment")
    print("=" * 60)
    
    item = get_item_scaled('iron_sword', rotation=0, player_level=1, force_quality=True)
    
    if item:
        print(f"\nПредмет: {item.name}")
        print(f"  - weapon_type: {getattr(item, 'weapon_type', 'N/A')}")
        print(f"  - armor_type: {getattr(item, 'armor_type', 'N/A')}")  
        print(f"  - requirements: {getattr(item, 'requirements', 'N/A')}")
        print(f"  - uid: {getattr(item, 'uid', 'N/A')}")
        print(f"  - equipped: {getattr(item, 'equipped', False)}")
        
        # Попробуй сохранить/загрузить
        try:
            from save_system import serialize_item, deserialize_item
            
            serialized = serialize_item(item)
            print(f"\n✓ Сериализация успешна")
            print(f"  - Ключи: {list(serialized.keys())}")
            
            deserialized = deserialize_item(serialized)
            print(f"✓ Десериализация успешна")
            print(f"  - Требования совпадают: {getattr(deserialized, 'requirements', None) == getattr(item, 'requirements', None)}")
        except Exception as e:
            print(f"✗ Ошибка при сериализации: {e}")

if __name__ == '__main__':
    try:
        test_admin_equipment_with_requirements()
        test_admin_enemy_with_combat_mechanics()
        test_admin_player_dodge_crit()
        test_admin_add_item_with_requirements()
        test_serialization_with_new_fields()
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
