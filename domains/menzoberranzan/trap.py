# Trap at menzoberranzan
def trigger(player):
    damage = 76
    stealth = 17
    trap_type = 'poison'
    trigger_type = 'proximity'
    if player.perception < stealth:
        print(f"{player.name} triggers a {trigger_type} {trap_type} trap at menzoberranzan for {damage} damage!")
    else:
        print(f"{player.name} detects and avoids a {trap_type} trap at menzoberranzan!")
