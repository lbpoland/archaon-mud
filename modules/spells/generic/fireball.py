# Spell: fireball
def cast(caster, target):
    damage = 129
    range = 140
    mana_cost = 29
    cooldown = 3
    element = 'divine'
    school = 'abjuration'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        caster.cooldowns['fireball'] = cooldown
        print(f"{caster.name} casts fireball ({element}, {school}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for fireball!")
# Enhanced by Selune
def lunar_effect(caster):
    boost = 47
    effect = 'boost'
    duration = 17
    print(f"Selune enhances fireball with {effect} for {boost} over {duration} seconds!")
# Optimized by Azuth
def optimize_cast(caster):
    mana_reduction = 39
    cast_time = -4
    efficiency = 29
    print(f"Azuth optimizes fireball: -{mana_reduction} mana, {cast_time}s cast time, +{efficiency}% efficiency!")
