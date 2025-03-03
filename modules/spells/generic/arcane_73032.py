# Spell: arcane_73032
def cast(caster, target):
    damage = 158
    mana_cost = 40
    element = 'lightning'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts arcane_73032 ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
