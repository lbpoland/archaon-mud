# Spell: arcane_2527
def cast(caster, target):
    damage = 54
    mana_cost = 21
    element = 'fire'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_2527 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
