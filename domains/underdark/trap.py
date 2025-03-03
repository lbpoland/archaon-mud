# Trap at underdark
def trigger(player):
    damage = 86
    stealth = 22
    trap_type = 'web'
    trigger_type = 'magic'
    if player.perception < stealth:
        print(f"{player.name} triggers a {trigger_type} {trap_type} trap at underdark for {damage} damage!")
    else:
        print(f"{player.name} detects and avoids a {trap_type} trap at underdark!")
