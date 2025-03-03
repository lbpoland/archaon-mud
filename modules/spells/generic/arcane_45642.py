# Spell: arcane_45642
def cast(caster, target):
    damage = 140
    mana_cost = 46
    element = 'fire'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_45642 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
