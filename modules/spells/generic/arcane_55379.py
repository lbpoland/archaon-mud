# Spell: arcane_55379
def cast(caster, target):
    damage = 144
    mana_cost = 23
    element = 'arcane'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_55379 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
