"""Character creation screen."""
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

from locales import t
from ui_theme import asset_path, panel, themed_root

_ROW_H = 64
_CLASS_COUNT = 4


class CharacterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_class = "warrior"

        content = BoxLayout(orientation="vertical", padding=16, spacing=8)

        self.heading = Label(
            text="",
            font_size="24sp",
            size_hint_y=None,
            height="36dp",
        )
        content.add_widget(self.heading)

        self.name_input = TextInput(
            hint_text="",
            multiline=False,
            size_hint_y=None,
            height="48dp",
            font_size="18sp",
        )
        content.add_widget(self.name_input)

        self.class_label = Label(
            text="", size_hint_y=None, height="26dp", font_size="16sp"
        )
        content.add_widget(self.class_label)

        # All classes visible — no ScrollView (only 4 classes).
        list_h = _CLASS_COUNT * _ROW_H + (_CLASS_COUNT - 1) * 6
        self.class_box = BoxLayout(
            orientation="vertical",
            spacing=6,
            size_hint_y=None,
            height=f"{list_h}dp",
        )
        content.add_widget(self.class_box)

        self.desc = Label(
            text="",
            size_hint_y=None,
            height="72dp",
            text_size=(None, None),
            halign="left",
            valign="top",
        )
        self.desc.bind(texture_size=self._on_desc_texture)
        self.desc.bind(width=self._on_desc_width)
        desc_wrap = BoxLayout(size_hint_y=None, height="96dp")
        desc_scroll = ScrollView(size_hint=(1, 1))
        desc_scroll.add_widget(self.desc)
        desc_wrap.add_widget(desc_scroll)
        content.add_widget(panel(desc_wrap, alpha=0.5))

        actions = BoxLayout(size_hint_y=None, height="56dp", spacing=8)
        self.btn_back = Button(text="")
        self.btn_back.bind(on_release=lambda *_: setattr(self.manager, "current", "menu"))
        self.btn_start = Button(text="")
        self.btn_start.bind(on_release=self._start)
        actions.add_widget(self.btn_back)
        actions.add_widget(self.btn_start)
        content.add_widget(actions)

        self.add_widget(themed_root("bg_menu.jpg", content))

    def _on_desc_width(self, instance, value):
        instance.text_size = (max(value - 4, 100), None)

    def _on_desc_texture(self, instance, value):
        instance.height = max(value[1], 40)

    def on_pre_enter(self, *_):
        self._refresh_ui()
        self._rebuild_classes()

    def _refresh_ui(self):
        self.heading.text = t("new_character")
        self.name_input.hint_text = t("name_hint")
        self.class_label.text = t("class_label")
        self.btn_back.text = t("back")
        self.btn_start.text = t("start")

    def _session(self):
        return App.get_running_app().session

    def _rebuild_classes(self):
        self.class_box.clear_widgets()
        self._class_buttons = []
        for cid, name, description in self._session().list_classes():
            row = BoxLayout(size_hint_y=None, height=f"{_ROW_H}dp", spacing=8)
            icon = asset_path(f"class_{cid}.png")
            if os.path.isfile(icon):
                row.add_widget(
                    Image(
                        source=icon,
                        size_hint_x=None,
                        width=f"{_ROW_H}dp",
                        fit_mode="cover",
                    )
                )
            btn = Button(text=name, font_size="16sp")

            def make_select(c=cid, d=description, n=name, button=btn):
                def _sel(_btn):
                    self.selected_class = c
                    self.desc.text = f"{n}: {d}"
                    for b in self._class_buttons:
                        b.background_color = (0.22, 0.32, 0.42, 0.88)
                    button.background_color = (0.45, 0.38, 0.22, 1)

                return _sel

            btn.bind(on_release=make_select())
            self._class_buttons.append(btn)
            row.add_widget(btn)
            self.class_box.add_widget(row)

        classes = self._session().list_classes()
        for cid, name, description in classes:
            if cid == self.selected_class:
                self.desc.text = f"{name}: {description}"
                break
        for b, (cid, _n, _d) in zip(self._class_buttons, classes):
            if cid == self.selected_class:
                b.background_color = (0.45, 0.38, 0.22, 1)

    def _start(self, *_):
        from kivy.uix.popup import Popup

        ok, msg = self._session().new_game(self.name_input.text, self.selected_class)
        if ok:
            self.manager.current = "hub"
        else:
            Popup(
                title=t("error"),
                content=Label(text=msg or t("new_game_failed")),
                size_hint=(0.8, 0.3),
            ).open()
