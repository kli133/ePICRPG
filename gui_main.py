"""
Графический интерфейс для текстовой RPG игры
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import random
from player import Player
from classes import CLASSES, get_class
from inventory import Inventory
from items import ITEMS_DATABASE, get_item_scaled, get_random_artifact, QUALITY_MULTIPLIER, QUALITY_ICONS, QUALITY_DISPLAY
from combat import create_enemy
from save_system import save_game, load_game, has_save_file
import save_system
from version import GAME_NAME, VERSION
from locales import t, set_locale, get_locale
from events_data import create_event_manager


class RPGGame:
    def __init__(self, root):
        self.root = root
        
        # Set window title from central version metadata
        try:
            self.root.title(f"{GAME_NAME} v{VERSION}")
        except Exception:
            # fallback to localized app title
            self.root.title(t('app_title'))
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Игровые переменные
        self.player = None
        self.inventory = Inventory()
        self.rotation = 0
        self.victories = 0
        self.running = True
        self.in_combat = False
        self.current_enemy = None
        
        # Система событий
        self.event_manager = create_event_manager()
        self.current_event = None
        self.in_event = False
        
        # Админ режим
        self.admin_mode = False
        self.admin_password = "FOXKLI133"  # Пароль для входа в админ режим
        
        # Цветовые темы
        self.themes = {
            'dark': {
                'name': '🌙 Темная',
                'bg': '#2b2b2b',
                'text_bg': '#1e1e1e',
                'text_fg': '#e0e0e0',
                'button_bg': '#3c3c3c',
                'button_fg': '#ffffff',
                'button_active': '#505050',
                'green': '#4CAF50',
                'red': '#f44336',
                'yellow': '#ffeb3b',
                'cyan': '#00bcd4',
                'magenta': '#e91e63'
            },
            'light': {
                'name': '☀️ Светлая',
                'bg': '#f5f5f5',
                'text_bg': '#ffffff',
                'text_fg': '#212121',
                'button_bg': '#e0e0e0',
                'button_fg': '#212121',
                'button_active': '#bdbdbd',
                'green': '#2e7d32',
                'red': '#c62828',
                'yellow': '#f57c00',
                'cyan': '#0277bd',
                'magenta': '#ad1457'
            },
            'cyberpunk': {
                'name': '🌆 Киберпанк',
                'bg': '#0a0e27',
                'text_bg': '#1a1f3a',
                'text_fg': '#00ffff',
                'button_bg': '#2d3561',
                'button_fg': '#ff00ff',
                'button_active': '#3d4571',
                'green': '#00ff00',
                'red': '#ff0055',
                'yellow': '#ffff00',
                'cyan': '#00ffff',
                'magenta': '#ff00ff'
            },
            'forest': {
                'name': '🌲 Лесная',
                'bg': '#1b3a2f',
                'text_bg': '#0d2818',
                'text_fg': '#b8d4b8',
                'button_bg': '#2d5a3d',
                'button_fg': '#e8f5e8',
                'button_active': '#3d6a4d',
                'green': '#66bb6a',
                'red': '#ef5350',
                'yellow': '#fdd835',
                'cyan': '#4dd0e1',
                'magenta': '#ab47bc'
            },
            'sunset': {
                'name': '🌅 Закат',
                'bg': '#2d1b2e',
                'text_bg': '#1a0f1b',
                'text_fg': '#f4c2c2',
                'button_bg': '#4a2c4a',
                'button_fg': '#ffd4d4',
                'button_active': '#5a3c5a',
                'green': '#81c784',
                'red': '#ff6b6b',
                'yellow': '#ffd54f',
                'cyan': '#64b5f6',
                'magenta': '#f06292'
            }
        }
        self.current_theme = 'dark'
        self.colors = self.themes[self.current_theme]
        
        self.create_widgets()
        self.show_start_screen()
    
    def create_widgets(self):
        """Создать основные виджеты"""
        # Верхняя панель с информацией о игроке
        self.info_frame = tk.Frame(self.root, bg=self.colors['button_bg'], height=80)
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)
        self.info_frame.pack_propagate(False)
        
        self.info_label = tk.Label(
            self.info_frame,
            text=t('welcome'),
            bg=self.colors['button_bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 11),
            justify=tk.LEFT,
            anchor='w'
        )
        self.info_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Основное текстовое поле
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            font=('Consolas', 10),
            insertbackground=self.colors['text_fg']
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель кнопок
        self.button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Создадим кнопки (изначально скрыты)
        self.game_buttons = {}
        self.create_game_buttons()
    
    def create_game_buttons(self):
        """Создать игровые кнопки"""
        try:
            # Удалим старые виджеты и сбросим конфигурацию колонок, чтобы
            # избежать смещения при повторном создании (после боевого режима)
            try:
                for child in list(self.button_frame.winfo_children()):
                    try:
                        child.destroy()
                    except Exception:
                        pass
            except Exception:
                pass
            # Сброс columnconfigure на несколько колонок
            for ci in range(10):
                try:
                    self.button_frame.columnconfigure(ci, weight=0)
                except Exception:
                    pass

            buttons_config = [
                ('explore', f"⚔️ {t('explore')}", self.explore),
                ('inventory', f"🎒 {t('inventory')}", self.show_inventory),
                ('stats', f"📊 {t('stats')}", self.show_stats),
                ('prestige', f"🔁 {t('prestige')}", self.show_prestige),
                ('shop', f"🏪 {t('shop')}", self.show_shop),
                ('stat_points', f"⭐ {t('stat_points_action')}", self.spend_stat_points),
                ('rest', f"💚 {t('rest')}", self.rest),
                ('theme', f"🎨 {t('theme')}", self.change_theme),
                ('save', f"💾 {t('save')}", self.save_game_data),
                ('load', f"📂 {t('load')}", self.load_game_data),
                ('quit', f"🚪 {t('quit')}", self.quit_game)
            ]
            
            # Добавить кнопку админ-панели если режим включён
            if self.admin_mode:
                buttons_config.insert(5, ('admin', "⚙️ Админ", self.show_admin_panel))
            
            row = 0
            col = 0
            for btn_id, text, command in buttons_config:
                btn = tk.Button(
                    self.button_frame,
                    text=text,
                    command=command,
                    bg=self.colors['button_bg'],
                    fg=self.colors['button_fg'],
                    activebackground=self.colors['button_active'],
                    font=('Arial', 10),
                    relief=tk.FLAT,
                    padx=10,
                    pady=8,
                    cursor='hand2'
                )
                btn.grid(row=row, column=col, padx=3, pady=3, sticky='ew')
                self.game_buttons[btn_id] = btn
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            
            # Настроить равномерное распределение колонок
            for i in range(3):
                self.button_frame.columnconfigure(i, weight=1)
            
            # Обновим панель инфо/цвет кнопок если игрок уже создан
            try:
                self.update_info_panel()
            except Exception:
                pass
            
            self.root.update()
        except Exception as e:
            self.print(f"Ошибка при создании кнопок: {str(e)}", 'red')
            import traceback
            traceback.print_exc()
    
    def print(self, text, color='text_fg', tag=None):
        """Вывести текст в текстовое поле"""
        try:
            if hasattr(self, 'text_area') and self.text_area:
                self.text_area.insert(tk.END, text + '\n')
                if color != 'text_fg' and color in self.colors:
                    # Создаём тег для цвета
                    tag_name = f'color_{color}'
                    self.text_area.tag_config(tag_name, foreground=self.colors[color])
                    # Применяем к последней строке
                    last_line = self.text_area.index('end-1c linestart')
                    end_line = self.text_area.index('end-1c')
                    self.text_area.tag_add(tag_name, last_line, end_line)
                
                self.text_area.see(tk.END)
                self.root.update()
        except Exception:
            pass
    
    def clear_text(self):
        """Очистить текстовое поле"""
        self.text_area.delete(1.0, tk.END)
    
    def update_info_panel(self):
        """Обновить панель информации"""
        if self.player:
            info = t(
                'info_label_format',
                hp=self.player.hp,
                max=self.player.max_hp,
                level=self.player.level,
                prestige=getattr(self.player, 'prestige_level', 0),
                gold=self.player.gold,
                rotation=self.rotation
            )
            if self.player.stat_points > 0:
                info += f"  |  📈 {t('stat_points_label')}: {self.player.stat_points}"
            self.info_label.config(text=info)
            
            # Выделить кнопку очков характеристик (только если она существует)
            if 'stat_points' in self.game_buttons:
                try:
                    btn = self.game_buttons['stat_points']
                    # Проверяем, что виджет всё ещё существует
                    btn.winfo_exists()
                    
                    if self.player.stat_points > 0:
                        btn.config(
                            bg=self.colors['green'],
                            fg='white',
                            text=f"⭐ {t('stat_points_action')} ({self.player.stat_points})"
                        )
                    else:
                        btn.config(
                            bg=self.colors['button_bg'],
                            fg=self.colors['button_fg'],
                            text=f"⭐ {t('stat_points_action')}"
                        )
                except Exception:
                    pass

            if 'prestige' in self.game_buttons:
                try:
                    btn = self.game_buttons['prestige']
                    btn.winfo_exists()

                    if self.player.can_prestige():
                        btn.config(
                            bg=self.colors['magenta'],
                            fg='white',
                            text=f"🔁 {t('prestige')}!"
                        )
                    else:
                        btn.config(
                            bg=self.colors['button_bg'],
                            fg=self.colors['button_fg'],
                            text=f"🔁 {t('prestige')}"
                        )
                except Exception:
                    pass
        else:
            self.info_label.config(text=t('welcome'))
    
    def show_start_screen(self):
        """Показать стартовый экран (только при инициализации или Game Over)"""
        self.clear_text()
        self.print("="*60, 'yellow')
        self.print(t('game_banner'), 'cyan')
        self.print("="*60, 'yellow')
        self.print("")

        # Покажем простое меню — две кнопки внизу: Новая игра / Загрузить
        try:
            for child in list(self.button_frame.winfo_children()):
                try:
                    child.destroy()
                except Exception:
                    pass
        except Exception:
            pass

        new_btn = tk.Button(self.button_frame, text=t('start_new_game'), command=self.create_new_character,
                            bg=self.colors['button_bg'], fg=self.colors['button_fg'], padx=20, pady=10)
        load_btn = tk.Button(self.button_frame, text=t('load'), command=lambda: self.show_save_slots(mode='load'),
                             bg=self.colors['button_bg'], fg=self.colors['button_fg'], padx=20, pady=10)
        lang_btn = tk.Button(self.button_frame, text=f"🌐 {t('language_button')}", command=self.change_language,
                     bg=self.colors['button_bg'], fg=self.colors['button_fg'], padx=20, pady=10)
        new_btn.pack(side=tk.LEFT, padx=10, pady=10)
        load_btn.pack(side=tk.LEFT, padx=10, pady=10)
        lang_btn.pack(side=tk.LEFT, padx=10, pady=10)
        self.root.update()
    
    def create_new_character(self):
        """Создать нового персонажа"""
        try:
            # Диалог ввода имени
            name = simpledialog.askstring("Имя персонажа", "Введите имя персонажа:", parent=self.root)
            if not name:
                name = "Герой"
            
            self.print(f"\nВыберите класс для {name}:", 'cyan')
            self.print("")
            
            # Показать классы
            keys = list(CLASSES.keys())
            for i, k in enumerate(keys, 1):
                cls = CLASSES[k]
                self.print(f"{i}. {cls.name} - {cls.description}", 'green')
            
            # Диалог выбора класса
            class_choice = simpledialog.askinteger(
                "Выбор класса",
                f"Выберите класс (1-{len(keys)}):",
                parent=self.root,
                minvalue=1,
                maxvalue=len(keys)
            )
            
            if class_choice is None:
                class_choice = 1
            
            class_id = keys[class_choice - 1]
            
            # Создать игрока
            self.player = Player(name, class_id=class_id)
            self.inventory = Inventory()
            self.rotation = 0
            self.victories = 0
            
            # Стартовое зелье
            starter = get_item_scaled('small_potion', rotation=self.rotation, player_level=self.player.level)
            if starter:
                self.inventory.add_item(starter)
            
            self.print(f"\n{self.player.name} ({self.player.class_name}) создан!", 'green')
            self.print("")
            
            self.update_info_panel()
            # Create full game buttons now that player exists
            self.create_game_buttons()
            
            self.print_main_menu()
        except Exception as e:
            self.print(f"❌ Ошибка при создании персонажа: {str(e)}", 'red')
            import traceback
            traceback.print_exc()
            self.show_start_screen()

    def change_language(self):
        """Переключить язык интерфейса"""
        try:
            current = get_locale()
            new_locale = 'en' if current == 'ru' else 'ru'
            set_locale(new_locale)
            try:
                save_system.save_settings(new_locale)
            except Exception:
                pass

            if self.player:
                # Игрок уже создан — обновляем игровые кнопки и инфо
                try:
                    self.create_game_buttons()
                except Exception:
                    pass
                try:
                    self.update_info_panel()
                except Exception:
                    pass
            else:
                # Пока нет игрока — просто перерисуем стартовый экран
                try:
                    self.show_start_screen()
                except Exception:
                    pass

            # Сообщаем пользователю
            lang_name = t('language_en') if new_locale == 'en' else t('language_ru')
            try:
                self.print(t('language_switched', lang=lang_name), 'cyan')
            except Exception:
                pass
        except Exception:
            pass
    
    def print_main_menu(self):
        """Показать главное меню"""
        self.print("\n" + "="*60, 'yellow')
        self.print("Используйте кнопки ниже для управления игрой", 'cyan')
        self.print("="*60, 'yellow')
    
    def explore(self):
        """Исследование - случайное событие или бой с врагом"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return
        
        self.clear_text()
        self.print("Вы отправляетесь исследовать окрестности...\n", 'cyan')
        
        # 35% шанс встретить событие вместо врага
        if random.random() < 0.35:
            event = self.event_manager.get_random_event()
            if event:
                self.current_event = event
                self.in_event = True
                self.show_event()
                # Автосохранение
                try:
                    ok, msg = save_system.save_game_slot(self.player, self.inventory, self.rotation, self.victories, slot=save_system.MAX_SLOTS)
                    if ok:
                        try:
                            self.print(t('autosave_done'), 'cyan')
                        except Exception:
                            pass
                except Exception:
                    pass
                return
        
        # Иначе - обычный бой с врагом
        # Создать врага
        self.current_enemy = create_enemy(self.player.level, rotation=self.rotation)
        
        self.print("="*50, 'yellow')
        self.print("⚔️  НАЧАЛО БОЯ!", 'yellow')
        self.print("="*50, 'yellow')
        self.print(f"Вы встретили: {self.current_enemy.name} (Уровень {self.current_enemy.level})", 'red')
        self.print(f"Здоровье врага: {self.current_enemy.hp}/{self.current_enemy.max_hp}", 'red')
        self.print("="*50 + "\n", 'yellow')
        
        self.in_combat = True
        self.show_combat_menu()
        # Автосохранение в зарезервированный слот при смене состояния (начало боя/изменение локации)
        try:
            ok, msg = save_system.save_game_slot(self.player, self.inventory, self.rotation, self.victories, slot=save_system.MAX_SLOTS)
            if ok:
                try:
                    self.print(t('autosave_done'), 'cyan')
                except Exception:
                    pass
        except Exception:
            pass
    
    def show_combat_menu(self):
        """Показать меню боя"""
        if not self.in_combat or not self.current_enemy:
            return
        
        self.print(f"Ваше HP: {self.player.hp}/{self.player.max_hp}", 'green')
        self.print(f"HP {self.current_enemy.name}: {self.current_enemy.hp}/{self.current_enemy.max_hp}\n", 'red')

        # Переключаем нижнюю панель на боевые действия
        self.enter_combat_mode()
    
    def combat_attack(self):
        """Атака в бою"""
        damage = random.randint(int(self.player.get_total_attack() * 0.8),
                               int(self.player.get_total_attack() * 1.2))
        
        # Враг пытается уклониться
        if self.current_enemy.check_evade():
            self.print(f"{self.current_enemy.name} уклонился от вашей атаки!", 'yellow')
            self.enemy_turn()
            return
        
        # Проверяем критический удар игрока
        crit_multiplier = self.player.check_crit()
        if crit_multiplier > 1.0:
            damage = int(damage * crit_multiplier)
            # Разные сообщения в зависимости от множителя
            if crit_multiplier >= 2.5:
                self.print(f"⚡⚡⚡ ТРОЙНОЙ КРИТ! Урон ×{crit_multiplier:.1f}!", 'magenta')
            elif crit_multiplier >= 2.0:
                self.print(f"⚡⚡ ДВОЙНОЙ КРИТ! Урон ×2.0!", 'cyan')
            else:
                self.print(f"⚡ КРИТИЧЕСКИЙ УДАР! Урон ×1.5!", 'cyan')
        
        actual_damage = self.current_enemy.take_damage(damage)
        try:
            self.player.apply_artifact_on_hit(self.current_enemy, actual_damage)
        except Exception:
            pass
        
        if crit_multiplier > 1.0:
            if crit_multiplier >= 2.0:
                self.print(f"Вы наносите мощный критический удар {self.current_enemy.name} и урон составляет {actual_damage}!", 'cyan')
            else:
                self.print(f"Вы наносите критический удар {self.current_enemy.name} и урон составляет {actual_damage}!", 'cyan')
        else:
            self.print(f"Вы атакуете {self.current_enemy.name} и наносите {actual_damage} урона!", 'green')
        
        if not self.current_enemy.is_alive():
            self.combat_victory()
            return
        
        self.enemy_turn()
    
    def combat_use_potion(self):
        """Использовать зелье в бою"""
        from items import Potion
        potions = [(i, item) for i, item in enumerate(self.inventory.items) if isinstance(item, Potion)]
        
        if not potions:
            self.print("У вас нет зелий!", 'red')
            self.show_combat_menu()
            return
        
        # Диалог выбора зелья
        potion_window = tk.Toplevel(self.root)
        potion_window.title("Выбор зелья")
        potion_window.geometry("400x300")
        potion_window.configure(bg=self.colors['bg'])
        potion_window.transient(self.root)
        potion_window.grab_set()
        
        tk.Label(
            potion_window,
            text="Выберите зелье:",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        def use_potion_at_index(inv_index):
            potion_window.destroy()
            self.inventory.use_item(inv_index, self.player)
            self.update_info_panel()
            self.enemy_turn()
        
        for idx, (inv_idx, potion) in enumerate(potions, 1):
            btn = tk.Button(
                potion_window,
                text=f"{idx}. {potion.name} ({potion.description})",
                command=lambda i=inv_idx: use_potion_at_index(i),
                bg=self.colors['button_bg'],
                fg=self.colors['button_fg'],
                font=('Arial', 10),
                relief=tk.FLAT,
                padx=10,
                pady=8
            )
            btn.pack(fill=tk.X, padx=20, pady=3)
    
    def combat_use_ability(self):
        """Использовать способность в бою"""
        if not self.player.abilities:
            self.print("У вас нет способностей!", 'red')
            self.enter_combat_mode()
            return

        # Покажем способности в нижней панели (заменим боевые кнопки)
        try:
            for btn in list(self.game_buttons.values()):
                try:
                    btn.destroy()
                except Exception:
                    pass
        except Exception:
            pass
        self.game_buttons = {}

        available = [(aid, *data) for aid, data in self.player.abilities.items()]

        def make_use(aid):
            def _inner():
                if self.player.can_use_ability(aid):
                    self.player.use_ability(aid, self.current_enemy)
                    if not self.current_enemy.is_alive():
                        self.combat_victory()
                    else:
                        self.enemy_turn()
                else:
                    self.print(t('ability_on_cd'), 'red')
                    self.enter_combat_mode()
            return _inner

        col = 0
        for aid, name, desc, cd in available:
            rc = self.player.ability_cooldowns.get(aid, 0)
            status = t('status_ready') if rc == 0 else t('status_cd', rc=rc)
            text = f"{name} ({status})"
            btn = tk.Button(
                self.button_frame,
                text=text,
                command=make_use(aid),
                bg=self.colors['button_bg'],
                fg=self.colors['button_fg'],
                font=('Arial', 10),
                relief=tk.FLAT,
                padx=10,
                pady=8,
                cursor='hand2'
            )
            btn.grid(row=0, column=col, padx=3, pady=3, sticky='ew')
            self.game_buttons[aid] = btn
            col += 1

        # Back button to restore combat actions
        def back_to_combat():
            self.enter_combat_mode()

        back_btn = tk.Button(
            self.button_frame,
            text=t('close'),
            command=back_to_combat,
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor='hand2'
        )
        back_btn.grid(row=0, column=col, padx=3, pady=3, sticky='ew')
        self.game_buttons['back'] = back_btn
        for i in range(col+1):
            self.button_frame.columnconfigure(i, weight=1)
    
    def combat_run(self):
        """Попытка побега"""
        if random.random() < 0.5:
            self.print(t('you_fled'), 'cyan')
            self.in_combat = False
            self.current_enemy = None
            # Выйти из боевого режима (восстановить кнопки)
            self.exit_combat_mode()
            self.print_main_menu()
        else:
            self.print(t('flee_failed'), 'red')
            self.enemy_turn()
    
    def enemy_turn(self):
        """Ход врага"""
        from combat import can_use_magic
        if getattr(self.current_enemy, 'stunned_turns', 0) > 0:
            self.print(t('enemy_stunned', name=self.current_enemy.name), 'cyan')
            self.current_enemy.stunned_turns -= 1
        else:
            attack_type = 'physical'
            # Только враги, которые могут использовать магию, используют элементальные атаки
            if can_use_magic(self.current_enemy) and random.random() < 0.15:
                attack_type = random.choice(['fire', 'cold'])
            
            enemy_damage = random.randint(int(self.current_enemy.attack * 0.8),
                                         int(self.current_enemy.attack * 1.2))
            
            # Проверяем критический удар врага
            crit_multiplier = self.current_enemy.check_crit()
            if crit_multiplier > 1.0:
                enemy_damage = int(enemy_damage * crit_multiplier)
                if crit_multiplier >= 2.0:
                    self.print(f"⚡⚡ {self.current_enemy.name} наносит ДВОЙНОЙ КРИТ!", 'red')
                else:
                    self.print(f"⚡ {self.current_enemy.name} наносит КРИТИЧЕСКИЙ УДАР!", 'red')
            
            if attack_type != 'physical':
                self.print(f"{self.current_enemy.name} использует {attack_type}-атаку!", 'red')
            
            actual_damage = self.player.take_damage(enemy_damage, element=attack_type,
                                                   defense_penetration=getattr(self.current_enemy, 'penetration', 0.0))
            
            if crit_multiplier > 1.0:
                self.print(f"{self.current_enemy.name} наносит вам критический удар урон составляет {actual_damage}!\n", 'red')
            else:
                self.print(f"{self.current_enemy.name} атакует вас и наносит {actual_damage} урона!\n", 'red')
        
        self.update_info_panel()
        
        if not self.player.is_alive():
            self.combat_defeat()
            return
        
        self.player.reduce_cooldowns()
        self.show_combat_menu()
    
    def combat_victory(self):
        """Победа в бою"""
        self.in_combat = False
        
        self.print("\n" + "="*50, 'yellow')
        self.print(f"🎉 ПОБЕДА! Вы победили {self.current_enemy.name}!", 'green')
        self.print("="*50, 'yellow')
        
        # Награды
        prestige_exp_mult = 1.0
        prestige_gold_mult = 1.0
        artifact_gold_mult = 1.0
        try:
            prestige_exp_mult = self.player.get_prestige_exp_multiplier()
            prestige_gold_mult = self.player.get_prestige_gold_multiplier()
        except Exception:
            pass
        try:
            artifact_gold_mult = self.player.get_artifact_gold_multiplier()
        except Exception:
            pass

        xp_gain = int(
            self.current_enemy.exp_reward
            * (1 + getattr(self.player, 'intellect', 0) * 0.05 + self.rotation * 0.10)
            * prestige_exp_mult
        )
        gold_gain = int(
            self.current_enemy.gold_reward
            * (1 + self.player.get_total_luck() * 0.05 + self.rotation * 0.12)
            * prestige_gold_mult
            * artifact_gold_mult
        )
        
        # Показываем полученный опыт
        old_level = self.player.level
        self.player.exp += xp_gain
        self.print(f"Получено {xp_gain} опыта!", 'green')
        
        # Проверяем повышение уровня
        while self.player.exp >= self.player.exp_to_next_level:
            self.player.level_up()
            self.print(f"\n{'='*40}", 'yellow')
            self.print(f"🎉 ПОВЫШЕНИЕ УРОВНЯ! Теперь вы {self.player.level} уровня!", 'yellow')
            self.print(f"{'='*40}", 'yellow')
            self.print(f"Здоровье: +20 (теперь {self.player.max_hp})", 'green')
            self.print(f"Атака: +3 (теперь {self.player.attack})", 'green')
            self.print(f"Защита: +2 (теперь {self.player.defense})", 'green')
            self.print(f"Получено 3 очка характеристик!", 'cyan')
            self.print(f"{'='*40}\n", 'yellow')
        
        self.player.gold += gold_gain
        self.print(f"Получено золота: {gold_gain}", 'yellow')
        self.print("="*50 + "\n", 'yellow')
        
        # Лут
        loot_bonus = 0.0
        try:
            loot_bonus = self.player.get_prestige_loot_bonus()
        except Exception:
            pass
        try:
            loot_bonus += self.player.get_artifact_loot_bonus()
        except Exception:
            pass
        loot_chance = min(
            0.95,
            0.35 + self.rotation * 0.05 + self.player.get_total_luck() * 0.04
            + self.player.level * 0.01 + loot_bonus
        )
        if random.random() < loot_chance:
            loot_items = ['small_potion', 'medium_potion']
            if self.player.level >= 2 or self.rotation >= 1:
                loot_items.extend(['wooden_sword', 'leather_armor'])
            if self.player.level >= 3 or self.rotation >= 2:
                loot_items.extend(['iron_sword', 'iron_armor'])
            if self.player.level >= 4 or self.rotation >= 3:
                loot_items.extend(['steel_sword', 'steel_armor'])
            if self.rotation >= 4:
                loot_items.extend(['legendary_sword', 'legendary_armor'])
            
            choice_id = random.choice(loot_items)
            loot = get_item_scaled(choice_id, rotation=self.rotation, player_level=self.player.level)
            if loot:
                self.inventory.add_item(loot)
                self.print(f"Получен предмет: {loot.name}", 'cyan')
            
            # Дополнительный лут
            extra_drop = random.random() < min(0.35, self.player.get_total_luck() * 0.03 + self.rotation * 0.02)
            if extra_drop:
                choice_id = random.choice(loot_items)
                loot2 = get_item_scaled(choice_id, rotation=self.rotation, player_level=self.player.level)
                if loot2:
                    self.inventory.add_item(loot2)
                    self.print(f"Получен предмет: {loot2.name}", 'cyan')

        # Редкий дроп артефакта
        try:
            artifact_chance = min(0.20, 0.02 + self.rotation * 0.01 + self.player.get_total_luck() * 0.002)
            if random.random() < artifact_chance:
                artifact = get_random_artifact(rotation=self.rotation, player_luck=self.player.get_total_luck())
                if artifact:
                    self.inventory.add_item(artifact)
                    self.print(t('artifact_found', name=artifact.name), 'magenta')
                    self.print(f"   Бонусы: {artifact.get_slot_description()}", 'cyan')
        except Exception:
            pass
        
        self.victories += 1
        if self.victories > 0 and self.victories % 5 == 0:
            self.rotation += 1
            self.print(f"--- Ротация увеличена! Текущая ротация: {self.rotation} ---\n", 'magenta')
        
        self.update_info_panel()
        self.current_enemy = None
        # Восстановить обычную панель кнопок
        self.exit_combat_mode()
        self.print_main_menu()
        # Автосохранение в зарезервированный слот после победы
        try:
            ok, msg = save_system.save_game_slot(self.player, self.inventory, self.rotation, self.victories, slot=save_system.MAX_SLOTS)
            if ok:
                try:
                    self.print(t('autosave_done'), 'green')
                except Exception:
                    pass
        except Exception:
            pass
    
    def combat_defeat(self):
        """Поражение в бою"""
        self.in_combat = False
        self.current_enemy = None
        
        self.print("\n" + "="*50, 'red')
        self.print("💀 ПОРАЖЕНИЕ! Game Over", 'red')
        self.print("="*50, 'red')
        self.print(f"Вы достигли {self.player.level} уровня", 'yellow')
        self.print("="*50 + "\n", 'red')
        
        response = messagebox.askyesno("Game Over", "Начать новую игру?")
        if response:
            self.show_start_screen()
        else:
            self.root.quit()

    def enter_combat_mode(self):
        """Заменить нижнюю панель на боевые действия"""
        # Очистим текущие кнопки
        try:
            for btn in list(self.game_buttons.values()):
                try:
                    btn.destroy()
                except Exception:
                    pass
        except Exception:
            pass
        self.game_buttons = {}

        # Создать боевые кнопки
        def btn_attack():
            self.combat_attack()

        def btn_potion():
            self.combat_use_potion()

        def btn_ability():
            self.combat_use_ability()

        def btn_run():
            self.combat_run()

        combat_buttons = [
            ('attack', '⚔️ Атаковать', btn_attack),
            ('potion', '🍷 Зелье', btn_potion),
            ('ability', '✨ Способность', btn_ability),
            ('run', '🏃 Убежать', btn_run)
        ]

        col = 0
        for bid, text, cmd in combat_buttons:
            btn = tk.Button(
                self.button_frame,
                text=text,
                command=cmd,
                bg=self.colors['button_bg'],
                fg=self.colors['button_fg'],
                activebackground=self.colors['button_active'],
                font=('Arial', 10),
                relief=tk.FLAT,
                padx=10,
                pady=8,
                cursor='hand2'
            )
            btn.grid(row=0, column=col, padx=3, pady=3, sticky='ew')
            self.game_buttons[bid] = btn
            col += 1
        for i in range(col):
            self.button_frame.columnconfigure(i, weight=1)

    def exit_combat_mode(self):
        """Восстановить обычную панель кнопок после боя"""
        try:
            for btn in list(self.game_buttons.values()):
                try:
                    btn.destroy()
                except Exception:
                    pass
        except Exception:
            pass
        self.game_buttons = {}
        # Воссоздадим стандартные кнопки
        self.create_game_buttons()
    
    def show_inventory(self, show_sell_button=False):
        """Показать инвентарь"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return
        
        if not self.inventory.items:
            messagebox.showinfo(t('inventory'), t('inventory_empty'))
            return
        
        # Окно инвентаря
        inv_window = tk.Toplevel(self.root)
        inv_window.title(t('inventory_title', count=len(self.inventory.items), max=self.inventory.max_size))
        inv_window.geometry("700x500")
        inv_window.configure(bg=self.colors['bg'])
        inv_window.transient(self.root)
        
        # Параметры фильтра
        ctrl_frame = tk.Frame(inv_window, bg=self.colors['bg'])
        ctrl_frame.pack(fill=tk.X, padx=10, pady=(5, 0))

        tk.Label(ctrl_frame, text=t('filter_label'), bg=self.colors['bg'], fg=self.colors['text_fg']).pack(side=tk.LEFT, padx=(0,5))
        filter_var = tk.StringVar(value=t('filter_all'))
        filter_box = ttk.Combobox(ctrl_frame, textvariable=filter_var, state='readonly', width=16)
        # Отображаемые русские метки, но используем внутренние ключи для фильтрации
        filter_display = [
            t('filter_all'),
            t('filter_weapons'),
            t('filter_armor'),
            t('filter_potions'),
            t('filter_artifacts'),
            t('filter_materials'),
            t('filter_stronger'),
            t('filter_weaker')
        ]
        filter_mapping = {
            t('filter_all'): 'all',
            t('filter_weapons'): 'weapons',
            t('filter_armor'): 'armor',
            t('filter_potions'): 'potions',
            t('filter_artifacts'): 'artifacts',
            t('filter_materials'): 'materials',
            t('filter_stronger'): 'stronger',
            t('filter_weaker'): 'weaker'
        }
        filter_box['values'] = filter_display
        filter_box.pack(side=tk.LEFT)

        show_strength_var = tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl_frame, text=t('show_strength'), variable=show_strength_var, bg=self.colors['bg'], fg=self.colors['text_fg'], selectcolor=self.colors['bg']).pack(side=tk.LEFT, padx=10)

        # Search box
        tk.Label(ctrl_frame, text=t('search_label'), bg=self.colors['bg'], fg=self.colors['text_fg']).pack(side=tk.LEFT, padx=(10,3))
        search_var = tk.StringVar()
        search_entry = tk.Entry(ctrl_frame, textvariable=search_var, bg=self.colors['text_bg'], fg=self.colors['text_fg'])
        search_entry.pack(side=tk.LEFT, padx=(0,5))

        # Sort box
        tk.Label(ctrl_frame, text=t('sort_label'), bg=self.colors['bg'], fg=self.colors['text_fg']).pack(side=tk.LEFT, padx=(10,3))
        sort_var = tk.StringVar(value=t('sort_none'))
        sort_box = ttk.Combobox(ctrl_frame, textvariable=sort_var, state='readonly', width=12)
        sort_box['values'] = [t('sort_none'), t('sort_attack'), t('sort_defense'), t('sort_quality')]
        sort_box.pack(side=tk.LEFT, padx=(0,5))

        # Список предметов и слоты экипировки в grid layout
        content_frame = tk.Frame(inv_window, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=0)
        content_frame.rowconfigure(0, weight=1)
        
        # Левая часть - список предметов
        list_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        list_frame.grid(row=0, column=0, sticky='nsew', padx=(0,10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            list_frame,
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            font=('Consolas', 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Информация о требованиях к предмету
        info_label = tk.Label(list_frame, text="", bg=self.colors['text_bg'], fg=self.colors['text_fg'], anchor='nw', justify=tk.LEFT, wraplength=300)
        info_label.pack(fill=tk.X, padx=5, pady=(5,0))

        # Массив соответствий отображаемого индекса -> индекс в inventory.items
        displayed_indices = []

        # Правая часть - рамка для экипировки (слоты оружия/брони)
        equip_frame = tk.Frame(content_frame, bg=self.colors['bg'], width=200)
        equip_frame.grid(row=0, column=1, sticky='ns')
        equip_frame.grid_propagate(False)

        tk.Label(equip_frame, text=t('equipment_title'), bg=self.colors['bg'], fg=self.colors['text_fg'], font=('Arial', 11, 'bold')).pack(pady=(0,10))

        # Слот оружия
        weapon_frame = tk.LabelFrame(equip_frame, text=t('equip_slot_weapon'), bg=self.colors['bg'], fg=self.colors['text_fg'])
        weapon_frame.pack(fill=tk.X, pady=(0,10))
        weapon_label = tk.Label(weapon_frame, text=t('none'), bg=self.colors['text_bg'], fg=self.colors['text_fg'], anchor='w', wraplength=180)
        weapon_label.pack(fill=tk.X, padx=5, pady=5)
        weapon_unequip = tk.Button(weapon_frame, text=t('unequip'), command=lambda: None, bg=self.colors['button_bg'], fg=self.colors['button_fg'])
        weapon_unequip.pack(fill=tk.X, padx=5, pady=(0,5))

        # Слот брони
        armor_frame = tk.LabelFrame(equip_frame, text=t('equip_slot_armor'), bg=self.colors['bg'], fg=self.colors['text_fg'])
        armor_frame.pack(fill=tk.X, pady=(0,10))
        armor_label = tk.Label(armor_frame, text=t('none'), bg=self.colors['text_bg'], fg=self.colors['text_fg'], anchor='w', wraplength=180)
        armor_label.pack(fill=tk.X, padx=5, pady=5)
        armor_unequip = tk.Button(armor_frame, text=t('unequip'), command=lambda: None, bg=self.colors['button_bg'], fg=self.colors['button_fg'])
        armor_unequip.pack(fill=tk.X, padx=5, pady=(0,5))

        # Слот артефакта
        artifact_frame = tk.LabelFrame(equip_frame, text=t('equip_slot_artifact'), bg=self.colors['bg'], fg=self.colors['text_fg'])
        artifact_frame.pack(fill=tk.X, pady=(0,10))
        artifact_label = tk.Label(artifact_frame, text=t('none'), bg=self.colors['text_bg'], fg=self.colors['text_fg'], anchor='w', wraplength=180)
        artifact_label.pack(fill=tk.X, padx=5, pady=5)
        artifact_unequip = tk.Button(artifact_frame, text=t('unequip'), command=lambda: None, bg=self.colors['button_bg'], fg=self.colors['button_fg'])
        artifact_unequip.pack(fill=tk.X, padx=5, pady=(0,5))

        def refresh_list():
            listbox.delete(0, tk.END)
            displayed_indices.clear()
            # Получаем внутренний ключ фильтра из отображаемой метки
            f = filter_mapping.get(filter_var.get(), 'all')
            show_strength = show_strength_var.get()
            q = search_var.get().lower().strip()
            sort_key = sort_var.get()
            for i, item in enumerate(self.inventory.items):
                # Логика фильтрации аналогична Inventory.show_inventory
                def passes_filter(it):
                    if f == 'all':
                        return True
                    if f == 'weapons' and hasattr(it, 'attack_bonus'):
                        return True
                    if f == 'armor' and hasattr(it, 'defense_bonus'):
                        return True
                    if f == 'potions' and hasattr(it, 'heal_amount'):
                        return True
                    if f == 'artifacts' and hasattr(it, 'effect_id'):
                        return True
                    if f == 'materials' and not (hasattr(it, 'attack_bonus') or hasattr(it, 'defense_bonus') or hasattr(it, 'heal_amount') or hasattr(it, 'effect_id')):
                        return True
                    if f == 'stronger':
                        return self.inventory.evaluate_strength(it, self.player) == 'stronger'
                    if f == 'weaker':
                        return self.inventory.evaluate_strength(it, self.player) == 'weaker'
                    return False

                if not passes_filter(item):
                    continue

                # Apply search
                if q:
                    name = getattr(item, 'name', '').lower()
                    desc = getattr(item, 'description', '').lower() if hasattr(item, 'description') else ''
                    if q not in name and q not in desc:
                        continue

                equipped = ''
                # Prefer explicit equipped flag (handles duplicates reliably)
                try:
                    if getattr(item, 'equipped', False):
                        equipped = ' [Экипировано]'
                    else:
                        # Fallback to uid/identity checks
                        weapon_uid = getattr(getattr(self.player, 'weapon', None), 'uid', None)
                        armor_uid = getattr(getattr(self.player, 'armor', None), 'uid', None)
                        artifact_uid = getattr(getattr(self.player, 'artifact', None), 'uid', None)
                        item_uid = getattr(item, 'uid', None)
                        if hasattr(item, 'attack_bonus') and item_uid and weapon_uid == item_uid:
                            equipped = ' [Экипировано]'
                        elif hasattr(item, 'attack_bonus') and getattr(self.player, 'weapon', None) is item:
                            equipped = ' [Экипировано]'
                        if hasattr(item, 'defense_bonus') and item_uid and armor_uid == item_uid:
                            equipped = ' [Экипировано]'
                        elif hasattr(item, 'defense_bonus') and getattr(self.player, 'armor', None) is item:
                            equipped = ' [Экипировано]'
                        if hasattr(item, 'effect_id') and item_uid and artifact_uid == item_uid:
                            equipped = ' [Экипировано]'
                        elif hasattr(item, 'effect_id') and getattr(self.player, 'artifact', None) is item:
                            equipped = ' [Экипировано]'
                except Exception:
                    if hasattr(item, 'attack_bonus') and getattr(self.player, 'weapon', None) is item:
                        equipped = ' [Экипировано]'
                    if hasattr(item, 'defense_bonus') and getattr(self.player, 'armor', None) is item:
                        equipped = ' [Экипировано]'
                    if hasattr(item, 'effect_id') and getattr(self.player, 'artifact', None) is item:
                        equipped = ' [Экипировано]'

                strength_tag = ''
                if show_strength and self.player:
                    s = self.inventory.evaluate_strength(item, self.player)
                    if s == 'stronger':
                        strength_tag = ' [Сильнее]'
                    elif s == 'weaker':
                        strength_tag = ' [Слабее]'
                    elif s == 'equal':
                        strength_tag = ' [Равное]'

                # add quality icon if available
                if hasattr(item, 'effect_id'):
                    icon = '✪'
                else:
                    icon = QUALITY_ICONS.get(getattr(item, 'quality', None), '')
                item_text = f"{i+1}. {icon} {item.name}{equipped}{strength_tag}"
                displayed_indices.append(i)
                # Temporarily store display text and sort keys
                listbox.insert(tk.END, item_text)
                # Color by quality if available
                try:
                    quality = getattr(item, 'quality', None)
                    if quality:
                        qc = {
                            'wooden': '#9e9e9e',
                            'rusty': '#a1887f',
                            'iron': '#bdbdbd',
                            'silver': '#c0c0ff',
                            'luxury': '#ffd54f',
                            'dragon': '#e91e63'
                        }.get(quality, self.colors['text_fg'])
                        listbox.itemconfig(tk.END, fg=qc)
                    elif hasattr(item, 'effect_id'):
                        listbox.itemconfig(tk.END, fg=self.colors.get('magenta', '#e91e63'))
                except Exception:
                    pass
            # update equip labels
            try:
                weapon_label.config(text=(self.player.weapon.name if getattr(self.player, 'weapon', None) else 'Нет'))
                # Visual marker for equipped slot
                if getattr(self.player, 'weapon', None):
                    weapon_label.config(bg=self.colors.get('green', '#4CAF50'), fg='white')
                else:
                    weapon_label.config(bg=self.colors['text_bg'], fg=self.colors['text_fg'])
                # ensure frame label color
                try:
                    weapon_frame.config(bg=self.colors['bg'])
                except Exception:
                    pass
            except Exception:
                pass
            try:
                armor_label.config(text=(self.player.armor.name if getattr(self.player, 'armor', None) else 'Нет'))
                if getattr(self.player, 'armor', None):
                    armor_label.config(bg=self.colors.get('cyan', '#00bcd4'), fg='white')
                else:
                    armor_label.config(bg=self.colors['text_bg'], fg=self.colors['text_fg'])
                try:
                    armor_frame.config(bg=self.colors['bg'])
                except Exception:
                    pass
            except Exception:
                pass
            try:
                artifact_label.config(text=(self.player.artifact.name if getattr(self.player, 'artifact', None) else 'Нет'))
                if getattr(self.player, 'artifact', None):
                    artifact_label.config(bg=self.colors.get('magenta', '#e91e63'), fg='white')
                else:
                    artifact_label.config(bg=self.colors['text_bg'], fg=self.colors['text_fg'])
                try:
                    artifact_frame.config(bg=self.colors['bg'])
                except Exception:
                    pass
            except Exception:
                pass

            # Apply sorting if requested
            if sort_key != 'Нет':
                try:
                    # Build list of tuples (sort_value, idx, text)
                    items_for_sort = []
                    for pos, real_idx in enumerate(displayed_indices):
                        itm = self.inventory.items[real_idx]
                        if sort_key == 'По атаке':
                            sv = getattr(itm, 'attack_bonus', 0)
                        elif sort_key == 'По защите':
                            sv = getattr(itm, 'defense_bonus', 0)
                        elif sort_key == 'По качеству':
                            qname = getattr(itm, 'quality', 'wooden')
                            sv = QUALITY_MULTIPLIER.get(qname, 0)
                        else:
                            sv = 0
                        items_for_sort.append((sv, real_idx))

                    # Sort descending by value
                    items_for_sort.sort(key=lambda x: x[0], reverse=True)

                    # Rebuild listbox
                    listbox.delete(0, tk.END)
                    new_displayed = []
                    for sv, real_idx in items_for_sort:
                        itm = self.inventory.items[real_idx]
                        equipped = ''
                        try:
                            if getattr(itm, 'equipped', False):
                                equipped = ' [Экипировано]'
                            else:
                                item_uid = getattr(itm, 'uid', None)
                                weapon_uid = getattr(getattr(self.player, 'weapon', None), 'uid', None)
                                armor_uid = getattr(getattr(self.player, 'armor', None), 'uid', None)
                                artifact_uid = getattr(getattr(self.player, 'artifact', None), 'uid', None)
                                if hasattr(itm, 'attack_bonus') and item_uid and weapon_uid == item_uid:
                                    equipped = ' [Экипировано]'
                                elif hasattr(itm, 'attack_bonus') and getattr(self.player, 'weapon', None) is itm:
                                    equipped = ' [Экипировано]'
                                if hasattr(itm, 'defense_bonus') and item_uid and armor_uid == item_uid:
                                    equipped = ' [Экипировано]'
                                elif hasattr(itm, 'defense_bonus') and getattr(self.player, 'armor', None) is itm:
                                    equipped = ' [Экипировано]'
                                if hasattr(itm, 'effect_id') and item_uid and artifact_uid == item_uid:
                                    equipped = ' [Экипировано]'
                                elif hasattr(itm, 'effect_id') and getattr(self.player, 'artifact', None) is itm:
                                    equipped = ' [Экипировано]'
                        except Exception:
                            if hasattr(itm, 'attack_bonus') and getattr(self.player, 'weapon', None) is itm:
                                equipped = ' [Экипировано]'
                            if hasattr(itm, 'defense_bonus') and getattr(self.player, 'armor', None) is itm:
                                equipped = ' [Экипировано]'
                            if hasattr(itm, 'effect_id') and getattr(self.player, 'artifact', None) is itm:
                                equipped = ' [Экипировано]'
                        s_tag = ''
                        if show_strength and self.player:
                            s = self.inventory.evaluate_strength(itm, self.player)
                            if s == 'stronger':
                                s_tag = ' [Сильнее]'
                            elif s == 'weaker':
                                s_tag = ' [Слабее]'
                            elif s == 'equal':
                                s_tag = ' [Равное]'
                        if hasattr(itm, 'effect_id'):
                            icon = '✪'
                        else:
                            icon = QUALITY_ICONS.get(getattr(itm, 'quality', None), '')
                        item_text = f"{real_idx+1}. {icon} {itm.name}{equipped}{s_tag}"
                        listbox.insert(tk.END, item_text)
                        # color by quality
                        try:
                            quality = getattr(itm, 'quality', None)
                            if quality:
                                qc = {
                                    'wooden': '#9e9e9e',
                                    'rusty': '#a1887f',
                                    'iron': '#bdbdbd',
                                    'silver': '#c0c0ff',
                                    'luxury': '#ffd54f',
                                    'dragon': '#e91e63'
                                }.get(quality, self.colors['text_fg'])
                                listbox.itemconfig(tk.END, fg=qc)
                            elif hasattr(itm, 'effect_id'):
                                listbox.itemconfig(tk.END, fg=self.colors.get('magenta', '#e91e63'))
                        except Exception:
                            pass
                        new_displayed.append(real_idx)

                    displayed_indices[:] = new_displayed
                except Exception:
                    pass

        # Обновляем список при смене фильтра/чекбокса/поиска/сортировки
        def on_filter_change(event=None):
            refresh_list()

        filter_box.bind('<<ComboboxSelected>>', on_filter_change)
        show_strength_var.trace_add('write', lambda *args: refresh_list())
        search_var.trace_add('write', lambda *args: refresh_list())
        sort_box.bind('<<ComboboxSelected>>', on_filter_change)

        # Drag & drop and equip handlers
        drag_data = {'start_index': None}

        def equip_item_by_index(real_idx, slot):
            try:
                if real_idx < 0 or real_idx >= len(self.inventory.items):
                    return
                item = self.inventory.items[real_idx]

                # Equip by setting flags, do not remove from inventory to avoid duplicates confusion
                if slot == 'weapon' and hasattr(item, 'attack_bonus'):
                    old = getattr(self.player, 'weapon', None)
                    if old:
                        try:
                            old.equipped = False
                        except Exception:
                            pass
                    try:
                        item.equipped = True
                    except Exception:
                        pass
                    self.player.weapon = item

                elif slot == 'armor' and hasattr(item, 'defense_bonus'):
                    old = getattr(self.player, 'armor', None)
                    if old:
                        try:
                            old.equipped = False
                        except Exception:
                            pass
                    try:
                        item.equipped = True
                    except Exception:
                        pass
                    self.player.armor = item

                elif slot == 'artifact' and (hasattr(item, 'effect_id') or hasattr(item, 'bonus_slots')):
                    old = getattr(self.player, 'artifact', None)
                    if old:
                        try:
                            old.equipped = False
                        except Exception:
                            pass
                    try:
                        item.equipped = True
                    except Exception:
                        pass
                    self.player.artifact = item

                # Обновляем отображение
                self.update_info_panel()
                refresh_list()
            except Exception as e:
                print(f"Ошибка при экипировке: {e}")
                self.update_info_panel()
                refresh_list()

        def unequip_weapon():
            if getattr(self.player, 'weapon', None):
                try:
                    self.player.weapon.equipped = False
                except Exception:
                    pass
                self.player.weapon = None
                self.update_info_panel()
                refresh_list()

        def unequip_armor():
            if getattr(self.player, 'armor', None):
                try:
                    self.player.armor.equipped = False
                except Exception:
                    pass
                self.player.armor = None
                self.update_info_panel()
                refresh_list()

        def unequip_artifact():
            if getattr(self.player, 'artifact', None):
                try:
                    self.player.artifact.equipped = False
                except Exception:
                    pass
                self.player.artifact = None
                self.update_info_panel()
                refresh_list()

        # Wire unequip buttons
        try:
            weapon_unequip.config(command=unequip_weapon)
            armor_unequip.config(command=unequip_armor)
            artifact_unequip.config(command=unequip_artifact)
        except Exception:
            pass

        def on_listbox_button_press(event):
            try:
                idx = listbox.nearest(event.y)
                drag_data['start_index'] = idx
                
                # Показать информацию о выбранном предмете
                try:
                    real_idx = displayed_indices[idx]
                    item = self.inventory.items[real_idx]
                    
                    info_text = f"{item.name}"
                    
                    # Информация об артефакте (бонусы слотов)
                    if hasattr(item, 'bonus_slots') and item.bonus_slots:
                        info_text += f"\n\n✨ Артефакт ({len(item.bonus_slots)} слотов):\n"
                        for i, slot in enumerate(item.bonus_slots, 1):
                            if slot['type'] == 'stat':
                                stat = slot['stat']
                                value = slot['value']
                                info_text += f"  [{i}] +{value} {stat}\n"
                            elif slot['type'] == 'crit':
                                value = slot['value']
                                info_text += f"  [{i}] +{value}% крит\n"
                            elif slot['type'] == 'evade':
                                value = slot['value']
                                info_text += f"  [{i}] +{value}% уклонение\n"
                    
                    # Форматируем информацию о требованиях (для оружия/брони)
                    req_text = ""
                    if hasattr(item, 'requirements') and item.requirements:
                        req_text = "\nТребования:\n"
                        stat_labels = {
                            'attack': t('stat_attack'),
                            'defense': t('stat_defense'),
                            'intellect': t('stat_intellect'),
                            'luck': t('stat_luck'),
                            'fire_resist': t('stat_fire_resist'),
                            'cold_resist': t('stat_cold_resist'),
                            'max_hp': t('stat_max_hp')
                        }
                        
                        for stat, req_value in item.requirements.items():
                            player_stat = getattr(self.player, stat, 0)
                            is_met = player_stat >= req_value
                            status = "✓" if is_met else "✗"
                            stat_display = stat_labels.get(stat, stat)
                            req_text += f"  {status} {stat_display}: {req_value} (у вас: {player_stat})\n"
                        
                        # Показываем бонус скейлинга если требования выполнены
                        if hasattr(item, 'get_effective_bonus'):
                            base_bonus = item.attack_bonus if hasattr(item, 'attack_bonus') else item.defense_bonus if hasattr(item, 'defense_bonus') else 0
                            effective_bonus = item.get_effective_bonus(self.player)
                            bonus_text = f"\nДополнительный бонус: +{effective_bonus - base_bonus}"
                            req_text += bonus_text
                    
                    # Обновляем метку с информацией
                    info_text += req_text
                    info_label.config(text=info_text)
                except Exception as e:
                    pass
            except Exception:
                drag_data['start_index'] = None

        def on_listbox_release(event):
            si = drag_data.get('start_index')
            if si is None:
                return
            
            try:
                real_idx = displayed_indices[si]
            except (IndexError, Exception):
                drag_data['start_index'] = None
                return
            
            # Получить координаты слотов экипировки относительно экрана
            try:
                weapon_x = weapon_label.winfo_rootx()
                weapon_y = weapon_label.winfo_rooty()
                weapon_w = weapon_label.winfo_width()
                weapon_h = weapon_label.winfo_height()
                
                armor_x = armor_label.winfo_rootx()
                armor_y = armor_label.winfo_rooty()
                armor_w = armor_label.winfo_width()
                armor_h = armor_label.winfo_height()

                artifact_x = artifact_label.winfo_rootx()
                artifact_y = artifact_label.winfo_rooty()
                artifact_w = artifact_label.winfo_width()
                artifact_h = artifact_label.winfo_height()
                
                # Проверяем, находится ли курсор над слотом оружия
                if (weapon_x <= event.x_root <= weapon_x + weapon_w and 
                    weapon_y <= event.y_root <= weapon_y + weapon_h):
                    equip_item_by_index(real_idx, 'weapon')
                # Проверяем, находится ли курсор над слотом брони
                elif (armor_x <= event.x_root <= armor_x + armor_w and 
                      armor_y <= event.y_root <= armor_y + armor_h):
                    equip_item_by_index(real_idx, 'armor')
                elif (artifact_x <= event.x_root <= artifact_x + artifact_w and
                      artifact_y <= event.y_root <= artifact_y + artifact_h):
                    equip_item_by_index(real_idx, 'artifact')
            except Exception as e:
                print(f"Ошибка при перетаскивании: {e}")
            
            drag_data['start_index'] = None

        def on_double_click(event):
            sel = listbox.curselection()
            if not sel:
                return
            sel = sel[0]
            try:
                real_idx = displayed_indices[sel]
            except Exception:
                return
            item = self.inventory.items[real_idx]
            if hasattr(item, 'attack_bonus'):
                equip_item_by_index(real_idx, 'weapon')
            elif hasattr(item, 'defense_bonus'):
                equip_item_by_index(real_idx, 'armor')
            elif hasattr(item, 'effect_id'):
                equip_item_by_index(real_idx, 'artifact')

        listbox.bind('<ButtonPress-1>', on_listbox_button_press)
        listbox.bind('<ButtonRelease-1>', on_listbox_release)
        listbox.bind('<Double-Button-1>', on_double_click)

        # Инициалный рендер
        refresh_list()
        
        # Кнопки действий снизу
        btn_frame = tk.Frame(inv_window, bg=self.colors['bg'])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def use_selected():
            selection = listbox.curselection()
            if selection:
                sel = selection[0]
                real_idx = displayed_indices[sel]
                self.inventory.use_item(real_idx, self.player)
                self.update_info_panel()
                inv_window.destroy()
                self.show_inventory()
        
        def upgrade_selected():
            selection = listbox.curselection()
            if selection:
                sel = selection[0]
                idx = displayed_indices[sel]
                item = self.inventory.items[idx]
                
                # Получить информацию об улучшении
                info = self.inventory.upgrade_item_gui(idx, self.player, rotation=self.rotation, stones_to_use=-1)
                
                if 'error' in info:
                    messagebox.showerror("Ошибка", info['error'])
                    return
                
                # Спросить о камнях улучшения
                stones_to_use = 0
                if info['max_stones_use'] > 0:
                    msg = f"Улучшение {info['item_name']}:\n\n"
                    msg += f"Текущий уровень: {info['current_level']}\n"
                    msg += f"Базовая стоимость: {info['base_cost']} золота\n\n"
                    msg += f"У вас камней улучшения: {info['stones_available']}\n"
                    msg += f"Можно использовать до {info['max_stones_use']} камней\n"
                    msg += f"(каждый уменьшает цену на 30%)\n\n"
                    msg += f"Сколько камней использовать? (0-{info['max_stones_use']})"
                    
                    stones_input = simpledialog.askinteger(
                        "Камни улучшения",
                        msg,
                        minvalue=0,
                        maxvalue=info['max_stones_use']
                    )
                    
                    if stones_input is None:  # Пользователь отменил
                        return
                    
                    stones_to_use = stones_input
                
                # Рассчитать финальную стоимость
                final_cost = int(info['base_cost'] * (0.7 ** stones_to_use))
                
                # Подтверждение
                confirm_msg = f"Улучшить {info['item_name']}?\n\n"
                confirm_msg += f"Стоимость: {final_cost} золота\n"
                if stones_to_use > 0:
                    confirm_msg += f"Будет использовано камней: {stones_to_use}\n"
                confirm_msg += f"\nУ вас: {self.player.gold} золота"
                
                if not messagebox.askyesno("Подтверждение улучшения", confirm_msg):
                    return
                
                # Выполнить улучшение
                result = self.inventory.upgrade_item_gui(idx, self.player, rotation=self.rotation, stones_to_use=stones_to_use)
                
                if 'error' in result:
                    messagebox.showerror("Ошибка", result['error'])
                else:
                    self.print(f"Предмет улучшен до уровня {result['new_level']}! Потрачено: {result['cost']} золота", 'green')
                    if result['stones_used'] > 0:
                        self.print(f"Использовано камней: {result['stones_used']}", 'cyan')
                    self.update_info_panel()
                    inv_window.destroy()
                    self.show_inventory()
        
        def sell_selected():
            selection = listbox.curselection()
            if selection:
                sel = selection[0]
                idx = displayed_indices[sel]
                item = self.inventory.items[idx]
                
                # Рассчитать цену продажи
                try:
                    from items import QUALITY_MULTIPLIER
                except Exception:
                    QUALITY_MULTIPLIER = {}
                
                base_price = getattr(item, 'price', 0)
                level = getattr(item, 'level', 1)
                quality = getattr(item, 'quality', 'wooden')
                quality_mul = QUALITY_MULTIPLIER.get(quality, 0)
                sell_price = int((base_price + level * 50) * (1 + quality_mul) * 0.5 + self.rotation * 10)
                sell_price = int(sell_price * (1 + self.player.get_total_luck() * 0.02))
                
                # Подтверждение продажи
                response = messagebox.askyesno(
                    "Продажа предмета",
                    f"Продать {item.name} за {sell_price} золота?"
                )
                
                if response:
                    self.player.gold += sell_price
                    self.inventory.items.pop(idx)
                    self.print(f"Предмет продан. Получено {sell_price} золота.", 'green')
                    self.update_info_panel()
                    inv_window.destroy()
                    self.show_inventory(show_sell_button=True)
        
        tk.Button(
            btn_frame,
            text="Использовать",
            command=use_selected,
            bg=self.colors['green'],
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Улучшить",
            command=upgrade_selected,
            bg=self.colors['cyan'],
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Кнопка продажи показывается только при вызове из магазина
        if show_sell_button:
            tk.Button(
                btn_frame,
                text="Продать",
                command=sell_selected,
                bg=self.colors['yellow'],
                fg='black',
                font=('Arial', 10),
                relief=tk.FLAT,
                padx=15,
                pady=8
            ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Закрыть",
            command=inv_window.destroy,
            bg=self.colors['red'],
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT, padx=5)
    
    def show_stats(self):
        """Показать характеристики"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return
        
        self.clear_text()
        self.print("="*40, 'yellow')
        self.print("📊 ХАРАКТЕРИСТИКИ ПЕРСОНАЖА", 'cyan')
        self.print("="*40, 'yellow')
        self.print(f"Имя: {self.player.name}", 'text_fg')
        self.print(f"Класс: {self.player.class_name}", 'text_fg')
        self.print(f"Уровень: {self.player.level}", 'green')
        self.print(f"Престиж: {getattr(self.player, 'prestige_level', 0)}", 'magenta')
        self.print(f"Опыт: {self.player.exp}/{self.player.exp_to_next_level}", 'green')
        self.print(f"Здоровье: {self.player.hp}/{self.player.max_hp}", 'green')
        self.print(f"Атака: {self.player.attack} (всего: {self.player.get_total_attack()})", 'magenta')
        self.print(f"Защита: {self.player.defense} (всего: {self.player.get_total_defense()})", 'cyan')
        self.print(f"Сопротивление огню: {getattr(self.player, 'fire_resist', 0)}%", 'red')
        self.print(f"Сопротивление холоду: {getattr(self.player, 'cold_resist', 0)}%", 'cyan')
        self.print(f"Удача: {self.player.get_total_luck()}", 'yellow')
        self.print(f"Интеллект: {getattr(self.player, 'intellect', 0)}", 'magenta')
        self.print(f"Золото: {self.player.gold}", 'yellow')
        self.print(f"Очки характеристик: {self.player.stat_points}", 'green')
        self.print(f"Артефакт: {self.player.artifact.name if getattr(self.player, 'artifact', None) else 'Нет'}", 'cyan')
        self.print(f"\nОружие: {self.player.weapon.name if self.player.weapon else 'Нет'}", 'text_fg')
        self.print(f"Броня: {self.player.armor.name if self.player.armor else 'Нет'}", 'text_fg')
        self.print("="*40 + "\n", 'yellow')

    def show_prestige(self):
        """Показать окно престижа"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return

        self.show_prestige_bonuses()

    def show_prestige_bonuses(self):
        """Отдельный экран бонусов престижа"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return

        req = self.player.get_prestige_requirement()
        cur_level = getattr(self.player, 'prestige_level', 0)
        next_level = cur_level + 1
        cur_bonus = self.player.get_prestige_bonus(level=cur_level)
        next_bonus = self.player.get_prestige_bonus(level=next_level)

        win = tk.Toplevel(self.root)
        win.title(t('prestige_bonuses_title'))
        win.geometry('520x420')
        win.configure(bg=self.colors['bg'])
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win,
            text=t('prestige_title'),
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 14, 'bold')
        ).pack(pady=(10, 6))

        tk.Label(
            win,
            text=t('prestige_req', level=req),
            bg=self.colors['bg'],
            fg=self.colors['yellow'],
            font=('Arial', 10)
        ).pack(pady=(0, 10))

        def bonus_block(title_key, bonus):
            xp_pct = int((bonus.get('exp_mult', 1.0) - 1.0) * 100)
            gold_pct = int((bonus.get('gold_mult', 1.0) - 1.0) * 100)
            loot_pct = int(bonus.get('loot_bonus', 0.0) * 100)
            frame = tk.LabelFrame(
                win,
                text=t(title_key),
                bg=self.colors['bg'],
                fg=self.colors['text_fg']
            )
            frame.pack(fill=tk.X, padx=12, pady=6)
            lines = [
                t('prestige_bonus_line', label='HP', value=bonus.get('hp', 0)),
                t('prestige_bonus_line', label='ATK', value=bonus.get('attack', 0)),
                t('prestige_bonus_line', label='DEF', value=bonus.get('defense', 0)),
                t('prestige_bonus_line', label=t('prestige_sp_label'), value=bonus.get('stat_points', 0)),
                t('prestige_bonus_pct', label=t('prestige_xp_label'), value=xp_pct),
                t('prestige_bonus_pct', label=t('prestige_gold_label'), value=gold_pct),
                t('prestige_bonus_pct', label=t('prestige_loot_label'), value=loot_pct),
            ]
            for ln in lines:
                tk.Label(
                    frame,
                    text=ln,
                    bg=self.colors['bg'],
                    fg=self.colors['text_fg'],
                    font=('Arial', 10)
                ).pack(anchor='w', padx=8)

        bonus_block('prestige_current', cur_bonus)
        bonus_block('prestige_next', next_bonus)

        tk.Label(
            win,
            text=t('prestige_reset_note'),
            bg=self.colors['bg'],
            fg=self.colors['magenta'],
            font=('Arial', 9)
        ).pack(pady=(6, 6))

        btn_frame = tk.Frame(win, bg=self.colors['bg'])
        btn_frame.pack(fill=tk.X, padx=12, pady=10)

        def do_prestige():
            if not self.player.can_prestige():
                messagebox.showinfo(t('prestige_title'), t('prestige_locked', level=req))
                return
            confirm = messagebox.askyesno(
                t('prestige_title'),
                t('prestige_confirm_short', level=next_level)
            )
            if not confirm:
                return

            self.player.prestige_reset()
            self.inventory = Inventory()
            self.rotation = 0
            self.victories = 0
            self.in_combat = False
            self.current_enemy = None

            # Стартовое зелье после престижа
            starter = get_item_scaled('small_potion', rotation=self.rotation, player_level=self.player.level)
            if starter:
                self.inventory.add_item(starter)

            self.update_info_panel()
            self.create_game_buttons()
            self.clear_text()
            self.print(t('prestige_done', level=self.player.prestige_level), 'magenta')
            self.print_main_menu()
            win.destroy()

        prestige_btn = tk.Button(
            btn_frame,
            text=t('prestige_now'),
            command=do_prestige,
            bg=self.colors['magenta'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=14,
            pady=8
        )
        prestige_btn.pack(side=tk.LEFT)

        if not self.player.can_prestige():
            prestige_btn.config(state=tk.DISABLED)

        tk.Button(
            btn_frame,
            text=t('close'),
            command=win.destroy,
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            relief=tk.FLAT,
            padx=14,
            pady=8
        ).pack(side=tk.RIGHT)
    
    def spend_stat_points(self):
        """Распределить очки характеристик"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return
        
        if self.player.stat_points <= 0:
            messagebox.showinfo("Очки характеристик", "У вас нет доступных очков характеристик!")
            return
        
        # Окно распределения
        stat_window = tk.Toplevel(self.root)
        stat_window.title(f"Очки характеристик: {self.player.stat_points}")
        stat_window.geometry("500x400")
        stat_window.configure(bg=self.colors['bg'])
        stat_window.transient(self.root)
        stat_window.grab_set()
        
        tk.Label(
            stat_window,
            text=f"Доступно очков: {self.player.stat_points}",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        stats = [
            ("Здоровье (+15 HP)", lambda: self.add_stat('hp')),
            ("Атака (+2)", lambda: self.add_stat('attack')),
            ("Защита (+2)", lambda: self.add_stat('defense')),
            ("Сопротивление огню (+2)", lambda: self.add_stat('fire_resist')),
            ("Сопротивление холоду (+2)", lambda: self.add_stat('cold_resist')),
            ("Удача (+1)", lambda: self.add_stat('luck')),
            ("Интеллект (+1)", lambda: self.add_stat('intellect'))
        ]
        
        def apply_stat(stat_func):
            stat_func()
            stat_window.destroy()
            self.update_info_panel()
            if self.player.stat_points > 0:
                self.spend_stat_points()
        
        for text, func in stats:
            btn = tk.Button(
                stat_window,
                text=text,
                command=lambda f=func: apply_stat(f),
                bg=self.colors['button_bg'],
                fg=self.colors['button_fg'],
                font=('Arial', 10),
                relief=tk.FLAT,
                padx=20,
                pady=10
            )
            btn.pack(fill=tk.X, padx=20, pady=3)
    
    def add_stat(self, stat_name):
        """Добавить очко к характеристике"""
        if self.player.stat_points <= 0:
            return
        
        if stat_name == 'hp':
            self.player.max_hp += 15
            self.player.hp += 15
        elif stat_name == 'attack':
            self.player.attack += 2
        elif stat_name == 'defense':
            self.player.defense += 2
        elif stat_name == 'fire_resist':
            self.player.fire_resist += 2
        elif stat_name == 'cold_resist':
            self.player.cold_resist += 2
        elif stat_name == 'luck':
            self.player.luck += 1
        elif stat_name == 'intellect':
            self.player.intellect += 1
        
        self.player.stat_points -= 1
        self.print(f"Характеристика улучшена! Осталось очков: {self.player.stat_points}", 'green')
    
    def show_shop(self):
        """Показать магазин"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return
        
        # Формируем пул товаров
        base_pool = ['small_potion', 'medium_potion', 'large_potion', 'wooden_sword', 'leather_armor']
        # Книги навыков больше не добавляются детерминированно; они редкие и появляются по шансам ниже
        if self.rotation >= 1:
            base_pool += ['iron_sword', 'iron_armor']
        if self.rotation >= 2:
            base_pool += ['steel_sword', 'steel_armor']
        if self.rotation >= 3:
            base_pool += ['legendary_sword', 'legendary_armor']
        
        shop_list = []
        for iid in base_pool:
            item = get_item_scaled(iid, rotation=self.rotation, player_level=self.player.level)
            if not item:
                continue
            quality_mul = QUALITY_MULTIPLIER.get(getattr(item, 'quality', 'wooden'), 0)
            price = int(getattr(item, 'price', 0) + getattr(item, 'level', 1) * 50 + quality_mul * 200 + self.rotation * 30)
            shop_list.append((iid, item, price))

        # Шанс появления книги навыка в магазине (одной книги за посещение магазина)
        try:
            book_spawn_chance = min(0.5, 0.12 + self.rotation * 0.08 + self.player.get_total_luck() * 0.01)
            if random.random() < book_spawn_chance:
                book_pool = ['book_warrior_rage', 'book_mage_lightning', 'book_rogue_evade']
                bid = random.choice(book_pool)
                book = get_item_scaled(bid, rotation=self.rotation, player_level=self.player.level)
                if book:
                    # Небольшой шанс, что книга будет улучшенной (+1 уровень поверх ротационного бонуса)
                    upg_chance = min(0.35, 0.05 * self.rotation + self.player.get_total_luck() * 0.01)
                    if random.random() < upg_chance and hasattr(book, 'levels'):
                        try:
                            from skills import get_skill
                            meta = get_skill(book.skill_id) or {}
                            maxl = meta.get('max_level', getattr(book, 'levels', 1))
                        except Exception:
                            maxl = getattr(book, 'levels', 1)
                        book.levels = min(maxl, getattr(book, 'levels', 1) + 1)
                        book.price = int(getattr(book, 'price', 0) * 1.5)
                        # отметим в имени
                        if '(+' not in book.name:
                            book.name = f"{book.name} (+{book.levels})"
                    shop_list.append((bid, book, getattr(book, 'price', 0)))
        except Exception:
            pass
        
        # Окно магазина
        shop_window = tk.Toplevel(self.root)
        shop_window.title("🏪 Магазин")
        shop_window.geometry("700x500")
        shop_window.configure(bg=self.colors['bg'])
        shop_window.transient(self.root)
        
        tk.Label(
            shop_window,
            text=f"💰 Ваше золото: {self.player.gold}",
            bg=self.colors['bg'],
            fg=self.colors['yellow'],
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        # Список товаров
        frame = tk.Frame(shop_window, bg=self.colors['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            frame,
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            font=('Consolas', 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for i, (iid, item, price) in enumerate(shop_list):
            listbox.insert(tk.END, f"{i+1}. {item.name} - {price} золота")
        
        # Кнопки
        btn_frame = tk.Frame(shop_window, bg=self.colors['bg'])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def buy_selected():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                iid, item, price = shop_list[idx]
                if self.player.gold >= price:
                    self.player.gold -= price
                    self.inventory.add_item(item)
                    self.update_info_panel()
                    messagebox.showinfo("Покупка", f"Вы купили {item.name}!")
                    shop_window.destroy()
                else:
                    messagebox.showwarning("Недостаточно золота", f"Нужно {price} золота!")
        
        def sell_items():
            shop_window.destroy()
            self.show_inventory(show_sell_button=True)
        
        tk.Button(
            btn_frame,
            text="Купить",
            command=buy_selected,
            bg=self.colors['green'],
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Продать предметы",
            command=sell_items,
            bg=self.colors['yellow'],
            fg='black',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Закрыть",
            command=shop_window.destroy,
            bg=self.colors['red'],
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT, padx=5)
    
    def rest(self):
        """Отдохнуть"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return
        
        if self.player.hp >= self.player.max_hp:
            messagebox.showinfo("Отдых", "У вас уже максимальное здоровье!")
            return
        
        cost = 20
        if self.player.gold >= cost:
            response = messagebox.askyesno(
                "Отдохнуть?",
                f"Отдых стоит {cost} золота. Восстановить HP до максимума?"
            )
            if response:
                self.player.gold -= cost
                self.player.hp = self.player.max_hp
                self.update_info_panel()
                self.print(f"Вы отдохнули в таверне за {cost} золота.", 'green')
                self.print(f"Здоровье восстановлено: {self.player.hp}/{self.player.max_hp}\n", 'green')
        else:
            messagebox.showwarning("Недостаточно золота", f"Нужно {cost} золота!")
    
    def save_game_data(self):
        """Сохранить игру"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Нечего сохранять!")
            return
        # Открыть интерфейс слотов сохранений
        self.show_save_slots(mode='save')
    
    def load_game_data(self):
        """Загрузить игру"""
        # Показать UI слотов для загрузки
        return self.show_save_slots(mode='load')

    def show_save_slots(self, mode='load'):
        """Показать окно слотов сохранений. mode = 'save' или 'load'"""
        slots = save_system.list_save_slots()
        win = tk.Toplevel(self.root)
        win.title(t('save_slots_title') if mode == 'save' else t('load_slots_title'))
        win.geometry('700x350')
        win.transient(self.root)
        win.grab_set()

        frame = tk.Frame(win, bg=self.colors['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def make_slot_row(n, info):
            is_autosave = (n == save_system.MAX_SLOTS)
            if not info['exists']:
                label_name = t('autosave_slot_label') if is_autosave else t('save_slot_label', slot=n)
                lbl_text = f"{label_name}: {t('slot_empty')}"
            else:
                # format date and time DD.MM.YYYY HH:MM
                try:
                    import datetime
                    ts = info.get('mtime')
                    date_str = datetime.datetime.fromtimestamp(ts).strftime('%d.%m.%Y %H:%M') if ts else ''
                except Exception:
                    date_str = ''
                pname = info.get('player_name') or t('default_hero_name')
                class_id = info.get('class_id')
                try:
                    cls = get_class(class_id)
                    cname = cls.name if cls else (class_id or '')
                except Exception:
                    cname = class_id or ''
                level = info.get('level')
                lvl_part = f" L{level}" if level else ''
                class_part = f" ({cname}{lvl_part})" if cname else (f"{lvl_part}" if lvl_part else '')
                label_name = t('autosave_slot_label') if is_autosave else t('save_slot_label', slot=n)
                lbl_text = f"{label_name}: {pname}{class_part} | {date_str}"
            lbl = tk.Label(frame, text=lbl_text, bg=self.colors['bg'], fg=self.colors['text_fg'])
            lbl.grid(row=n-1, column=0, sticky='w', padx=5, pady=5)
            def on_action():
                if mode == 'save':
                    ok, msg = save_system.save_game_slot(self.player, self.inventory, self.rotation, self.victories, slot=n)
                    if ok:
                        self.print(msg, 'green')
                        messagebox.showinfo(t('save'), msg)
                        win.destroy()
                    else:
                        messagebox.showerror(t('error'), msg)
                else:
                    res, msg = save_system.load_game_slot(slot=n)
                    if res:
                        self.player, self.inventory, self.rotation, self.victories = res
                        # restore full UI
                        self.create_game_buttons()
                        self.update_info_panel()
                        self.clear_text()
                        self.print(msg, 'green')
                        self.print_main_menu()
                        messagebox.showinfo(t('load'), msg)
                        win.destroy()
                    else:
                        messagebox.showerror(t('error'), msg)

            # Disable manual Save button for the reserved autosave slot
            if mode == 'save' and is_autosave:
                btn = tk.Button(frame, text=(t('save') if mode == 'save' else t('load')), state='disabled',
                                bg=self.colors['button_bg'], fg=self.colors['button_fg'])
            else:
                btn = tk.Button(frame, text=(t('save') if mode == 'save' else t('load')), command=on_action,
                                bg=self.colors['button_bg'], fg=self.colors['button_fg'])
            btn.grid(row=n-1, column=1, padx=5, pady=5)

            def on_delete():
                fn = save_system._slot_filename(n)
                if os.path.exists(fn):
                    try:
                        os.remove(fn)
                        messagebox.showinfo(t('delete'), t('slot_deleted'))
                        win.destroy()
                    except Exception as e:
                        messagebox.showerror(t('error'), str(e))

            # Disable delete for the autosave slot
            if is_autosave:
                del_btn = tk.Button(frame, text=t('delete'), state='disabled', bg=self.colors['button_bg'], fg=self.colors['button_fg'])
            else:
                del_btn = tk.Button(frame, text=t('delete'), command=on_delete, bg=self.colors['button_bg'], fg=self.colors['button_fg'])
            del_btn.grid(row=n-1, column=2, padx=5, pady=5)

        import os
        for i in range(1, save_system.MAX_SLOTS + 1):
            make_slot_row(i, slots.get(i, {'exists': False}))

        return True
    
    def change_theme(self):
        """Изменить цветовую тему"""
        theme_window = tk.Toplevel(self.root)
        theme_window.title(t('choose_theme'))
        theme_window.geometry("450x450")
        theme_window.configure(bg=self.colors['bg'])
        theme_window.transient(self.root)
        theme_window.grab_set()
        
        tk.Label(
            theme_window,
            text=t('choose_theme'),
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        def apply_theme(theme_id):
            self.current_theme = theme_id
            self.colors = self.themes[theme_id]
            self.apply_theme_to_widgets()
            theme_window.destroy()
            self.print(f"\nТема изменена на: {self.themes[theme_id]['name']}\n", 'green')
        
        for theme_id, theme_data in self.themes.items():
            btn = tk.Button(
                theme_window,
                text=theme_data['name'],
                command=lambda t=theme_id: apply_theme(t),
                bg=theme_data['button_bg'],
                fg=theme_data['button_fg'],
                font=('Arial', 11),
                relief=tk.FLAT,
                padx=20,
                pady=12,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, padx=20, pady=5)

        # Языковой переключатель внутри окна тем
        lang_frame = tk.Frame(theme_window, bg=self.colors['bg'])
        lang_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(
            lang_frame,
            text=t('language_label'),
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 10))

        def apply_language(locale_code):
            try:
                set_locale(locale_code)
                try:
                    save_system.save_settings(locale_code)
                except Exception:
                    pass
                # Обновим интерфейс и кнопки
                try:
                    self.create_game_buttons()
                    self.update_info_panel()
                except Exception:
                    pass
                # Обновим тексты в окне выбора темы после смены языка
                try:
                    theme_window.title(t('choose_theme'))
                    for widget in theme_window.winfo_children():
                        if isinstance(widget, tk.Label) and widget.cget('font') == ('Arial', 12, 'bold'):
                            widget.config(text=t('choose_theme'))
                except Exception:
                    pass
                # Сообщение пользователю
                lang_name = t('language_en') if locale_code == 'en' else t('language_ru')
                try:
                    self.print(t('language_switched', lang=lang_name), 'cyan')
                except Exception:
                    pass
            except Exception:
                pass

        tk.Button(
            lang_frame,
            text=t('language_en'),
            command=lambda: apply_language('en'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            padx=12,
            pady=8,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            lang_frame,
            text=t('language_ru'),
            command=lambda: apply_language('ru'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            padx=12,
            pady=8,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)
        
        # Кнопка админ режима
        admin_frame = tk.Frame(theme_window, bg=self.colors['bg'])
        admin_frame.pack(fill=tk.X, padx=20, pady=10)
        
        admin_status = "🟢 Включён" if self.admin_mode else "🔴 Выключен"
        tk.Label(
            admin_frame,
            text=f"Админ режим: {admin_status}",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        def toggle_admin():
            if self.admin_mode:
                # Выключить админ режим
                self.admin_mode = False
                messagebox.showinfo("Админ режим", "Админ режим выключен")
                theme_window.destroy()
                self.create_game_buttons()
            else:
                # Запросить пароль
                password = simpledialog.askstring("Админ режим", "Введите пароль:", show='*', parent=theme_window)
                if password == self.admin_password:
                    self.admin_mode = True
                    messagebox.showinfo("Админ режим", "Админ режим активирован!")
                    theme_window.destroy()
                    self.create_game_buttons()
                else:
                    messagebox.showerror("Ошибка", "Неверный пароль!")
        
        tk.Button(
            admin_frame,
            text="⚙️ Переключить",
            command=toggle_admin,
            bg=self.colors['cyan'],
            fg='white',
            padx=12,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
    def apply_theme_to_widgets(self):
        """Применить тему ко всем виджетам"""
        # Основное окно
        self.root.configure(bg=self.colors['bg'])
        
        # Информационная панель
        self.info_frame.configure(bg=self.colors['button_bg'])
        self.info_label.configure(bg=self.colors['button_bg'], fg=self.colors['text_fg'])
        
        # Текстовое поле
        self.text_area.configure(bg=self.colors['text_bg'], fg=self.colors['text_fg'])
        
        # Панель кнопок
        self.button_frame.configure(bg=self.colors['bg'])
        
        # Обновить все кнопки
        for btn_id, btn in self.game_buttons.items():
            btn.configure(
                bg=self.colors['button_bg'],
                fg=self.colors['button_fg'],
                activebackground=self.colors['button_active']
            )
        
        # Обновить цветовые теги в тексте
        for color_name in ['green', 'red', 'yellow', 'cyan', 'magenta']:
            tag_name = f'color_{color_name}'
            self.text_area.tag_config(tag_name, foreground=self.colors[color_name])
    
    # ========================================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С СОБЫТИЯМИ
    # ========================================================================
    
    def trigger_random_event(self):
        """Вызвать случайное событие"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return
        
        self.clear_text()
        event = self.event_manager.get_random_event()
        
        if not event:
            self.print("Нет доступных событий", 'red')
            return
        
        self.current_event = event
        self.in_event = True
        self.show_event()
    
    def show_event(self):
        """Показать текущее событие и выборы"""
        if not self.current_event:
            return
        
        event = self.current_event
        
        self.print("=" * 60, 'cyan')
        self.print(f"📖 {event.title}", 'magenta')
        self.print("=" * 60, 'cyan')
        self.print(f"\n{event.description}\n", 'text_fg')
        self.print(f"Место: {event.location} | Сложность: {event.difficulty}", 'yellow')
        self.print("\n" + "=" * 60 + "\n", 'cyan')
        
        # Получить доступные выборы
        available_choices = event.get_available_choices(self.player)
        
        if not available_choices:
            self.print("У вас нет доступных выборов для этого события!", 'red')
            self.in_event = False
            return
        
        # Переключиться на режим выбора событий
        self.enter_event_mode(available_choices)
    
    def enter_event_mode(self, available_choices):
        """Переключить на режим выбора события"""
        # Очистить текущие кнопки
        try:
            for btn in list(self.game_buttons.values()):
                try:
                    btn.destroy()
                except Exception:
                    pass
        except Exception:
            pass
        self.game_buttons = {}
        
        # Создать кнопки для каждого выбора
        def make_choice_handler(choice_idx):
            def handler():
                self.execute_choice(choice_idx)
            return handler
        
        for idx, (choice_idx, choice) in enumerate(available_choices):
            # Не показываем текущие требования/шанс прохождения — игрок не должен знать их заранее
            btn = tk.Button(
                self.button_frame,
                text=choice.text,
                command=make_choice_handler(choice_idx),
                bg=self.colors['button_bg'],
                fg=self.colors['button_fg'],
                activebackground=self.colors['button_active'],
                font=('Arial', 10),
                relief=tk.FLAT,
                padx=10,
                pady=8,
                cursor='hand2',
                wraplength=200,
                justify=tk.LEFT
            )
            btn.grid(row=idx, column=0, padx=3, pady=3, sticky='ew')
            self.game_buttons[f'choice_{choice_idx}'] = btn
        
        current_row = len(available_choices)
        
        # Кнопка "Проигнорировать" - показывается только если событие можно проигнорировать
        if getattr(self.current_event, 'can_ignore', True):
            ignore_btn = tk.Button(
                self.button_frame,
                text="⏭️ Проигнорировать",
                command=self.ignore_event,
                bg=self.colors['yellow'],
                fg='black',
                activebackground=self.colors['button_active'],
                font=('Arial', 9),
                relief=tk.FLAT,
                padx=10,
                pady=8,
                cursor='hand2'
            )
            ignore_btn.grid(row=current_row, column=0, padx=3, pady=3, sticky='ew')
            self.game_buttons['ignore'] = ignore_btn
            current_row += 1
        
        # Кнопка "Отменить" - показывается только админу
        if self.admin_mode:
            cancel_btn = tk.Button(
                self.button_frame,
                text="❌ Отменить (Админ)",
                command=self.cancel_event,
                bg=self.colors['red'],
                fg=self.colors['button_fg'],
                activebackground=self.colors['button_active'],
                font=('Arial', 9),
                relief=tk.FLAT,
                padx=10,
                pady=8,
                cursor='hand2'
            )
            cancel_btn.grid(row=current_row, column=0, padx=3, pady=3, sticky='ew')
            self.game_buttons['cancel'] = cancel_btn
        
        # Настроить колонку
        self.button_frame.columnconfigure(0, weight=1)
    
    def execute_choice(self, choice_idx):
        """Выполнить выбор события"""
        if not self.current_event:
            return
        
        event = self.current_event
        choice = event.choices[choice_idx]
        
        # Выполнить выбор
        outcome_text, effects, gold_reward, exp_reward = choice.execute(self.player)
        
        # Применить результат к игроку
        self.clear_text()
        self.print("=" * 60, 'cyan')
        self.print(f"📖 {event.title} - Результат", 'magenta')
        self.print("=" * 60 + "\n", 'cyan')
        self.print(outcome_text + "\n", 'green')
        
        # Применить эффекты
        if effects:
            self.print("\n--- Эффекты ---", 'yellow')
            for stat, value in effects.items():
                sign = "+" if value > 0 else ""
                try:
                    current_value = getattr(self.player, stat, 0)
                    setattr(self.player, stat, max(0, current_value + value))
                    self.print(f"{stat}: {sign}{value}", 'yellow')
                except Exception as e:
                    self.print(f"Ошибка при применении {stat}: {e}", 'red')
        
        # Добавить награды
        if gold_reward > 0:
            self.player.gold += gold_reward
            self.print(f"\n💰 +{gold_reward} золота", 'green')
        
        if exp_reward > 0:
            self.player.exp += exp_reward
            self.print(f"⭐ +{exp_reward} опыта", 'cyan')
        
        # Проверить повышение уровня
        while self.player.exp >= self.player.exp_to_next_level:
            self.player.level_up()
            self.print(f"\n🎉 Вы достигли уровня {self.player.level}!", 'green')
        
        self.print("\n" + "=" * 60, 'cyan')
        
        # Завершить событие
        self.in_event = False
        self.current_event = None
        self.update_info_panel()
        
        # Вернуться к нормальным кнопкам
        self.exit_event_mode()
    
    def ignore_event(self):
        """Проигнорировать текущее событие"""
        self.in_event = False
        self.current_event = None
        self.clear_text()
        self.print("Вы решили проигнорировать это событие и пошли дальше.", 'cyan')
        self.print("Получено 5 опыта за внимательность.\n", 'green')
        self.player.exp += 5
        self.update_info_panel()
        self.exit_event_mode()
        self.print_main_menu()
    
    def cancel_event(self):
        """Отменить текущее событие (только для админа)"""
        self.in_event = False
        self.current_event = None
        self.clear_text()
        self.print("⚙️ АДМИН: Событие отменено.", 'yellow')
        self.exit_event_mode()
        self.print_main_menu()
    
    def exit_event_mode(self):
        """Восстановить обычную панель кнопок после события"""
        try:
            for btn in list(self.game_buttons.values()):
                try:
                    btn.destroy()
                except Exception:
                    pass
        except Exception:
            pass
        self.game_buttons = {}
        # Воссоздадим стандартные кнопки
        self.create_game_buttons()
    
    def show_event_list(self):
        """Показать список всех доступных событий"""
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return
        
        self.clear_text()
        events = self.event_manager.list_events()
        
        self.print("=" * 60, 'cyan')
        self.print("📋 Доступные события", 'magenta')
        self.print("=" * 60, 'cyan')
        self.print(f"Всего событий: {len(events)}\n", 'yellow')
        
        for idx, event_info in enumerate(events, 1):
            self.print(f"{idx}. {event_info['title']}", 'green')
            self.print(f"   ID: {event_info['id']}", 'text_fg')
            self.print(f"   Место: {event_info['location']} | Сложность: {event_info['difficulty']}", 'yellow')
            self.print(f"   Выборов: {event_info['choices_count']}\n", 'text_fg')
    
    # ========================================================================
    # АДМИН ПАНЕЛЬ
    # ========================================================================
    
    def show_admin_panel(self):
        """Показать админ панель"""
        if not self.admin_mode:
            messagebox.showwarning("Ошибка", "Админ режим не активирован!")
            return
        
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала создайте персонажа!")
            return
        
        admin_window = tk.Toplevel(self.root)
        admin_window.title("⚙️ Админ панель")
        admin_window.geometry("700x600")
        admin_window.configure(bg=self.colors['bg'])
        admin_window.transient(self.root)
        
        # Создать вкладки
        notebook = ttk.Notebook(admin_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Характеристики игрока
        tab_stats = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(tab_stats, text="📊 Характеристики")
        self._create_stats_tab(tab_stats, admin_window)
        
        # Вкладка 2: События
        tab_events = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(tab_events, text="📖 События")
        self._create_events_tab(tab_events, admin_window)
        
        # Вкладка 3: Призыв врагов
        tab_combat = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(tab_combat, text="⚔️ Бой")
        self._create_combat_tab(tab_combat, admin_window)
        
        # Вкладка 4: Игрок (HP, опыт, уровень, ротация)
        tab_player = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(tab_player, text="🎮 Игрок")
        self._create_player_tab(tab_player, admin_window)
        
        # Вкладка 5: Инвентарь
        tab_inventory = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(tab_inventory, text="🎒 Инвентарь")
        self._create_inventory_tab(tab_inventory, admin_window)
        
        # Вкладка 6: Конструктор артефактов
        tab_artifact_constructor = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(tab_artifact_constructor, text="🎁 Конструктор артефактов")
        self._create_artifact_constructor_tab(tab_artifact_constructor, admin_window)
    
    def _create_stats_tab(self, parent, window):
        """Вкладка редактирования характеристик"""
        # Верхняя фрейм с основными характеристиками
        scroll_frame = tk.Frame(parent, bg=self.colors['bg'])
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(scroll_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(
            scrollable_frame,
            text="📊 Редактировать характеристики",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 10))
        
        stats_to_edit = [
            ('attack', 'Атака', 1),
            ('defense', 'Защита', 1),
            ('max_hp', 'Макс. HP', 10),
            ('fire_resist', 'Огнестойкость', 5),
            ('cold_resist', 'Холодостойкость', 5),
            ('luck', 'Удача', 1),
            ('intellect', 'Интеллект', 1),
        ]
        
        for stat_name, display_name, increment in stats_to_edit:
            frame = tk.Frame(scrollable_frame, bg=self.colors['bg'])
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            current_val = getattr(self.player, stat_name, 0)
            tk.Label(
                frame,
                text=f"{display_name}: {current_val}",
                bg=self.colors['bg'],
                fg=self.colors['text_fg'],
                font=('Arial', 11),
                width=20,
                anchor='w'
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            def make_add(stat, inc):
                def add():
                    current = getattr(self.player, stat, 0)
                    setattr(self.player, stat, current + inc)
                    if stat == 'max_hp':
                        self.player.hp = min(self.player.hp + inc, self.player.max_hp)
                    self.update_info_panel()
                    window.destroy()
                    self.show_admin_panel()
                return add
            
            tk.Button(
                frame,
                text=f"+{increment}",
                command=make_add(stat_name, increment),
                bg=self.colors['green'],
                fg='white',
                font=('Arial', 9),
                padx=10,
                pady=3
            ).pack(side=tk.LEFT, padx=2)
            
            tk.Button(
                frame,
                text=f"+{increment*10}",
                command=make_add(stat_name, increment*10),
                bg=self.colors['cyan'],
                fg='white',
                font=('Arial', 9),
                padx=10,
                pady=3
            ).pack(side=tk.LEFT, padx=2)
        
        # Разделитель
        tk.Frame(scrollable_frame, bg=self.colors['text_fg'], height=2).pack(fill=tk.X, padx=5, pady=10)
        
        # Информация о боевых механиках (dodge/crit)
        tk.Label(
            scrollable_frame,
            text="⚔️ Боевые механики",
            bg=self.colors['bg'],
            fg=self.colors['yellow'],
            font=('Arial', 12, 'bold')
        ).pack(pady=(10, 10))
        
        # Evade chance
        evade_chance = self.player.get_evade_chance() if hasattr(self.player, 'get_evade_chance') else 0
        evade_frame = tk.Frame(scrollable_frame, bg=self.colors['text_bg'], relief=tk.SUNKEN, borderwidth=1)
        evade_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            evade_frame,
            text=f"🛡️ Вероятность уклонения: {evade_chance * 100:.1f}%",
            bg=self.colors['text_bg'],
            fg=self.colors['cyan'],
            font=('Arial', 10)
        ).pack(anchor='w', padx=10, pady=5)
        
        tk.Label(
            evade_frame,
            text=f"(Удача: {self.player.get_total_luck()} × 0.5% + бонус артефакта)",
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 9)
        ).pack(anchor='w', padx=15, pady=(0, 5))
        
        # Crit chance
        crit_chance = self.player.get_crit_chance() if hasattr(self.player, 'get_crit_chance') else 0
        crit_frame = tk.Frame(scrollable_frame, bg=self.colors['text_bg'], relief=tk.SUNKEN, borderwidth=1)
        crit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            crit_frame,
            text=f"⚡ Вероятность критического удара: {crit_chance * 100:.1f}%",
            bg=self.colors['text_bg'],
            fg=self.colors['yellow'],
            font=('Arial', 10)
        ).pack(anchor='w', padx=10, pady=5)
        
        tk.Label(
            crit_frame,
            text=f"(Удача: {self.player.get_total_luck()} ÷ 3% + бонус артефакта, урон × 1.5)",
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 9)
        ).pack(anchor='w', padx=15, pady=(0, 5))
        
        # Общая атака с учетом скейлинга
        total_attack = self.player.get_total_attack()
        total_defense = self.player.get_total_defense()
        
        stats_frame = tk.Frame(scrollable_frame, bg=self.colors['text_bg'], relief=tk.SUNKEN, borderwidth=1)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            stats_frame,
            text=f"📈 Итоговые характеристики (с оборудованием)",
            bg=self.colors['text_bg'],
            fg=self.colors['green'],
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', padx=10, pady=(5, 0))
        
        tk.Label(
            stats_frame,
            text=f"  Атака: {self.player.attack} → {total_attack}",
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 9)
        ).pack(anchor='w', padx=15, pady=2)
        
        tk.Label(
            stats_frame,
            text=f"  Защита: {self.player.defense} → {total_defense}",
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 9)
        ).pack(anchor='w', padx=15, pady=(0, 5))
    
    def _create_events_tab(self, parent, window):
        """Вкладка вызова событий"""
        tk.Label(
            parent,
            text="Призвать событие",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Получить все события
        events = self.event_manager.list_events()
        
        # Scrollable frame
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        for event_info in events:
            frame = tk.Frame(scrollable_frame, bg=self.colors['text_bg'], relief=tk.RAISED, borderwidth=1)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(
                frame,
                text=event_info['title'],
                bg=self.colors['text_bg'],
                fg=self.colors['text_fg'],
                font=('Arial', 11, 'bold'),
                anchor='w'
            ).pack(fill=tk.X, padx=10, pady=(5,0))
            
            tk.Label(
                frame,
                text=f"{event_info['location']} | {event_info['difficulty']}",
                bg=self.colors['text_bg'],
                fg=self.colors['yellow'],
                font=('Arial', 9),
                anchor='w'
            ).pack(fill=tk.X, padx=10)
            
            def make_trigger(event_id):
                def trigger():
                    event = self.event_manager.get_event_by_id(event_id)
                    if event:
                        self.current_event = event
                        self.in_event = True
                        window.destroy()
                        self.clear_text()
                        self.show_event()
                    else:
                        messagebox.showerror("Ошибка", "Событие не найдено!")
                return trigger
            
            tk.Button(
                frame,
                text="▶ Запустить",
                command=make_trigger(event_info['id']),
                bg=self.colors['green'],
                fg='white',
                font=('Arial', 9),
                padx=10,
                pady=3
            ).pack(anchor='e', padx=10, pady=(0,5))
    
    def _create_combat_tab(self, parent, window):
        """Вкладка призыва врагов"""
        tk.Label(
            parent,
            text="Призвать врага",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Уровень врага
        level_frame = tk.Frame(parent, bg=self.colors['bg'])
        level_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            level_frame,
            text="Уровень врага:",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 11)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        level_var = tk.IntVar(value=self.player.level if self.player else 1)
        level_spinbox = tk.Spinbox(
            level_frame,
            from_=1,
            to=100,
            textvariable=level_var,
            font=('Arial', 11),
            width=10
        )
        level_spinbox.pack(side=tk.LEFT)
        
        # Ротация врага
        rotation_frame = tk.Frame(parent, bg=self.colors['bg'])
        rotation_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            rotation_frame,
            text="Ротация врага:",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 11)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        rotation_var = tk.IntVar(value=self.rotation)
        rotation_spinbox = tk.Spinbox(
            rotation_frame,
            from_=0,
            to=50,
            textvariable=rotation_var,
            font=('Arial', 11),
            width=10
        )
        rotation_spinbox.pack(side=tk.LEFT)
        
        # Кнопка призыва
        def summon_enemy():
            enemy_level = level_var.get()
            enemy_rotation = rotation_var.get()
            
            self.current_enemy = create_enemy(enemy_level, rotation=enemy_rotation)
            self.in_combat = True
            
            window.destroy()
            self.clear_text()
            
            self.print("="*50, 'yellow')
            self.print("⚔️  АДМИН: ПРИЗВАН ВРАГ!", 'yellow')
            self.print("="*50, 'yellow')
            self.print(f"Вы встретили: {self.current_enemy.name} (Уровень {self.current_enemy.level})", 'red')
            self.print(f"Здоровье врага: {self.current_enemy.hp}/{self.current_enemy.max_hp}", 'red')
            self.print(f"Атака: {self.current_enemy.attack}, Защита: {getattr(self.current_enemy, 'defense', 0)}", 'red')
            
            # Показать механики боя врага
            if hasattr(self.current_enemy, 'get_evade_chance'):
                evade_chance = self.current_enemy.get_evade_chance()
                self.print(f"🛡️ Уклонение: {evade_chance * 100:.1f}%", 'cyan')
            
            if hasattr(self.current_enemy, 'get_crit_chance'):
                crit_chance = self.current_enemy.get_crit_chance()
                self.print(f"⚡ Крит. удар: {crit_chance * 100:.1f}%", 'yellow')
            
            self.print("="*50 + "\n", 'yellow')
            
            self.show_combat_menu()
        
        tk.Button(
            parent,
            text="⚔️ Призвать врага",
            command=summon_enemy,
            bg=self.colors['red'],
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=15,
            cursor='hand2'
        ).pack(pady=30)
    
    def _create_player_tab(self, parent, window):
        """Вкладка редактирования параметров игрока"""
        tk.Label(
            parent,
            text="Редактировать параметры игрока",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # HP
        hp_frame = tk.Frame(parent, bg=self.colors['bg'])
        hp_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            hp_frame,
            text=f"HP: {self.player.hp}/{self.player.max_hp}",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 11),
            width=25,
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        def heal_full():
            self.player.hp = self.player.max_hp
            self.update_info_panel()
            window.destroy()
            self.show_admin_panel()
        
        def set_hp():
            val = simpledialog.askinteger("HP", f"Установить HP (макс: {self.player.max_hp}):", parent=window, minvalue=1, maxvalue=self.player.max_hp)
            if val is not None:
                self.player.hp = val
                self.update_info_panel()
                window.destroy()
                self.show_admin_panel()
        
        tk.Button(hp_frame, text="Полное HP", command=heal_full, bg=self.colors['green'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        tk.Button(hp_frame, text="Установить", command=set_hp, bg=self.colors['cyan'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        
        # Опыт
        exp_frame = tk.Frame(parent, bg=self.colors['bg'])
        exp_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            exp_frame,
            text=f"Опыт: {self.player.exp}/{self.player.exp_to_next_level}",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 11),
            width=25,
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        def add_exp(amount):
            self.player.exp += amount
            while self.player.exp >= self.player.exp_to_next_level:
                self.player.level_up()
            self.update_info_panel()
            window.destroy()
            self.show_admin_panel()
        
        tk.Button(exp_frame, text="+100", command=lambda: add_exp(100), bg=self.colors['green'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        tk.Button(exp_frame, text="+1000", command=lambda: add_exp(1000), bg=self.colors['cyan'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        
        # Уровень
        level_frame = tk.Frame(parent, bg=self.colors['bg'])
        level_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            level_frame,
            text=f"Уровень: {self.player.level}",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 11),
            width=25,
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        def set_level():
            val = simpledialog.askinteger("Уровень", "Установить уровень:", parent=window, minvalue=1, maxvalue=100)
            if val is not None:
                diff = val - self.player.level
                if diff > 0:
                    for _ in range(diff):
                        self.player.level_up()
                else:
                    self.player.level = val
                    self.player.exp = 0
                    self.player.exp_to_next_level = 100 * (1.5 ** (val - 1))
                self.update_info_panel()
                window.destroy()
                self.show_admin_panel()
        
        tk.Button(level_frame, text="Установить", command=set_level, bg=self.colors['cyan'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        
        # Золото
        gold_frame = tk.Frame(parent, bg=self.colors['bg'])
        gold_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            gold_frame,
            text=f"Золото: {self.player.gold}",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 11),
            width=25,
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        def add_gold(amount):
            self.player.gold += amount
            self.update_info_panel()
            window.destroy()
            self.show_admin_panel()
        
        tk.Button(gold_frame, text="+100", command=lambda: add_gold(100), bg=self.colors['green'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        tk.Button(gold_frame, text="+1000", command=lambda: add_gold(1000), bg=self.colors['cyan'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        tk.Button(gold_frame, text="+10000", command=lambda: add_gold(10000), bg=self.colors['magenta'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        
        # Ротация
        rotation_frame = tk.Frame(parent, bg=self.colors['bg'])
        rotation_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            rotation_frame,
            text=f"Ротация: {self.rotation}",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 11),
            width=25,
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        def change_rotation(delta):
            self.rotation = max(0, self.rotation + delta)
            self.update_info_panel()
            window.destroy()
            self.show_admin_panel()
        
        def set_rotation():
            val = simpledialog.askinteger("Ротация", "Установить ротацию:", parent=window, minvalue=0, maxvalue=50)
            if val is not None:
                self.rotation = val
                self.update_info_panel()
                window.destroy()
                self.show_admin_panel()
        
        tk.Button(rotation_frame, text="-1", command=lambda: change_rotation(-1), bg=self.colors['red'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        tk.Button(rotation_frame, text="+1", command=lambda: change_rotation(1), bg=self.colors['green'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        tk.Button(rotation_frame, text="Установить", command=set_rotation, bg=self.colors['cyan'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
    
    def _create_inventory_tab(self, parent, window):
        """Вкладка управления инвентарём"""
        # Верхняя часть - список предметов
        top_frame = tk.Frame(parent, bg=self.colors['bg'])
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            top_frame,
            text=f"Инвентарь ({len(self.inventory.items)}/{self.inventory.max_size})",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 5))
        
        # Список предметов с прокруткой
        list_frame = tk.Frame(top_frame, bg=self.colors['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        items_listbox = tk.Listbox(
            list_frame,
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            font=('Consolas', 9),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            height=8
        )
        items_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=items_listbox.yview)
        
        # Заполнить список
        for i, item in enumerate(self.inventory.items):
            quality_icon = QUALITY_ICONS.get(getattr(item, 'quality', None), '')
            item_level = getattr(item, 'level', 1)
            item_text = f"{i+1}. {quality_icon} {item.name} (Ур.{item_level})"
            items_listbox.insert(tk.END, item_text)
        
        # Кнопки управления предметами
        buttons_frame = tk.Frame(top_frame, bg=self.colors['bg'])
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        def delete_selected():
            sel = items_listbox.curselection()
            if sel:
                idx = sel[0]
                if messagebox.askyesno("Удаление", f"Удалить {self.inventory.items[idx].name}?", parent=window):
                    self.inventory.items.pop(idx)
                    window.destroy()
                    self.show_admin_panel()
            else:
                messagebox.showwarning("Ошибка", "Выберите предмет!", parent=window)
        
        def clear_inventory():
            if messagebox.askyesno("Очистить инвентарь", "Удалить ВСЕ предметы?", parent=window):
                self.inventory.items.clear()
                window.destroy()
                self.show_admin_panel()
        
        tk.Button(buttons_frame, text="🗑️ Удалить", command=delete_selected, bg=self.colors['red'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        tk.Button(buttons_frame, text="🧹 Очистить всё", command=clear_inventory, bg=self.colors['red'], fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        
        # Разделитель
        tk.Frame(parent, bg=self.colors['text_fg'], height=2).pack(fill=tk.X, padx=10, pady=10)
        
        # Нижняя часть - добавление предметов
        bottom_frame = tk.Frame(parent, bg=self.colors['bg'])
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(
            bottom_frame,
            text="Добавить предмет",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 12, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')
        
        # Тип предмета
        tk.Label(bottom_frame, text="Тип:", bg=self.colors['bg'], fg=self.colors['text_fg'], font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=2)
        item_type_var = tk.StringVar(value="Оружие")
        item_type_combo = ttk.Combobox(bottom_frame, textvariable=item_type_var, state='readonly', width=15)
        item_type_combo['values'] = ["Оружие", "Броня", "Зелье"]
        item_type_combo.grid(row=1, column=1, sticky='w', pady=2, padx=(5, 0))
        
        # Базовый предмет
        tk.Label(bottom_frame, text="Предмет:", bg=self.colors['bg'], fg=self.colors['text_fg'], font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=2)
        base_item_var = tk.StringVar(value="wooden_sword")
        base_item_combo = ttk.Combobox(bottom_frame, textvariable=base_item_var, state='readonly', width=15)
        base_item_combo.grid(row=2, column=1, sticky='w', pady=2, padx=(5, 0))
        
        # Обновить список предметов при смене типа
        def update_base_items(*args):
            item_type = item_type_var.get()
            if item_type == "Оружие":
                base_item_combo['values'] = ["wooden_sword", "iron_sword", "steel_sword", "legendary_sword"]
                base_item_var.set("wooden_sword")
            elif item_type == "Броня":
                base_item_combo['values'] = ["leather_armor", "iron_armor", "steel_armor", "legendary_armor"]
                base_item_var.set("leather_armor")
            else:  # Зелье
                base_item_combo['values'] = ["small_potion", "medium_potion", "large_potion"]
                base_item_var.set("small_potion")
        
        item_type_var.trace_add('write', update_base_items)
        update_base_items()
        
        # Качество
        tk.Label(bottom_frame, text="Качество:", bg=self.colors['bg'], fg=self.colors['text_fg'], font=('Arial', 10)).grid(row=3, column=0, sticky='w', pady=2)
        quality_var = tk.StringVar(value="wooden")
        quality_combo = ttk.Combobox(bottom_frame, textvariable=quality_var, state='readonly', width=15)
        quality_combo['values'] = ["wooden", "rusty", "iron", "silver", "luxury", "dragon"]
        quality_combo.grid(row=3, column=1, sticky='w', pady=2, padx=(5, 0))
        
        # Уровень
        tk.Label(bottom_frame, text="Уровень:", bg=self.colors['bg'], fg=self.colors['text_fg'], font=('Arial', 10)).grid(row=4, column=0, sticky='w', pady=2)
        level_var = tk.IntVar(value=1)
        level_spin = tk.Spinbox(bottom_frame, from_=1, to=100, textvariable=level_var, width=13)
        level_spin.grid(row=4, column=1, sticky='w', pady=2, padx=(5, 0))
        
        # Кнопка добавления
        def add_item_to_inventory():
            if len(self.inventory.items) >= self.inventory.max_size:
                messagebox.showwarning("Инвентарь полон", "Сначала удалите предметы!", parent=window)
                return
            
            base_id = base_item_var.get()
            quality = quality_var.get()
            level = level_var.get()
            
            # Создать предмет через существующую систему
            # generate_equipment уже формирует правильное название с характеристиками
            # force_quality=True позволяет создавать любые комбинации качества и базы
            item = get_item_scaled(base_id, rotation=0, player_level=level, quality=quality, item_level=level, force_quality=True)
            if item:
                self.inventory.add_item(item)
                
                # Показать детали созданного предмета
                details = f"✅ Добавлено: {item.name}"
                if hasattr(item, 'level'):
                    details += f"\n📊 Уровень: {item.level}"
                if hasattr(item, 'quality'):
                    details += f"\n💎 Качество: {QUALITY_DISPLAY.get(item.quality, item.quality)}"
                if hasattr(item, 'attack_bonus'):
                    details += f"\n⚔️ Атака: +{item.attack_bonus}"
                if hasattr(item, 'defense_bonus'):
                    details += f"\n🛡️ Защита: +{item.defense_bonus}"
                if hasattr(item, 'heal_amount'):
                    details += f"\n💊 Лечение: {item.heal_amount} HP"
                
                # Добавить информацию о требованиях
                if hasattr(item, 'requirements') and item.requirements:
                    details += f"\n\n📋 Требования:"
                    stat_labels = {
                        'attack': 'Атака',
                        'defense': 'Защита',
                        'intellect': 'Интеллект',
                        'luck': 'Удача',
                        'strength': 'Сила',
                        'dexterity': 'Ловкость',
                        'fire_resist': 'Сопротивление огню',
                        'cold_resist': 'Сопротивление холоду',
                        'max_hp': 'Макс. HP'
                    }
                    for stat, req_value in item.requirements.items():
                        player_stat = getattr(self.player, stat, 0)
                        is_met = player_stat >= req_value
                        status = "✓" if is_met else "✗"
                        stat_display = stat_labels.get(stat, stat)
                        details += f"\n  {status} {stat_display}: {req_value} (у вас: {player_stat})"
                    
                    # Показать бонус скейлинга если применимо
                    if hasattr(item, 'get_effective_bonus'):
                        base_bonus = getattr(item, 'attack_bonus', 0) or getattr(item, 'defense_bonus', 0) or 0
                        effective_bonus = item.get_effective_bonus(self.player)
                        if effective_bonus > base_bonus:
                            details += f"\n\n🎯 Бонус скейлинга: +{effective_bonus - base_bonus}"
                
                messagebox.showinfo("Успех", details, parent=window)
                window.destroy()
                self.show_admin_panel()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать предмет!", parent=window)
        
        tk.Button(
            bottom_frame,
            text="➕ Добавить предмет",
            command=add_item_to_inventory,
            bg=self.colors['green'],
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        ).grid(row=5, column=0, columnspan=2, pady=(10, 0))
    
    def _create_artifact_constructor_tab(self, parent, window):
        """Вкладка конструктора артефактов"""
        from items import Artifact
        
        tk.Label(
            parent,
            text="🎁 Конструктор артефактов",
            bg=self.colors['bg'],
            fg=self.colors['text_fg'],
            font=('Arial', 12, 'bold')
        ).pack(pady=(10, 5))
        
        tk.Label(
            parent,
            text="Создайте артефакт с произвольными слотами бонусов",
            bg=self.colors['bg'],
            fg=self.colors['yellow'],
            font=('Arial', 9)
        ).pack(pady=(0, 10))
        
        # Параметры артефакта
        params_frame = tk.Frame(parent, bg=self.colors['bg'])
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Имя артефакта
        tk.Label(params_frame, text="Имя:", bg=self.colors['bg'], fg=self.colors['text_fg']).grid(row=0, column=0, sticky='w', pady=2)
        artifact_name_var = tk.StringVar(value="Артефакт админа")
        name_entry = tk.Entry(params_frame, textvariable=artifact_name_var, width=20)
        name_entry.grid(row=0, column=1, sticky='w', padx=5)
        
        # Количество слотов
        tk.Label(params_frame, text="Слотов:", bg=self.colors['bg'], fg=self.colors['text_fg']).grid(row=1, column=0, sticky='w', pady=2)
        slots_var = tk.IntVar(value=3)
        slots_spin = tk.Spinbox(params_frame, from_=1, to=5, textvariable=slots_var, width=5)
        slots_spin.grid(row=1, column=1, sticky='w', padx=5)
        
        # Список слотов
        slots_frame = tk.LabelFrame(parent, text="Бонусы слотов", bg=self.colors['bg'], fg=self.colors['text_fg'])
        slots_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas с прокруткой
        canvas = tk.Canvas(slots_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(slots_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Хранилище для слотов
        slot_widgets = []
        
        def add_slot_row(scroll_frame, index=None):
            """Добавить строку для редактирования слота"""
            slot_frame = tk.Frame(scroll_frame, bg=self.colors['text_bg'], relief=tk.RAISED, borderwidth=1)
            slot_frame.pack(fill=tk.X, padx=5, pady=3)
            
            # Тип бонуса
            tk.Label(slot_frame, text=f"Слот {len(slot_widgets)+1}:", bg=self.colors['text_bg'], fg=self.colors['text_fg'], width=10).pack(side=tk.LEFT, padx=5, pady=3)
            
            bonus_type_var = tk.StringVar(value="stat")
            bonus_type = ttk.Combobox(slot_frame, textvariable=bonus_type_var, state='readonly', width=10)
            bonus_type['values'] = ['stat', 'crit', 'evade']
            bonus_type.pack(side=tk.LEFT, padx=2)
            
            # Подтип (для stat выбираем характеристику)
            subtype_var = tk.StringVar(value="attack")
            subtype_combo = ttk.Combobox(slot_frame, textvariable=subtype_var, state='readonly', width=12)
            subtype_combo['values'] = ['attack', 'defense', 'max_hp', 'intellect', 'luck', 'fire_resist', 'cold_resist']
            subtype_combo.pack(side=tk.LEFT, padx=2)
            
            def update_subtype(*args):
                if bonus_type_var.get() == 'stat':
                    subtype_combo.config(state='readonly')
                else:
                    subtype_combo.config(state='disabled')
            
            bonus_type_var.trace_add('write', update_subtype)
            
            # Значение
            value_var = tk.IntVar(value=10)
            value_spin = tk.Spinbox(slot_frame, from_=1, to=100, textvariable=value_var, width=5)
            value_spin.pack(side=tk.LEFT, padx=2)
            
            # Кнопка удаления
            def remove_slot():
                slot_frame.destroy()
                slot_widgets.remove(slot_data)
            
            remove_btn = tk.Button(slot_frame, text="✗", command=remove_slot, bg=self.colors['red'], fg='white', padx=3, pady=0)
            remove_btn.pack(side=tk.LEFT, padx=2)
            
            slot_data = {
                'frame': slot_frame,
                'type_var': bonus_type_var,
                'subtype_var': subtype_var,
                'value_var': value_var
            }
            slot_widgets.append(slot_data)
        
        # Добавляем начальные строки
        def refresh_slots(*args):
            # Очищаем старые слоты
            for w in slot_widgets[:]:
                w['frame'].destroy()
                slot_widgets.remove(w)
            
            # Добавляем новое количество
            for _ in range(slots_var.get()):
                add_slot_row(scrollable_frame)
        
        slots_var.trace_add('write', refresh_slots)
        refresh_slots()
        
        # Кнопка создания
        def create_artifact():
            if not slot_widgets:
                messagebox.showwarning("Ошибка", "Добавьте хотя бы один слот!", parent=window)
                return
            
            # Собираем бонусы
            bonus_slots = []
            for slot in slot_widgets:
                bonus_type = slot['type_var'].get()
                if bonus_type == 'stat':
                    bonus_slots.append({
                        'type': 'stat',
                        'stat': slot['subtype_var'].get(),
                        'value': slot['value_var'].get()
                    })
                else:
                    bonus_slots.append({
                        'type': bonus_type,
                        'value': slot['value_var'].get()
                    })
            
            # Создаём артефакт
            name = artifact_name_var.get() or "Артефакт админа"
            desc = f"Артефакт с {len(bonus_slots)} слотом(и)"
            price = 1000 + len(bonus_slots) * 500
            
            artifact = Artifact(name, desc, price, bonus_slots=bonus_slots)
            
            # Добавляем в инвентарь
            if len(self.inventory.items) >= self.inventory.max_size:
                messagebox.showwarning("Ошибка", "Инвентарь полон!", parent=window)
                return
            
            self.inventory.add_item(artifact)
            
            # Показываем результат
            details = f"✅ Создан артефакт\n\n"
            details += f"Имя: {artifact.name}\n"
            details += f"Слотов: {len(bonus_slots)}\n"
            details += f"Цена: {price}g\n\n"
            details += f"Бонусы:\n"
            for i, slot in enumerate(bonus_slots, 1):
                if slot['type'] == 'stat':
                    details += f"  [{i}] +{slot['value']} {slot['stat']}\n"
                else:
                    details += f"  [{i}] +{slot['value']}% {slot['type']}\n"
            
            messagebox.showinfo("Успех", details, parent=window)
            window.destroy()
            self.show_admin_panel()
        
        tk.Button(
            parent,
            text="🎁 Создать артефакт",
            command=create_artifact,
            bg=self.colors['green'],
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        ).pack(pady=(0, 10))
    
    def quit_game(self):
        """Выйти из игры"""
        if self.player:
            response = messagebox.askyesnocancel(
                "Выход",
                "Хотите сохранить игру перед выходом?"
            )
            if response is None:  # Отмена
                return
            elif response:  # Да
                # Autosave to reserved slot
                try:
                    ok, msg = save_system.save_game_slot(self.player, self.inventory, self.rotation, self.victories, slot=save_system.MAX_SLOTS)
                    if ok:
                        self.print(msg, 'green')
                    else:
                        self.print(msg, 'red')
                except Exception:
                    # fallback to default save
                    success, message = save_game(self.player, self.inventory, self.rotation, self.victories)
                    if success:
                        self.print(message, 'green')
                    else:
                        self.print(message, 'red')
        
        self.root.quit()


def main():
    # Apply saved settings (e.g., locale) before creating UI
    try:
        save_system.load_settings()
    except Exception:
        pass

    root = tk.Tk()
    # Ensure main root has same title
    try:
        root.title(f"{GAME_NAME} v{VERSION}")
    except Exception:
        pass
    game = RPGGame(root)
    root.mainloop()
