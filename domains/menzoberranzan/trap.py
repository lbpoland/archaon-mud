# Trap at menzoberranzan
def trigger(player):
    damage = 135
    stealth = 13
    trap_type = 'web'
    trigger_type = 'pressure'
    if player.perception < stealth:
        print(f"{player.name} triggers a {trigger_type} {trap_type} trap at menzoberranzan for {damage} damage!")
    else:
        print(f"{player.name} detects and avoids a {trap_type} trap at menzoberranzan!")
