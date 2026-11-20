"""Character stats screen with point allocation."""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from locales import t
from ui_theme import panel, themed_root

_STAT_OPTIONS = (
    ("hp", "stat_option_hp"),
    ("attack", "stat_option_attack"),
    ("defense", "stat_option_defense"),
    ("fire_resist", "stat_option_fire_resist"),
    ("cold_resist", "stat_option_cold_resist"),
    ("luck", "stat_option_luck"),
    ("intellect", "stat_option_intellect"),
)


class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        content = BoxLayout(orientation="vertical", padding=12, spacing=8)

        self.summary = Label(
            text="",
            size_hint_y=None,
            font_size="14sp",
            halign="left",
            valign="top",
        )
        self.summary.bind(
            texture_size=lambda i, v: setattr(i, "height", max(v[1], 40)),
            size=lambda i, v: setattr(i, "text_size", (i.width, None)),
        )
        summary_scroll = ScrollView(size_hint=(1, 0.42))
        summary_scroll.add_widget(self.summary)
        content.add_widget(panel(summary_scroll, alpha=0.55))

        self.points_label = Label(
            text="",
            size_hint_y=None,
            height="36dp",
            font_size="15sp",
            halign="left",
            valign="middle",
        )
        self.points_label.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        content.add_widget(panel(self.points_label, alpha=0.5))

        self.options_inner = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        self.options_inner.bind(minimum_height=self.options_inner.setter("height"))
        options_scroll = ScrollView(size_hint=(1, 0.38))
        options_scroll.add_widget(self.options_inner)
        content.add_widget(panel(options_scroll, alpha=0.5))

        self.feedback = Label(
            text="",
            size_hint_y=None,
            height="36dp",
            font_size="13sp",
            halign="left",
            valign="middle",
        )
        self.feedback.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        content.add_widget(panel(self.feedback, alpha=0.45))

        self.btn_back = Button(text="", size_hint_y=None, height="48dp")
        self.btn_back.bind(on_release=self._back)
        content.add_widget(self.btn_back)

        self.add_widget(themed_root("bg_hub.jpg", content))

    def _session(self):
        return App.get_running_app().session

    def on_pre_enter(self, *_):
        self.feedback.text = ""
        self.refresh()

    def refresh(self):
        session = self._session()
        self.btn_back.text = t("back")
        detail = session.stats_detail()
        if not detail:
            self.summary.text = t("no_character")
            self.points_label.text = ""
            self.options_inner.clear_widgets()
            return

        self.summary.text = session.stats_summary()
        pts = detail.get("stat_points", 0)
        self.points_label.text = t("stat_points_available", pts=pts)

        self.options_inner.clear_widgets()
        if pts <= 0:
            empty = Label(
                text=t("no_stat_points"),
                size_hint_y=None,
                height="48dp",
                halign="left",
            )
            empty.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
            self.options_inner.add_widget(empty)
            return

        for stat_id, loc_key in _STAT_OPTIONS:
            btn = Button(
                text=t(loc_key),
                size_hint_y=None,
                height="48dp",
                font_size="14sp",
            )
            btn.bind(on_release=self._make_spend(stat_id))
            self.options_inner.add_widget(btn)

    def _make_spend(self, stat_id):
        def _act(*_):
            ok, msg = self._session().spend_stat(stat_id)
            self.feedback.text = msg
            self.refresh()
            if not ok:
                self.feedback.text = str(msg)

        return _act

    def _back(self, *_):
        self.manager.current = "hub"
