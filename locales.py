LOCALES = {
    'en': {
        'app_title': 'Text RPG Game',
        'welcome': 'Welcome!',
        'explore': 'Explore',
        'inventory': 'Inventory',
        'stats': 'Stats',
        'shop': 'Shop',
        'stat_points': 'Distribute Points',
        'rest': 'Rest',
        'theme': 'Theme',
        'save': 'Save',
        'load': 'Load',
        'quit': 'Quit',
        'inventory_title': 'Inventory ({count}/{max})',
        'filter_label': 'Filter:',
        'filter_all': 'All',
        'filter_weapons': 'Weapons',
        'filter_armor': 'Armor',
        'filter_potions': 'Potions',
        'filter_artifacts': 'Artifacts',
        'filter_materials': 'Materials',
        'filter_stronger': 'Stronger',
        'filter_weaker': 'Weaker',
        'show_strength': 'Show strength',
        'confirm_upgrade': 'Confirm upgrade',
        'upgrade_success': 'Item upgraded to level {level}! Cost: {cost}',
        'error': 'Error',
        'confirm': 'Confirm',
        'cancel': 'Cancel'
    },
    'ru': {
        'app_title': 'Текстовая RPG Игра',
        'language_en': 'English',
        'language_ru': 'Русский',
        'language_button': 'Язык',
        'language_switched': 'Язык переключен на {lang}',
        'welcome': 'Добро пожаловать!',
        'explore': 'Исследовать',
        'inventory': 'Инвентарь',
        'stats': 'Характеристики',
        'shop': 'Магазин',
        'stat_points': 'Распределить очки',
        'rest': 'Отдохнуть',
        'theme': 'Тема',
        'save': 'Сохранить',
        'load': 'Загрузить',
        'quit': 'Выйти',
        'inventory_title': 'Инвентарь ({count}/{max})',
        'filter_label': 'Фильтр:',
        'filter_all': 'Все',
        'filter_weapons': 'Оружие',
        'filter_armor': 'Броня',
        'filter_potions': 'Зелья',
        'filter_artifacts': 'Артефакты',
        'filter_materials': 'Материалы',
        'filter_stronger': 'Сильнее',
        'filter_weaker': 'Слабее',
        'show_strength': 'Показывать силу',
        'confirm_upgrade': 'Подтвердите улучшение',
        'upgrade_success': 'Предмет улучшен до уровня {level}! Стоимость: {cost}',
        'error': 'Ошибка',
        'confirm': 'Подтвердить',
        'cancel': 'Отмена'
    }
}

_current = 'ru'

def set_locale(code):
    global _current
    if code in LOCALES:
        _current = code


def t(key, **kwargs):
    # Возвращает перевод по ключу
    txt = LOCALES.get(_current, {}).get(key) or LOCALES.get('en', {}).get(key) or key
    if kwargs:
        try:
            return txt.format(**kwargs)
        except Exception:
            return txt
    return txt

# Дополнительные ключи (GUI диалоги)
LOCALES['en'].update({
    'game_over': 'Game Over',
    'start_new_game': 'Start a new game?',
    'exit': 'Exit',
    'save_before_quit': 'Save game before exiting?',
    'create_character_first': 'Create a character first!',
    'choose_theme': 'Choose a theme:',
    'theme_changed': 'Theme changed to: {name}',
    'language_en': 'English',
    'language_ru': 'Русский',
    'load_prompt_title': 'Load save?',
    'load_prompt_msg': 'A save was found. Load saved game?',
    'name_prompt_title': 'Character Name',
    'name_prompt_msg': 'Enter character name:',
    'class_choice_title': 'Choose class',
    'class_choice_msg': 'Choose a class (1-{max}):',
    'combat_action_title': 'Combat action',
    'choose_action': 'Choose action:',
    'attack': 'Attack',
    'use_potion': 'Use potion',
    'ability': 'Class ability',
    'run': 'Run away',
    'attack_short': 'Attack',
    'use_potion_short': 'Potion',
    'ability_short': 'Ability',
    'run_short': 'Run',
    'choose_potion_title': 'Choose potion',
    'choose_potion_label': 'Choose a potion:',
    'ability_title': 'Choose ability',
    'ability_label': 'Choose an ability:',
    'no_potions': 'You have no potions!',
    'no_abilities': 'You have no abilities!',
    'ability_on_cd': 'Ability on cooldown!',
    'use': 'Use',
    'upgrade': 'Upgrade',
    'sell': 'Sell',
    'close': 'Close',
    'shop_title': 'Shop',
    'your_gold': 'Your gold: {gold}',
    'buy': 'Buy',
    'sell_items': 'Sell items',
    'rest_title': 'Rest',
    'rest_msg': 'Rest costs {cost} gold. Restore HP to full?',
    'not_enough_gold': 'Not enough gold',
    'language_en': 'English',
    'language_ru': 'Русский',
    'language_button': 'Language',
    'language_switched': 'Language switched to {lang}'
})

