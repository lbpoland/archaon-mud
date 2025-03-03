# Spell: expand_cormanthor_spell
def cast(caster, target):
    damage = 113
    mana_cost = 75
    element = 'arcane'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts expand_cormanthor_spell ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
