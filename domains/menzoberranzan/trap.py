# Trap at menzoberranzan
def trigger(player):
    damage = 86
    stealth = 23
    trap_type = 'illusion'
    trigger_type = 'touch'
    if player.perception < stealth:
        print(f"{player.name} triggers a {trigger_type} {trap_type} trap at menzoberranzan for {damage} damage!")
    else:
        print(f"{player.name} detects and avoids a {trap_type} trap at menzoberranzan!")