LOCALES['ru'].update({
    'game_over': 'Поражение',
    'start_new_game': 'Начать новую игру?',
    'exit': 'Выход',
    'save_before_quit': 'Хотите сохранить игру перед выходом?',
    'create_character_first': 'Сначала создайте персонажа!',
    'choose_theme': 'Выберите цветовую тему:',
    'theme_changed': 'Тема изменена на: {name}',
    'language_en': 'English',
    'language_ru': 'Русский',
    'load_prompt_title': 'Загрузить игру?',
    'load_prompt_msg': 'Найдено сохранение. Загрузить сохранённую игру?',
    'name_prompt_title': 'Имя персонажа',
    'name_prompt_msg': 'Введите имя персонажа:',
    'class_choice_title': 'Выбор класса',
    'class_choice_msg': 'Выберите класс (1-{max}):',
    'combat_action_title': 'Боевое действие',
    'choose_action': 'Выберите действие:',
    'attack': 'Атаковать',
    'use_potion': 'Использовать зелье',
    'ability': 'Способность класса',
    'run': 'Убежать',
    'attack_short': 'Атака',
    'use_potion_short': 'Зелье',
    'ability_short': 'Способность',
    'run_short': 'Бежать',
    'choose_potion_title': 'Выбор зелья',
    'choose_potion_label': 'Выберите зелье:',
    'ability_title': 'Выбор способности',
    'ability_label': 'Выберите способность:',
    'no_potions': 'У вас нет зелий!',
    'no_abilities': 'У вас нет способностей!',
    'ability_on_cd': 'Способность в перезарядке!',
    'use': 'Использовать',
    'upgrade': 'Улучшить',
    'sell': 'Продать',
    'close': 'Закрыть',
    'shop_title': 'Магазин',
    'your_gold': 'Ваше золото: {gold}',
    'buy': 'Купить',
    'sell_items': 'Продать предметы',
    'rest_title': 'Отдохнуть',
    'rest_msg': 'Отдых стоит {cost} золота. Восстановить HP до максимума?',
    'not_enough_gold': 'Недостаточно золота',
    'language_label': 'Язык:'
})

# Inventory UI extras
LOCALES['en'].update({
    'search_label': 'Search:',
    'sort_label': 'Sort:',
    'sort_none': 'None',
    'sort_attack': 'Attack',
    'sort_defense': 'Defense',
    'sort_quality': 'Quality'
})

LOCALES['ru'].update({
    'search_label': 'Поиск:',
    'sort_label': 'Сортировать:',
    'sort_none': 'Нет',
    'sort_attack': 'Урон',
    'sort_defense': 'Защита',
    'sort_quality': 'Качество'
})

