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
)
from locales import set_locale, t  # noqa: E402
from player import Player  # noqa: E402
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
            return getattr(item, "description", "") or ""
        return getattr(item, "description", "") or ""

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

    def list_inventory(self) -> List[dict]:
        """Return inventory rows for mobile UI."""
        rows = []
        for i, item in enumerate(self.inventory.items):
            kind = self.item_kind(item)
            rows.append(
                {
                    "index": i,
                    "name": item.name,
                    "kind": kind,
                    "kind_label": t(f"inv_kind_{kind}"),
                    "equipped": bool(getattr(item, "equipped", False)),
                    "description": getattr(item, "description", "") or "",
                    "stats_line": self.item_stats_line(item),
                }
            )
        return rows

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
        """Spend one stat point. Mirror of desktop gui_main.add_stat."""
        if not self.player:
            return False, t("no_character")
        if self.player.stat_points <= 0:
            return False, t("no_stat_points")
        p = self.player
        if stat_id == "hp":
            p.max_hp += 15
            p.hp += 15
        elif stat_id == "attack":
            p.attack += 2
        elif stat_id == "defense":
            p.defense += 2
        elif stat_id == "fire_resist":
            p.fire_resist += 2
        elif stat_id == "cold_resist":
            p.cold_resist += 2
        elif stat_id == "luck":
            p.luck += 1
        elif stat_id == "intellect":
            p.intellect += 1
        else:
            return False, t("invalid_item")
        p.stat_points -= 1
        msg = t("stat_improved", pts=p.stat_points)
        self._msg(msg)
        return True, msg

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
        save_system.save_settings(code)

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
        return save_system.save_game_slot(
            self.player, self.inventory, self.rotation, self.victories, slot
        )

    def load(self, slot: int = 1) -> Tuple[bool, str]:
        result, msg = save_system.load_game_slot(slot)
        if not result:
            return False, msg
        player, inventory, rotation, victories = result
        self.player = player
        self.inventory = inventory
        self.rotation = rotation
        self.victories = victories
        self.in_combat = False
        self.current_enemy = None
        self.clear_log()
        self._msg(msg)
        return True, msg

    def list_slots(self):
        return save_system.list_save_slots()

    def delete_slot(self, slot: int) -> Tuple[bool, str]:
        return save_system.delete_save_slot(slot)

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

    def list_shop(self) -> List[dict]:
        """Build shop rows (item id, display name, price, ready item)."""
        if not self.player:
            return []
        base_pool = [
            "small_potion",
            "medium_potion",
            "large_potion",
            "wooden_sword",
            "leather_armor",
        ]
        if self.rotation >= 1:
            base_pool += ["iron_sword", "iron_armor"]
        if self.rotation >= 2:
            base_pool += ["steel_sword", "steel_armor"]
        if self.rotation >= 3:
            base_pool += ["legendary_sword", "legendary_armor"]
        rows = []
        for iid in base_pool:
            item = get_item_scaled(
                iid, rotation=self.rotation, player_level=self.player.level
            )
            if not item:
                continue
            quality_mul = QUALITY_MULTIPLIER.get(getattr(item, "quality", "wooden"), 0)
            price = int(
                getattr(item, "price", 0)
                + getattr(item, "level", 1) * 50
                + quality_mul * 200
                + self.rotation * 30
            )
            kind = self.item_kind(item)
            rows.append(
                {
                    "id": iid,
                    "name": item.name,
                    "price": price,
                    "item": item,
                    "kind": kind,
                    "kind_label": t(f"inv_kind_{kind}"),
                    "stats_line": self.item_stats_line(item),
                    "description": getattr(item, "description", "") or "",
                    "affordable": bool(self.player.gold >= price),
                }
            )
        return rows

    def buy_shop_item(self, index: int) -> Tuple[bool, str]:
        rows = self.list_shop()
        if index < 0 or index >= len(rows):
            return False, t("invalid_item")
        row = rows[index]
        if self.player.gold < row["price"]:
            return False, t("shop_not_enough")
        # Fresh item instance for purchase
        item = get_item_scaled(
            row["id"], rotation=self.rotation, player_level=self.player.level
        )
        if not item:
            return False, t("invalid_item")
        if not self.inventory.add_item(item):
            return False, t("inventory_full")
        self.player.gold -= row["price"]
        msg = t("shop_bought", name=item.name)
        self._msg(msg)
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
        lines.append(t("mobile_hit", name=enemy.name, damage=actual))

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
            lines.append(t("mobile_defeat"))
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
            if self.player.level >= 2 or self.rotation >= 1:
                loot_items.extend(["wooden_sword", "leather_armor"])
            if self.player.level >= 3 or self.rotation >= 2:
                loot_items.extend(["iron_sword", "iron_armor"])
            if self.player.level >= 4 or self.rotation >= 3:
                loot_items.extend(["steel_sword", "steel_armor"])
            if self.rotation >= 4:
                loot_items.extend(["legendary_sword", "legendary_armor"])
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

        self.rotation += 1
        lines.append(t("rotation_now", rotation=self.rotation))
        self.current_enemy = None
        # Quiet autosave after victory
        try:
            ok, _ = save_system.save_game_slot(
                self.player, self.inventory, self.rotation, self.victories, slot=1
            )
            if ok:
                lines.append(t("autosave_ok"))
        except Exception:
            pass
        return lines
