# Spell: fireball
def cast(caster, target):
    damage = 171
    range = 107
    mana_cost = 68
    cooldown = 3
    element = 'arcane'
    school = 'evocation'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        caster.cooldowns['fireball'] = cooldown
        print(f"{caster.name} casts fireball ({element}, {school}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for fireball!")
# Enhanced by Selune
def lunar_effect(caster):
    boost = 80
    effect = 'shield'
    duration = 12
    print(f"Selune enhances fireball with {effect} for {boost} over {duration} seconds!")
# Optimized by Azuth
def optimize_cast(caster):
    mana_reduction = 18
    cast_time = -9
    efficiency = 22
    print(f"Azuth optimizes fireball: -{mana_reduction} mana, {cast_time}s cast time, +{efficiency}% efficiency!")