# In-game narrative and UI messages
LOCALES['en'].update({
    'game_banner': '     TEXT RPG GAME',
    'starting_new_game': "Couldn't load save. Starting a new game.",
    'choose_class_for': 'Choose class for {name}:',
    'created_character': '{name} ({class_name}) created!',
    'use_buttons_prompt': 'Use buttons below to control the game',
    'explore_start': 'You go exploring the surroundings...',
    'combat_begin': '⚔️  BEGIN COMBAT!',
    'encountered': 'You encountered: {name} (Level {level})',
    'enemy_hp': 'Enemy HP: {hp}/{max_hp}',
    'your_hp': 'Your HP: {hp}/{max_hp}',
    'you_attack': 'You attack {name} and deal {damage} damage!',
    'you_fled': 'You successfully fled from combat!',
    'flee_failed': 'Escape failed!',
    'enemy_stunned': '{name} is stunned and skips a turn!',
    'enemy_elemental': '{name} uses {element}-attack!',
    'enemy_hits': '{name} attacks you and deals {damage} damage!',
    'victory': '🎉 VICTORY! You defeated {name}!',
    'xp_gained': 'Gained {xp} XP!',
    'level_up_title': '🎉 LEVEL UP! You are now level {level}!',
    'hp_increase': 'HP: +20 (now {max_hp})',
    'attack_increase': 'Attack: +3 (now {attack})',
    'defense_increase': 'Defense: +2 (now {defense})',
    'stat_points_gained': 'Gained 3 stat points!',
    'stat_points_action': 'Distribute Points',
    'stat_points_label': 'Stat points',
    'gold_gained': 'Gained gold: {gold}',
    'loot_received': 'Received item: {name}',
    'rotation_increased': '--- Rotation increased! Current rotation: {rotation} ---',
    'defeat': '💀 DEFEAT! Game Over',
    'reached_level': 'You reached level {level}',
    'item_upgraded_text': 'Item upgraded to level {level}! Spent: {cost} gold',
    'stones_used_text': 'Used stones: {stones}',
    'item_sold_text': 'Item sold. Gained {gold} gold.',
    'character_stats': '📊 CHARACTER STATS',
    'stat_name': 'Name: {name}',
    'stat_class': 'Class: {class_name}',
    'stat_level': 'Level: {level}',
    'stat_exp': 'Exp: {exp}/{next}',
    'stat_hp': 'HP: {hp}/{max_hp}',
    'stat_attack': 'Attack: {attack} (total: {total_attack})',
    'stat_defense': 'Defense: {defense} (total: {total_defense})',
    'stat_fire_resist': 'Fire resist: {val}%',
    'stat_cold_resist': 'Cold resist: {val}%',
    'stat_luck': 'Luck: {val}',
    'stat_intellect': 'Intellect: {val}',
    'stat_gold': 'Gold: {gold}',
    'stat_points': 'Stat points: {pts}',
    'stat_weapon': 'Weapon: {name}',
    'stat_armor': 'Armor: {name}',
    'stat_separator': '{sep}',
    'stat_improved': 'Stat improved! Remaining points: {pts}',
    'rested': 'You rested at the tavern for {cost} gold.',
    'restored_hp': 'HP restored: {hp}/{max_hp}',
    'theme_dark': 'Dark',
    'theme_light': 'Light',
    'theme_cyberpunk': 'Cyberpunk',
    'theme_forest': 'Forest',
    'theme_sunset': 'Sunset',
    'equipped_tag': ' [Equipped]',
    'stronger_tag': ' [Stronger]',
    'weaker_tag': ' [Weaker]',
    'equal_tag': ' [Equal]',
    'you_have_gold': 'You have: {gold} gold',
    'shop_item_line': '{index}. {name} - {price} gold',
    'status_ready': 'ready',
    'status_cd': 'cooldown {rc}',
    'default_hero_name': 'Hero',
    'stat_option_hp': 'Health (+15 HP)',
    'stat_option_attack': 'Attack (+2)',
    'stat_option_defense': 'Defense (+2)',
    'stat_option_fire_resist': 'Fire Resist (+2)',
    'stat_option_cold_resist': 'Cold Resist (+2)',
    'stat_option_luck': 'Luck (+1)',
    'stat_option_intellect': 'Intellect (+1)'
    , 'need_gold': 'Need {price} gold!'
})

