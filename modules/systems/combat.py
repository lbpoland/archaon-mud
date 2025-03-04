# Combat System - D&D 5e with Discworld Flair
import random

class Combatant:
    def __init__(self, name, hp, ac, align):
        self.name = name
        self.hp = hp
        self.ac = ac
        self.align = align

def roll_d20():
    return random.randint(1, 20)

def fight(attacker, defender):
    attack_roll = roll_d20() + (5 if attacker.align > 0 else 0)
    if attack_roll >= defender.ac:
        damage = random.randint(5, 15)
        defender.hp -= damage
        print(f"{attacker.name} hits {defender.name} for {damage} damage!")
    else:
        print(f"{attacker.name} misses {defender.name}!")
