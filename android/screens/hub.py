"""Hub / main adventure screen."""
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from locales import t
from screens.dialogs import _confirm, show_game_over
from ui_theme import panel, themed_root


class HubScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        content = BoxLayout(orientation="vertical", padding=16, spacing=10)

        self.status = Label(
            text="",
            size_hint_y=None,
            height="72dp",
            font_size="15sp",
            halign="left",
            valign="middle",
        )
        self.status.bind(size=self._sync_text_size)
        content.add_widget(panel(self.status, alpha=0.55))

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
        content.add_widget(panel(self.log_scroll, alpha=0.5))

        adventure_row = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height="58dp",
        )
        self.btn_adventure = self._btn("", self._adventure)
        self.btn_adventure.size_hint_y = 1
        self.btn_adventure.height = "58dp"
        self.btn_adventure.font_size = "17sp"
        self.btn_rest = self._btn("", self._rest)
        self.btn_rest.size_hint_y = 1
        self.btn_rest.height = "58dp"
        self.btn_rest.font_size = "13sp"
        self.btn_rest.halign = "center"
        self.btn_rest.valign = "middle"
        self.btn_rest.bind(
            size=lambda i, _v: setattr(i, "text_size", (i.width - 12, i.height))
        )
        adventure_row.add_widget(self.btn_adventure)
        adventure_row.add_widget(self.btn_rest)
        content.add_widget(adventure_row)

        self.btn_inventory = self._btn("", self._inventory)
        self.btn_stats = self._btn("", self._stats)
        self.btn_shop = self._btn("", self._shop)
        self.btn_save = self._btn("", self._save)
        self.btn_prestige = self._btn("", self._prestige)
        self.btn_menu = self._btn("", self._menu)

        actions = BoxLayout(orientation="vertical", spacing=8, size_hint=(1, 0.38))
        grid = GridLayout(cols=2, spacing=8, size_hint_y=1)
        for b in (
            self.btn_inventory,
            self.btn_stats,
            self.btn_shop,
            self.btn_save,
            self.btn_prestige,
            self.btn_menu,
        ):
            b.size_hint_y = 1
            b.height = "52dp"
            grid.add_widget(b)
        actions.add_widget(grid)
        content.add_widget(actions)
        self.add_widget(themed_root("bg_hub.jpg", content))

    def _sync_text_size(self, instance, value):
        instance.text_size = (instance.width, None)

    def _on_log_scroll_width(self, instance, value):
        if value > 40:
            self.log.text_size = (value - 8, None)

    def _on_log_texture(self, instance, value):
        instance.height = max(value[1], 40)

    def _btn(self, text, handler):
        b = Button(text=text, size_hint_y=None, height="48dp", font_size="15sp")
        b.bind(on_release=handler)
        return b

    def _session(self):
        return App.get_running_app().session

    def on_pre_enter(self, *_):
        self._refresh_ui()
        self.refresh()
        session = self._session()
        if session.player and not session.player.is_alive():
            Clock.schedule_once(
                lambda *_: show_game_over(self.manager, session),
                0,
            )

    def _refresh_ui(self):
        self.btn_adventure.text = t("explore")
        self.btn_inventory.text = t("inventory")
        session = self._session()
        cost = session.rest_cost()
        self.btn_rest.text = t("rest_btn", cost=cost)
        pts = 0
        if session.player:
            pts = int(getattr(session.player, "stat_points", 0) or 0)
        self.btn_stats.text = f"{t('stats')} ({pts})" if pts > 0 else t("stats")
        self.btn_shop.text = t("shop")
        self.btn_save.text = t("save")
        self.btn_prestige.text = t("prestige")
        self.btn_menu.text = t("menu")
        dead = bool(session.player and not session.player.is_alive())
        full_hp = bool(
            session.player
            and session.player.is_alive()
            and session.player.hp >= session.player.max_hp
        )
        self.btn_adventure.disabled = dead
        self.btn_rest.disabled = dead or full_hp or not session.player
        self.btn_save.disabled = dead or not session.player
        self.btn_prestige.disabled = not session.can_prestige()

    def refresh(self):
        session = self._session()
        self.status.text = session.status_line()
        self.log.text = "\n".join(session.log[-12:]) if session.log else t("ready")
        self._refresh_ui()
        Clock.schedule_once(lambda *_: setattr(self.log_scroll, "scroll_y", 0), 0)

    def _info_popup(self, title, body):
        content = BoxLayout(orientation="vertical", padding=8, spacing=8)
        lbl = Label(text=body, halign="left", valign="top")
        lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        scroll = ScrollView()
        scroll.add_widget(lbl)
        content.add_widget(scroll)
        close = Button(text=t("ok"), size_hint_y=None, height="48dp")
        popup = Popup(title=title, content=content, size_hint=(0.92, 0.7))
        close.bind(on_release=lambda *_: popup.dismiss())
        content.add_widget(close)
        popup.open()

    def _adventure(self, *_):
        session = self._session()
        kind, payload = session.start_adventure()
        self.refresh()
        if kind == "combat":
            self.manager.current = "combat"
        elif kind == "event":
            self._show_event(payload)
        else:
            self._info_popup(t("explore"), str(payload))

    def _rest(self, *_):
        session = self._session()
        if not session.player:
            return
        if session.player.hp >= session.player.max_hp:
            self._info_popup(t("rest_title"), t("rest_full"))
            return
        cost = session.rest_cost()

        def _do():
            ok, msg = session.rest()
            self.refresh()
            self._info_popup(t("rest_title"), msg if ok else str(msg))

        _confirm(t("rest_title"), t("rest_msg", cost=cost), _do)

    def _show_event(self, payload):
        session = self._session()
        box = BoxLayout(orientation="vertical", spacing=6, padding=8)
        desc = Label(text=payload.get("description", ""), halign="left", valign="top")
        desc.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        scroll = ScrollView(size_hint=(1, 0.45))
        scroll.add_widget(desc)
        box.add_widget(scroll)
        popup = Popup(
            title=payload.get("title", t("explore")),
            content=box,
            size_hint=(0.95, 0.85),
        )

        def make_choice(idx):
            def _act(_btn):
                _ok, msg = session.resolve_explore_choice(idx)
                popup.dismiss()
                self.refresh()
                self._info_popup(t("explore"), msg)

            return _act

        for ch in payload.get("choices", []):
            btn = Button(text=ch["text"], size_hint_y=None, height="48dp")
            btn.bind(on_release=make_choice(ch["index"]))
            box.add_widget(btn)

        if payload.get("can_ignore", True):
            ign = Button(text=t("event_ignore"), size_hint_y=None, height="48dp")

            def _ign(*_):
                session.dismiss_explore()
                popup.dismiss()
                self.refresh()

            ign.bind(on_release=_ign)
            box.add_widget(ign)
        popup.open()

    def _inventory(self, *_):
        self.manager.current = "inventory"

    def _stats(self, *_):
        self.manager.current = "stats"

    def _shop(self, *_):
        self.manager.current = "shop"

    def _save(self, *_):
        session = self._session()
        box = BoxLayout(orientation="vertical", spacing=8, padding=8)
        popup = Popup(title=t("save_slot_title"), content=box, size_hint=(0.95, 0.75))

        def rebuild():
            box.clear_widgets()
            slots_now = session.list_slots()
            import save_system as _save_system

            for slot in range(1, 6):
                info = slots_now.get(slot, {})
                row = BoxLayout(size_hint_y=None, height="48dp", spacing=6)
                is_autosave = slot == _save_system.MAX_SLOTS
                pname = info.get("player_name") or "?"
                plevel = info.get("level") or "?"
                if is_autosave:
                    label = t("autosave_slot_label")
                    if info.get("exists"):
                        label = f"{label}: {pname} Lv{plevel}"
                elif info.get("exists"):
                    label = t("slot_label_filled", slot=slot, name=pname, level=plevel)
                else:
                    label = t("slot_label_empty", slot=slot)
                save_btn = Button(text=label, size_hint_x=0.65)

                def make_saver(s):
                    def _save(_btn):
                        ok, msg = session.save(s)
                        popup.dismiss()
                        self.refresh()
                        self._info_popup(t("save"), msg if ok else str(msg))

                    return _save

                # Reserved autosave slot — system-only writes
                if is_autosave:
                    save_btn.disabled = True
                else:
                    save_btn.bind(on_release=make_saver(slot))
                row.add_widget(save_btn)

                del_btn = Button(text=t("delete"), size_hint_x=0.35)
                if is_autosave:
                    del_btn.disabled = True
                elif info.get("exists"):

                    def make_deleter(s, name, level):
                        def _do_delete():
                            ok, msg = session.delete_slot(s)
                            self._info_popup(t("delete"), msg if ok else str(msg))
                            rebuild()

                        def _ask(*_):
                            _confirm(
                                t("delete"),
                                t("slot_label_filled", slot=s, name=name, level=level),
                                _do_delete,
                            )

                        return _ask

                    del_btn.bind(on_release=make_deleter(slot, pname, plevel))
                else:
                    del_btn.disabled = True
                row.add_widget(del_btn)
                box.add_widget(row)

            close = Button(text=t("cancel"), size_hint_y=None, height="48dp")
            close.bind(on_release=lambda *_: popup.dismiss())
            box.add_widget(close)

        rebuild()
        popup.open()

    def _prestige(self, *_):
        session = self._session()
        if not session.can_prestige():
            self._info_popup(
                t("prestige"),
                t("prestige_locked", level=session.prestige_requirement()),
            )
            return

        def _do():
            ok, msg = session.do_prestige()
            self.refresh()
            self._info_popup(t("prestige"), msg)

        _confirm(t("prestige"), t("prestige_confirm"), _do)

    def _menu(self, *_):
        self.manager.current = "menu"
