"""Inventory screen — slots, list, detail card (mobile RPG pattern)."""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from locales import t
from screens.dialogs import _confirm
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
        self.list_scroll = ScrollView(size_hint=(1, 0.38))
        self.list_scroll.add_widget(self.list_inner)
        content.add_widget(panel(self.list_scroll, alpha=0.5))

        self.detail = BoxLayout(
            orientation="vertical", spacing=6, size_hint_y=None, height="200dp"
        )
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
            height="72dp",
            font_size="13sp",
            halign="left",
            valign="top",
        )
        self.detail_body.bind(size=self._fit_detail_body)
        self.detail_body.bind(texture_size=self._fit_detail_body)
        actions = BoxLayout(size_hint_y=None, height="48dp", spacing=8)
        self.btn_action = Button(text="", font_size="15sp")
        self.btn_action.bind(on_release=self._do_action)
        self.btn_action.disabled = True
        self.btn_sell = Button(
            text="",
            font_size="14sp",
            halign="center",
            valign="middle",
        )
        self.btn_sell.bind(
            size=lambda i, _v: setattr(i, "text_size", (i.width - 10, i.height))
        )
        self.btn_sell.bind(on_release=self._do_sell)
        self.btn_sell.disabled = True
        actions.add_widget(self.btn_action)
        actions.add_widget(self.btn_sell)
        self.detail.add_widget(self.detail_title)
        self.detail.add_widget(self.detail_body)
        self.detail.add_widget(actions)
        content.add_widget(panel(self.detail, alpha=0.55))

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

    def _fit_detail_body(self, *_):
        """Grow detail body so sell price is not clipped by action buttons."""
        lbl = self.detail_body
        if lbl.width > 40:
            lbl.text_size = (lbl.width, None)
        h = max(int(lbl.texture_size[1]) + 8, 56)
        # Cap so list still has room on small phones
        h = min(h, 120)
        lbl.height = h
        # title + body + actions + spacings
        self.detail.height = 28 + h + 48 + 18

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
            section_keys = {
                "weapon": "inv_section_weapon",
                "armor": "inv_section_armor",
                "artifact": "inv_section_artifact",
                "potion": "inv_section_potion",
                "item": "inv_section_other",
            }
            last_kind = None
            for row in rows:
                kind = row.get("kind") or "item"
                if kind != last_kind:
                    last_kind = kind
                    sec = Label(
                        text=t(section_keys.get(kind, "inv_section_other")),
                        size_hint_y=None,
                        height="28dp",
                        font_size="12sp",
                        halign="left",
                        valign="middle",
                        bold=True,
                    )
                    sec.bind(
                        size=lambda i, v: setattr(i, "text_size", (i.width, None))
                    )
                    self.list_inner.add_widget(sec)
                mark = t("equipped_mark") if row["equipped"] else ""
                stats = row.get("stats_line") or ""
                cmp = row.get("compare_mark") or ""
                text = f"{row['name']}{mark}"
                extras = "  ".join(p for p in (stats, cmp) if p)
                if extras:
                    text = f"{text}\n{extras}"
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
            self.btn_sell.text = t("sell")
            self.btn_sell.disabled = True
            self._fit_detail_body()
            return
        mark = t("equipped_mark") if row["equipped"] else ""
        stats = row.get("stats_line") or ""
        cmp = row.get("compare_mark") or ""
        price = int(row.get("sell_price") or 0)
        title = f"[{row['kind_label']}] {row['name']}{mark}"
        if cmp:
            title = f"{title}  {cmp}"
        self.detail_title.text = title
        # Keep body short: compare + stats; price lives on the Sell button
        parts = []
        if cmp and not row["equipped"]:
            parts.append(f"{t('compare_with')} {cmp}")
        if stats:
            parts.append(stats)
        desc = row.get("description") or ""
        if desc and desc != stats:
            parts.append(desc)
        if row["equipped"]:
            parts.append(t("cannot_sell_equipped"))
        self.detail_body.text = "\n".join(p for p in parts if p)
        if row["kind"] == "potion":
            self.btn_action.text = t("use")
        else:
            self.btn_action.text = t("equip")
        self.btn_action.disabled = False
        self.btn_sell.text = t("sell_btn_price", price=price)
        self.btn_sell.disabled = bool(row["equipped"])
        self._fit_detail_body()

    def _do_action(self, *_):
        if not self._selected:
            return
        session = self._session()
        idx = self._selected["index"]
        ok, msg = session.equip_or_use_item(idx)
        self.feedback.text = msg
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

    def _do_sell(self, *_):
        if not self._selected:
            return
        row = self._selected
        if row.get("equipped"):
            self.feedback.text = t("cannot_sell_equipped")
            return
        price = int(row.get("sell_price") or 0)
        idx = row["index"]

        def _yes():
            ok, msg = self._session().sell_item(idx)
            self.feedback.text = msg
            self._selected = None
            self.refresh()
            if not ok:
                self.feedback.text = str(msg)

        _confirm(
            t("sell_item_title"),
            t("sell_item_msg", name=row["name"], price=price),
            _yes,
        )

    def _back(self, *_):
        self.manager.current = "hub"
