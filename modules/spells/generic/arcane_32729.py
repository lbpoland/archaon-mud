# Spell: arcane_32729
description = "A arcane-infused spell from Faerûn's arcane weave."
def cast(caster, target):
    damage = 198
    mana_cost = 52
    element = 'arcane'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts arcane_32729 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for arcane_32729!")