LOCALES['ru'].update({
    'game_banner': '     ТЕКСТОВАЯ RPG ИГРА',
    'starting_new_game': 'Не удалось загрузить сохранение. Начинаем новую игру.',
    'choose_class_for': 'Выберите класс для {name}:',
    'created_character': '{name} ({class_name}) создан!',
    'use_buttons_prompt': 'Используйте кнопки ниже для управления игрой',
    'explore_start': 'Вы отправляетесь исследовать окрестности...',
    'combat_begin': '⚔️  НАЧАЛО БОЯ!',
    'encountered': 'Вы встретили: {name} (Уровень {level})',
    'enemy_hp': 'Здоровье врага: {hp}/{max_hp}',
    'your_hp': 'Ваше HP: {hp}/{max_hp}',
    'you_attack': 'Вы атакуете {name} и наносите {damage} урона!',
    'you_fled': 'Вы успешно сбежали от боя!',
    'flee_failed': 'Побег не удался!',
    'enemy_stunned': '{name} оглушён и пропускает ход!',
    'enemy_elemental': '{name} использует {element}-атаку!',
    'enemy_hits': '{name} атакует вас и наносит {damage} урона!',
    'victory': '🎉 ПОБЕДА! Вы победили {name}!',
    'xp_gained': 'Получено {xp} опыта!',
    'level_up_title': '🎉 ПОВЫШЕНИЕ УРОВНЯ! Теперь вы {level} уровня!',
    'hp_increase': 'Здоровье: +20 (теперь {max_hp})',
    'attack_increase': 'Атака: +3 (теперь {attack})',
    'defense_increase': 'Защита: +2 (теперь {defense})',
    'stat_points_gained': 'Получено 3 очка характеристик!',
    'stat_points_action': 'Распределить очки',
    'stat_points_label': 'Очки характеристик',
    'gold_gained': 'Получено золота: {gold}',
    'loot_received': 'Получен предмет: {name}',
    'rotation_increased': '--- Ротация увеличена! Текущая ротация: {rotation} ---',
    'defeat': '💀 ПОРАЖЕНИЕ! Game Over',
    'reached_level': 'Вы достигли {level} уровня',
    'item_upgraded_text': 'Предмет улучшен до уровня {level}! Потрачено: {cost} золота',
    'stones_used_text': 'Использовано камней: {stones}',
    'item_sold_text': 'Предмет продан. Получено {gold} золота.',
    'character_stats': '📊 ХАРАКТЕРИСТИКИ ПЕРСОНАЖА',
    'stat_name': 'Имя: {name}',
    'stat_class': 'Класс: {class_name}',
    'stat_level': 'Уровень: {level}',
    'stat_exp': 'Опыт: {exp}/{next}',
    'stat_hp': 'Здоровье: {hp}/{max_hp}',
    'stat_attack': 'Атака: {attack} (всего: {total_attack})',
    'stat_defense': 'Защита: {defense} (всего: {total_defense})',
    'stat_fire_resist': 'Сопротивление огню: {val}%',
    'stat_cold_resist': 'Сопротивление холоду: {val}%',
    'stat_luck': 'Удача: {val}',
    'stat_intellect': 'Интеллект: {val}',
    'stat_gold': 'Золото: {gold}',
    'stat_points': 'Очки характеристик: {pts}',
    'stat_weapon': 'Оружие: {name}',
    'stat_armor': 'Броня: {name}',
    'stat_separator': '{sep}',
    'stat_improved': 'Характеристика улучшена! Осталось очков: {pts}',
    'rested': 'Вы отдохнули в таверне за {cost} золота.',
    'restored_hp': 'Здоровье восстановлено: {hp}/{max_hp}',
    'theme_dark': 'Темная',
    'theme_light': 'Светлая',
    'theme_cyberpunk': 'Киберпанк',
    'theme_forest': 'Лесная',
    'theme_sunset': 'Закат',
    'equipped_tag': ' [Экипировано]',
    'stronger_tag': ' [Сильнее]',
    'weaker_tag': ' [Слабее]',
    'equal_tag': ' [Равное]',
    'you_have_gold': 'У вас: {gold} золота',
    'shop_item_line': '{index}. {name} - {price} золота',
    'status_ready': 'готова',
    'status_cd': 'перезарядка {rc}',
    'default_hero_name': 'Герой',
    'stat_option_hp': 'Здоровье (+15 HP)',
    'stat_option_attack': 'Атака (+2)',
    'stat_option_defense': 'Защита (+2)',
    'stat_option_fire_resist': 'Сопротивление огню (+2)',
    'stat_option_cold_resist': 'Сопротивление холоду (+2)',
    'stat_option_luck': 'Удача (+1)',
    'stat_option_intellect': 'Интеллект (+1)'
    , 'need_gold': 'Нужно {price} золота!'
})

