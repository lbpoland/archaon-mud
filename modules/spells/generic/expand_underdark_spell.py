# Spell: expand_underdark_spell
def cast(caster, target):
    damage = 94
    mana_cost = 90
    element = 'arcane'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts expand_underdark_spell ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
