"""
Тест новой системы артефактов со слотами бонусов
"""

import sys
sys.path.insert(0, r'c:\Users\user\Desktop\rpg')

from items import get_random_artifact
from player import Player
import random

def test_artifact_generation():
    """Тестировать генерацию артефактов с разными параметрами"""
    print("\n" + "="*70)
    print("ТЕСТ: Генерация артефактов со слотами бонусов")
    print("="*70)
    
    test_cases = [
        (0, 0, "Начало игры (ротация 0, удача 0)"),
        (1, 5, "Ранняя игра (ротация 1, удача 5)"),
        (3, 15, "Средняя игра (ротация 3, удача 15)"),
        (5, 25, "Поздняя игра (ротация 5, удача 25)"),
        (10, 40, "Поздняя-поздняя игра (ротация 10, удача 40)"),
    ]
    
    for rotation, luck, description in test_cases:
        print(f"\n🎲 {description}")
        print("-" * 70)
        
        for attempt in range(3):
            artifact = get_random_artifact(rotation=rotation, player_luck=luck)
            
            print(f"\n  Артефакт #{attempt + 1}: {artifact.name}")
            print(f"  Слотов: {len(artifact.bonus_slots)}")
            print(f"  Цена: {artifact.price}g")
            print(f"  Бонусы:")
            
            for i, slot in enumerate(artifact.bonus_slots, 1):
                if slot['type'] == 'stat':
                    stat = slot['stat']
                    value = slot['value']
                    print(f"    [{i}] +{value} {stat}")
                elif slot['type'] == 'crit':
                    value = slot['value']
                    print(f"    [{i}] +{value}% критический удар")
                elif slot['type'] == 'evade':
                    value = slot['value']
                    print(f"    [{i}] +{value}% уклонения")

def test_artifact_bonuses_on_player():
    """Тестировать применение бонусов артефакта к игроку"""
    print("\n\n" + "="*70)
    print("ТЕСТ: Применение бонусов артефакта к игроку")
    print("="*70)
    
    player = Player("TestWarrior", "warrior")
    
    # До артефакта
    print(f"\n👤 Персонаж: {player.name}")
    print(f"\n  До артефакта:")
    print(f"    Атака: {player.get_total_attack()}")
    print(f"    Защита: {player.get_total_defense()}")
    print(f"    Крит: {player.get_crit_chance()*100:.1f}%")
    print(f"    Уклонение: {player.get_evade_chance()*100:.1f}%")
    
    # Экипируем артефакт с бонусами
    artifact = get_random_artifact(rotation=5, player_luck=30)
    player.artifact = artifact
    
    print(f"\n  ⭐ Экипирован артефакт: {artifact.name}")
    print(f"     Бонусы: {artifact.get_slot_description()}")
    
    print(f"\n  После артефакта:")
    print(f"    Атака: {player.get_total_attack()}")
    print(f"    Защита: {player.get_total_defense()}")
    print(f"    Крит: {player.get_crit_chance()*100:.1f}%")
    print(f"    Уклонение: {player.get_evade_chance()*100:.1f}%")
    
    # Показываем какие бонусы применились
    print(f"\n  📊 Примененные бонусы:")
    for slot in artifact.bonus_slots:
        if slot['type'] == 'stat':
            stat = slot['stat']
            value = slot['value']
            actual = getattr(player, stat, 0)
            print(f"    {stat}: ✓ {value} (всего: {actual})")
        elif slot['type'] == 'crit':
            print(f"    крит: ✓ {slot['value']}% (всего: {player.get_crit_chance()*100:.1f}%)")
        elif slot['type'] == 'evade':
            print(f"    уклонение: ✓ {slot['value']}% (всего: {player.get_evade_chance()*100:.1f}%)")

def test_artifact_slot_distribution():
    """Тестировать распределение типов бонусов в слотах"""
    print("\n\n" + "="*70)
    print("ТЕСТ: Распределение типов бонусов (из 100 артефактов)")
    print("="*70)
    
    from collections import defaultdict
    stat_counts = defaultdict(int)
    slot_type_counts = defaultdict(int)
    slot_numbers = defaultdict(int)
    
    for _ in range(100):
        artifact = get_random_artifact(rotation=3, player_luck=15)
        slot_numbers[len(artifact.bonus_slots)] += 1
        
        for slot in artifact.bonus_slots:
            if slot['type'] == 'stat':
                slot_type_counts['stat'] += 1
                stat_counts[slot['stat']] += 1
            else:
                slot_type_counts[slot['type']] += 1
    
    print(f"\n📊 Количество слотов в артефактах:")
    for slots in sorted(slot_numbers.keys()):
        count = slot_numbers[slots]
        print(f"  {slots} слотов: {count} артефактов")
    
    print(f"\n📊 Распределение типов бонусов:")
    total_slots = sum(slot_type_counts.values())
    for slot_type in sorted(slot_type_counts.keys()):
        count = slot_type_counts[slot_type]
        pct = count * 100 // total_slots
        print(f"  {slot_type}: {count} ({pct}%)")
    
    print(f"\n📊 Распределение характеристик (для stat слотов):")
    total_stats = sum(stat_counts.values())
    for stat in sorted(stat_counts.keys()):
        count = stat_counts[stat]
        pct = count * 100 // total_stats
        print(f"  {stat}: {count} ({pct}%)")

if __name__ == '__main__':
    try:
        test_artifact_generation()
        test_artifact_bonuses_on_player()
        test_artifact_slot_distribution()
        
        print("\n" + "="*70)
        print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
