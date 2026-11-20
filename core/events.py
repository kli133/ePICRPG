"""
Система событий с конструктором для легкого добавления новых событий
Позволяет создавать события с выборами, зависимыми от характеристик игрока
"""
import random
from typing import List, Dict, Callable, Any, Optional, Tuple


class EventOutcome:
    """Исход события после выбора"""
    
    def __init__(self, text: str, effects: Dict[str, int] = None, 
                 reward_gold: int = 0, reward_exp: int = 0, 
                 condition_check: Callable[[Any], bool] = None):
        """
        text: Описание исхода события
        effects: Словарь изменений характеристик {stat_name: amount}
        reward_gold: Награда золотом
        reward_exp: Награда опытом
        condition_check: Функция для проверки условия (если None, всегда успех)
        """
        self.text = text
        self.effects = effects or {}
        self.reward_gold = reward_gold
        self.reward_exp = reward_exp
        self.condition_check = condition_check
    
    def check_success(self, player) -> Tuple[bool, str]:
        """
        Проверить, успешен ли исход для игрока
        Возвращает (success, message)
        """
        if self.condition_check is None:
            return True, self.text
        
        try:
            success = self.condition_check(player)
            if success:
                return True, self.text
            else:
                return False, f"{self.text} (Неудача)"
        except Exception as e:
            print(f"Ошибка при проверке условия: {e}")
            return False, f"{self.text} (Ошибка)"


class EventChoice:
    """Выбор в событии с несколькими возможными исходами"""
    
    def __init__(self, text: str, outcomes: List[EventOutcome], 
                 required_stat: str = None, required_value: int = 0):
        """
        text: Текст выбора
        outcomes: Список возможных исходов (будет выбран случайный)
        required_stat: Характеристика для проверки доступности выбора
        required_value: Минимальное значение характеристики для использования
        """
        self.text = text
        self.outcomes = outcomes
        self.required_stat = required_stat
        self.required_value = required_value
    
    def is_available(self, player) -> bool:
        """Проверить доступность выбора для игрока"""
        if self.required_stat is None:
            return True
        
        player_value = getattr(player, self.required_stat, 0)
        return player_value >= self.required_value
    
    def execute(self, player) -> Tuple[str, Dict[str, int], int, int]:
        """
        Выполнить выбор
        Возвращает (outcome_text, effects, gold, exp)
        """
        # Выбираем случайный исход (в будущем можно добавить вероятности)
        outcome = random.choice(self.outcomes)
        success, message = outcome.check_success(player)
        
        # Если условие не выполнено, применяем штраф (уменьшенные награды)
        if not success:
            gold = max(0, outcome.reward_gold // 2)
            exp = max(0, outcome.reward_exp // 2)
        else:
            gold = outcome.reward_gold
            exp = outcome.reward_exp
        
        return message, outcome.effects, gold, exp


class Event:
    """Основной класс события"""
    
    def __init__(self, event_id: str, title: str, description: str, 
                 choices: List[EventChoice], location: str = "", 
                 difficulty: str = "normal", can_ignore: bool = True):
        """
        event_id: Уникальный идентификатор события
        title: Название события
        description: Описание/текст события
        choices: Список выборов для игрока
        location: Место события (для группировки)
        difficulty: Сложность (easy, normal, hard, deadly)
        can_ignore: Можно ли проигнорировать событие (False для нападений)
        """
        self.event_id = event_id
        self.title = title
        self.description = description
        self.choices = choices
        self.location = location
        self.difficulty = difficulty
        self.can_ignore = can_ignore
    
    def get_available_choices(self, player) -> List[Tuple[int, EventChoice]]:
        """Получить доступные для игрока выборы"""
        available = []
        for idx, choice in enumerate(self.choices):
            if choice.is_available(player):
                available.append((idx, choice))
        return available
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать событие в словарь (для сохранения/отладки)"""
        return {
            'id': self.event_id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'difficulty': self.difficulty,
            'choices_count': len(self.choices)
        }


class EventManager:
    """Менеджер для управления событиями"""
    
    def __init__(self):
        self.events: Dict[str, Event] = {}
        self.event_weights: Dict[str, int] = {}  # Вероятности событий
    
    def register_event(self, event: Event, weight: int = 1) -> None:
        """Зарегистрировать событие в менеджере"""
        self.events[event.event_id] = event
        self.event_weights[event.event_id] = weight
    
    def register_events(self, events: List[Tuple[Event, int]]) -> None:
        """Зарегистрировать список событий с их весами"""
        for event, weight in events:
            self.register_event(event, weight)
    
    def get_random_event(self) -> Optional[Event]:
        """Получить случайное событие с учётом весов"""
        if not self.events:
            return None
        
        event_ids = list(self.events.keys())
        weights = [self.event_weights.get(eid, 1) for eid in event_ids]
        
        selected_id = random.choices(event_ids, weights=weights, k=1)[0]
        return self.events[selected_id]
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """Получить событие по ID"""
        return self.events.get(event_id)
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Получить событие по ID (алиас для get_event)"""
        return self.get_event(event_id)
    
    def list_events(self) -> List[Dict[str, Any]]:
        """Получить список всех событий"""
        return [event.to_dict() for event in self.events.values()]
    
    def get_event_count(self) -> int:
        """Получить количество зарегистрированных событий"""
        return len(self.events)


# ============================================================================
# Вспомогательные функции для создания условий
# ============================================================================

def stat_check(stat_name: str, min_value: int = 0, 
               threshold: int = None) -> Callable:
    """
    Создать проверку характеристики
    
    stat_name: Название характеристики (attack, defense, luck и т.д.)
    min_value: Минимальное значение для успеха
    threshold: Альтернативно, проверка > threshold (если указано)
    """
    def check(player) -> bool:
        value = getattr(player, stat_name, 0)
        if threshold is not None:
            return value > threshold
        return value >= min_value
    return check


def luck_check(success_chance: float = 0.5) -> Callable:
    """Проверка удачи с заданным шансом успеха"""
    def check(player) -> bool:
        luck_bonus = getattr(player, 'luck', 0) * 0.01
        final_chance = min(0.95, success_chance + luck_bonus)
        return random.random() < final_chance
    return check


def combined_check(stat_name: str, stat_weight: float = 0.7,
                   luck_weight: float = 0.3, base_chance: float = 0.5) -> Callable:
    """
    Комбинированная проверка: сочетание характеристики и удачи
    
    stat_weight: Вес характеристики (0.0-1.0)
    luck_weight: Вес удачи (0.0-1.0)
    base_chance: Базовый шанс успеха
    """
    def check(player) -> bool:
        stat_value = getattr(player, stat_name, 0)
        luck_value = getattr(player, 'luck', 0)
        
        # Нормализуем значения (примерно)
        stat_contribution = (stat_value / 100.0) * stat_weight
        luck_contribution = (luck_value / 100.0) * luck_weight
        
        final_chance = min(0.95, base_chance + stat_contribution + luck_contribution)
        return random.random() < final_chance
    return check


def intellect_check(min_intellect: int = 5) -> Callable:
    """Проверка интеллекта"""
    return stat_check('intellect', min_value=min_intellect)


def defense_check(min_defense: int = 10) -> Callable:
    """Проверка защиты"""
    return stat_check('defense', min_value=min_defense)


def attack_check(min_attack: int = 15) -> Callable:
    """Проверка атаки"""
    return stat_check('attack', min_value=min_attack)
