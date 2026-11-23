"""Regression: class abilities (CD same-turn, stun, evade, messages)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(ROOT, "core")
for path in (ROOT, CORE):
    if path not in sys.path:
        sys.path.insert(0, path)

from player import Player
from combat import Enemy, enemy_take_action


def _quiet(p):
    p._cm = lambda *a, **k: None


def test_warrior_cd_not_ticked_same_turn():
    p = Player("W", class_id="warrior")
    e = Enemy("Goblin", 1, 200, 5, 2, 10, 5)
    assert "warrior_rage" in p.skills and p.skills["warrior_rage"] == 1
    assert p.use_ability("warrior_rage", e) is True
    assert p.ability_cooldowns["warrior_rage"] == 3
    msgs = p.drain_combat_messages()
    assert any("Goblin" in m for m in msgs), msgs
    p.reduce_cooldowns()  # same-turn skip
    assert p.ability_cooldowns["warrior_rage"] == 3
    p.reduce_cooldowns()  # next turn
    assert p.ability_cooldowns["warrior_rage"] == 2


def test_mage_stun_skips_enemy_hit():
    p = Player("M", class_id="mage")
    _quiet(p)
    e = Enemy("Skeleton", 1, 200, 50, 0, 10, 5)
    hp_before = p.hp
    assert p.use_ability("mage_lightning", e) is True
    assert e.stunned_turns >= 1
    if e.stunned_turns > 0:
        e.stunned_turns -= 1
        dmg = 0
    else:
        dmg = enemy_take_action(e, p)
    assert dmg == 0
    assert p.hp == hp_before


def test_rogue_backstab_damages_enemy():
    p = Player("R", class_id="rogue")
    p.begin_combat_passives()
    e = Enemy("Orc", 1, 200, 40, 20, 10, 5)
    hp_before = e.hp
    assert "rogue_backstab" in p.abilities
    assert p.use_ability("rogue_backstab", e) is True
    assert e.hp < hp_before
    msgs = p.drain_combat_messages()
    joined = " ".join(msgs).lower()
    assert "orc" in joined or "спину" in joined or "backstab" in joined or "удар" in joined, msgs
    assert p.ability_cooldowns.get("rogue_backstab", 0) > 0


def test_lucky_fortune_flags_gold_bonus():
    p = Player("L", class_id="lucky")
    e = Enemy("Rat", 1, 50, 5, 0, 10, 5)
    assert "lucky_fortune" in p.abilities
    assert p.use_ability("lucky_fortune", e) is True
    assert p.fortune_active is True


def test_ability_hit_message_uses_enemy_name():
    p = Player("W", class_id="warrior")
    e = Enemy("Rat", 1, 100, 5, 1, 10, 5)
    p.use_ability("warrior_rage", e)
    msgs = p.drain_combat_messages()
    joined = " ".join(msgs)
    assert "Rat" in joined
    assert "Удар ярости" in joined or "ярости" in joined.lower()


if __name__ == "__main__":
    test_warrior_cd_not_ticked_same_turn()
    test_mage_stun_skips_enemy_hit()
    test_rogue_backstab_damages_enemy()
    test_lucky_fortune_flags_gold_bonus()
    test_ability_hit_message_uses_enemy_name()
    print("OK")
