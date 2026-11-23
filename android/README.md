# ePICRPG — Android (Kivy + Buildozer)

Мобильный клиент ePICRPG. Общая логика игры — в [`../core/`](../core/) (`player`, `combat`, `items`, …).  
Desktop Tkinter: [`../desktop/gui_main.py`](../desktop/gui_main.py).

## Status

| | |
|---|---|
| Release APK (игра) | `bin/ePICRPG-2.2.9b-arm64.apk` — подписанный release |
| Debug APK | `bin/epicrpg-2.2.9-arm64-v8a-debug.apk` |
| Release asset | `ePICRPG-2.2.9b-arm64.apk` на [Releases](https://github.com/kli133/ePICRPG/releases) |
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
| `wsl_release.sh` | Sync + подписанный release APK |

## Run on Windows (UI debug)

```bash
pip install -r android/requirements-android.txt
python android/main.py
```

Сейвы: `android/.data/`.

## Build APK (WSL)

Не собирайте с `/mnt/c` напрямую. Хелпер копирует проект в `~/epicrpg`:

```bash
# Debug (разработка)
wsl -d Ubuntu -- bash /mnt/c/Users/user/Desktop/rpg/android/wsl_build.sh

# Release (подписанный APK «как игра»)
wsl -d Ubuntu -- bash /mnt/c/Users/user/Desktop/rpg/android/wsl_release.sh
```

APK появляется в `android/bin/*.apk`. Release-ключ хранится только в WSL (`~/epicrpg-release-keys/`), в git не попадает.

### Install

```bash
adb install -r android/bin/ePICRPG-2.2.9b-arm64.apk
```

Нужен **arm64**. Для release APK USB debugging не обязателен — можно просто открыть файл на телефоне.

## Notes

- На устройстве сейвы в `App.user_data_dir`
- Ориентация: portrait
- После правок кода — снова `wsl_build.sh` / `wsl_release.sh`
