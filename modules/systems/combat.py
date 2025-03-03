# Combat System
def fight(attacker, defender):
    damage = random.randint(10, 50)
    defender.hp -= damage
    print(f"{attacker.name} hits {defender.name} for {damage} damage!")
