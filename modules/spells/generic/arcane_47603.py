# Spell: arcane_47603
description = "A ice-infused spell from Faerûn's arcane weave."
def cast(caster, target):
    damage = 181
    mana_cost = 83
    element = 'ice'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts arcane_47603 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for arcane_47603!")