# Upgrade dialog fragments
LOCALES['en'].update({
    'upgrade_info_title': 'Upgrade {item}',
    'upgrade_current_level': 'Current level: {level}',
    'upgrade_base_cost': 'Base cost: {cost} gold',
    'upgrade_stones_available': 'You have upgrade stones: {count}',
    'upgrade_max_stones': 'You can use up to {max} stones',
    'upgrade_each_reduces': '(each reduces price by 30%)',
    'upgrade_how_many': 'How many stones to use? (0-{max})',
    'upgrade_confirm_title': 'Confirm upgrade',
    'upgrade_confirm_cost': 'Cost: {cost} gold',
    'upgrade_stones_title': 'Upgrade stones',
    'upgrade_confirm_msg': 'Upgrade {item}?\n\nCost: {cost} gold\nWill use stones: {stones}\n\nYou have: {gold} gold',
    'already_max_hp': 'You already have maximum HP!',
    'stat_points_title': 'Stat Points: {pts}',
    'stat_points_available': 'Available points: {pts}',
    'none': 'None',
    'info_label_format': '💚 HP: {hp}/{max}  |  ⭐ Level: {level}  |  ✨ Prestige: {prestige}  |  💰 Gold: {gold}  |  🔁 Rotation: {rotation}',
    'prestige': 'Prestige',
    'prestige_title': 'Prestige',
    'prestige_bonuses_title': 'Prestige Bonuses',
    'prestige_locked': 'Reach level {level} to prestige.',
    'prestige_req': 'Requirement: level {level}',
    'prestige_current': 'Current bonuses',
    'prestige_next': 'Next prestige bonuses',
    'prestige_reset_note': 'Prestige resets level, stats, items, gold, and rotation.',
    'prestige_now': 'Prestige now',
    'prestige_confirm_short': 'Prestige to level {level}? This will reset progress.',
    'prestige_bonus_line': '{label}: +{value}',
    'prestige_bonus_pct': '{label}: +{value}%',
    'prestige_sp_label': 'Stat points',
    'prestige_xp_label': 'EXP',
    'prestige_gold_label': 'Gold',
    'prestige_loot_label': 'Loot',
    'prestige_done': 'Prestige complete! You are now Prestige {level}.'
})

LOCALES['ru'].update({
    'upgrade_info_title': 'Улучшение {item}',
    'upgrade_current_level': 'Текущий уровень: {level}',
    'upgrade_base_cost': 'Базовая стоимость: {cost} золота',
    'upgrade_stones_available': 'У вас камней улучшения: {count}',
    'upgrade_max_stones': 'Можно использовать до {max} камней',
    'upgrade_each_reduces': '(каждый уменьшает цену на 30%)',
    'upgrade_how_many': 'Сколько камней использовать? (0-{max})',
    'upgrade_confirm_title': 'Подтверждение улучшения',
    'upgrade_confirm_cost': 'Стоимость: {cost} золота',
    'upgrade_stones_title': 'Камни улучшения',
    'upgrade_confirm_msg': 'Улучшить {item}?\n\nСтоимость: {cost} золота\nБудет использовано камней: {stones}\n\nУ вас: {gold} золота',
    'already_max_hp': 'У вас уже максимальное здоровье!',
    'stat_points_title': 'Очки характеристик: {pts}',
    'stat_points_available': 'Доступно очков: {pts}',
    'none': 'Нет',
    'info_label_format': '💚 HP: {hp}/{max}  |  ⭐ Уровень: {level}  |  ✨ Престиж: {prestige}  |  💰 Золото: {gold}  |  🔁 Ротация: {rotation}',
    'prestige': 'Престиж',
    'prestige_title': 'Престиж',
    'prestige_bonuses_title': 'Бонусы престижа',
    'prestige_locked': 'Нужен {level} уровень для престижа.',
    'prestige_req': 'Требование: уровень {level}',
    'prestige_current': 'Текущие бонусы',
    'prestige_next': 'Бонусы следующего престижа',
    'prestige_reset_note': 'Престиж сбрасывает уровень, характеристики, предметы, золото и ротацию.',
    'prestige_now': 'Сделать престиж',
    'prestige_confirm_short': 'Сделать престиж {level} уровня? Прогресс будет сброшен.',
    'prestige_bonus_line': '{label}: +{value}',
    'prestige_bonus_pct': '{label}: +{value}%',
    'prestige_sp_label': 'Очки характеристик',
    'prestige_xp_label': 'Опыт',
    'prestige_gold_label': 'Золото',
    'prestige_loot_label': 'Лут',
    'prestige_done': 'Престиж выполнен! Теперь у вас Престиж {level}.'
})


# Save/load messages
LOCALES['en'].update({
    'save_success': 'Game saved successfully!',
    'autosave_done': 'Autosave updated.',
    'save_error': 'Error saving game: {error}',
    'load_error': 'Error loading game: {error}',
    'save_file_not_found': 'Save file not found!',
    'load_success': 'Game loaded successfully!'
})

