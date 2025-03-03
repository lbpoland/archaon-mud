# Spell: initialize MUD structure_spell
def cast(caster, target):
    damage = 51
    mana_cost = 43
    element = 'arcane'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts initialize MUD structure_spell ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
