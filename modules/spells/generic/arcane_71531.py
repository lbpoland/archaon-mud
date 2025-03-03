# Spell: arcane_71531
def cast(caster, target):
    damage = 96
    mana_cost = 50
    element = 'lightning'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_71531 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
