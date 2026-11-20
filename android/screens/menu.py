"""Main menu screen."""
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from locales import t, get_locale
from screens.dialogs import show_load_slots
from ui_theme import asset_path, themed_root


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        content = BoxLayout(orientation="vertical", padding=24, spacing=14)

        logo = asset_path("logo_menu.png")
        if os.path.isfile(logo):
            content.add_widget(
                Image(
                    source=logo,
                    size_hint_y=None,
                    height="140dp",
                    fit_mode="contain",
                )
            )

        self.title = Label(
            text="ePICRPG",
            font_size="34sp",
            size_hint_y=None,
            height="48dp",
            bold=True,
        )
        content.add_widget(self.title)
        content.add_widget(Label(size_hint_y=0.15))  # spacer

        self.btn_new = self._btn("", self._new_game)
        self.btn_load = self._btn("", self._load_game)
        self.btn_lang = self._btn("", self._toggle_lang)
        self.btn_quit = self._btn("", self._quit)
        for b in (self.btn_new, self.btn_load, self.btn_lang, self.btn_quit):
            content.add_widget(b)

        self.add_widget(themed_root("bg_menu.jpg", content))
        self._refresh_ui()

    def on_pre_enter(self, *_):
        self._refresh_ui()

    def _refresh_ui(self):
        lang = get_locale().upper()
        self.title.text = f"ePICRPG [{lang}]"
        self.btn_new.text = t("menu_new_game")
        self.btn_load.text = t("menu_load_game")
        self.btn_lang.text = t("menu_language", lang=lang)
        self.btn_quit.text = t("menu_quit")

    def _btn(self, text, handler):
        b = Button(
            text=text,
            size_hint_y=None,
            height="56dp",
            font_size="18sp",
        )
        b.bind(on_release=handler)
        return b

    def _session(self):
        return App.get_running_app().session

    def _new_game(self, *_):
        self.manager.current = "character"

    def _load_game(self, *_):
        show_load_slots(self._session(), self.manager)

    def _toggle_lang(self, *_):
        session = self._session()
        nxt = "en" if get_locale() == "ru" else "ru"
        session.set_language(nxt)
        self._refresh_ui()

    def _quit(self, *_):
        App.get_running_app().stop()
