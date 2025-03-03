# Spell: initialize MUD structure_spell
def cast(caster, target):
    damage = 178
    range = 21
    mana_cost = 100
    cooldown = 4
    element = 'divine'
    school = 'transmutation'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        caster.cooldowns['initialize MUD structure_spell'] = cooldown
        print(f"{caster.name} casts initialize MUD structure_spell ({element}, {school}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for initialize MUD structure_spell!")
