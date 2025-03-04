# Spell: fireball
description = "A fire-infused spell from Faerûn’s arcane weave."
def cast(caster, target):
    damage = 181
    mana_cost = 24
    element = 'fire'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts fireball ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for fireball!")
