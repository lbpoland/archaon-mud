# Spell: fireball
def cast(caster, target):
    damage = 79
    mana_cost = 38
    element = 'fire'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{caster.name} casts fireball ({element}) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana!")

# Optimized by Azuth
def optimize():
    print('Spell optimized!')

# Enhanced by Selune
def lunar_boost():
    print('Lunar boost applied!')
