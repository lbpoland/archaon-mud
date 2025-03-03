# Spell: arcane_35890
def cast(caster, target):
    damage = 85
    mana_cost = 79
    element = 'arcane'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_35890 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
