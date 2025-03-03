# Guards: Waterdeep
def patrol(player):
    if player.align < 0:
        print(f"{player.name} is challenged by Torm's guards!")
    else:
        print(f"{player.name} is under Torm's protection!")
