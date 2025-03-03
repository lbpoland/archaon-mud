# Spell: initialize MUD structure_spell
def cast(caster, target):
    damage = 136
    range = 80
    mana_cost = 31
    cooldown = 9
    element = 'divine'
    school = 'necromancy'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        caster.cooldowns['initialize MUD structure_spell'] = cooldown
        print(f"{caster.name} casts initialize MUD structure_spell ({element}, {school}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for initialize MUD structure_spell!")