LOCALES['ru'].update({
    'save_success': 'Игра сохранена успешно!',
    'autosave_done': 'Автосохранение обновлено!',
    'save_error': 'Ошибка при сохранении: {error}',
    'load_error': 'Ошибка при загрузке: {error}',
    'save_file_not_found': 'Файл сохранения не найден!',
    'load_success': 'Игра загружена успешно!'
})

# Inventory / items console messages
LOCALES['en'].update({
    'inventory_full': 'Inventory is full!',
    'received_item': 'Received item: {name}',
    'inventory_empty': 'Your inventory is empty!',
    'section_other': 'Other',
    'attack_label': 'Attack: {val}',
    'defense_label': 'Defense: {val}',
    'heal_label': 'Heal: {val} HP',
    'price_in_shop': 'Price (shop): {price}',
    'invalid_index': 'Invalid item number!',
    'type_weapon': 'Type: Weapon | Level: {level} | Quality: {quality} | Rotation: R{rotation}',
    'type_armor': 'Type: Armor | Level: {level} | Quality: {quality} | Rotation: R{rotation}',
    'type_potion': 'Type: Potion | Heal: {heal} HP',
    'type_material': 'Type: Material',
    'sell_will_get': 'You will get {price} gold for {name}.',
    'sell_confirm_prompt': 'Confirm sale? (y/n): ',
    'sale_cancelled': 'Sale cancelled.',
    'item_sold_console': 'Item sold. Gained {gold} gold.',
    'upgrade_not_upgradable': 'This item cannot be upgraded.',
    'upgrade_failed': 'Failed to upgrade the item.'
})

LOCALES['ru'].update({
    'inventory_full': 'Инвентарь полон!',
    'received_item': 'Получен предмет: {name}',
    'inventory_empty': 'Ваш инвентарь пуст!',
    'section_other': 'Прочее',
    'attack_label': 'Атака: {val}',
    'defense_label': 'Защита: {val}',
    'heal_label': 'Восстановление: {val} HP',
    'price_in_shop': 'Цена (в магазине): {price}',
    'invalid_index': 'Неверный номер предмета!',
    'type_weapon': 'Тип: Оружие | Уровень: {level} | Качество: {quality} | Ротация: R{rotation}',
    'type_armor': 'Тип: Броня | Уровень: {level} | Качество: {quality} | Ротация: R{rotation}',
    'type_potion': 'Тип: Зелье | Восстановление: {heal} HP',
    'type_material': 'Тип: Материал',
    'sell_will_get': 'Вы получите {price} золота за {name}.',
    'sell_confirm_prompt': 'Подтвердить продажу? (y/n): ',
    'sale_cancelled': 'Продажа отменена.',
    'item_sold_console': 'Предмет продан. Получено {gold} золота.',
    'upgrade_not_upgradable': 'Этот предмет нельзя улучшить.',
    'upgrade_failed': 'Не удалось улучшить предмет.'
})

LOCALES['en'].update({
    'upgrade_cancelled': 'Upgrade cancelled.',
    'label_name': 'Name: {name}',
    'label_description': 'Description: {text}',
    'label_base_id': 'Base ID: {id}'
})

LOCALES['ru'].update({
    'upgrade_cancelled': 'Улучшение отменено.',
    'label_name': 'Название: {name}',
    'label_description': 'Описание: {text}',
    'label_base_id': 'Базовый ID: {id}'
})

# Player messages
LOCALES['en'].update({
    'evade_success': 'You evaded the attack!',
    'passive_evade': 'Passive evade! You avoided damage.',
    'resist_fire_reduce': 'Fire resistance reduces damage by {pct}%.',
    'resist_cold_reduce': 'Cold resistance reduces damage by {pct}%.',
    'ability_unavailable': 'Ability unavailable (on cooldown or missing).',
    'used_potion': 'You used {item} and restored {hp} HP! Current HP: {hp_now}/{max_hp}'
})

LOCALES['ru'].update({
    'evade_success': 'Вы уклонились от атаки!',
    'passive_evade': 'Пассивное уклонение! Вы избежали урона.',
    'resist_fire_reduce': 'Сопротивление огню снижает урон на {pct}%.',
    'resist_cold_reduce': 'Сопротивление холоду снижает урон на {pct}%.',
    'ability_unavailable': 'Способность недоступна (в перезарядке или не существует).',
    'used_potion': 'Вы использовали {item} и восстановили {hp} HP! Текущее здоровье: {hp_now}/{max_hp}'
})

