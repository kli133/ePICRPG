"""Skill definitions and scaling rules.

Each skill has:
- id: key
- name, description
- base_power: multiplier or flat used by use_ability
- stat: which player stat scales the skill ('attack','intellect','defense', etc.)
- stat_scale: additional multiplier per stat point
- max_level: maximum upgrade level
- base_cooldown: default cooldown for the ability
- learn_cost: skill points required to learn (default 1)
"""

SKILLS = {
    'warrior_rage': {
        'name': 'Удар ярости',
        'description': 'Мощный удар: усиливается с уровнем навыка и атакой героя, частично игнорирует защиту врага.',
        'base_multiplier': 1.8,
        'stat': 'attack',
        'stat_scale': 0.05,
        'max_level': 5,
        'base_cooldown': 3,
        'learn_cost': 1,
    },
    'mage_lightning': {
        'name': 'Молния',
        'description': 'Молния наносит урон, увеличивающийся с интеллектом, и оглушает врага.',
        'base_multiplier': 1.5,
        'stat': 'intellect',
        'stat_scale': 0.08,
        'max_level': 5,
        'base_cooldown': 4,
        'learn_cost': 1,
    },
    'rogue_evade': {
        'name': 'Уклонение',
        'description': 'Уклониться от следующей атаки; шанс уклонения растёт с уровнем навыка.',
        'base_multiplier': 0.0,
        'stat': 'dexterity',
        'stat_scale': 0.0,
        'max_level': 5,
        'base_cooldown': 3,
        'learn_cost': 1,
    }
}


def get_skill(skill_id):
    return SKILLS.get(skill_id)
