# Trap: Underdark
def trigger(player):
    damage = 63
    trap_type = 'web'
    if random.random() > 0.3:  # 70% chance to trigger
        player.hp -= damage
        print(f"{player.name} triggers a {trap_type} trap for {damage} damage!")
    else:
        print(f"{player.name} narrowly avoids a {trap_type} trap!")