# Combat / prompts
LOCALES['en'].update({
    'round_header': '--- Round {n} ---',
    'choose_potion_prompt': 'Potion number (0 - cancel): ',
    'invalid_input': 'Invalid input!',
    'invalid_choice': 'Invalid choice!',
    'defeated_by': 'You were defeated by {name}...',
})

LOCALES['ru'].update({
    'round_header': '--- Раунд {n} ---',
    'choose_potion_prompt': 'Номер зелья (0 - отмена): ',
    'invalid_input': 'Неверный ввод!',
    'invalid_choice': 'Неверный выбор!',
    'defeated_by': 'Вы были побеждены {name}...'
})

# Item description templates
LOCALES['en'].update({
    'potion_description': 'Restores {heal} HP',
    'weapon_description': 'Attack +{val}',
    'armor_description': 'Defense +{val}'
})

LOCALES['ru'].update({
    'potion_description': 'Восстанавливает {heal} HP',
    'weapon_description': 'Атака +{val}',
    'armor_description': 'Защита +{val}'
})

# Additional confirmation and small messages
LOCALES['en'].update({
    'sell_item_title': 'Sell item',
    'sell_item_msg': 'Sell {name} for {price} gold?',
    'no_stat_points': 'You have no available stat points!',
    'equipment_title': '⚔️ Equipment',
    'purchased': 'You purchased {item}!',
    'nothing_to_save': 'Nothing to save!'
    , 'rarity': 'Rarity: {rarity} {icon}',
    'compare_with': 'Compare with equipped:'
    , 'equip_slot_weapon': 'Weapon slot',
    'equip_slot_armor': 'Armor slot',
    'equip_slot_artifact': 'Artifact slot',
    'drop_to_equip': 'Drop item here to equip',
    'unequip': 'Unequip'
    , 'small_potion_name': 'Small Health Potion'
    , 'medium_potion_name': 'Medium Health Potion'
    , 'large_potion_name': 'Large Health Potion'
    , 'sword_name': 'Sword'
    , 'armor_name': 'Armor'
    , 'upgrade_stone_name': 'Upgrade Stone'
    , 'upgrade_stone_desc': 'Material used to upgrade equipment'
    , 'artifact_blood_thorn_name': 'Bloodthorn Relic'
    , 'artifact_blood_thorn_desc': 'Steals a portion of damage as HP.'
    , 'artifact_storm_lens_name': 'Storm Lens'
    , 'artifact_storm_lens_desc': 'Attacks can briefly stun enemies.'
    , 'artifact_greed_idol_name': 'Idol of Greed'
    , 'artifact_greed_idol_desc': 'Increases gold and loot chance.'
    , 'artifact_aegis_sigil_name': 'Aegis Sigil'
    , 'artifact_aegis_sigil_desc': 'Reduces damage taken.'
    , 'artifact_chrono_shard_name': 'Chrono Shard'
    , 'artifact_chrono_shard_desc': 'Reduces ability cooldowns faster.'
    , 'artifact_equipped': 'Artifact equipped: {name}'
    , 'artifact_unequipped': 'Artifact removed: {name}'
    , 'artifact_found': 'Found artifact: {name}'
    , 'artifact_lifesteal': 'Artifact restores {heal} HP.'
    , 'artifact_stun': 'Artifact effect: enemy stunned!'
    , 'removed_item': 'Removed {name}'
    , 'equipped_item': 'You equipped {name}! Attack: {stat}'
    , 'equipped_item_armor': 'You equipped {name}! Defense: {stat}'
    , 'quality_wooden': 'Wooden'
    , 'quality_rusty': 'Rusty'
    , 'quality_iron': 'Iron'
    , 'quality_silver': 'Silver'
    , 'quality_luxury': 'Luxury'
    , 'quality_dragon': 'Dragon'
    , 'save_slots_title': 'Save slots'
    , 'load_slots_title': 'Load slots'
    , 'slot_empty': 'Empty'
    , 'slot_filled': 'Saved'
    , 'delete': 'Delete'
    , 'slot_deleted': 'Slot deleted'
    , 'save_slot_label': 'Slot {slot}'
    , 'autosave_slot_label': 'Autosave'
    # Stat names
    , 'stat_attack': 'Attack'
    , 'stat_defense': 'Defense'
    , 'stat_intellect': 'Intellect'
    , 'stat_luck': 'Luck'
    , 'stat_fire_resist': 'Fire Resistance'
    , 'stat_cold_resist': 'Cold Resistance'
    , 'stat_max_hp': 'Max HP'
    , 'requirement_met': '✓ Requirement met'
    , 'requirement_not_met': '✗ Requirement not met'
})

