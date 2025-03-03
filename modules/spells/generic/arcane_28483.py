# Spell: arcane_28483
description = "A arcane-infused spell from Faerûn's arcane weave."
def cast(caster, target):
    damage = 199
    mana_cost = 96
    element = 'arcane'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts arcane_28483 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for arcane_28483!")
