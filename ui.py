"""Небольшая обертка для цветного вывода в консоль.
Пытается использовать colorama на Windows, но корректно отходит к ANSI-последовательностям.
"""
try:
    import colorama  # type: ignore[import-not-found]
    colorama.init()
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

COLORS = {
    'reset': '\u001b[0m',
    'red': '\u001b[31m',
    'green': '\u001b[32m',
    'yellow': '\u001b[33m',
    'blue': '\u001b[34m',
    'magenta': '\u001b[35m',
    'cyan': '\u001b[36m',
    'white': '\u001b[37m',
}


def color_text(text, color_name):
    code = COLORS.get(color_name, '')
    if not code:
        return text
    return f"{code}{text}{COLORS['reset']}"


def cprint(text, color=None, end='\n'):
    try:
        if color:
            print(color_text(text, color), end=end)
        else:
            print(text, end=end)
    except Exception:
        print(text, end=end)


def progress_bar(current, maximum, width=30, color='green'):
    """Вернуть строку прогресс-бара с цветом.

    current / maximum rendered as block characters.
    """
    try:
        pct = max(0, min(1.0, float(current) / float(maximum))) if maximum > 0 else 0
    except Exception:
        pct = 0
    filled = int(round(width * pct))
    empty = width - filled
    bar = '█' * filled + '·' * empty
    return color_text(bar, color)


# Simple Tkinter tooltip helper for GUI widgets
try:
    import tkinter as _tk
except Exception:
    _tk = None


class Tooltip:
    """Attach to a widget to show a small tooltip on hover.

    Usage:
        tip = Tooltip(widget, text='Hello')
        tip.show() / tip.hide() are available but normally automatic.
    """
    def __init__(self, widget, text='', delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._id = None
        self._tw = None
        if _tk is not None:
            widget.bind('<Enter>', self._on_enter)
            widget.bind('<Leave>', self._on_leave)
            widget.bind('<ButtonPress>', self._on_leave)

    def _on_enter(self, event=None):
        self._schedule()

    def _on_leave(self, event=None):
        self._unschedule()
        self._hide()

    def _schedule(self):
        self._unschedule()
        try:
            self._id = self.widget.after(self.delay, self._show)
        except Exception:
            self._id = None

    def _unschedule(self):
        if self._id:
            try:
                self.widget.after_cancel(self._id)
            except Exception:
                pass
            self._id = None

    def _show(self):
        if not _tk:
            return
        if self._tw:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self._tw = _tk.Toplevel(self.widget)
        self._tw.wm_overrideredirect(True)
        try:
            self._tw.wm_attributes('-topmost', True)
        except Exception:
            pass
        label = _tk.Label(self._tw, text=self.text, justify=_tk.LEFT,
                          background='#ffffe0', relief=_tk.SOLID, borderwidth=1,
                          font=('Arial', 9))
        label.pack(ipadx=4, ipady=2)
        self._tw.wm_geometry(f'+{x}+{y}')

    def _hide(self):
        if self._tw:
            try:
                self._tw.destroy()
            except Exception:
                pass
            self._tw = None

    def show(self):
        self._show()

    def hide(self):
        self._hide()
