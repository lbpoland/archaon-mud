# Spell: arcane_79038
description = "A lightning-infused spell from Faerûn's arcane weave."
def cast(caster, target):
    damage = 56
    mana_cost = 64
    element = 'lightning'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts arcane_79038 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for arcane_79038!")
