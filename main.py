"""
Buildozer / Android entry point.

On device only .pyc ships — must import modules, not run_path(.py).

Desktop Tkinter:  python desktop/gui_main.py
Desktop Kivy:     python android/main.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ANDROID = os.path.join(_HERE, "android")
_CORE = os.path.join(_HERE, "core")

# Put mobile client modules first (storage, screens, app_entry, game_session).
# Do NOT "import android" as a package — that name is reserved by pyjnius on device.
for _p in (_ANDROID, _CORE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app_entry import main  # noqa: E402

if __name__ == "__main__":
    main()
