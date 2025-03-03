# Spell: fireball
def cast(caster, target):
    damage = 173
    range = 109
    mana_cost = 89
    cooldown = 5
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        caster.cooldowns['fireball'] = cooldown
        print(f"{caster.name} casts fireball (arcane, conjuration) on {target.name} for {damage} damage!")
    else:
        print(f"{caster.name} lacks mana for fireball!")
