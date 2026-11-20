"""Shared visual helpers for Kivy screens."""
from __future__ import annotations

import os

from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

_ANDROID_DIR = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_ANDROID_DIR, "assets")


def asset_path(*parts: str) -> str:
    return os.path.join(_ASSETS, *parts)


def themed_root(bg_name: str, content: Widget) -> FloatLayout:
    """Full-bleed background image with dim overlay and foreground content."""
    root = FloatLayout()
    path = asset_path(bg_name)
    if os.path.isfile(path):
        bg = Image(
            source=path,
            fit_mode="cover",
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        root.add_widget(bg)

    dim = Widget(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})

    def _paint(*_):
        dim.canvas.before.clear()
        with dim.canvas.before:
            Color(0.05, 0.06, 0.09, 0.55)
            Rectangle(pos=dim.pos, size=dim.size)

    dim.bind(pos=_paint, size=_paint)
    root.add_widget(dim)

    if not isinstance(content, BoxLayout):
        wrap = BoxLayout(orientation="vertical", size_hint=(1, 1))
        wrap.add_widget(content)
        content = wrap
    content.size_hint = (1, 1)
    content.pos_hint = {"x": 0, "y": 0}
    root.add_widget(content)
    return root


def panel(widget: Widget, alpha: float = 0.45) -> BoxLayout:
    """Semi-transparent panel behind a child for readable text on art."""
    box = BoxLayout(padding=10, spacing=6)
    # Keep fixed-height children from stretching the panel.
    if getattr(widget, "size_hint_y", 1) is None:
        box.size_hint_y = None
        box.height = getattr(widget, "height", 48) + 20
    with box.canvas.before:
        Color(0.08, 0.10, 0.14, alpha)
        box._bg_rect = Rectangle(pos=box.pos, size=box.size)

    def _sync(*_):
        box._bg_rect.pos = box.pos
        box._bg_rect.size = box.size

    box.bind(pos=_sync, size=_sync)
    box.add_widget(widget)
    return box
