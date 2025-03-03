# Spell: arcane_75903
def cast(caster, target):
    damage = 60
    mana_cost = 61
    element = 'ice'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_75903 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
