# Spell: initialize MUD structure_spell
def cast(caster, target):
    damage = 190
    range = 141
    mana_cost = 99
    cooldown = 6
    element = 'fire'
    school = 'abjuration'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        caster.cooldowns['initialize MUD structure_spell'] = cooldown
        print(f"{caster.name} casts initialize MUD structure_spell ({element}, {school}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for initialize MUD structure_spell!")
