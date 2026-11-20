# ePICRPG — Android (Kivy + Buildozer)

Мобильный клиент ePICRPG. Общая логика игры — в [`../core/`](../core/) (`player`, `combat`, `items`, …).  
Desktop Tkinter: [`../desktop/gui_main.py`](../desktop/gui_main.py).

## Status

| | |
|---|---|
| APK (локальная сборка) | `bin/epicrpg-2.2.9-arm64-v8a-debug.apk` |
| Release asset | `ePICRPG-2.2.9b-arm64-v8a-debug.apk` на [Releases](https://github.com/kli133/ePICRPG/releases) |
| Package | `org.epicrpg.epicrpg` |
| Arch | `arm64-v8a` |
| Toolchain | WSL Ubuntu + Buildozer |

### Playable

Меню → персонаж → хаб → **Исследовать** (бой или событие) → бой (атака / способность / зелье / бегство) → инвентарь, магазин, характеристики (трата очков) → сохранение / удаление слотов → поражение: новая игра или загрузка.

Ещё не на мобильном: темы оформления, админ-панель, полный паритет desktop UI.

## Layout

| Path | Role |
|------|------|
| `../main.py` | Вход Buildozer |
| `main.py` / `app_entry.py` | Kivy app |
| `game_session.py` | Фасад над `core/` |
| `storage.py` | `sys.path` → `core/` + data dir |
| `screens/` | menu, character, hub, combat, inventory, shop, stats |
| `assets/` | icon, splash, фоны, иконки классов |
| `buildozer.spec` | `source.dir = ..`, включает `core/*` |
| `wsl_build.sh` | Sync на ext4 + debug APK |

## Run on Windows (UI debug)

```bash
pip install -r android/requirements-android.txt
python android/main.py
```

Сейвы: `android/.data/`.

## Build APK (WSL)

Не собирайте с `/mnt/c` напрямую. Хелпер копирует проект в `~/epicrpg`:

```bash
wsl -d Ubuntu -- bash /mnt/c/Users/user/Desktop/rpg/android/wsl_build.sh
```

APK появляется в `android/bin/*.apk`.

### Install

```bash
adb install -r android/bin/epicrpg-2.2.9-arm64-v8a-debug.apk
```

Нужен **arm64** и USB debugging.

## Notes

- На устройстве сейвы в `App.user_data_dir`
- Ориентация: portrait
- После правок кода — снова `wsl_build.sh`
