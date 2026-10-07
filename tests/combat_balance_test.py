import random
import statistics
from player import Player
from combat import create_enemy


def simulate(player_level, rotation, samples=2000, seed=42):
    random.seed(seed + rotation + player_level)
    p = Player("Tester")
    p.level = player_level
    p.hp = p.max_hp

    enemy = create_enemy(p.level, rotation=rotation)

    damages = []
    for _ in range(samples):
        attack_type = 'physical' if random.random() >= 0.15 else random.choice(['fire', 'cold'])
        enemy_damage = random.randint(int(enemy.attack * 0.8), int(enemy.attack * 1.2))
        d = p.take_damage(enemy_damage, element=attack_type, defense_penetration=getattr(enemy, 'penetration', 0.0))
        damages.append(d)
        p.hp = p.max_hp

    return {
        'player_level': player_level,
        'rotation': rotation,
        'enemy_name': enemy.name,
        'enemy_level': enemy.level,
        'enemy_attack': enemy.attack,
        'enemy_defense': enemy.defense,
        'enemy_penetration': getattr(enemy, 'penetration', 0.0),
        'samples': samples,
        'avg': statistics.mean(damages),
        'median': statistics.median(damages),
        'min': min(damages),
        'max': max(damages),
        'pct_min1': sum(1 for x in damages if x <= 1) / samples * 100.0,
    }


def main():
    player_levels = [1, 3, 5]
    rotations = list(range(0, 6))
    samples = 2000

    print("Combat balance test — average damage per enemy attack")
    print("Samples per cell:", samples)
    print("PlayerLevels:", player_levels)
    print("Rotations:", rotations)
    print("---")

    for pl in player_levels:
        print(f"\n=== Player level {pl} ===")
        for r in rotations:
            res = simulate(pl, r, samples=samples)
            print(
                f"R{r}: Enemy {res['enemy_name']} (Lv{res['enemy_level']}) atk={res['enemy_attack']} def={res['enemy_defense']} pen={res['enemy_penetration']:.2f} | "
                f"avg={res['avg']:.2f} med={res['median']} min={res['min']} max={res['max']} pct<=1={res['pct_min1']:.1f}%"
            )


if __name__ == '__main__':
    main()
