"""Character stats screen — mobile RPG character sheet with draft +/-."""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from locales import t
from player import Player
from ui_theme import panel, themed_root

_STAT_OPTIONS = (
    ("hp", "stat_option_hp"),
    ("attack", "stat_option_attack"),
    ("defense", "stat_option_defense"),
    ("agility", "stat_option_agility"),
    ("luck", "stat_option_luck"),
    ("intellect", "stat_option_intellect"),
    ("fire_resist", "stat_option_fire_resist"),
    ("cold_resist", "stat_option_cold_resist"),
)


class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._draft = {sid: 0 for sid, _ in _STAT_OPTIONS}
        self._row_value_labels = {}

        content = BoxLayout(orientation="vertical", padding=12, spacing=8)

        self.header = Label(
            text="",
            size_hint_y=None,
            height="48dp",
            font_size="15sp",
            halign="left",
            valign="middle",
        )
        self.header.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        content.add_widget(panel(self.header, alpha=0.55))

        self.derived = Label(
            text="",
            size_hint_y=None,
            height="36dp",
            font_size="13sp",
            halign="left",
            valign="middle",
        )
        self.derived.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        content.add_widget(panel(self.derived, alpha=0.5))

        self.points_label = Label(
            text="",
            size_hint_y=None,
            height="36dp",
            font_size="14sp",
            halign="left",
            valign="middle",
        )
        self.points_label.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        content.add_widget(panel(self.points_label, alpha=0.5))

        self.options_inner = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        self.options_inner.bind(minimum_height=self.options_inner.setter("height"))
        options_scroll = ScrollView(size_hint=(1, 0.42))
        options_scroll.add_widget(self.options_inner)
        content.add_widget(panel(options_scroll, alpha=0.5))

        self.feedback = Label(
            text="",
            size_hint_y=None,
            height="32dp",
            font_size="13sp",
            halign="left",
            valign="middle",
        )
        self.feedback.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        content.add_widget(panel(self.feedback, alpha=0.45))

        footer = BoxLayout(size_hint_y=None, height="48dp", spacing=8)
        self.btn_reset = Button(text="")
        self.btn_reset.bind(on_release=self._reset_draft)
        self.btn_confirm = Button(text="")
        self.btn_confirm.bind(on_release=self._confirm)
        footer.add_widget(self.btn_reset)
        footer.add_widget(self.btn_confirm)
        content.add_widget(footer)

        self.btn_back = Button(text="", size_hint_y=None, height="48dp")
        self.btn_back.bind(on_release=self._back)
        content.add_widget(self.btn_back)

        self.add_widget(themed_root("bg_hub.jpg", content))

    def _session(self):
        return App.get_running_app().session

    def on_pre_enter(self, *_):
        self.feedback.text = ""
        self._reset_draft()
        self.refresh()

    def _draft_used(self) -> int:
        return sum(self._draft.values())

    def _points_left(self) -> int:
        detail = self._session().stats_detail()
        total = int(detail.get("stat_points", 0) or 0)
        return max(0, total - self._draft_used())

    def refresh(self):
        session = self._session()
        self.btn_back.text = t("back")
        self.btn_reset.text = t("stat_reset")
        self.btn_confirm.text = t("stat_confirm")
        detail = session.stats_detail()
        if not detail:
            self.header.text = t("no_character")
            self.derived.text = ""
            self.points_label.text = ""
            self.options_inner.clear_widgets()
            self.btn_confirm.disabled = True
            return

        self.header.text = f"{detail['name']}  ·  {detail['cls']}  ·  Lv{detail['level']}"
        base = session.base_stat_values()
        luck = int(base.get("luck", 0)) + int(self._draft.get("luck", 0))
        intellect = int(base.get("intellect", 0)) + int(self._draft.get("intellect", 0))
        agility = int(base.get("agility", 0)) + int(self._draft.get("agility", 0))
        # Include artifact luck/agility in preview via live totals delta
        try:
            art_luck = session.player.get_total_luck() - getattr(session.player, "luck", 0)
        except Exception:
            art_luck = 0
        try:
            art_agi = session.player.get_total_agility() - getattr(session.player, "agility", 0)
        except Exception:
            art_agi = 0
        preview = Player.stat_effect_preview(
            luck + art_luck, intellect, agility + art_agi
        )
        self.derived.text = t(
            "stat_derived",
            evade=preview["evade_pct"],
            crit=preview["crit_pct"],
            xp=preview["xp_bonus_pct"],
        )
        used = self._draft_used()
        left = self._points_left()
        self.points_label.text = t("stat_points_draft", left=left, used=used)
        self.btn_confirm.disabled = used <= 0
        self.btn_reset.disabled = used <= 0

        self.options_inner.clear_widgets()
        self._row_value_labels = {}
        for stat_id, loc_key in _STAT_OPTIONS:
            row = BoxLayout(size_hint_y=None, height="52dp", spacing=6)
            info = BoxLayout(orientation="vertical", size_hint_x=0.55)
            name_lbl = Label(
                text=t(loc_key),
                font_size="13sp",
                halign="left",
                valign="middle",
            )
            name_lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
            info.add_widget(name_lbl)
            row.add_widget(info)

            val_lbl = Label(
                text="",
                size_hint_x=0.25,
                font_size="14sp",
                halign="center",
                valign="middle",
            )
            val_lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
            self._row_value_labels[stat_id] = val_lbl
            row.add_widget(val_lbl)

            minus = Button(text="−", size_hint_x=0.1, font_size="18sp")
            plus = Button(text="+", size_hint_x=0.1, font_size="18sp")
            minus.bind(on_release=self._make_delta(stat_id, -1))
            plus.bind(on_release=self._make_delta(stat_id, +1))
            row.add_widget(minus)
            row.add_widget(plus)
            self.options_inner.add_widget(row)

        self._refresh_row_values()

    def _refresh_row_values(self):
        base = self._session().base_stat_values()
        for stat_id, lbl in self._row_value_labels.items():
            b = int(base.get(stat_id, 0))
            d = int(self._draft.get(stat_id, 0))
            if d > 0:
                lbl.text = t("stat_value_draft", base=b, delta=d)
            else:
                lbl.text = str(b)

    def _make_delta(self, stat_id, step):
        def _act(*_):
            if step > 0:
                if self._points_left() <= 0:
                    self.feedback.text = t("no_stat_points")
                    return
                self._draft[stat_id] = self._draft.get(stat_id, 0) + 1
            else:
                if self._draft.get(stat_id, 0) <= 0:
                    return
                self._draft[stat_id] -= 1
            self.feedback.text = ""
            # Light refresh of counters without rebuilding rows
            used = self._draft_used()
            left = self._points_left()
            self.points_label.text = t("stat_points_draft", left=left, used=used)
            self.btn_confirm.disabled = used <= 0
            self.btn_reset.disabled = used <= 0
            base = self._session().base_stat_values()
            luck = int(base.get("luck", 0)) + int(self._draft.get("luck", 0))
            intellect = int(base.get("intellect", 0)) + int(self._draft.get("intellect", 0))
            agility = int(base.get("agility", 0)) + int(self._draft.get("agility", 0))
            try:
                art_luck = self._session().player.get_total_luck() - getattr(
                    self._session().player, "luck", 0
                )
            except Exception:
                art_luck = 0
            try:
                art_agi = self._session().player.get_total_agility() - getattr(
                    self._session().player, "agility", 0
                )
            except Exception:
                art_agi = 0
            preview = Player.stat_effect_preview(
                luck + art_luck, intellect, agility + art_agi
            )
            self.derived.text = t(
                "stat_derived",
                evade=preview["evade_pct"],
                crit=preview["crit_pct"],
                xp=preview["xp_bonus_pct"],
            )
            self._refresh_row_values()

        return _act

    def _reset_draft(self, *_):
        self._draft = {sid: 0 for sid, _ in _STAT_OPTIONS}
        self.feedback.text = ""
        if self._session().player:
            self.refresh()

    def _confirm(self, *_):
        deltas = {k: v for k, v in self._draft.items() if v > 0}
        if not deltas:
            return
        ok, msg = self._session().spend_stat_batch(deltas)
        self.feedback.text = msg
        self._draft = {sid: 0 for sid, _ in _STAT_OPTIONS}
        self.refresh()
        if not ok:
            self.feedback.text = str(msg)

    def _back(self, *_):
        self._draft = {sid: 0 for sid, _ in _STAT_OPTIONS}
        self.manager.current = "hub"
