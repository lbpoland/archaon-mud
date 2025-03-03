# Spell: arcane_33598
def cast(caster, target):
    damage = 84
    mana_cost = 54
    element = 'ice'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_33598 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
