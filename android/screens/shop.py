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
        self.refresh(rebuild_stock=True)

    def refresh(self, rebuild_stock: bool = False):
        session = self._session()
        self._rows = session.list_shop(refresh=rebuild_stock)
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
            cmp = row.get("compare_mark") or ""
            prefix = f"{t('shop_upgrade_offer')} " if row.get("featured") else ""
            text = f"{prefix}[{row['kind_label']}] {row['name']} — {row['price']}"
            extras = "  ".join(p for p in (stats, cmp) if p)
            if extras:
                text = f"{text}\n{extras}"
            # Dim worse gear more so junk is obvious
            opacity = 1.0 if affordable else 0.45
            if cmp.startswith("▼") and affordable and not row.get("featured"):
                opacity = min(opacity, 0.65)
            btn = Button(
                text=text,
                size_hint_y=None,
                height="56dp",
                font_size="13sp",
                halign="left",
                valign="middle",
                opacity=opacity,
            )
            btn.bind(size=lambda inst, v: setattr(inst, "text_size", (inst.width - 16, None)))
            btn.bind(on_release=self._make_select(i))
            self.list_inner.add_widget(btn)

        if self._selected is not None:
            sel_item = self._selected.get("item")
            match = next(
                (r for r in self._rows if r.get("item") is sel_item),
                None,
            )
            if match is None:
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
        cmp = row.get("compare_mark") or ""
        featured = t("shop_upgrade_offer") if row.get("featured") else ""
        title = f"[{row['kind_label']}] {row['name']}"
        if featured:
            title = f"{featured} {title}"
        if cmp:
            title = f"{title}  {cmp}"
        self.detail_title.text = title
        parts = []
        if featured:
            parts.append(featured)
        if cmp:
            parts.append(f"{t('compare_with')} {cmp}")
        parts.extend(
            [
                row.get("stats_line") or "",
                row.get("description") or "",
                t("shop_price", name=row["name"], price=row["price"]),
            ]
        )
        self.detail_body.text = "\n".join(p for p in parts if p)
        can_buy = bool(row.get("affordable", False)) and not inventory_full
        self.btn_buy.disabled = not can_buy

    def _do_buy(self, *_):
        if not self._selected:
            return
        session = self._session()
        # Prefer row identity so featured duplicate ids cannot mis-buy
        idx = next(
            (i for i, r in enumerate(self._rows) if r is self._selected),
            -1,
        )
        if idx < 0:
            sel_item = self._selected.get("item")
            idx = next(
                (i for i, r in enumerate(self._rows) if r.get("item") is sel_item),
                -1,
            )
        if idx < 0:
            return
        ok, msg = session.buy_shop_item(idx)
        self.feedback.text = msg
        # Stock already rebuilt inside buy_shop_item
        self.refresh(rebuild_stock=False)
        self._selected = next(
            (r for r in self._rows if r.get("featured")),
            self._rows[0] if self._rows else None,
        )
        inv_count = len(session.inventory.items) if session.inventory else 0
        max_size = getattr(session.inventory, "max_size", 20)
        self._update_detail(inv_count >= max_size)
        if not ok:
            self.feedback.text = str(msg)

    def _back(self, *_):
        self.manager.current = "hub"
