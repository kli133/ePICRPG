"""Combat balance harness: incoming/outgoing damage, TTK, win-rate."""
import os
import random
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(ROOT, "core")
for path in (ROOT, CORE):
    if path not in sys.path:
        sys.path.insert(0, path)

from player import Player
import combat as _combat
from combat import create_enemy, enemy_take_action
import ui as _ui


def _silence_combat_logs():
    """Mute cprint during auto-fights (ui / combat / player bindings)."""
    quiet = lambda *a, **k: None
    _ui.cprint = quiet
    _combat.cprint = quiet
    try:
        import player as _player
        _player.cprint = quiet
    except Exception:
        pass


def _make_player(level=1, class_id=None):
    p = Player("Tester", class_id=class_id)
    p.level = level
    # Replay level-up bonuses for levels beyond 1 (rough match to real growth)
    for _ in range(1, level):
        p.max_hp += 20
        p.attack += 3
        p.defense += 2
        try:
            p.apply_class_passive_on_levelup()
        except Exception:
            pass
    p.hp = p.max_hp
    return p


def simulate_incoming(player_level, rotation, samples=2000, seed=42, class_id=None):
    random.seed(seed + rotation + player_level)
    p = _make_player(player_level, class_id=class_id)
    enemy = create_enemy(p.level, rotation=rotation)

    damages = []
    for _ in range(samples):
        attack_type = "physical" if random.random() >= 0.15 else random.choice(["fire", "cold"])
        enemy_damage = random.randint(int(enemy.attack * 0.8), int(enemy.attack * 1.2))
        crit = enemy.check_crit()
        if crit > 1.0:
            enemy_damage = int(enemy_damage * crit)
        d = p.take_damage(
            enemy_damage,
            element=attack_type,
            defense_penetration=getattr(enemy, "penetration", 0.0),
        )
        damages.append(d)
        p.hp = p.max_hp

    return {
        "player_level": player_level,
        "rotation": rotation,
        "enemy_name": enemy.name,
        "enemy_level": enemy.level,
        "enemy_attack": enemy.attack,
        "enemy_defense": enemy.defense,
        "enemy_penetration": getattr(enemy, "penetration", 0.0),
        "samples": samples,
        "avg": statistics.mean(damages),
        "median": statistics.median(damages),
        "min": min(damages),
        "max": max(damages),
        "pct_min1": sum(1 for x in damages if x <= 1) / samples * 100.0,
    }


def simulate_outgoing(player_level, rotation, samples=2000, seed=42, class_id=None):
    random.seed(seed + 1000 + rotation + player_level)
    p = _make_player(player_level, class_id=class_id)
    enemy = create_enemy(p.level, rotation=rotation)

    damages = []
    dodges = 0
    for _ in range(samples):
        if enemy.check_evade():
            dodges += 1
            damages.append(0)
            continue
        damage = random.randint(int(p.get_total_attack() * 0.8), int(p.get_total_attack() * 1.2))
        crit = p.check_crit()
        if crit > 1.0:
            damage = int(damage * crit)
        # Don't mutate enemy HP across samples — compute mitigation only
        actual = max(1, damage - enemy.defense)
        damages.append(actual)

    return {
        "avg": statistics.mean(damages),
        "median": statistics.median(damages),
        "dodge_pct": dodges / samples * 100.0,
        "enemy_def": enemy.defense,
        "player_atk": p.get_total_attack(),
    }


def _player_hit(player, enemy):
    """One player attack; returns damage dealt (0 if dodged)."""
    if enemy.check_evade():
        return 0
    damage = random.randint(int(player.get_total_attack() * 0.8), int(player.get_total_attack() * 1.2))
    crit = player.check_crit()
    if crit > 1.0:
        damage = int(damage * crit)
    return enemy.take_damage(damage)


def simulate_fight(player, enemy, max_rounds=80, potions=0, potion_heal=30):
    """Full auto fight (basic attacks). Optional potions used when HP < 40%."""
    rounds = 0
    potions_left = potions
    while player.is_alive() and enemy.is_alive() and rounds < max_rounds:
        rounds += 1
        # Heal instead of attacking if critically low and potions remain
        if potions_left > 0 and player.hp < player.max_hp * 0.4:
            player.hp = min(player.max_hp, player.hp + potion_heal)
            potions_left -= 1
        else:
            _player_hit(player, enemy)
        if not enemy.is_alive():
            return "win", rounds, player.hp
        if getattr(enemy, "stunned_turns", 0) > 0:
            enemy.stunned_turns -= 1
        else:
            enemy_take_action(enemy, player)
        if not player.is_alive():
            return "loss", rounds, 0
    return "loss", rounds, max(0, player.hp)


