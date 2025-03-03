# Spell: arcane_5543
def cast(caster, target):
    damage = 129
    mana_cost = 94
    element = 'fire'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_5543 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
