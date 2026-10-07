"""
Тестирование системы улучшения с использованием камней
"""
from player import Player
from inventory import Inventory
from items import generate_equipment, Item

# Создаем тестового игрока
player = Player("Тест", class_id='warrior')
player.gold = 2000
player.level = 10

# Создаем инвентарь
inventory = Inventory()

# Генерируем оружие 3 уровня
weapon = generate_equipment('iron_sword', rotation=1, player_level=5, quality='iron', item_level=3)
if weapon:
    inventory.add_item(weapon)
    print(f"Добавлено оружие: {weapon.name}, Атака: {weapon.attack_bonus}, Уровень: {weapon.level}")

# Добавляем много камней улучшения
for i in range(5):
    stone = Item("Камень улучшения", "Используется для улучшения снаряжения", 50)
    stone.base_id = 'upgrade_stone'
    inventory.add_item(stone)
print(f"Добавлено камней улучшения: 5")

# Показываем инвентарь
print("\n=== ИНВЕНТАРЬ ===")
for i, item in enumerate(inventory.items):
    base_id = getattr(item, 'base_id', 'нет')
    level = getattr(item, 'level', 'N/A')
    print(f"{i}. {item.name} - base_id: {base_id}, level: {level}")

# Тестируем GUI версию метода улучшения
print("\n=== ТЕСТ УЛУЧШЕНИЯ С КАМНЯМИ ===")
print(f"Золото игрока до улучшения: {player.gold}")

# Получаем информацию
info = inventory.upgrade_item_gui(0, player, rotation=1, stones_to_use=-1)
print(f"\nИнформация об улучшении:")
print(f"  Предмет: {info.get('item_name', 'N/A')}")
print(f"  Текущий уровень: {info.get('current_level', 'N/A')}")
print(f"  Базовая стоимость: {info.get('base_cost', 'N/A')}")
print(f"  Доступно камней: {info.get('stones_available', 'N/A')}")
print(f"  Максимум камней: {info.get('max_stones_use', 'N/A')}")

# Рассчитаем стоимость с разным количеством камней
print("\nРасчёт стоимости:")
for stones in range(0, info['max_stones_use'] + 1):
    cost = int(info['base_cost'] * (0.7 ** stones))
    print(f"  С {stones} камнями: {cost} золота (скидка {int((1 - 0.7 ** stones) * 100)}%)")

# Выполняем улучшение с 1 камнем
stones_to_use = 1
result = inventory.upgrade_item_gui(0, player, rotation=1, stones_to_use=stones_to_use)
if 'success' in result:
    print(f"\n✓ Улучшение успешно!")
    print(f"  Новый уровень: {result['new_level']}")
    print(f"  Потрачено золота: {result['cost']}")
    print(f"  Использовано камней: {result['stones_used']}")
    print(f"  Экономия: {info['base_cost'] - result['cost']} золота")
else:
    print(f"\n✗ Ошибка: {result.get('error', 'Неизвестная ошибка')}")

print(f"\nЗолото игрока после улучшения: {player.gold}")

# Проверяем предмет после улучшения
weapon_after = inventory.items[0]
print(f"Оружие после улучшения: {weapon_after.name}, Атака: {weapon_after.attack_bonus}, Уровень: {weapon_after.level}")

# Проверяем, что камень был удалён
stones_left = inventory.count_materials('upgrade_stone')
print(f"Осталось камней улучшения: {stones_left}")

print("\n=== ТЕСТ ЗАВЕРШЁН ===")
