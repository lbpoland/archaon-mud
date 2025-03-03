# Spell: arcane_58585
def cast(caster, target):
    damage = 131
    mana_cost = 50
    element = 'lightning'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_58585 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
