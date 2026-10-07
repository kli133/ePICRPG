"""
Тестирование системы улучшения снаряжения
"""
from player import Player
from inventory import Inventory
from items import generate_equipment, Item

# Создаем тестового игрока
player = Player("Тест", class_id='warrior')
player.gold = 1000
player.level = 5

# Создаем инвентарь
inventory = Inventory()

# Генерируем оружие
weapon = generate_equipment('iron_sword', rotation=0, player_level=1, quality='iron', item_level=1)
if weapon:
    inventory.add_item(weapon)
    print(f"Добавлено оружие: {weapon.name}, Атака: {weapon.attack_bonus}, Уровень: {weapon.level}")

# Добавляем камни улучшения
stone = Item("Камень улучшения", "Используется для улучшения снаряжения", 50)
stone.base_id = 'upgrade_stone'
inventory.add_item(stone)
stone2 = Item("Камень улучшения", "Используется для улучшения снаряжения", 50)
stone2.base_id = 'upgrade_stone'
inventory.add_item(stone2)
print(f"Добавлено камней улучшения: 2")

# Показываем инвентарь
print("\n=== ИНВЕНТАРЬ ===")
for i, item in enumerate(inventory.items):
    print(f"{i}. {item.name} - base_id: {getattr(item, 'base_id', 'нет')}")

# Тестируем GUI версию метода улучшения
print("\n=== ТЕСТ GUI МЕТОДА ===")
print(f"Золото игрока до улучшения: {player.gold}")

# Получаем информацию
info = inventory.upgrade_item_gui(0, player, rotation=0, stones_to_use=-1)
print(f"\nИнформация об улучшении:")
print(f"  Предмет: {info.get('item_name', 'N/A')}")
print(f"  Текущий уровень: {info.get('current_level', 'N/A')}")
print(f"  Базовая стоимость: {info.get('base_cost', 'N/A')}")
print(f"  Доступно камней: {info.get('stones_available', 'N/A')}")
print(f"  Максимум камней: {info.get('max_stones_use', 'N/A')}")

# Выполняем улучшение без камней
result = inventory.upgrade_item_gui(0, player, rotation=0, stones_to_use=0)
if 'success' in result:
    print(f"\n✓ Улучшение успешно!")
    print(f"  Новый уровень: {result['new_level']}")
    print(f"  Потрачено золота: {result['cost']}")
    print(f"  Использовано камней: {result['stones_used']}")
else:
    print(f"\n✗ Ошибка: {result.get('error', 'Неизвестная ошибка')}")

print(f"\nЗолото игрока после улучшения: {player.gold}")

# Проверяем предмет после улучшения
weapon_after = inventory.items[0]
print(f"Оружие после улучшения: {weapon_after.name}, Атака: {weapon_after.attack_bonus}, Уровень: {weapon_after.level}")

print("\n=== ТЕСТ ЗАВЕРШЁН ===")
