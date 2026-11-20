# ePICRPG — Android (Kivy + Buildozer)

Mobile client for ePICRPG. Game logic stays in the repo root (`player`, `combat`, `items`, …).  
Desktop Tkinter (`gui_main.py`) is unchanged.

## Status (first debug APK)

| | |
|---|---|
| APK | [`bin/epicrpg-2.2.9-arm64-v8a-debug.apk`](bin/epicrpg-2.2.9-arm64-v8a-debug.apk) (~21 MB) |
| Package | `org.epicrpg.epicrpg` |
| Arch | `arm64-v8a` |
| Built | WSL Ubuntu + Buildozer 1.6.0 |

Playable MVP: New Game → Fight → Attack / Ability / Potion / Flee → Inventory equip/use → Save/Load.

Not ported yet: full shop, events UI, admin panel, multi-theme desktop parity.

## Layout

| Path | Role |
|------|------|
| `main.py` | Kivy app entry |
| `game_session.py` | Facade over core game modules |
| `storage.py` | Points `save_system` at a writable data dir |
| `screens/` | Menu, character, hub, combat |
| `assets/` | Icon / presplash placeholders |
| `buildozer.spec` | APK build config (`source.dir = ..`) |
| `wsl_build.sh` | Sync to `~/epicrpg` + build via venv |
| `../main.py` | Buildozer entry (loads `android/main.py` via `runpy`) |

## Run on Windows (UI debug)

```bash
pip install -r android/requirements-android.txt
python android/main.py
```

Saves go to `android/.data/`.

Smoke flow:

1. **New Game** → class → **Start**
2. **Fight** → **Attack**
3. **Inventory** → tap item to equip/use
4. **Save** → slot

## Build APK (WSL)

Do **not** build from `/mnt/c` directly (slow / fragile). Use the helper (copies to `~/epicrpg` on ext4):

```bash
wsl -d Ubuntu -- bash /mnt/c/Users/user/Desktop/rpg/android/wsl_build.sh
```

One-time toolchain (already done on this machine): JDK 17, `python3-venv`, Buildozer in `~/epicrpg-build-venv`.

If WSL cannot reach the network (VPN), set DNS + mirrored networking:

- `~/.wslconfig` → `networkingMode=mirrored`
- `/etc/resolv.conf` → `8.8.8.8` / `1.1.1.1` with `generateResolvConf = false` in `/etc/wsl.conf`
- then `wsl --shutdown`

APK is copied to `android/bin/*.apk`.

### Install on a phone

```bash
adb install -r android/bin/epicrpg-2.2.9-arm64-v8a-debug.apk
```

Enable USB debugging. Arm64 device required for this debug build.

## Notes

- On device, saves use `App.user_data_dir`
- Orientation: portrait
- Rebuild after code changes with the same `wsl_build.sh`

## Next porting steps

1. Port shop + events screens
2. Replace placeholder icon/splash
3. Add `armeabi-v7a` if needed
4. `buildozer android release` + signing for Play Store
