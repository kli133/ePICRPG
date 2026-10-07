"""
Тест новой системы: крит, уклонение, расширенное снаряжение
"""

from player import Player
from items import generate_equipment, ITEMS_DATABASE, ARMOR_TYPES, WEAPON_TYPES
from combat import Enemy


def test_combat_system():
    """Тест систем уклонения и крита"""
    print("=== Тест систем уклонения и критических ударов ===\n")
    
    # Создаем персонажей
    warrior = Player("Боец", "warrior")
    mage = Player("Маг", "mage")
    rogue = Player("Разбойник", "rogue")
    
    print(f"Боец: ловкость={warrior.luck}, удача для крита={int(warrior.get_crit_chance()*100)}%, уклонение={int(warrior.get_evade_chance()*100)}%")
    print(f"Маг: ловкость={mage.luck}, удача для крита={int(mage.get_crit_chance()*100)}%, уклонение={int(mage.get_evade_chance()*100)}%")
    print(f"Разбойник: ловкость={rogue.luck}, удача для крита={int(rogue.get_crit_chance()*100)}%, уклонение={int(rogue.get_evade_chance()*100)}%")
    print()
    
    # Проверим эффект уклонения с долговечностью
    rogue.luck = 20  # Много ловкости
    print(f"Разбойник с ловкостью 20:")
    print(f"  - Шанс уклонения: {int(rogue.get_evade_chance()*100)}%")
    print(f"  - Шанс крита: {int(rogue.get_crit_chance()*100)}%")
    print()
    
    # Проверим эффект атаки врага
    enemy = Enemy("Гоблин", 1, 30, 8, 2, 25, 10)
    print(f"Враг (Гоблин): шанс крита={int(enemy.get_crit_chance()*100)}%, уклонение={int(enemy.get_evade_chance()*100)}%")
    print()
    
    # Проверим новое снаряжение
    print("=== Проверка расширенного снаряжения ===\n")
    
    # Оружие для разных классов
    warrior_sword = generate_equipment('longsword', rotation=3, player_level=5)
    mage_staff = generate_equipment('arcane_staff', rotation=3, player_level=5)
    rogue_bow = generate_equipment('steel_bow', rotation=3, player_level=5)
    
    print(f"Боец с Long Sword:\n  {warrior_sword.name}")
    print(f"  Требования: {warrior_sword.requirements}")
    print(f"  Наносит урона: {warrior_sword.get_effective_bonus(warrior)}\n")
    
    print(f"Маг с Arcane Staff:\n  {mage_staff.name}")
    print(f"  Требования: {mage_staff.requirements}")
    print(f"  Наносит урона: {mage_staff.get_effective_bonus(mage)}\n")
    
    print(f"Разбойник со Steel Bow:\n  {rogue_bow.name}")
    print(f"  Требования: {rogue_bow.requirements}")
    print(f"  Наносит урона: {rogue_bow.get_effective_bonus(rogue)}\n")
    
    # Броня
    warrior_armor = generate_equipment('plate_armor', rotation=3, player_level=5)
    mage_armor = generate_equipment('enchanted_robe', rotation=3, player_level=5)
    rogue_armor = generate_equipment('shadow_leather', rotation=3, player_level=5)
    
    print(f"Боец в Plate Armor:\n  {warrior_armor.name}")
    print(f"  Требования: {warrior_armor.requirements}")
    print(f"  Защита: {warrior_armor.get_effective_bonus(warrior)}\n")
    
    print(f"Маг в Enchanted Robe:\n  {mage_armor.name}")
    print(f"  Требования: {mage_armor.requirements}")
    print(f"  Защита: {mage_armor.get_effective_bonus(mage)}\n")
    
    print(f"Разбойник в Shadow Leather:\n  {rogue_armor.name}")
    print(f"  Требования: {rogue_armor.requirements}")
    print(f"  Защита: {rogue_armor.get_effective_bonus(rogue)}\n")
    
    # Экипируем и проверим боевые характеристики
    print("=== Боевые характеристики после экипировки ===\n")
    
    warrior.weapon = warrior_sword
    warrior.armor = warrior_armor
    
    mage.weapon = mage_staff
    mage.armor = mage_armor
    
    rogue.weapon = rogue_bow
    rogue.armor = rogue_armor
    
    print(f"Боец:")
    print(f"  Атака: {warrior.attack} + {warrior_sword.get_effective_bonus(warrior)} = {warrior.get_total_attack()}")
    print(f"  Защита: {warrior.defense} + {warrior_armor.get_effective_bonus(warrior)} = {warrior.get_total_defense()}")
    print(f"  Уклонение: {int(warrior.get_evade_chance()*100)}%")
    print(f"  Крит: {int(warrior.get_crit_chance()*100)}%\n")
    
    print(f"Маг:")
    print(f"  Атака: {mage.attack} + {mage_staff.get_effective_bonus(mage)} = {mage.get_total_attack()}")
    print(f"  Защита: {mage.defense} + {mage_armor.get_effective_bonus(mage)} = {mage.get_total_defense()}")
    print(f"  Уклонение: {int(mage.get_evade_chance()*100)}%")
    print(f"  Крит: {int(mage.get_crit_chance()*100)}%\n")
    
    print(f"Разбойник:")
    print(f"  Атака: {rogue.attack} + {rogue_bow.get_effective_bonus(rogue)} = {rogue.get_total_attack()}")
    print(f"  Защита: {rogue.defense} + {rogue_armor.get_effective_bonus(rogue)} = {rogue.get_total_defense()}")
    print(f"  Уклонение: {int(rogue.get_evade_chance()*100)}%")
    print(f"  Крит: {int(rogue.get_crit_chance()*100)}%\n")
    
    print("✓ Тест успешно пройден!")


if __name__ == "__main__":
    test_combat_system()
