# Spell: arcane_13934
def cast(caster, target):
    damage = 174
    mana_cost = 87
    element = 'ice'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_13934 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
