"""Background music with crossfade; delayed combat; hub rotation; mute.

Optimized for Android UI: deferred load/play, prefetch, small cache, light fade.
"""
from __future__ import annotations

import os
import random
from typing import Optional

from kivy.clock import Clock
from kivy.core.audio import SoundLoader


_ANDROID_DIR = os.path.dirname(os.path.abspath(__file__))
_MUSIC_DIR = os.path.join(_ANDROID_DIR, "assets", "music")

HUB_TRACKS = (
    "tavern_inn.mp3",
    "tavern_2.ogg",
    "dungeon.ogg",
    "cave.ogg",
    "dark_cavern.ogg",
    "forest.ogg",
    "prepare.ogg",
)
BATTLE_TRACK = "battle.mp3"

DEFAULT_VOLUME = 0.35
CROSSFADE_SEC = 1.2
COMBAT_DELAY_SEC = 12.0
HUB_ROTATE_SEC = 90.0
PREFETCH_DELAY_SEC = 0.5
_TICK = 0.1  # 10 Hz — lighter than 30 Hz for UI
CACHE_MAX = 3

_ROTATE_SCREENS = frozenset({"menu"})
_HUB_SCREENS = frozenset(
    {"menu", "character", "hub", "inventory", "shop", "stats"}
)


class MusicPlayer:
    def __init__(self, music_dir: Optional[str] = None, volume: float = DEFAULT_VOLUME):
        self.music_dir = music_dir or _MUSIC_DIR
        self.target_volume = float(volume)
        self.enabled = True
        self._active = None
        self._fading = None
        self._fade_ev = None
        self._combat_ev = None
        self._rotate_ev = None
        self._prefetch_ev = None
        self._crossfade_ev = None
        self._paused = False  # app lifecycle pause
        self._cache = {}  # filename -> Sound
        self._cache_order = []  # LRU filenames
        self._hub_track: Optional[str] = None
        self._hub_queue: list = []  # remaining tracks this cycle (no repeats)
        self._playing_battle = False
        self._screen: Optional[str] = None
        self._started = False
        self._pending_crossfade: Optional[str] = None

    def _path(self, filename: str) -> str:
        return os.path.join(self.music_dir, filename)

    def _unload_sound(self, filename: str) -> None:
        sound = self._cache.get(filename)
        if sound is None:
            return
        if sound is self._active or sound is self._fading:
            return
        self._cache.pop(filename, None)
        if filename in self._cache_order:
            self._cache_order.remove(filename)
        try:
            sound.stop()
        except Exception:
            pass
        try:
            if hasattr(sound, "unload"):
                sound.unload()
        except Exception:
            pass

    def _touch_cache(self, filename: str) -> None:
        if filename in self._cache_order:
            self._cache_order.remove(filename)
        self._cache_order.append(filename)

    def _trim_cache(self, keep: Optional[set] = None) -> None:
        keep = set(keep or ())
        if self._hub_track:
            keep.add(self._hub_track)
        if self._pending_crossfade:
            keep.add(self._pending_crossfade)
        keep.add(BATTLE_TRACK)
        # Map active/fading sounds back to filenames
        for name, snd in list(self._cache.items()):
            if snd is self._active or snd is self._fading:
                keep.add(name)
        while len(self._cache) > CACHE_MAX:
            victims = [n for n in self._cache_order if n not in keep]
            if not victims:
                break
            self._unload_sound(victims[0])

    def _load_file(self, filename: str):
        if filename in self._cache:
            self._touch_cache(filename)
            return self._cache[filename]
        path = self._path(filename)
        if not os.path.isfile(path):
            return None
        try:
            sound = SoundLoader.load(path)
        except Exception:
            return None
        if sound is None:
            return None
        sound.loop = True
        self._cache[filename] = sound
        self._touch_cache(filename)
        self._trim_cache(keep={filename})
        return sound

    def _prefetch(self, filename: Optional[str]) -> None:
        if not filename or not self.enabled or self._paused:
            return
        if filename in self._cache:
            self._touch_cache(filename)
            return
        self._load_file(filename)

    def _cancel_fade(self):
        if self._fade_ev is not None:
            Clock.unschedule(self._fade_ev)
            self._fade_ev = None

    def _cancel_combat_delay(self):
        if self._combat_ev is not None:
            Clock.unschedule(self._combat_ev)
            self._combat_ev = None

    def _cancel_rotate(self):
        if self._rotate_ev is not None:
            Clock.unschedule(self._rotate_ev)
            self._rotate_ev = None

    def _cancel_prefetch(self):
        if self._prefetch_ev is not None:
            Clock.unschedule(self._prefetch_ev)
            self._prefetch_ev = None

    def _cancel_pending_crossfade(self):
        if self._crossfade_ev is not None:
            Clock.unschedule(self._crossfade_ev)
            self._crossfade_ev = None
        self._pending_crossfade = None

    def _schedule_rotate(self):
        self._cancel_rotate()
        if not self.enabled or self._paused or self._playing_battle:
            return
        self._rotate_ev = Clock.schedule_once(self._on_rotate_tick, HUB_ROTATE_SEC)

    def _schedule_prefetch(self):
        self._cancel_prefetch()
        if not self.enabled or self._paused or self._playing_battle:
            return
        nxt = self._peek_next_hub()
        if not nxt:
            return

        def _do(_dt):
            self._prefetch_ev = None
            self._prefetch(nxt)

        self._prefetch_ev = Clock.schedule_once(_do, PREFETCH_DELAY_SEC)

    def _on_rotate_tick(self, *_args):
        self._rotate_ev = None
        if not self.enabled or self._paused or self._playing_battle:
            return
        if self._screen == "combat":
            return
        self._ensure_hub(rotate=True)

    def _available_hub_tracks(self) -> list:
        return [t for t in HUB_TRACKS if os.path.isfile(self._path(t))]

    def _refill_hub_queue(self, avoid: Optional[str] = None) -> None:
        """Shuffle full pool; avoid starting with the track that just finished."""
        pool = self._available_hub_tracks()
        if not pool:
            self._hub_queue = []
            return
        random.shuffle(pool)
        if avoid and len(pool) > 1 and pool[0] == avoid:
            for i in range(1, len(pool)):
                if pool[i] != avoid:
                    pool[0], pool[i] = pool[i], pool[0]
                    break
        self._hub_queue = pool

    def _peek_next_hub(self) -> Optional[str]:
        if not self._hub_queue:
            # Preview refill without mutating permanent queue yet
            pool = self._available_hub_tracks()
            if not pool:
                return None
            random.shuffle(pool)
            avoid = self._hub_track
            if avoid and len(pool) > 1 and pool[0] == avoid:
                for i in range(1, len(pool)):
                    if pool[i] != avoid:
                        pool[0], pool[i] = pool[i], pool[0]
                        break
            return pool[0] if pool else None
        return self._hub_queue[0]

    def _pick_hub_track(self, exclude: Optional[str] = None) -> Optional[str]:
        """Next track from a no-repeat shuffle bag (full pool before any repeat)."""
        if not self._hub_queue:
            self._refill_hub_queue(avoid=exclude or self._hub_track)
        while (
            self._hub_queue
            and exclude
            and self._hub_queue[0] == exclude
            and len(self._hub_queue) > 1
        ):
            self._hub_queue.append(self._hub_queue.pop(0))
        if not self._hub_queue:
            return None
        return self._hub_queue.pop(0)

    def _crossfade_to(self, filename: str) -> None:
        """Queue load/play on next frame so screen transitions stay smooth."""
        if not self.enabled:
            return
        self._cancel_pending_crossfade()
        self._pending_crossfade = filename

        def _run(_dt):
            self._crossfade_ev = None
            target = self._pending_crossfade
            self._pending_crossfade = None
            if not target or not self.enabled or self._paused:
                return
            self._do_crossfade(target)

        self._crossfade_ev = Clock.schedule_once(_run, 0)

    def _do_crossfade(self, filename: str) -> None:
        new_sound = self._load_file(filename)
        if new_sound is None:
            return

        self._cancel_fade()

        if self._fading is not None and self._fading is not self._active:
            try:
                self._fading.stop()
            except Exception:
                pass
            self._fading = None

        old = self._active
        if old is None or old is new_sound:
            try:
                new_sound.volume = self.target_volume
                if getattr(new_sound, "state", None) != "play":
                    new_sound.play()
            except Exception:
                return
            self._active = new_sound
            self._trim_cache()
            if not self._playing_battle:
                self._schedule_prefetch()
            return

        self._fading = old
        self._active = new_sound
        try:
            new_sound.volume = 0.0
            new_sound.play()
        except Exception:
            self._active = old
            self._fading = None
            return

        steps = max(1, int(CROSSFADE_SEC / _TICK))
        state = {"i": 0}

        def _step(_dt):
            state["i"] += 1
            t = min(1.0, state["i"] / steps)
            try:
                new_sound.volume = self.target_volume * t
            except Exception:
                pass
            try:
                old.volume = self.target_volume * (1.0 - t)
            except Exception:
                pass
            if t >= 1.0:
                self._fade_ev = None
                try:
                    old.stop()
                    old.volume = self.target_volume
                except Exception:
                    pass
                self._fading = None
                self._trim_cache()
                if not self._playing_battle:
                    self._schedule_prefetch()
                return False
            return True

        self._fade_ev = Clock.schedule_interval(_step, _TICK)

    def _ensure_hub(self, rotate: bool) -> None:
        if not self.enabled:
            return
        if rotate or not self._hub_track:
            self._hub_track = self._pick_hub_track(exclude=self._hub_track)
        if not self._hub_track:
            return
        if self._playing_battle or self._active is None:
            self._crossfade_to(self._hub_track)
        elif rotate:
            self._crossfade_to(self._hub_track)
        self._playing_battle = False
        self._schedule_rotate()

    def _start_battle(self, *_args) -> None:
        self._combat_ev = None
        if not self.enabled or self._paused or self._screen != "combat":
            return
        self._cancel_rotate()
        self._cancel_prefetch()
        self._crossfade_to(BATTLE_TRACK)
        self._playing_battle = True

    def notify_screen(self, name: str) -> None:
        """React to ScreenManager current changes."""
        if self._paused or not self.enabled:
            self._screen = name
            return

        prev = self._screen
        self._screen = name

        if name == "combat":
            self._cancel_combat_delay()
            if not self._started:
                self._ensure_hub(rotate=True)
                self._started = True
            self._combat_ev = Clock.schedule_once(
                self._start_battle, COMBAT_DELAY_SEC
            )
            return

        self._cancel_combat_delay()

        if prev == "combat":
            if self._playing_battle:
                self._ensure_hub(rotate=False)
            else:
                self._schedule_rotate()
                self._schedule_prefetch()
            return

        if not self._started:
            self._ensure_hub(rotate=True)
            self._started = True
            return

        if name in _ROTATE_SCREENS:
            self._ensure_hub(rotate=True)
            return

        if name in _HUB_SCREENS:
            if self._active is None and not self._playing_battle:
                self._ensure_hub(rotate=False)
            else:
                self._schedule_rotate()
            return

    def set_enabled(self, enabled: bool) -> None:
        enabled = bool(enabled)
        if enabled == self.enabled:
            return
        self.enabled = enabled
        if not enabled:
            self._cancel_combat_delay()
            self._cancel_rotate()
            self._cancel_prefetch()
            self._cancel_pending_crossfade()
            self.stop_playback()
            return
        self._paused = False
        self._started = False
        screen = self._screen or "menu"
        self._screen = None
        self.notify_screen(screen)

    def stop_playback(self) -> None:
        self._cancel_fade()
        self._cancel_pending_crossfade()
        for s in (self._active, self._fading):
            if s is None:
                continue
            try:
                s.stop()
            except Exception:
                pass
        self._active = None
        self._fading = None
        self._playing_battle = False

    def stop(self) -> None:
        self._cancel_fade()
        self._cancel_combat_delay()
        self._cancel_rotate()
        self._cancel_prefetch()
        self._cancel_pending_crossfade()
        self.stop_playback()
        self._paused = False

    def pause(self) -> None:
        if self._paused:
            return
        self._cancel_fade()
        self._cancel_combat_delay()
        self._cancel_rotate()
        self._cancel_prefetch()
        self._cancel_pending_crossfade()
        if self._fading is not None:
            try:
                self._fading.stop()
            except Exception:
                pass
            self._fading = None
        if self._active is not None:
            try:
                self._active.stop()
            except Exception:
                pass
        self._paused = True

    def resume(self) -> None:
        if not self._paused:
            return
        self._paused = False
        if not self.enabled:
            return
        screen = self._screen or "menu"
        self._screen = None
        self._started = True
        if screen == "combat":
            self._screen = "hub"
            self.notify_screen("combat")
        elif self._hub_track:
            self._crossfade_to(self._hub_track)
            self._playing_battle = False
            self._screen = screen
            self._schedule_rotate()
        else:
            self.notify_screen(screen)
