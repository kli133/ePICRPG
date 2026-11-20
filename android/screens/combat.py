"""Combat screen — touch actions over GameSession combat API."""
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from locales import t
from screens.dialogs import show_game_over
from ui_theme import panel, themed_root


class CombatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        content = BoxLayout(orientation="vertical", padding=16, spacing=10)

        self.status = Label(
            text="",
            size_hint_y=None,
            height="64dp",
            font_size="15sp",
            halign="left",
            valign="middle",
        )
        self.status.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        content.add_widget(panel(self.status, alpha=0.6))

        self.log = Label(
            text="",
            size_hint_y=None,
            text_size=(400, None),
            halign="left",
            valign="top",
        )
        self.log_scroll = ScrollView(size_hint=(1, 0.42))
        self.log_scroll.add_widget(self.log)
        self.log.bind(texture_size=self._on_log_texture)
        self.log_scroll.bind(width=self._on_log_scroll_width)
        content.add_widget(panel(self.log_scroll, alpha=0.55))

        self.btn_attack = Button(text="", size_hint_y=None, height="52dp", font_size="18sp")
        self.btn_ability = Button(text="", size_hint_y=None, height="52dp", font_size="18sp")
        self.btn_potion = Button(text="", size_hint_y=None, height="52dp", font_size="18sp")
        self.btn_flee = Button(text="", size_hint_y=None, height="52dp", font_size="18sp")
        self.btn_attack.bind(on_release=self._attack)
        self.btn_ability.bind(on_release=self._ability)
        self.btn_potion.bind(on_release=self._potion)
        self.btn_flee.bind(on_release=self._flee)

        actions = BoxLayout(orientation="vertical", spacing=8)
        for btn in (self.btn_attack, self.btn_ability, self.btn_potion, self.btn_flee):
            actions.add_widget(btn)
        content.add_widget(actions)
        self.add_widget(themed_root("bg_combat.jpg", content))
        self._round_log = []
        self._busy = False

    def _on_log_scroll_width(self, instance, value):
        if value > 40:
            self.log.text_size = (value - 8, None)

    def _on_log_texture(self, instance, value):
        instance.height = max(value[1], 40)

    def _session(self):
        return App.get_running_app().session

    def on_pre_enter(self, *_):
        self._busy = False
        session = self._session()
        # Escape hatch: combat ended / player dead but screen still open.
        if not session.in_combat or (session.player and not session.player.is_alive()):
            Clock.schedule_once(lambda *_: self._leave_combat_screen(), 0)
            return
        self._refresh_ui()
        self._round_log = list(session.log[-8:])
        self.refresh()

    def _leave_combat_screen(self):
        session = self._session()
        if session.player and not session.player.is_alive():
            show_game_over(self.manager, session)
        else:
            self.manager.current = "hub"

    def _refresh_ui(self):
        self.btn_attack.text = t("attack_short")
        self.btn_potion.text = t("use_potion_short")
        self.btn_flee.text = t("flee")
        session = self._session()
        active = bool(session.in_combat and session.current_enemy)
        choices = session.ability_choices() if active else []
        if not choices:
            self.btn_ability.disabled = True
            self.btn_ability.text = t("no_abilities")
        else:
            aid, name, _desc, _cd, rc = choices[0]
            if rc > 0:
                self.btn_ability.disabled = True
                self.btn_ability.text = t("ability_cd_btn", name=name, cd=rc)
            else:
                self.btn_ability.disabled = False
                self.btn_ability.text = name or t("ability_short")
        self.btn_attack.disabled = not active
        self.btn_potion.disabled = not active
        # Flee doubles as "leave" when combat already ended.
        self.btn_flee.disabled = False
        if not active:
            self.btn_flee.text = t("continue")

    def refresh(self):
        session = self._session()
        self.status.text = session.status_line()
        self.log.text = "\n".join(self._round_log) if self._round_log else ""
        self._refresh_ui()
        Clock.schedule_once(lambda *_: setattr(self.log_scroll, "scroll_y", 0), 0)

    def _append(self, text):
        if text:
            self._round_log.append(text)
        self.refresh()

    def _outcome_title(self, outcome):
        return {
            "victory": t("outcome_victory"),
            "defeat": t("outcome_defeat"),
            "fled": t("outcome_fled"),
        }.get(outcome, t("ok"))

    def _show_outcome(self, outcome, body):
        if outcome == "defeat":
            summary = body or ""
            msg = f"{summary}\n\n{t('game_over_msg')}" if summary else t("game_over_msg")
            # Leave combat immediately so buttons cannot spam "not in combat".
            self.manager.current = "hub"
            show_game_over(self.manager, self._session(), msg)
            return

        box = BoxLayout(orientation="vertical", spacing=8, padding=8)
        lbl = Label(text=body or "", halign="left", valign="top")
        lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(lbl)
        box.add_widget(scroll)
        btn = Button(text=t("continue"), size_hint_y=None, height="48dp")
        popup = Popup(
            title=self._outcome_title(outcome),
            content=box,
            size_hint=(0.92, 0.7),
            auto_dismiss=False,
        )

        def _go(*_):
            popup.dismiss()
            self.manager.current = "hub"

        btn.bind(on_release=_go)
        box.add_widget(btn)
        popup.open()

    def _finish_if_needed(self, outcome):
        if outcome in ("victory", "defeat", "fled"):
            body = self._session().last_outcome_summary or "\n".join(self._round_log[-8:])
            self._show_outcome(outcome, body)

    def _run_action(self, fn):
        if self._busy:
            return
        session = self._session()
        if not session.in_combat or (session.player and not session.player.is_alive()):
            self._leave_combat_screen()
            return
        self._busy = True
        try:
            text, outcome = fn()
            self._append(text)
            self._finish_if_needed(outcome)
        finally:
            self._busy = False

    def _attack(self, *_):
        self._run_action(self._session().combat_attack)

    def _ability(self, *_):
        self._run_action(self._session().combat_ability)

    def _potion(self, *_):
        self._run_action(self._session().combat_potion)

    def _flee(self, *_):
        session = self._session()
        if not session.in_combat or (session.player and not session.player.is_alive()):
            self._leave_combat_screen()
            return
        self._run_action(session.combat_flee)
