# Spell: arcane_40183
description = "A fire-infused spell from Faerûn's arcane weave."
def cast(caster, target):
    damage = 93
    mana_cost = 93
    element = 'fire'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts arcane_40183 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for arcane_40183!")
