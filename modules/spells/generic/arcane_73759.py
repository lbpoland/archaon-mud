# Spell: arcane_73759
description = "A lightning-infused spell from Faerûn's arcane weave."
def cast(caster, target):
    damage = 91
    mana_cost = 63
    element = 'lightning'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        target.hp -= damage
        print(f"{caster.name} casts arcane_73759 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for arcane_73759!")
