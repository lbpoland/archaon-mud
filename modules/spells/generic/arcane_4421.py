# Spell: arcane_4421
def cast(caster, target):
    damage = 146
    mana_cost = 20
    element = 'fire'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_4421 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
