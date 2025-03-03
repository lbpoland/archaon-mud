# Spell: fireball
def cast(caster, target):
    damage = 199
    range = 63
    mana_cost = 32
    cooldown = 9
    element = 'shadow'
    school = 'illusion'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        caster.cooldowns['fireball'] = cooldown
        print(f"{caster.name} casts fireball ({element}, {school}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for fireball!")
# Enhanced by Selune
def lunar_effect(caster):
    boost = 70
    effect = 'boost'
    duration = 13
    print(f"Selune enhances fireball with {effect} for {boost} over {duration} seconds!")
# Optimized by Azuth
def optimize_cast(caster):
    mana_reduction = 41
    cast_time = -4
    efficiency = 25
    print(f"Azuth optimizes fireball: -{mana_reduction} mana, {cast_time}s cast time, +{efficiency}% efficiency!")
