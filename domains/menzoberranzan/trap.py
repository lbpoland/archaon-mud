# Trap at menzoberranzan
def trigger(player):
    damage = 77
    stealth = 11
    trap_type = 'poison'
    trigger_type = 'touch'
    if player.perception < stealth:
        print(f"{player.name} triggers a {trigger_type} {trap_type} trap at menzoberranzan for {damage} damage!")
    else:
        print(f"{player.name} detects and avoids a {trap_type} trap at menzoberranzan!")
