# Spell: expand_sword_coast_spell
def cast(caster, target):
    damage = 156
    mana_cost = 27
    element = 'lightning'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts expand_sword_coast_spell ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
