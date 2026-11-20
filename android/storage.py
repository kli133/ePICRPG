"""Save/settings path helpers for the Android (Kivy) client."""
import os
import sys
from typing import Optional

# Ensure repo root is on sys.path so core modules import cleanly.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def ensure_core_path():
    """Idempotent: put game root on sys.path."""
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    return _ROOT


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
