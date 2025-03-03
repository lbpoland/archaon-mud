# Spell: arcane_29769
description = "A ice-infused spell from Faerûn's arcane weave."
def cast(caster, target):
    damage = 56
    mana_cost = 78
    element = 'ice'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts arcane_29769 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for arcane_29769!")
