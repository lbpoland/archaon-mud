# Spell: expand_icewind_dale_spell
def cast(caster, target):
    damage = 78
    mana_cost = 80
    element = 'lightning'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts expand_icewind_dale_spell ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")
