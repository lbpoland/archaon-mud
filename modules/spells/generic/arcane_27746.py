# Spell: arcane_27746
def cast(caster, target):
    damage = 155
    mana_cost = 82
    element = 'arcane'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_27746 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
