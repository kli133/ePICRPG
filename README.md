<div align="center">

# ePICRPG

**Fantasy RPG on Python — desktop (Tkinter) and Android (Kivy)**

Классы и навыки, пошаговые бои, лут и артефакты, события с выбором,
магазин, прокачка характеристик, престиж и ротации. RU / EN.

![Version](https://img.shields.io/badge/version-2.2.9b-blueviolet)
![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white)
![Desktop](https://img.shields.io/badge/Desktop-Tkinter-orange)
![Android](https://img.shields.io/badge/Android-Kivy%20APK-3DDC84?logo=android&logoColor=white)
![Language](https://img.shields.io/badge/lang-RU%20%7C%20EN-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

</div>

---

## Содержание

- [Возможности](#возможности)
- [Быстрый старт](#быстрый-старт)
- [Игровые механики](#игровые-механики)
- [Сборка](#сборка)
- [Структура проекта](#структура-проекта)
- [Тесты](#тесты)
- [Документация](#документация)
- [Лицензия](#лицензия)

## Возможности

| | |
|---|---|
| **4 класса** | Воин, Маг, Разбойник, Удачливый — бонусы и активные способности |
| **Пошаговые бои** | Криты, уклонения, оглушения, стихии, навыки врагов |
| **Снаряжение** | Оружие и броня с качеством, требованиями и скейлингом |
| **Артефакты** | Случайные бонус-слоты (ротация + удача) |
| **События** | Встречи с выбором и проверками характеристик |
| **Исследование** | На Android: одна кнопка — бой или случайное событие |
| **Магазин и инвентарь** | Экипировка, зелья, покупки; экраны на мобильном |
| **Прокачка** | Очки характеристик после повышения уровня |
| **Престиж и ротации** | Метапрогресс и растущая сложность |
| **Сохранения** | До 5 слотов (+ удаление слотов на Android) |
| **Локализация** | Русский и английский |
| **Desktop-only** | Темы оформления и админ-панель (Tkinter) |

## Быстрый старт

### Готовые сборки

Скачайте из [Releases](https://github.com/kli133/ePICRPG/releases):

| Файл | Платформа |
|------|-----------|
| `ePICRPG.exe` | Windows (Python не нужен) |
| `ePICRPG-2.2.9b-arm64-v8a-debug.apk` | Android **arm64** (USB debugging / установка APK) |

### Desktop из исходников

Python 3.8+ с Tkinter:

```bash
git clone https://github.com/kli133/ePICRPG.git
cd ePICRPG
python desktop/gui_main.py
```

На Linux: `sudo apt install python3-tk` при необходимости.  
`requirements.txt` нужен в основном для сборки EXE (PyInstaller).

### Android (Kivy)

```bash
pip install -r android/requirements-android.txt
python android/main.py
```

Сборка APK (WSL + Buildozer): см. [android/README.md](android/README.md).

## Игровые механики

<details>
<summary><b>Классы персонажей</b></summary>

| Класс | Бонусы | Способность | Перезарядка |
|---|---|---|---|
| **Воин** | +30 HP, +5 атака, +3 защита, +5 к сопротивлениям | **Удар ярости**: частично игнорирует защиту врага | 3 хода |
| **Маг** | +10 HP, +8 атака, −1 защита, +2 интеллект | **Молния**: сильный урон и оглушение на 1 ход | 4 хода |
| **Разбойник** | +15 HP, +4 атака, +3 защита | **Уклонение**: избегает следующей атаки | 3 хода |
| **Удачливый** | +5 удача | Повышенный шанс лута и золота | — |

</details>

<details>
<summary><b>Боевая система</b></summary>

- **Крит** — повышенный урон, шанс от удачи
- **Уклонение** — полный промах атаки
- **Стихийный урон** — огонь и холод, снижаются сопротивлениями
- **Навыки врагов** — дыхание, удар щитом, похищение жизни
- **Звери** не используют магию

Сила врагов растёт с ротацией.

</details>

<details>
<summary><b>Снаряжение и артефакты</b></summary>

Качество предметов растёт от деревянного до драконьего. Бонусы зависят от требований класса и уровня предмета.  
Артефакты получают 1–5 случайных слотов бонусов. Подробнее: [docs/EQUIPMENT_BALANCE.md](docs/EQUIPMENT_BALANCE.md), [docs/ARTIFACT_SLOTS_SYSTEM.md](docs/ARTIFACT_SLOTS_SYSTEM.md).

</details>

<details>
<summary><b>Престиж и ротации</b></summary>

**Престиж** (с 50 уровня, затем +15 за шаг): сброс забега с постоянными бонусами к HP/атаке/защите, очкам характеристик, опыту, золоту и луту.  
**Ротация** усиливает врагов и награды, расширяет ассортимент магазина.

</details>

<details>
<summary><b>События</b></summary>

При исследовании возможны встречи с проверками характеристик и разными исходами.  
Как добавить событие: [docs/EVENTS_GUIDE.md](docs/EVENTS_GUIDE.md).

</details>

## Сборка

### Windows EXE

```bash
pip install -r requirements.txt
python desktop/build_exe.py
```

Результат: `dist/ePICRPG.exe`. Подробнее: [docs/BUILD_EXE.md](docs/BUILD_EXE.md).

### Android APK

```bash
wsl -d Ubuntu -- bash /mnt/c/Users/user/Desktop/rpg/android/wsl_build.sh
```

(пути подставьте свои; детали в [android/README.md](android/README.md).)

## Структура проекта

```
ePICRPG/
├── main.py            # Вход Buildozer / Android
├── version.py         # Название и версия
├── core/              # Общая игровая логика
├── desktop/           # Tkinter GUI + сборка EXE
├── android/           # Kivy-клиент и Buildozer
├── tests/
└── docs/
```

## Тесты

```bash
python -m tests.test_upgrade
python -m tests.test_artifact_slots
python -m tests.test_scaling_system
```

На Windows при `UnicodeEncodeError`: `PYTHONIOENCODING=utf-8`.

## Документация

| Документ | Описание |
|---|---|
| [android/README.md](android/README.md) | Мобильный клиент и сборка APK |
| [ADMIN_MODE.md](docs/ADMIN_MODE.md) | Админ-режим (desktop) |
| [EVENTS_GUIDE.md](docs/EVENTS_GUIDE.md) | Создание событий |
| [EQUIPMENT_BALANCE.md](docs/EQUIPMENT_BALANCE.md) | Снаряжение и баланс |
| [ARTIFACT_SLOTS_SYSTEM.md](docs/ARTIFACT_SLOTS_SYSTEM.md) | Артефакты |
| [BUILD_EXE.md](docs/BUILD_EXE.md) | Сборка EXE |
| [VERSIONING.md](docs/VERSIONING.md) | Версии |

## Лицензия

[MIT](LICENSE).
