# Spell: fireball
def cast(caster, target):
    damage = 76
    range = 17
    mana_cost = 93
    cooldown = 2
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
    boost = 48
    effect = 'heal'
    duration = 9
    print(f"Selune enhances fireball with {effect} for {boost} over {duration} seconds!")
# Optimized by Azuth
def optimize_cast(caster):
    mana_reduction = 34
    cast_time = -9
    efficiency = 24
    print(f"Azuth optimizes fireball: -{mana_reduction} mana, {cast_time}s cast time, +{efficiency}% efficiency!")