def simulate_winrate(player_level, rotation, fights=400, seed=7, class_id=None, potions=0):
    """Win-rate for basic-attack fights (potions=0 by default for strict balance)."""
    random.seed(seed + player_level * 10 + rotation)
    wins = 0
    round_counts = []
    ttk_enemy = []
    ttk_player = []

    for _ in range(fights):
        p = _make_player(player_level, class_id=class_id)
        enemy = create_enemy(p.level, rotation=rotation)
        result, rounds, _ = simulate_fight(p, enemy, potions=potions)
        round_counts.append(rounds)
        if result == "win":
            wins += 1
            ttk_enemy.append(rounds)
        else:
            ttk_player.append(rounds)

    return {
        "win_rate": wins / fights * 100.0,
        "avg_rounds": statistics.mean(round_counts) if round_counts else 0,
        "avg_ttk_win": statistics.mean(ttk_enemy) if ttk_enemy else None,
        "avg_ttk_loss": statistics.mean(ttk_player) if ttk_player else None,
        "fights": fights,
        "potions": potions,
    }


def main():
    _silence_combat_logs()
    print("Combat balance test — damage, TTK, win-rate")
    print("---")

    # Incoming damage grid
    for pl in (1, 3, 5):
        print(f"\n=== Incoming Player L{pl} (naked) ===")
        for r in range(0, 6):
            res = simulate_incoming(pl, r, samples=2000)
            print(
                f"R{r}: {res['enemy_name']} Lv{res['enemy_level']} "
                f"atk={res['enemy_attack']} def={res['enemy_defense']} pen={res['enemy_penetration']:.2f} | "
                f"avg={res['avg']:.2f} med={res['median']} min={res['min']} max={res['max']} "
                f"pct<=1={res['pct_min1']:.1f}%"
            )

    # Outgoing + win-rate checkpoints
    checkpoints = [
        (1, 0, None),
        (1, 0, "warrior"),
        (1, 1, None),
        (3, 2, None),
        (5, 5, None),
    ]
    print("\n=== Outgoing + win-rate checkpoints ===")
    for pl, rot, cid in checkpoints:
        label = cid or "naked"
        out = simulate_outgoing(pl, rot, samples=2000, class_id=cid)
        wr = simulate_winrate(pl, rot, fights=400, class_id=cid)
        ttk_w = f"{wr['avg_ttk_win']:.1f}" if wr["avg_ttk_win"] is not None else "n/a"
        ttk_l = f"{wr['avg_ttk_loss']:.1f}" if wr["avg_ttk_loss"] is not None else "n/a"
        print(
            f"L{pl} R{rot} ({label}): out_avg={out['avg']:.2f} dodge={out['dodge_pct']:.1f}% "
            f"atk={out['player_atk']} vs_def={out['enemy_def']} | "
            f"win={wr['win_rate']:.1f}% rounds={wr['avg_rounds']:.1f} "
            f"ttk_win={ttk_w} ttk_loss={ttk_l}"
        )

    # Target checks: naked L1, basic attacks only
    # R0 is intentionally favours the player; R1 is the first real pressure.
    inc = simulate_incoming(1, 0, samples=3000, seed=99)
    wr0 = simulate_winrate(1, 0, fights=500, seed=99, potions=0)
    wr1 = simulate_winrate(1, 1, fights=500, seed=99, potions=0)
    print("\n=== Target checks (L1 naked, no potions) ===")
    print(f"R0 incoming avg={inc['avg']:.2f} (target ~4-8), pct<=1={inc['pct_min1']:.1f}% (target <25%)")
    print(f"R0 win-rate={wr0['win_rate']:.1f}% (target 70-100%)")
    print(f"R1 win-rate={wr1['win_rate']:.1f}% (target 40-70%)")

    ok = True
    if not (4.0 <= inc["avg"] <= 8.5):
        print("WARN: R0 incoming avg outside 4-8.5")
        ok = False
    if inc["pct_min1"] >= 25.0:
        print("WARN: R0 pct<=1 >= 25%")
        ok = False
    if wr0["win_rate"] < 70.0:
        print("WARN: R0 win-rate < 70%")
        ok = False
    if not (40.0 <= wr1["win_rate"] <= 75.0):
        print("WARN: R1 win-rate outside 40-75%")
        ok = False
    print("RESULT:", "OK" if ok else "NEEDS_TUNE")


if __name__ == "__main__":
    main()
