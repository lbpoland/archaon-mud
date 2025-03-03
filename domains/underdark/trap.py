# Trap at underdark
def trigger(player):
    damage = 146
    stealth = 8
    trap_type = 'illusion'
    trigger_type = 'touch'
    if player.perception < stealth:
        print(f"{player.name} triggers a {trigger_type} {trap_type} trap at underdark for {damage} damage!")
    else:
        print(f"{player.name} detects and avoids a {trap_type} trap at underdark!")
