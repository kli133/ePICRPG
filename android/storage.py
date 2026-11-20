"""Save/settings path helpers for the Android (Kivy) client."""
import os
import sys
from typing import Optional

# Repo root and shared game logic (core/).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CORE = os.path.join(_ROOT, "core")


def ensure_core_path():
    """Idempotent: put core/ (then repo root) on sys.path for flat imports."""
    for path in (_CORE, _ROOT):
        if path not in sys.path:
            sys.path.insert(0, path)
    return _CORE


def init_data_dir(path: Optional[str] = None) -> str:
    """
    Point save_system at a writable directory.

    On Android pass App.user_data_dir. On desktop, default to
    <repo>/android/.data so mobile saves stay separate from desktop slots.
    """
    ensure_core_path()
    import save_system

    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".data")
    save_system.set_data_dir(path)
    return save_system.get_data_dir()