LOCALES['ru'].update({
    'sell_item_title': 'Продажа предмета',
    'sell_item_msg': 'Продать {name} за {price} золота?',
    'no_stat_points': 'У вас нет доступных очков характеристик!',
    'equipment_title': '⚔️ Экипировка',
    'purchased': 'Вы купили {item}!',
    'nothing_to_save': 'Нечего сохранять!'
    , 'rarity': 'Редкость: {rarity} {icon}',
    'compare_with': 'Сравнение с экипировкой:'
    , 'equip_slot_weapon': 'Слот оружия',
    'equip_slot_armor': 'Слот брони',
    'equip_slot_artifact': 'Слот артефакта',
    'drop_to_equip': 'Перетащите предмет сюда, чтобы экипировать',
    'unequip': 'Снять'
    , 'small_potion_name': 'Малое зелье здоровья'
    , 'medium_potion_name': 'Среднее зелье здоровья'
    , 'large_potion_name': 'Большое зелье здоровья'
    , 'sword_name': 'Меч'
    , 'armor_name': 'Броня'
    , 'upgrade_stone_name': 'Камень улучшения'
    , 'upgrade_stone_desc': 'Материал для улучшения экипировки'
    , 'artifact_blood_thorn_name': 'Реликт Кровошип'
    , 'artifact_blood_thorn_desc': 'Крадет часть урона в здоровье.'
    , 'artifact_storm_lens_name': 'Линза Бури'
    , 'artifact_storm_lens_desc': 'Атаки могут оглушать врага.'
    , 'artifact_greed_idol_name': 'Идол Жадности'
    , 'artifact_greed_idol_desc': 'Увеличивает золото и шанс лута.'
    , 'artifact_aegis_sigil_name': 'Печать Эгиды'
    , 'artifact_aegis_sigil_desc': 'Снижает получаемый урон.'
    , 'artifact_chrono_shard_name': 'Осколок Хроноса'
    , 'artifact_chrono_shard_desc': 'Быстрее снижает кулдауны способностей.'
    , 'artifact_equipped': 'Артефакт экипирован: {name}'
    , 'artifact_unequipped': 'Артефакт снят: {name}'
    , 'artifact_found': 'Найден артефакт: {name}'
    , 'artifact_lifesteal': 'Артефакт восстановил {heal} HP.'
    , 'artifact_stun': 'Эффект артефакта: враг оглушен!'
    , 'removed_item': 'Вы сняли {name}'
    , 'equipped_item': 'Вы экипировали {name}! Атака: {stat}'
    , 'equipped_item_armor': 'Вы экипировали {name}! Защита: {stat}'
    , 'quality_wooden': 'Деревянное'
    , 'quality_rusty': 'Ржавое'
    , 'quality_iron': 'Железное'
    , 'quality_silver': 'Серебряное'
    , 'quality_luxury': 'Роскошное'
    , 'quality_dragon': 'Драконье'
    , 'save_slots_title': 'Слоты сохранений'
    , 'load_slots_title': 'Слоты загрузки'
    , 'slot_empty': 'Пусто'
    , 'slot_filled': 'Сохранено'
    , 'delete': 'Удалить'
    , 'slot_deleted': 'Слот удалён'
    , 'save_slot_label': 'Слот {slot}'
    , 'autosave_slot_label': 'Автосохранение'
    # Названия характеристик
    , 'stat_attack': 'Атака'
    , 'stat_defense': 'Защита'
    , 'stat_intellect': 'Интеллект'
    , 'stat_luck': 'Удача'
    , 'stat_fire_resist': 'Сопротивление огню'
    , 'stat_cold_resist': 'Сопротивление холоду'
    , 'stat_max_hp': 'Макс. HP'
    , 'requirement_met': '✓ Требование выполнено'
    , 'requirement_not_met': '✗ Требование не выполнено'
})

# Crafting locale entries removed (crafting UI disabled).


def get_locale():
    return _current
