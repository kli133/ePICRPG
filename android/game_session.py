"""
UI-agnostic game session facade for the Android / Kivy client.

Wraps Player, Inventory, combat helpers and save_system without Tkinter.
Combat log messages are returned as strings (no stdout parsing).
"""
from __future__ import annotations

import random
from typing import List, Optional, Tuple

from storage import ensure_core_path

ensure_core_path()

from classes import CLASSES, get_class  # noqa: E402
from combat import create_enemy, enemy_take_action  # noqa: E402
from inventory import Inventory  # noqa: E402
from items import (  # noqa: E402
    Potion,
    Weapon,
    Armor,
    Artifact,
    get_item_scaled,
    get_random_artifact,
    QUALITY_MULTIPLIER,
    QUALITY_ORDER,
    WEAPON_TYPES,
    ARMOR_TYPES,
)
from locales import set_locale, t  # noqa: E402
from player import Player, calc_rest_cost  # noqa: E402
import save_system  # noqa: E402

try:
    from events_data import create_event_manager  # noqa: E402
except Exception:  # pragma: no cover
    create_event_manager = None


class GameSession:
    """Holds run state and exposes high-level actions for the mobile UI."""

    def __init__(self):
        self.player: Optional[Player] = None
        self.inventory: Inventory = Inventory()
        self.rotation = 0
        self.victories = 0
        self.in_combat = False
        self.current_enemy = None
        self.log: List[str] = []
        self.last_outcome_summary: str = ""
        self._event_manager = None
        self._active_event = None
        self._shop_rows: Optional[List[dict]] = None
        if create_event_manager:
            try:
                self._event_manager = create_event_manager()
            except Exception:
                self._event_manager = None

    # --- helpers ---------------------------------------------------------

    def clear_log(self):
        self.log.clear()

    def _msg(self, text: str) -> str:
        self.log.append(text)
        return text

    def status_line(self) -> str:
        if not self.player:
            return ""
        p = self.player
        enemy = ""
        if self.in_combat and self.current_enemy:
            e = self.current_enemy
            enemy = t("status_enemy", name=e.name, hp=e.hp, max_hp=e.max_hp)
        return t(
            "status_line",
            name=p.name,
            level=p.level,
            hp=p.hp,
            max_hp=p.max_hp,
            gold=p.gold,
            rotation=self.rotation,
            wins=self.victories,
            enemy=enemy,
        )

    def combat_status_player(self) -> str:
        """Short player HP line for the combat header."""
        if not self.player:
            return ""
        p = self.player
        return t(
            "combat_you_line",
            name=p.name,
            level=p.level,
            hp=p.hp,
            max_hp=p.max_hp,
        )

    def combat_status_enemy(self) -> str:
        """Short enemy HP line for the combat header."""
        if not (self.in_combat and self.current_enemy):
            return t("combat_enemy_none")
        e = self.current_enemy
        return t(
            "combat_enemy_line",
            name=e.name,
            hp=max(0, e.hp),
            max_hp=e.max_hp,
        )

    def inventory_summary(self) -> str:
        if not self.inventory.items:
            return t("inventory_empty_msg")
        lines = []
        for entry in self.list_inventory():
            mark = t("equipped_mark") if entry["equipped"] else ""
            lines.append(
                f"{entry['index'] + 1}. [{entry['kind_label']}] {entry['name']}{mark}"
            )
        return "\n".join(lines)

    def item_kind(self, item) -> str:
        if isinstance(item, Weapon):
            return "weapon"
        if isinstance(item, Armor):
            return "armor"
        if isinstance(item, Artifact):
            return "artifact"
        if isinstance(item, Potion):
            return "potion"
        return "item"

    def item_stats_line(self, item) -> str:
        """One-line stats for inventory/shop rows."""
        if isinstance(item, Weapon):
            return t("attack_label", val=getattr(item, "attack_bonus", 0))
        if isinstance(item, Armor):
            return t("defense_label", val=getattr(item, "defense_bonus", 0))
        if isinstance(item, Potion):
            return t("heal_label", val=getattr(item, "heal_amount", 0))
        if isinstance(item, Artifact):
            slots = getattr(item, "bonus_slots", None) or []
            if slots:
                from items import format_artifact_description

                return format_artifact_description(slots)
            return getattr(item, "description", "") or ""
        return getattr(item, "description", "") or ""

    def _item_power(self, item) -> int:
        if isinstance(item, Weapon):
            if hasattr(item, "get_effective_bonus") and self.player:
                try:
                    return int(item.get_effective_bonus(self.player))
                except Exception:
                    pass
            return int(getattr(item, "attack_bonus", 0) or 0)
        if isinstance(item, Armor):
            if hasattr(item, "get_effective_bonus") and self.player:
                try:
                    return int(item.get_effective_bonus(self.player))
                except Exception:
                    pass
            return int(getattr(item, "defense_bonus", 0) or 0)
        if isinstance(item, Potion):
            return int(getattr(item, "heal_amount", 0) or 0)
        return 0

    def item_compare_mark(self, item) -> str:
        """Short better/worse mark vs currently equipped weapon/armor."""
        if not self.player or self._is_equipped(item):
            return ""
        equipped = None
        if isinstance(item, Weapon):
            equipped = getattr(self.player, "weapon", None)
        elif isinstance(item, Armor):
            equipped = getattr(self.player, "armor", None)
        else:
            return ""
        if equipped is None:
            return t("inv_upgrade_empty")
        delta = self._item_power(item) - self._item_power(equipped)
        if delta > 0:
            return t("inv_better", delta=delta)
        if delta < 0:
            return t("inv_worse", delta=delta)
        return t("inv_same")

    def equipment_slots(self) -> dict:
        """Equipped gear names for slot strip UI."""
        empty = t("slot_empty")
        p = self.player
        if not p:
            return {"weapon": empty, "armor": empty, "artifact": empty}
        return {
            "weapon": p.weapon.name if getattr(p, "weapon", None) else empty,
            "armor": p.armor.name if getattr(p, "armor", None) else empty,
            "artifact": p.artifact.name if getattr(p, "artifact", None) else empty,
        }

    def _is_equipped(self, item) -> bool:
        if not self.player or item is None:
            return False
        if bool(getattr(item, "equipped", False)):
            return True
        p = self.player
        return item is getattr(p, "weapon", None) or item is getattr(p, "armor", None) or item is getattr(p, "artifact", None)

    def list_inventory(self) -> List[dict]:
        """Return inventory rows for mobile UI (grouped: weapon→armor→artifact→potion)."""
        from items import calc_sell_price

        kind_order = {"weapon": 0, "armor": 1, "artifact": 2, "potion": 3, "item": 4}
        rows = []
        for i, item in enumerate(self.inventory.items):
            kind = self.item_kind(item)
            equipped = self._is_equipped(item)
            stats = self.item_stats_line(item)
            # Prefer live localized stats for artifacts (saved desc may be EN)
            if isinstance(item, Artifact) and getattr(item, "bonus_slots", None):
                desc = stats
            else:
                desc = getattr(item, "description", "") or ""
            rows.append(
                {
                    "index": i,
                    "name": item.name,
                    "kind": kind,
                    "kind_label": t(f"inv_kind_{kind}"),
                    "equipped": equipped,
                    "description": desc,
                    "stats_line": stats,
                    "compare_mark": self.item_compare_mark(item),
                    "sell_price": calc_sell_price(item, self.player, rotation=self.rotation),
                    "_sort_kind": kind_order.get(kind, 9),
                    "_sort_power": self._item_power(item),
                }
            )
        rows.sort(
            key=lambda r: (
                r["_sort_kind"],
                0 if r["equipped"] else 1,
                -r["_sort_power"],
                r["index"],
            )
        )
        for r in rows:
            r.pop("_sort_kind", None)
            r.pop("_sort_power", None)
        return rows

    def sell_price_for(self, index: int) -> int:
        from items import calc_sell_price

        if index < 0 or index >= len(self.inventory.items):
            return 0
        return calc_sell_price(self.inventory.items[index], self.player, rotation=self.rotation)

    def sell_item(self, index: int) -> Tuple[bool, str]:
        """Sell inventory item (no confirm — UI confirms). Blocks equipped gear."""
        if not self.player:
            return False, t("no_character")
        if index < 0 or index >= len(self.inventory.items):
            return False, t("invalid_item")
        item = self.inventory.items[index]
        if self._is_equipped(item):
            return False, t("cannot_sell_equipped")
        from items import calc_sell_price

        price = calc_sell_price(item, self.player, rotation=self.rotation)
        self.player.gold += price
        self.inventory.remove_item(item)
        msg = t("item_sold_text", gold=price)
        self._msg(msg)
        return True, msg

    def equip_or_use_item(self, index: int) -> Tuple[bool, str]:
        """Equip gear / use potion or miscellaneous item by inventory index."""
        if not self.player:
            return False, t("no_character")
        if index < 0 or index >= len(self.inventory.items):
            return False, t("invalid_item")
        item = self.inventory.items[index]

        if isinstance(item, Potion):
            before = self.player.hp
            self.inventory.use_item(index, self.player)
            msg = t(
                "used_item_hp",
                name=item.name,
                before=before,
                hp=self.player.hp,
                max_hp=self.player.max_hp,
            )
            self._msg(msg)
            return True, msg

        if isinstance(item, Weapon):
            if self.player.weapon and self.player.weapon is not item:
                try:
                    self.player.weapon.equipped = False
                except Exception:
                    pass
            item.use(self.player)
            item.equipped = True
            self.player.weapon = item
            msg = t(
                "equipped_weapon_msg",
                name=item.name,
                atk=self.player.get_total_attack(),
            )
            self._msg(msg)
            return True, msg

        if isinstance(item, Armor):
            if self.player.armor and self.player.armor is not item:
                try:
                    self.player.armor.equipped = False
                except Exception:
                    pass
            item.use(self.player)
            item.equipped = True
            self.player.armor = item
            msg = t(
                "equipped_armor_msg",
                name=item.name,
                defense=self.player.get_total_defense(),
            )
            self._msg(msg)
            return True, msg

        if isinstance(item, Artifact):
            item.use(self.player)
            msg = t("equipped_artifact_msg", name=item.name)
            self._msg(msg)
            return True, msg

        # Fallback: Item.use / SkillBook etc.
        self.inventory.use_item(index, self.player)
        msg = t("used_item_msg", name=getattr(item, "name", "?"))
        self._msg(msg)
        return True, msg

    def stats_detail(self) -> dict:
        """Structured stats for the mobile stats screen."""
        if not self.player:
            return {}
        p = self.player
        return {
            "name": p.name,
            "cls": p.class_name,
            "level": p.level,
            "exp": p.exp,
            "exp_next": p.exp_to_next_level,
            "hp": p.hp,
            "max_hp": p.max_hp,
            "atk": p.get_total_attack(),
            "defense": p.get_total_defense(),
            "intellect": getattr(p, "intellect", 0),
            "luck": p.get_total_luck(),
            "agility": p.get_total_agility() if hasattr(p, "get_total_agility") else getattr(p, "agility", 0),
            "fire": getattr(p, "fire_resist", 0),
            "cold": getattr(p, "cold_resist", 0),
            "gold": p.gold,
            "prestige": getattr(p, "prestige_level", 0),
            "rotation": self.rotation,
            "wins": self.victories,
            "stat_points": int(getattr(p, "stat_points", 0) or 0),
        }

    def stats_summary(self) -> str:
        d = self.stats_detail()
        if not d:
            return ""
        base = t(
            "stats_block",
            name=d["name"],
            cls=d["cls"],
            level=d["level"],
            exp=d["exp"],
            exp_next=d["exp_next"],
            hp=d["hp"],
            max_hp=d["max_hp"],
            atk=d["atk"],
            defense=d["defense"],
            intellect=d["intellect"],
            luck=d["luck"],
            agility=d.get("agility", 0),
            fire=d["fire"],
            cold=d["cold"],
            gold=d["gold"],
            prestige=d["prestige"],
            rotation=d["rotation"],
            wins=d["wins"],
        )
        pts = d.get("stat_points", 0)
        return f"{base}\n{t('stat_points_available', pts=pts)}"

    def spend_stat(self, stat_id: str) -> Tuple[bool, str]:
        """Spend one stat point via Player.apply_stat_spend."""
        if not self.player:
            return False, t("no_character")
        if self.player.stat_points <= 0:
            return False, t("no_stat_points")
        if not self.player.apply_stat_spend(stat_id):
            return False, t("invalid_item")
        msg = t("stat_improved", pts=self.player.stat_points)
        self._msg(msg)
        return True, msg

    def spend_stat_batch(self, deltas: dict) -> Tuple[bool, str]:
        """Apply draft deltas {stat_id: count}. Returns false if not enough points."""
        if not self.player:
            return False, t("no_character")
        total = sum(int(v) for v in deltas.values() if int(v) > 0)
        if total <= 0:
            return False, t("no_stat_points")
        if total > self.player.stat_points:
            return False, t("no_stat_points")
        for stat_id, count in deltas.items():
            for _ in range(int(count)):
                if not self.player.apply_stat_spend(stat_id):
                    return False, t("invalid_item")
        msg = t("stat_improved", pts=self.player.stat_points)
        self._msg(msg)
        return True, msg

    def base_stat_values(self) -> dict:
        """Raw base stats (without equipment totals) for allocation UI."""
        if not self.player:
            return {}
        p = self.player
        return {
            "hp": p.max_hp,
            "attack": p.attack,
            "defense": p.defense,
            "fire_resist": getattr(p, "fire_resist", 0),
            "cold_resist": getattr(p, "cold_resist", 0),
            "luck": getattr(p, "luck", 0),
            "intellect": getattr(p, "intellect", 0),
            "agility": getattr(p, "agility", 0),
        }

    def list_classes(self):
        rows = []
        for cid, c in CLASSES.items():
            name = t(f"class_{cid}_name")
            desc = t(f"class_{cid}_desc")
            if name == f"class_{cid}_name":
                name = c.name
            if desc == f"class_{cid}_desc":
                desc = c.description
            rows.append((cid, name, desc))
        return rows

    # --- meta ------------------------------------------------------------

    def set_language(self, code: str) -> None:
        set_locale(code)
        save_system.save_settings(locale_code=code)

    def set_music_enabled(self, enabled: bool) -> None:
        save_system.save_settings(music_enabled=bool(enabled))

    def load_settings(self):
        return save_system.load_settings()

    # --- character / save ------------------------------------------------

    def new_game(self, name: str, class_id: str) -> Tuple[bool, str]:
        name = (name or "").strip() or t("default_hero")
        if class_id not in CLASSES:
            return False, t("unknown_class")
        self.player = Player(name, class_id=class_id)
        self.inventory = Inventory()
        self.rotation = 0
        self.victories = 0
        self.in_combat = False
        self.current_enemy = None
        self._shop_rows = None
        self.clear_log()
        starter = get_item_scaled("small_potion", rotation=0, player_level=1)
        if starter:
            self.inventory.add_item(starter)
        cls_name = t(f"class_{class_id}_name")
        if cls_name == f"class_{class_id}_name":
            cls = get_class(class_id)
            cls_name = cls.name if cls else class_id
        self._msg(f"{name} — {cls_name}")
        return True, "ok"

    def save(self, slot: int = 1) -> Tuple[bool, str]:
        if not self.player:
            return False, t("no_character")
        if not self.player.is_alive():
            return False, t("cannot_save_dead")
        return save_system.save_game_slot(
            self.player, self.inventory, self.rotation, self.victories, slot
        )

    def _autosave(self, lines: Optional[List[str]] = None) -> bool:
        """Quiet autosave to reserved slot (MAX_SLOTS). Never save a dead hero."""
        if not self.player or not self.player.is_alive():
            return False
        try:
            ok, _ = save_system.save_game_slot(
                self.player,
                self.inventory,
                self.rotation,
                self.victories,
                slot=save_system.MAX_SLOTS,
            )
            if ok and lines is not None:
                lines.append(t("autosave_ok"))
            return bool(ok)
        except Exception:
            return False

    def load(self, slot: int = 1) -> Tuple[bool, str]:
        # Drop dead saves before load so autosave cannot revive a corpse
        try:
            save_system.purge_dead_saves()
        except Exception:
            pass
        result, msg = save_system.load_game_slot(slot)
        if not result:
            return False, msg
        player, inventory, rotation, victories = result
        if not player.is_alive():
            try:
                save_system.delete_save_slot(slot)
            except Exception:
                pass
            return False, t("cannot_save_dead")
        self.player = player
        self.inventory = inventory
        self.rotation = rotation
        self.victories = victories
        self.in_combat = False
        self.current_enemy = None
        self._shop_rows = None
        self.clear_log()
        self._msg(msg)
        return True, msg

    def list_slots(self):
        return save_system.list_save_slots()

    def delete_slot(self, slot: int) -> Tuple[bool, str]:
        return save_system.delete_save_slot(slot)

    def rest_cost(self) -> int:
        if not self.player:
            return calc_rest_cost(0, self.rotation)
        return calc_rest_cost(getattr(self.player, "prestige_level", 0), self.rotation)

    def rest(self) -> Tuple[bool, str]:
        """Full heal between fights for gold (cheap; scales with prestige/rotation)."""
        if not self.player:
            return False, t("no_character")
        if not self.player.is_alive():
            return False, t("cannot_fight_dead")
        if self.player.hp >= self.player.max_hp:
            return False, t("rest_full")
        cost = self.rest_cost()
        if self.player.gold < cost:
            return False, t("rest_no_gold", cost=cost)
        self.player.gold -= cost
        self.player.hp = self.player.max_hp
        msg = t("rested", cost=cost)
        self._msg(msg)
        self._msg(t("restored_hp", hp=self.player.hp, max_hp=self.player.max_hp))
        return True, msg

    def can_prestige(self) -> bool:
        return bool(self.player and self.player.can_prestige())

    def prestige_requirement(self) -> int:
        if not self.player:
            return 50
        return self.player.get_prestige_requirement()

    def do_prestige(self) -> Tuple[bool, str]:
        if not self.player:
            return False, t("no_character")
        if not self.player.can_prestige():
            return False, t("prestige_locked", level=self.player.get_prestige_requirement())
        try:
            self.player.prestige_reset()
            self.rotation = 0
            self.victories = 0
            self.in_combat = False
            self.current_enemy = None
            self.inventory = Inventory()
            msg = t("prestige_now", level=getattr(self.player, "prestige_level", "?"))
            self._msg(msg)
            return True, msg
        except Exception as e:
            return False, str(e)

    def _class_gear_tiers(self) -> list:
        """Class-weighted gear tiers: [tier0, tier1, tier2, tier3+] item id lists."""
        cid = None
        if self.player and self.player.class_obj:
            cid = self.player.class_obj.id
        by_class = {
            "warrior": [
                ["wooden_sword", "leather_armor"],
                ["iron_sword", "iron_armor", "chainmail"],
                ["steel_sword", "steel_armor", "battle_axe"],
                ["legendary_sword", "plate_armor"],
            ],
            "mage": [
                ["wooden_staff", "cloth_armor"],
                ["crystal_staff", "silk_robe"],
                ["arcane_staff", "mystic_robe"],
                ["ancient_staff", "enchanted_robe"],
            ],
            "rogue": [
                ["wooden_bow", "dagger", "leather_armor_light"],
                ["iron_bow", "reinforced_leather"],
                ["steel_bow", "shadow_leather"],
                ["steel_bow", "shadow_leather"],
            ],
            "lucky": [
                ["wooden_sword", "wooden_bow", "dagger", "cloth_armor"],
                ["iron_sword", "iron_bow", "silk_robe", "reinforced_leather"],
                ["steel_sword", "steel_bow", "mystic_robe"],
                ["legendary_sword", "legendary_armor"],
            ],
        }
        return by_class.get(cid, by_class["warrior"])

    def _shop_price(self, item) -> int:
        quality_mul = QUALITY_MULTIPLIER.get(getattr(item, "quality", "wooden"), 0)
        return int(
            getattr(item, "price", 0)
            + getattr(item, "level", 1) * 50
            + quality_mul * 200
            + self.rotation * 30
        )

    def _make_shop_row(self, iid: str, item, featured: bool = False) -> dict:
        price = self._shop_price(item)
        kind = self.item_kind(item)
        return {
            "id": iid,
            "name": item.name,
            "price": price,
            "item": item,
            "kind": kind,
            "kind_label": t(f"inv_kind_{kind}"),
            "stats_line": self.item_stats_line(item),
            "description": getattr(item, "description", "") or "",
            "compare_mark": self.item_compare_mark(item),
            "affordable": bool(self.player and self.player.gold >= price),
            "featured": bool(featured),
        }

    def _is_shop_upgrade(self, item) -> bool:
        """True if item beats currently equipped gear of the same slot (or slot empty)."""
        if not self.player:
            return False
        if isinstance(item, Weapon):
            equipped = getattr(self.player, "weapon", None)
            if equipped is None:
                return True
            return self._item_power(item) > self._item_power(equipped)
        if isinstance(item, Armor):
            equipped = getattr(self.player, "armor", None)
            if equipped is None:
                return True
            return self._item_power(item) > self._item_power(equipped)
        return False

    def _featured_slot_prefer_weapon(self) -> bool:
        """Prefer empty slot; otherwise weapon."""
        if not self.player:
            return True
        if getattr(self.player, "weapon", None) is None:
            return True
        if getattr(self.player, "armor", None) is None:
            return False
        return True

    def _featured_candidate_ids(self, want_weapon: bool) -> List[str]:
        """All class-ladder gear ids for the slot (featured may go above rotation unlock)."""
        tiers = self._class_gear_tiers()
        ids: List[str] = []
        seen = set()
        for tier in tiers:
            for iid in tier:
                if iid in seen:
                    continue
                is_weapon = iid in WEAPON_TYPES
                is_armor = iid in ARMOR_TYPES
                if want_weapon and is_weapon:
                    seen.add(iid)
                    ids.append(iid)
                elif (not want_weapon) and is_armor:
                    seen.add(iid)
                    ids.append(iid)
        return ids

    def _make_stronger_gear(self, want_weapon: bool):
        """Build (item_id, item) stronger than equipped slot; bump quality/level as needed."""
        ids = self._featured_candidate_ids(want_weapon)
        if not ids:
            return None, None
        equipped = (
            getattr(self.player, "weapon", None)
            if want_weapon
            else getattr(self.player, "armor", None)
        )
        eq_power = self._item_power(equipped) if equipped is not None else -1
        base_level = max(1, self.player.level + self.rotation)
        # Prefer higher-tier ids; raise quality then item_level until stronger
        for iid in reversed(ids):
            item_level = base_level
            for _ in range(80):
                for quality in QUALITY_ORDER:
                    item = get_item_scaled(
                        iid,
                        rotation=self.rotation,
                        player_level=self.player.level,
                        quality=quality,
                        item_level=item_level,
                        force_quality=True,
                    )
                    if not item:
                        continue
                    if self._item_power(item) > eq_power:
                        return iid, item
                item_level += 2
        return None, None

    def _ensure_featured_upgrade(self, rows: List[dict]) -> None:
        """Mark or inject exactly one featured gear stronger than equipped."""
        for row in rows:
            row["featured"] = False
        for row in rows:
            item = row.get("item")
            if isinstance(item, (Weapon, Armor)) and self._is_shop_upgrade(item):
                row["featured"] = True
                return
        want_weapon = self._featured_slot_prefer_weapon()
        iid, item = self._make_stronger_gear(want_weapon)
        if not item:
            # Try the other slot
            iid, item = self._make_stronger_gear(not want_weapon)
        if not item:
            return
        featured = self._make_shop_row(iid, item, featured=True)
        # Drop duplicate id of same kind from stock so buy index stays unique
        kind = featured["kind"]
        rows[:] = [r for r in rows if not (r.get("id") == iid and r.get("kind") == kind)]
        insert_at = 0
        for i, r in enumerate(rows):
            if r.get("kind") != "potion":
                insert_at = i
                break
        else:
            insert_at = len(rows)
        rows.insert(insert_at, featured)

    def _refresh_shop_row_flags(self, rows: List[dict]) -> List[dict]:
        """Update affordable/compare_mark without regenerating items."""
        if not self.player:
            return rows
        for row in rows:
            item = row.get("item")
            price = int(row.get("price", 0) or 0)
            row["affordable"] = bool(self.player.gold >= price)
            if item is not None:
                row["compare_mark"] = self.item_compare_mark(item)
                row["stats_line"] = self.item_stats_line(item)
                row["name"] = getattr(item, "name", row.get("name", ""))
        return rows

    def list_shop(self, refresh: bool = False) -> List[dict]:
        """Build (or return cached) shop rows. refresh=True rebuilds stock."""
        if not self.player:
            self._shop_rows = None
            return []
        if self._shop_rows is not None and not refresh:
            return self._refresh_shop_row_flags(self._shop_rows)

        base_pool = [
            "small_potion",
            "medium_potion",
            "large_potion",
        ]
        tiers = self._class_gear_tiers()
        base_pool += list(tiers[0])
        if self.rotation >= 1:
            base_pool += list(tiers[1])
        if self.rotation >= 2:
            base_pool += list(tiers[2])
        if self.rotation >= 3:
            base_pool += list(tiers[3])
        seen = set()
        uniq = []
        for iid in base_pool:
            if iid not in seen:
                seen.add(iid)
                uniq.append(iid)
        base_pool = uniq

        rows: List[dict] = []
        for iid in base_pool:
            item = get_item_scaled(
                iid, rotation=self.rotation, player_level=self.player.level
            )
            if not item:
                continue
            rows.append(self._make_shop_row(iid, item, featured=False))

        self._ensure_featured_upgrade(rows)
        self._shop_rows = rows
        return self._refresh_shop_row_flags(self._shop_rows)

    def buy_shop_item(self, index: int) -> Tuple[bool, str]:
        rows = self.list_shop(refresh=False)
        if index < 0 or index >= len(rows):
            return False, t("invalid_item")
        row = rows[index]
        if self.player.gold < row["price"]:
            return False, t("shop_not_enough")
        item = row.get("item")
        if item is None:
            return False, t("invalid_item")
        if not self.inventory.add_item(item):
            return False, t("inventory_full")
        self.player.gold -= row["price"]
        msg = t("shop_bought", name=getattr(item, "name", row.get("name", "")))
        self._msg(msg)
        # Rebuild stock so a new upgrade offer appears
        self.list_shop(refresh=True)
        return True, msg

    def start_adventure(self) -> Tuple[str, object]:
        """Hub adventure button: 30% event, 70% combat.

        Returns (kind, payload) where kind is:
          - "error" + str message
          - "event" + event dict (same as start_explore payload)
          - "combat" + encounter message str
        """
        if not self.player:
            return "error", t("no_character")
        if not self.player.is_alive():
            return "error", t("cannot_fight_dead")
        # Prefer combat if event system is unavailable.
        want_event = random.random() < 0.30 and self._event_manager is not None
        if want_event:
            ok, payload = self.start_explore()
            if ok:
                return "event", payload
            # Fall through to combat if event roll failed to produce content.
        ok, msg = self.start_combat()
        if ok:
            return "combat", msg
        return "error", msg

    def start_explore(self) -> Tuple[bool, dict]:
        """Return (ok, event_payload) for mobile explore UI."""
        if not self.player or not self.player.is_alive():
            return False, {"error": t("cannot_fight_dead")}
        if not self._event_manager:
            return False, {"error": t("explore_none")}
        event = self._event_manager.get_random_event()
        if not event:
            return False, {"error": t("explore_none")}
        self._active_event = event
        choices = []
        for idx, choice in event.get_available_choices(self.player):
            choices.append({"index": idx, "text": choice.text})
        return True, {
            "title": event.title,
            "description": event.description,
            "choices": choices,
            "can_ignore": bool(getattr(event, "can_ignore", True)),
        }

    def resolve_explore_choice(self, choice_index: int) -> Tuple[bool, str]:
        if not self.player or not self._active_event:
            return False, t("explore_none")
        event = self._active_event
        if choice_index < 0 or choice_index >= len(event.choices):
            return False, t("explore_none")
        choice = event.choices[choice_index]
        if not choice.is_available(self.player):
            return False, t("explore_none")
        text, effects, gold, exp = choice.execute(self.player)
        for stat, amount in (effects or {}).items():
            if hasattr(self.player, stat):
                setattr(self.player, stat, getattr(self.player, stat) + amount)
                if stat == "max_hp":
                    self.player.hp = min(self.player.hp + amount, self.player.max_hp)
        if gold:
            self.player.gold += gold
        if exp:
            self.player.gain_exp(exp)
            lines = self.player.drain_combat_messages()
            for line in lines:
                self._msg(line)
        self._active_event = None
        msg = text
        self._msg(msg)
        return True, msg

    def dismiss_explore(self) -> str:
        self._active_event = None
        msg = t("event_ignore")
        self._msg(msg)
        return msg

    # --- combat ----------------------------------------------------------

    def start_combat(self) -> Tuple[bool, str]:
        if not self.player:
            return False, t("no_character")
        if not self.player.is_alive():
            return False, t("cannot_fight_dead")
        self.player.clear_combat_messages()
        try:
            self.player.begin_combat_passives()
        except Exception:
            pass
        # Checkpoint before the fight — on death this stay as "one step back"
        self._autosave()
        self.current_enemy = create_enemy(self.player.level, rotation=self.rotation)
        self.in_combat = True
        e = self.current_enemy
        msg = t(
            "mobile_encounter",
            name=e.name,
            level=e.level,
            hp=e.hp,
            max_hp=e.max_hp,
        )
        if getattr(self.player, "ambush_ready", False):
            msg = f"{msg}\n{t('ambush_ready')}"
        self._msg(msg)
        return True, msg

    def _finish_lines(self, lines: List[str], outcome: Optional[str]) -> Tuple[str, Optional[str]]:
        text = "\n".join(lines)
        self._msg(text)
        if outcome:
            self.last_outcome_summary = text
        return text, outcome

    def _player_stunned_turn(self, lines: List[str]) -> Tuple[str, Optional[str]]:
        lines.append(t("player_stunned"))
        self.player.stunned_turns = max(0, self.player.stunned_turns - 1)
        outcome = self._enemy_turn(lines)
        return self._finish_lines(lines, outcome)

    def combat_attack(self) -> Tuple[str, Optional[str]]:
        """
        Player attack + enemy reply if needed.
        Returns (log_text, outcome) where outcome is None | 'victory' | 'defeat' | 'fled'.
        """
        if not self._combat_ready():
            return t("not_in_combat"), None
        lines = []
        if getattr(self.player, "stunned_turns", 0) > 0:
            return self._player_stunned_turn(lines)

        enemy = self.current_enemy
        self.player.clear_combat_messages()
        damage = random.randint(
            int(self.player.get_total_attack() * 0.8),
            int(self.player.get_total_attack() * 1.2),
        )
        amb = 1.0
        try:
            amb = self.player.consume_ambush_multiplier()
        except Exception:
            amb = 1.0
        if amb > 1.0:
            damage = int(damage * amb)
            lines.append(t("ambush_proc"))
        if enemy.check_evade():
            lines.append(t("enemy_dodged", name=enemy.name))
            outcome = self._enemy_turn(lines)
            return self._finish_lines(lines, outcome)

        crit = self.player.check_crit()
        if crit > 1.0:
            damage = int(damage * crit)
            lines.append(t("mobile_crit", mult=f"{crit:.1f}"))
        actual = enemy.take_damage(damage)
        try:
            self.player.apply_artifact_on_hit(enemy, actual)
        except Exception:
            pass
        lines.extend(self.player.drain_combat_messages())
        lines.append(
            t(
                "mobile_hit",
                name=enemy.name,
                damage=actual,
                hp=max(0, enemy.hp),
                max_hp=enemy.max_hp,
            )
        )

        if not enemy.is_alive():
            lines.extend(self._apply_victory())
            return self._finish_lines(lines, "victory")

        outcome = self._enemy_turn(lines)
        return self._finish_lines(lines, outcome)

    def combat_use_ability(self, ability_id: Optional[str] = None) -> Tuple[str, Optional[str]]:
        if not self._combat_ready():
            return t("not_in_combat"), None
        lines = []
        if getattr(self.player, "stunned_turns", 0) > 0:
            return self._player_stunned_turn(lines)
        if not self.player.abilities:
            return t("no_abilities"), None
        if ability_id is None:
            ability_id = next(iter(self.player.abilities))
        if not self.player.can_use_ability(ability_id):
            return t("ability_on_cooldown"), None
        self.player.clear_combat_messages()
        ok = self.player.use_ability(ability_id, self.current_enemy)
        lines.extend(self.player.drain_combat_messages())
        if not ok and not lines:
            return t("ability_on_cooldown"), None
        if not self.current_enemy.is_alive():
            # No enemy-turn CD tick this round — drop the same-turn skip flag
            self.player._skip_cd_tick_once = False
            lines.extend(self._apply_victory())
            return self._finish_lines(lines, "victory")
        outcome = self._enemy_turn(lines)
        return self._finish_lines(lines, outcome)

    def combat_ability(self, ability_id: Optional[str] = None) -> Tuple[str, Optional[str]]:
        return self.combat_use_ability(ability_id)

    def combat_use_potion(self) -> Tuple[str, Optional[str]]:
        if not self._combat_ready():
            return t("not_in_combat"), None
        lines = []
        if getattr(self.player, "stunned_turns", 0) > 0:
            return self._player_stunned_turn(lines)
        potions = [
            (i, item)
            for i, item in enumerate(self.inventory.items)
            if isinstance(item, Potion)
        ]
        if not potions:
            return t("no_potions"), None
        inv_index, potion = potions[0]
        self.inventory.use_item(inv_index, self.player)
        lines = [
            t(
                "used_potion_hp",
                name=potion.name,
                hp=self.player.hp,
                max_hp=self.player.max_hp,
            )
        ]
        outcome = self._enemy_turn(lines)
        return self._finish_lines(lines, outcome)

    def combat_potion(self) -> Tuple[str, Optional[str]]:
        return self.combat_use_potion()

    def combat_flee(self) -> Tuple[str, Optional[str]]:
        if not self._combat_ready():
            return t("not_in_combat"), None
        lines = []
        if getattr(self.player, "stunned_turns", 0) > 0:
            return self._player_stunned_turn(lines)
        if random.random() < 0.5:
            self.in_combat = False
            self.current_enemy = None
            lines.append(t("mobile_fled"))
            return self._finish_lines(lines, "fled")
        lines.append(t("flee_failed"))
        outcome = self._enemy_turn(lines)
        return self._finish_lines(lines, outcome)

    def ability_choices(self):
        if not self.player:
            return []
        out = []
        for aid, (name, desc, cd) in self.player.abilities.items():
            rc = self.player.ability_cooldowns.get(aid, 0)
            out.append((aid, name, desc, cd, rc))
        return out

    # --- internal combat helpers -----------------------------------------

    def _combat_ready(self) -> bool:
        return bool(self.player and self.in_combat and self.current_enemy)

    def _enemy_turn(self, lines: List[str]) -> Optional[str]:
        enemy = self.current_enemy
        if getattr(enemy, "stunned_turns", 0) > 0:
            lines.append(t("enemy_stunned", name=enemy.name))
            enemy.stunned_turns -= 1
        else:
            self.player.clear_combat_messages()
            dmg = enemy_take_action(enemy, self.player)
            skill_lines = self.player.drain_combat_messages()
            if skill_lines:
                lines.extend(skill_lines)
                lines.append(
                    t(
                        "mobile_enemy_hit",
                        name=enemy.name,
                        damage=dmg,
                        hp=self.player.hp,
                        max_hp=self.player.max_hp,
                    )
                )
            else:
                lines.append(
                    t(
                        "mobile_enemy_hit",
                        name=enemy.name,
                        damage=dmg,
                        hp=self.player.hp,
                        max_hp=self.player.max_hp,
                    )
                )

        if not self.player.is_alive():
            self.in_combat = False
            self.current_enemy = None
            lines.append(t("mobile_defeat"))
            # Do not overwrite autosave — last living checkpoint stays loadable
            return "defeat"

        try:
            self.player.reduce_cooldowns()
        except Exception:
            pass
        return None

    def _apply_victory(self) -> List[str]:
        lines = []
        enemy = self.current_enemy
        self.in_combat = False
        self.victories += 1
        lines.append(t("mobile_victory", name=enemy.name))

        prestige_exp_mult = 1.0
        prestige_gold_mult = 1.0
        artifact_gold_mult = 1.0
        try:
            prestige_exp_mult = self.player.get_prestige_exp_multiplier()
            prestige_gold_mult = self.player.get_prestige_gold_multiplier()
        except Exception:
            pass
        try:
            artifact_gold_mult = self.player.get_artifact_gold_multiplier()
        except Exception:
            pass

        xp_gain = int(
            enemy.exp_reward
            * (1 + getattr(self.player, "intellect", 0) * 0.05 + self.rotation * 0.10)
            * prestige_exp_mult
        )
        gold_gain = int(
            enemy.gold_reward
            * (1 + self.player.get_total_luck() * 0.05 + self.rotation * 0.12)
            * prestige_gold_mult
            * artifact_gold_mult
        )
        if getattr(self.player, "fortune_active", False):
            gold_gain = int(gold_gain * 1.2)
            self.player.fortune_active = False
            lines.append(t("fortune_gold_bonus"))
        old_level = self.player.level
        self.player.gain_exp(xp_gain)
        self.player.gold += gold_gain
        lines.append(t("xp_gold_gain", xp=xp_gain, gold=gold_gain))
        if self.player.level > old_level:
            lines.append(t("level_up_now", level=self.player.level))
            lines.append(t("stat_points_gained"))

        loot_bonus = 0.0
        try:
            loot_bonus = self.player.get_prestige_loot_bonus()
        except Exception:
            pass
        try:
            loot_bonus += self.player.get_artifact_loot_bonus()
        except Exception:
            pass
        loot_chance = min(
            0.95,
            0.35
            + self.rotation * 0.05
            + self.player.get_total_luck() * 0.04
            + self.player.level * 0.01
            + loot_bonus,
        )
        if random.random() < loot_chance:
            loot_items = ["small_potion", "medium_potion"]
            tiers = self._class_gear_tiers()
            if self.player.level >= 2 or self.rotation >= 1:
                loot_items.extend(tiers[0])
            if self.player.level >= 3 or self.rotation >= 2:
                loot_items.extend(tiers[1])
            if self.player.level >= 4 or self.rotation >= 3:
                loot_items.extend(tiers[2])
            if self.rotation >= 4:
                loot_items.extend(tiers[3])
            choice_id = random.choice(loot_items)
            loot = get_item_scaled(
                choice_id, rotation=self.rotation, player_level=self.player.level
            )
            if loot:
                if self.inventory.add_item(loot):
                    lines.append(t("loot_got", name=loot.name))
                else:
                    lines.append(t("inventory_full"))
            if random.random() < min(
                0.35, self.player.get_total_luck() * 0.03 + self.rotation * 0.02
            ):
                loot2 = get_item_scaled(
                    random.choice(loot_items),
                    rotation=self.rotation,
                    player_level=self.player.level,
                )
                if loot2:
                    if self.inventory.add_item(loot2):
                        lines.append(t("loot_got", name=loot2.name))
                    else:
                        lines.append(t("inventory_full"))

        try:
            artifact_chance = min(
                0.20,
                0.02 + self.rotation * 0.01 + self.player.get_total_luck() * 0.002,
            )
            if random.random() < artifact_chance:
                artifact = get_random_artifact(
                    rotation=self.rotation, player_luck=self.player.get_total_luck()
                )
                if artifact:
                    if self.inventory.add_item(artifact):
                        lines.append(t("artifact_got", name=artifact.name))
                    else:
                        lines.append(t("inventory_full"))
        except Exception:
            pass

        # Match desktop: advance rotation every 5 victories
        if self.victories > 0 and self.victories % 5 == 0:
            self.rotation += 1
            lines.append(t("rotation_now", rotation=self.rotation))
        self.current_enemy = None
        self._autosave(lines)
        return lines
