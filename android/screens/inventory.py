"""Inventory screen — slots, list, detail card (mobile RPG pattern)."""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from locales import t
from ui_theme import panel, themed_root


class InventoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected = None
        self._row_buttons = []

        content = BoxLayout(orientation="vertical", padding=12, spacing=8)

        self.header = Label(
            text="",
            size_hint_y=None,
            height="40dp",
            font_size="15sp",
            halign="left",
            valign="middle",
        )
        self.header.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        content.add_widget(panel(self.header, alpha=0.55))

        self.slots = Label(
            text="",
            size_hint_y=None,
            height="72dp",
            font_size="13sp",
            halign="left",
            valign="middle",
        )
        self.slots.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        content.add_widget(panel(self.slots, alpha=0.5))

        self.list_inner = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        self.list_inner.bind(minimum_height=self.list_inner.setter("height"))
        self.list_scroll = ScrollView(size_hint=(1, 0.42))
        self.list_scroll.add_widget(self.list_inner)
        content.add_widget(panel(self.list_scroll, alpha=0.5))

        detail = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, height="150dp")
        self.detail_title = Label(
            text="",
            size_hint_y=None,
            height="28dp",
            font_size="15sp",
            halign="left",
            valign="middle",
        )
        self.detail_title.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        self.detail_body = Label(
            text="",
            size_hint_y=None,
            height="56dp",
            font_size="13sp",
            halign="left",
            valign="top",
        )
        self.detail_body.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        self.btn_action = Button(text="", size_hint_y=None, height="48dp", font_size="16sp")
        self.btn_action.bind(on_release=self._do_action)
        self.btn_action.disabled = True
        detail.add_widget(self.detail_title)
        detail.add_widget(self.detail_body)
        detail.add_widget(self.btn_action)
        content.add_widget(panel(detail, alpha=0.55))

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
        self._selected = None
        self.feedback.text = ""
        self.refresh()

    def refresh(self):
        session = self._session()
        rows = session.list_inventory()
        max_size = getattr(session.inventory, "max_size", 20)
        gold = session.player.gold if session.player else 0
        self.header.text = (
            f"{t('inventory_title', count=len(rows), max=max_size)}  |  "
            f"{t('shop_gold', gold=gold)}"
        )
        self.btn_back.text = t("back")

        slots = session.equipment_slots()
        self.slots.text = (
            f"{t('equip_slot_weapon')}: {slots['weapon']}\n"
            f"{t('equip_slot_armor')}: {slots['armor']}\n"
            f"{t('equip_slot_artifact')}: {slots['artifact']}"
        )

        self.list_inner.clear_widgets()
        self._row_buttons = []
        if not rows:
            empty = Label(
                text=t("inventory_empty_msg"),
                size_hint_y=None,
                height="48dp",
                halign="left",
            )
            empty.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
            self.list_inner.add_widget(empty)
        else:
            for row in rows:
                mark = t("equipped_mark") if row["equipped"] else ""
                stats = row.get("stats_line") or ""
                text = f"[{row['kind_label']}] {row['name']}{mark}"
                if stats:
                    text = f"{text}\n{stats}"
                btn = Button(
                    text=text,
                    size_hint_y=None,
                    height="56dp",
                    font_size="13sp",
                    halign="left",
                    valign="middle",
                )
                btn.bind(size=lambda i, v: setattr(i, "text_size", (i.width - 16, None)))
                btn.bind(on_release=self._make_select(row))
                self.list_inner.add_widget(btn)
                self._row_buttons.append((btn, row["index"]))

        # Keep selection if still valid
        if self._selected is not None:
            still = next((r for r in rows if r["index"] == self._selected["index"]), None)
            if still:
                self._selected = still
            else:
                self._selected = rows[0] if rows else None
        self._update_detail()

    def _make_select(self, row):
        def _sel(*_):
            self._selected = row
            self._update_detail()

        return _sel

    def _update_detail(self):
        row = self._selected
        if not row:
            self.detail_title.text = ""
            self.detail_body.text = t("inventory_empty_msg") if not self._row_buttons else ""
            self.btn_action.text = t("equip")
            self.btn_action.disabled = True
            return
        mark = t("equipped_mark") if row["equipped"] else ""
        stats = row.get("stats_line") or ""
        self.detail_title.text = f"[{row['kind_label']}] {row['name']}{mark}"
        parts = [stats, row.get("description") or ""]
        self.detail_body.text = "\n".join(p for p in parts if p)
        if row["kind"] == "potion":
            self.btn_action.text = t("use")
        else:
            self.btn_action.text = t("equip")
        self.btn_action.disabled = False

    def _do_action(self, *_):
        if not self._selected:
            return
        session = self._session()
        idx = self._selected["index"]
        ok, msg = session.equip_or_use_item(idx)
        self.feedback.text = msg
        # Prefer selecting same kind/name after refresh if indices shift
        name = self._selected["name"]
        self.refresh()
        rows = session.list_inventory()
        match = next((r for r in rows if r["name"] == name), None)
        if match:
            self._selected = match
        elif rows:
            self._selected = rows[min(idx, len(rows) - 1)]
        else:
            self._selected = None
        self._update_detail()
        if not ok:
            self.feedback.text = str(msg)

    def _back(self, *_):
        self.manager.current = "hub"
