# Spell: arcane_73513
def cast(caster, target):
    damage = 155
    mana_cost = 81
    element = 'ice'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_73513 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
