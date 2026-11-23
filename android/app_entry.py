"""
ePICRPG Kivy application entry (importable as bytecode on Android).

Desktop:
    python android/main.py

Buildozer:
    root main.py imports app_entry.main()
"""
import os
import sys

_ANDROID_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_ANDROID_DIR)
for path in (_ANDROID_DIR, _ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.utils import platform

from storage import init_data_dir
from game_session import GameSession
from music_player import MusicPlayer
from screens.menu import MenuScreen
from screens.character import CharacterScreen
from screens.hub import HubScreen
from screens.combat import CombatScreen
from screens.inventory import InventoryScreen
from screens.shop import ShopScreen
from screens.stats import StatsScreen


def _register_font():
    font_path = os.path.join(_ANDROID_DIR, "assets", "fonts", "DejaVuSans.ttf")
    if os.path.isfile(font_path):
        LabelBase.register(name="EpicFont", fn_regular=font_path)
        return "EpicFont"
    return None


_FONT = _register_font()
_FONT_LINE = f"    font_name: '{_FONT}'\n" if _FONT else ""

Builder.load_string(
    f"""
<Label>:
{_FONT_LINE}    color: 0.95, 0.94, 0.90, 1
<Button>:
{_FONT_LINE}    background_normal: ''
    background_color: 0.22, 0.32, 0.42, 0.88
    color: 1, 0.97, 0.92, 1
<TextInput>:
{_FONT_LINE}    background_color: 0.10, 0.12, 0.16, 0.92
    foreground_color: 0.95, 0.95, 0.95, 1
    cursor_color: 0.75, 0.55, 0.25, 1
"""
)

Window.clearcolor = (0.08, 0.10, 0.14, 1)
if platform in ("win", "linux", "macosx"):
    Window.size = (400, 720)


class EpicRPGApp(App):
    title = "ePICRPG"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = GameSession()
        self.music = MusicPlayer()

    def _on_screen(self, _sm, name):
        try:
            self.music.notify_screen(name)
        except Exception:
            pass

    def build(self):
        data_dir = None
        if platform == "android":
            data_dir = self.user_data_dir
        init_data_dir(data_dir)
        settings = self.session.load_settings() or {}
        music_on = settings.get("music_enabled", True)
        if music_on is False:
            self.music.enabled = False

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(CharacterScreen(name="character"))
        sm.add_widget(HubScreen(name="hub"))
        sm.add_widget(CombatScreen(name="combat"))
        sm.add_widget(InventoryScreen(name="inventory"))
        sm.add_widget(ShopScreen(name="shop"))
        sm.add_widget(StatsScreen(name="stats"))
        sm.bind(current=self._on_screen)
        self._on_screen(sm, sm.current or "menu")
        return sm

    def on_pause(self):
        try:
            self.music.pause()
        except Exception:
            pass
        return True

    def on_resume(self):
        try:
            if self.music.enabled:
                self.music.resume()
        except Exception:
            pass


def main():
    EpicRPGApp().run()
