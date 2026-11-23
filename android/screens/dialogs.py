"""Shared popups for Kivy screens."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from locales import t

# Prevent stacking multiple game-over dialogs.
_game_over_open = False


def _confirm(title, body, on_yes):
    box = BoxLayout(orientation="vertical", spacing=8, padding=8)
    lbl = Label(
        text=body,
        halign="center",
        valign="middle",
        font_size="15sp",
    )

    def _fit_label(*_):
        # Keep message inside popup; wrap long item names
        w = max(lbl.width - 16, 40)
        lbl.text_size = (w, None)
        lbl.height = max(lbl.texture_size[1] + 8, 48)
        lbl.size_hint_y = None

    lbl.bind(size=_fit_label, texture_size=_fit_label)
    box.add_widget(lbl)
    row = BoxLayout(size_hint_y=None, height="48dp", spacing=8)
    yes = Button(text=t("yes"))
    no = Button(text=t("no"))
    popup = Popup(title=title, content=box, size_hint=(0.9, 0.42))
    yes.bind(on_release=lambda *_: (popup.dismiss(), on_yes()))
    no.bind(on_release=lambda *_: popup.dismiss())
    row.add_widget(yes)
    row.add_widget(no)
    box.add_widget(row)
    popup.open()


def show_load_slots(session, manager, on_loaded=None, on_cancel=None):
    """Popup to pick a save slot; supports delete; on success go to hub."""
    box = BoxLayout(orientation="vertical", spacing=8, padding=8)
    popup = Popup(title=t("load_slot_title"), content=box, size_hint=(0.95, 0.75))
    loaded = {"ok": False}

    def rebuild():
        box.clear_widgets()
        slots = session.list_slots()
        try:
            import save_system as _save_system

            autosave_slot = _save_system.MAX_SLOTS
        except Exception:
            autosave_slot = 5
        for slot, info in slots.items():
            row = BoxLayout(size_hint_y=None, height="48dp", spacing=6)
            pname = info.get("player_name") or "?"
            plevel = info.get("level") or "?"
            if slot == autosave_slot:
                label = t("autosave_slot_label")
                if info.get("exists"):
                    label = f"{label}: {pname} Lv{plevel}"
                else:
                    label = f"{label}: —"
            elif info.get("exists"):
                label = t("slot_label_filled", slot=slot, name=pname, level=plevel)
            else:
                label = t("slot_label_empty", slot=slot)

            load_btn = Button(text=label, size_hint_x=0.65)
            if info.get("exists"):

                def make_loader(s):
                    def _load(_btn):
                        ok, msg = session.load(s)
                        if ok:
                            loaded["ok"] = True
                            popup.dismiss()
                            if on_loaded:
                                on_loaded()
                            else:
                                manager.current = "hub"
                        else:
                            err = Popup(
                                title=t("load"),
                                content=Label(text=str(msg)),
                                size_hint=(0.8, 0.3),
                            )
                            err.open()

                    return _load

                load_btn.bind(on_release=make_loader(slot))
            else:
                load_btn.disabled = True
            row.add_widget(load_btn)

            del_btn = Button(text=t("delete"), size_hint_x=0.35)
            if info.get("exists"):

                def make_deleter(s, name, level):
                    def _do_delete():
                        ok, msg = session.delete_slot(s)
                        note = Popup(
                            title=t("delete"),
                            content=Label(text=msg if ok else str(msg)),
                            size_hint=(0.8, 0.3),
                        )
                        note.open()
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

        close = Button(text=t("close"), size_hint_y=None, height="48dp")
        close.bind(on_release=lambda *_: popup.dismiss())
        box.add_widget(close)

    def _on_dismiss(*_):
        if not loaded["ok"] and on_cancel:
            on_cancel()

    popup.bind(on_dismiss=_on_dismiss)
    rebuild()
    popup.open()


def show_game_over(manager, session, body=None):
    """After death: leave combat, offer New Game or Load Save."""
    global _game_over_open
    if _game_over_open:
        return
    _game_over_open = True

    # Never leave the player stuck on the combat screen after death.
    if getattr(manager, "current", None) == "combat":
        manager.current = "hub"

    box = BoxLayout(orientation="vertical", spacing=8, padding=8)
    text = body or t("game_over_msg")
    lbl = Label(text=text, halign="left", valign="top")
    lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
    scroll = ScrollView(size_hint=(1, 0.55))
    scroll.add_widget(lbl)
    box.add_widget(scroll)

    popup = Popup(
        title=t("game_over"),
        content=box,
        size_hint=(0.92, 0.7),
        auto_dismiss=False,
    )

    def _clear_flag(*_):
        global _game_over_open
        _game_over_open = False

    popup.bind(on_dismiss=_clear_flag)

    def _new(*_):
        popup.dismiss()
        manager.current = "character"

    def _load(*_):
        popup.dismiss()

        def _reopen_if_dead():
            if session.player and not session.player.is_alive():
                show_game_over(manager, session, body)

        show_load_slots(session, manager, on_cancel=_reopen_if_dead)

    btn_new = Button(text=t("menu_new_game"), size_hint_y=None, height="48dp")
    btn_load = Button(text=t("menu_load_game"), size_hint_y=None, height="48dp")
    btn_new.bind(on_release=_new)
    btn_load.bind(on_release=_load)
    box.add_widget(btn_new)
    box.add_widget(btn_load)
    popup.open()
