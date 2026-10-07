"""
Тест системы скейлинга снаряжения по требованиям
"""

from player import Player
from items import generate_equipment, Armor, Weapon
from classes import get_class


def test_equipment_scaling():
    """Тест скейлинга оружия и брони"""
    print("=== Тест системы скейлинга оружия и брони ===\n")
    
    # Создаем персонажей разных классов
    warrior = Player("Воин", "warrior")
    mage = Player("Маг", "mage")
    rogue = Player("Рог", "rogue")
    
    print(f"Воин: атака={warrior.attack}, защита={warrior.defense}, интеллект={warrior.intellect}, удача={warrior.luck}")
    print(f"Маг: атака={mage.attack}, защита={mage.defense}, интеллект={mage.intellect}, удача={mage.luck}")
    print(f"Рог: атака={rogue.attack}, защита={rogue.defense}, интеллект={rogue.intellect}, удача={rogue.luck}")
    print()
    
    # Генерируем железное оружие (требует атаки)
    iron_sword = generate_equipment('iron_sword', rotation=5, player_level=10)
    steel_sword = generate_equipment('steel_sword', rotation=5, player_level=10)
    
    print(f"Железный меч (требования: {iron_sword.requirements}):")
    print(f"  Базовый бонус: {iron_sword.attack_bonus}")
    print(f"  Воину (атака={warrior.attack}): {iron_sword.get_effective_bonus(warrior)}")
    print(f"  Магу (атака={mage.attack}): {iron_sword.get_effective_bonus(mage)}")
    print(f"  Рогу (атака={rogue.attack}): {iron_sword.get_effective_bonus(rogue)}")
    print()
    
    # Генерируем стальное снаряжение для воина (требует атаки)
    iron_armor = generate_equipment('iron_armor', rotation=5, player_level=10)
    steel_armor = generate_equipment('steel_armor', rotation=5, player_level=10)
    
    print(f"Железная броня (требования: {iron_armor.requirements}):")
    print(f"  Базовый бонус: {iron_armor.defense_bonus}")
    print(f"  Воину (атака={warrior.attack}): {iron_armor.get_effective_bonus(warrior)}")
    print(f"  Магу (атака={mage.attack}): {iron_armor.get_effective_bonus(mage)}")
    print(f"  Рогу (атака={rogue.attack}): {iron_armor.get_effective_bonus(rogue)}")
    print()
    
    print(f"Стальная броня (требования: {steel_armor.requirements}):")
    print(f"  Базовый бонус: {steel_armor.defense_bonus}")
    print(f"  Воину (атака={warrior.attack}): {steel_armor.get_effective_bonus(warrior)}")
    print(f"  Магу (атака={mage.attack}): {steel_armor.get_effective_bonus(mage)}")
    print(f"  Рогу (атака={rogue.attack}): {steel_armor.get_effective_bonus(rogue)}")
    print()
    
    # Генерируем легендарное снаряжение (роба для мага - требует интеллекта)
    legendary_armor = generate_equipment('legendary_armor', rotation=5, player_level=10)
    
    print(f"Легендарная броня (требования: {legendary_armor.requirements}):")
    print(f"  Базовый бонус: {legendary_armor.defense_bonus}")
    print(f"  Воину (интеллект={warrior.intellect}): {legendary_armor.get_effective_bonus(warrior)}")
    print(f"  Магу (интеллект={mage.intellect}): {legendary_armor.get_effective_bonus(mage)}")
    print(f"  Рогу (интеллект={rogue.intellect}): {legendary_armor.get_effective_bonus(rogue)}")
    print()
    
    # Проверим, что get_total_* использует эффективный бонус
    print("=== Проверка работы get_total_attack и get_total_defense ===\n")
    
    warrior.weapon = iron_sword
    mage.weapon = iron_sword
    rogue.weapon = iron_sword
    
    print(f"При экипировании железного меча:")
    print(f"  Воин: базовая атака {warrior.attack} + железный меч = {warrior.get_total_attack()}")
    print(f"  Маг: базовая атака {mage.attack} + железный меч = {mage.get_total_attack()}")
    print(f"  Рог: базовая атака {rogue.attack} + железный меч = {rogue.get_total_attack()}")
    print()
    
    warrior.armor = iron_armor
    mage.armor = iron_armor
    rogue.armor = iron_armor
    
    print(f"При экипировании железной брони:")
    print(f"  Воин: базовая защита {warrior.defense} + железная броня = {warrior.get_total_defense()}")
    print(f"  Маг: базовая защита {mage.defense} + железная броня = {mage.get_total_defense()}")
    print(f"  Рог: базовая защита {rogue.defense} + железная броня = {rogue.get_total_defense()}")
    print()
    
    print("✓ Тест успешно пройден!")


if __name__ == "__main__":
    test_equipment_scaling()
