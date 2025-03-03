# Spell: arcane_74305
description = "A fire-infused spell from Faerûn's arcane weave."
def cast(caster, target):
    damage = 180
    mana_cost = 77
    element = 'fire'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts arcane_74305 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for arcane_74305!")
