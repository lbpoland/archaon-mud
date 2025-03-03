# Spell: arcane_88859
description = "A arcane-infused spell from Faerûn's arcane weave."
def cast(caster, target):
    damage = 130
    mana_cost = 61
    element = 'arcane'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts arcane_88859 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for arcane_88859!")
