"""Shop screen — list with stats, grey unaffordable, buy in-place."""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from locales import t
from ui_theme import panel, themed_root


class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected = None
        self._rows = []

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

        self.list_inner = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        self.list_inner.bind(minimum_height=self.list_inner.setter("height"))
        self.list_scroll = ScrollView(size_hint=(1, 0.48))
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
        self.btn_buy = Button(text="", size_hint_y=None, height="48dp", font_size="16sp")
        self.btn_buy.bind(on_release=self._do_buy)
        self.btn_buy.disabled = True
        detail.add_widget(self.detail_title)
        detail.add_widget(self.detail_body)
        detail.add_widget(self.btn_buy)
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
        self._rows = session.list_shop()
        gold = session.player.gold if session.player else 0
        inv_count = len(session.inventory.items) if session.inventory else 0
        max_size = getattr(session.inventory, "max_size", 20)
        full = inv_count >= max_size
        self.header.text = (
            f"{t('shop')}  |  {t('shop_gold', gold=gold)}  |  "
            f"{t('inventory_title', count=inv_count, max=max_size)}"
        )
        self.btn_back.text = t("back")
        self.btn_buy.text = t("shop_buy")

        self.list_inner.clear_widgets()
        for i, row in enumerate(self._rows):
            affordable = row.get("affordable", True) and not full
            stats = row.get("stats_line") or ""
            text = f"[{row['kind_label']}] {row['name']} — {row['price']}"
            if stats:
                text = f"{text}\n{stats}"
            btn = Button(
                text=text,
                size_hint_y=None,
                height="56dp",
                font_size="13sp",
                halign="left",
                valign="middle",
                opacity=1.0 if affordable else 0.45,
            )
            btn.bind(size=lambda inst, v: setattr(inst, "text_size", (inst.width - 16, None)))
            btn.bind(on_release=self._make_select(i))
            self.list_inner.add_widget(btn)

        if self._selected is not None:
            sid = self._selected.get("id")
            match = next((r for r in self._rows if r["id"] == sid), None)
            self._selected = match if match else (self._rows[0] if self._rows else None)
        self._update_detail(full)

    def _make_select(self, index):
        def _sel(*_):
            if 0 <= index < len(self._rows):
                self._selected = self._rows[index]
                session = self._session()
                inv_count = len(session.inventory.items) if session.inventory else 0
                max_size = getattr(session.inventory, "max_size", 20)
                self._update_detail(inv_count >= max_size)

        return _sel

    def _update_detail(self, inventory_full=False):
        row = self._selected
        if not row:
            self.detail_title.text = ""
            self.detail_body.text = ""
            self.btn_buy.disabled = True
            return
        self.detail_title.text = f"[{row['kind_label']}] {row['name']}"
        parts = [
            row.get("stats_line") or "",
            row.get("description") or "",
            t("shop_price", name=row["name"], price=row["price"]),
        ]
        self.detail_body.text = "\n".join(p for p in parts if p)
        can_buy = bool(row.get("affordable", False)) and not inventory_full
        self.btn_buy.disabled = not can_buy

    def _do_buy(self, *_):
        if not self._selected:
            return
        session = self._session()
        # Resolve index by id in current shop list
        idx = next(
            (i for i, r in enumerate(self._rows) if r["id"] == self._selected["id"]),
            -1,
        )
        if idx < 0:
            return
        ok, msg = session.buy_shop_item(idx)
        self.feedback.text = msg
        keep_id = self._selected["id"]
        self.refresh()
        match = next((r for r in self._rows if r["id"] == keep_id), None)
        self._selected = match if match else (self._rows[0] if self._rows else None)
        inv_count = len(session.inventory.items) if session.inventory else 0
        max_size = getattr(session.inventory, "max_size", 20)
        self._update_detail(inv_count >= max_size)
        if not ok:
            self.feedback.text = str(msg)

    def _back(self, *_):
        self.manager.current = "hub"
