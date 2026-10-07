"""
Test: Животные враги не должны использовать магические атаки
"""

import sys
sys.path.insert(0, r'c:\Users\user\Desktop\rpg')

from combat import create_enemy, can_use_magic, ANIMAL_ENEMIES

def test_animal_enemies_no_magic():
    """Проверить что животные враги не используют магию"""
    print("\n" + "="*70)
    print("ТЕСТ: Животные враги не используют магические атаки")
    print("="*70)
    
    # Тестируем врагов разных уровней
    test_cases = [
        (1, "Крыса", False, "🐭 Животное - магия запрещена"),
        (1, "Гоблин", False, "👹 Тупое существо - магия запрещена"),
        (2, "Волк", False, "🐺 Животное - магия запрещена"),
        (3, "Огр", False, "👹 Тупой враг - магия запрещена"),
        (3, "Скелет-маг", True, "🧙 Маг - может использовать магию"),
        (4, "Некромант", True, "🧙 Маг - может использовать магию"),
        (5, "Виверна", True, "🐉 Виверна с огненным дыханием - может использовать магию"),
    ]
    
    print("\n📋 Результаты проверки:\n")
    
    all_passed = True
    for level, expected_partial_name, should_use_magic, description in test_cases:
        for _ in range(5):  # Пробуем несколько раз для получения нужного врага
            enemy = create_enemy(level, rotation=0)
            if expected_partial_name in enemy.name:
                can_use = can_use_magic(enemy)
                status = "✅" if can_use == should_use_magic else "❌"
                
                if can_use != should_use_magic:
                    all_passed = False
                
                print(f"  {status} {description}")
                print(f"     Враг: {enemy.name}")
                print(f"     Может использовать магию: {can_use} (ожидалось: {should_use_magic})")
                
                # Проверяем что враг в списке животных если не может использовать магию
                if not should_use_magic:
                    is_animal = any(animal in enemy.name for animal in ANIMAL_ENEMIES)
                    print(f"     Животное: {is_animal}")
                
                print()
                break
    
    print("="*70)
    if all_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ - Животные враги не используют магию!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
    print("="*70)
    
    return all_passed

def test_animal_list():
    """Показать полный список животных врагов"""
    print("\n" + "="*70)
    print("📑 Полный список животных врагов (не могут использовать магию)")
    print("="*70)
    
    print("\nЖивотные враги:")
    for i, animal in enumerate(sorted(ANIMAL_ENEMIES), 1):
        print(f"  {i}. {animal}")
    
    print(f"\nВсего животных: {len(ANIMAL_ENEMIES)}")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        test_animal_list()
        result = test_animal_enemies_no_magic()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
