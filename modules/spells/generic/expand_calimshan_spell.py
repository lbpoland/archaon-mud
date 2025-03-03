# Spell: expand_calimshan_spell
def cast(caster, target):
    damage = 124
    mana_cost = 21
    element = 'ice'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts expand_calimshan_spell ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
