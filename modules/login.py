# login.py - Login and character creation system
import asyncio
import random

# ASCII art for welcome screen
WELCOME_ART = """
   _____ ______ ______ ______   ______ ______ ______ ____  
  /     |  ___ |  ___ |  ___ \ /     |  ___ |  ___ |  _ \ 
 |  ☼   | |_  | |_  | |_  | |  ☼   | |_  | |_  | |_) |
 |  ☾   |  _| |  _| |  _| | |  ☾   |  _| |  _| |  _ < 
  \     | |___| |   | |   | |\     | |   | |   | |_) |
   \____|______|_|   |_|   |_|_____|_|   |_|   |____/
   Welcome to Faerûn’s Forgotten Legacy - Powered by Mystra’s Weave
"""

# Races from Forgotten Realms (13 as per your earlier input)
RACES = {
    "human": {
        "desc": "Versatile and ambitious, humans thrive across Faerûn.",
        "bonuses": {"str": 1, "dex": 1, "int": 1, "con": 1, "wis": 1},
        "negatives": {},
        "zones": ["Waterdeep - Market Square", "Baldur’s Gate - Docks", "Suzail - Royal Plaza"]
    },
    "elf": {
        "desc": "Graceful and long-lived, elves wield ancient magic.",
        "bonuses": {"dex": 2, "int": 1},
        "negatives": {"con": -1},
        "zones": ["Evermeet - Crystal Spire", "Cormanthor - Elven Court", "High Forest - Starlit Glade"]
    },
    "dwarf": {
        "desc": "Stout and hardy, dwarves forge their fate in stone.",
        "bonuses": {"con": 2, "str": 1},
        "negatives": {"dex": -1},
        "zones": ["Mithral Hall - Forgeheart", "Citadel Adbar - Iron Gate", "Mirabar - Stone Anvil"]
    },
    # Add 10 more (e.g., gnome, halfling, tiefling, etc.) - abbreviated here
}

async def handle_login(reader, writer):
    from modules.skills import Player
    writer.write(f"{WELCOME_ART}\n".encode())
    writer.write("Options: (1) Login (2) New Player (3) Guest (4) Who’s On\n> ".encode())
    await writer.drain()
    choice = (await reader.read(100)).decode().strip()

    if choice == "1":  # Login
        writer.write("Enter your name: ".encode())
        await writer.drain()
        name = (await reader.read(100)).decode().strip()
        writer.write("Enter your password: ".encode())
        await writer.drain()
        password = (await reader.read(100)).decode().strip()
        # Placeholder validation (load from /players/)
        if name and password:  # Assume valid for now
            player = Player(name, deity="Mystra")
            writer.write(f"Welcome back, {name}, blessed by Mystra’s weave!\n".encode())
            return player
        writer.write("Invalid credentials!\n".encode())
        return None

    elif choice == "2":  # New Player
        writer.write("Choose your name: ".encode())
        await writer.drain()
        name = (await reader.read(100)).decode().strip()
        writer.write("Create a password: ".encode())
        await writer.drain()
        password = (await reader.read(100)).decode().strip()
        writer.write("Gender (m/f/n): ".encode())
        await writer.drain()
        gender = (await reader.read(100)).decode().strip().lower()[0]

        # Terminal settings
        writer.write("Terminal type (ansi/vt100/plain): ".encode())
        await writer.drain()
        term = (await reader.read(100)).decode().strip()
        writer.write("Colors (on/off): ".encode())
        await writer.drain()
        colors = (await reader.read(100)).decode().strip() == "on"
        writer.write("MXP/MCCP (on/off): ".encode())
        await writer.drain()
        mxp = (await reader.read(100)).decode().strip() == "on"

        # Race selection
        race_list = "\n".join(f"{i+1}. {race.capitalize()}" for i, race in enumerate(RACES.keys()))
        writer.write(f"\nChoose your race:\n{race_list}\n> ".encode())
        await writer.drain()
        race_choice = int((await reader.read(100)).decode().strip()) - 1
        race = list(RACES.keys())[race_choice]
        writer.write(f"More info on {race}? (y/n): ".encode())
        await writer.drain()
        if (await reader.read(100)).decode().strip().lower() == "y":
            r = RACES[race]
            info = f"{race.capitalize()}:\n{r['desc']}\nBonuses: {r['bonuses']}\nNegatives: {r['negatives']}\n"
            writer.write(f"{info}".encode())
            await writer.drain()

        # Starting zone
        zones = "\n".join(f"{i+1}. {zone}" for i, zone in enumerate(RACES[race]["zones"]))
        writer.write(f"\nStarting zones:\n{zones}\n> ".encode())
        await writer.drain()
        zone_choice = int((await reader.read(100)).decode().strip()) - 1
        start_zone = RACES[race]["zones"][zone_choice].split(" - ")[1]

        # Creation narrative
        narrative = f"\nThe Weave of Mystra pulses as {name}, a {gender} {race}, steps into Faerûn...\n"
        if race == "human":
            narrative += "Born amidst the clamor of mortal ambition, you rise from humble origins, your destiny unwritten.\n"
        elif race == "elf":
            narrative += "Emerging from the silvery glades of elven eternity, your eyes gleam with ancient wisdom.\n"
        elif race == "dwarf":
            narrative += "Forged in the fires of the deep earth, your hammer echoes with dwarven resolve.\n"
        narrative += f"You awaken in {start_zone}, the air alive with possibility. Mystra’s blessing guides your path...\n"
        writer.write(narrative.encode())
        await writer.drain()

        player = Player(name, deity="Mystra")
        player.stats.update(RACES[race]["bonuses"])
        for stat, penalty in RACES[race]["negatives"].items():
            player.stats[stat] += penalty
        # Save to /players/{name}.plr - placeholder
        return player

    elif choice == "3":  # Guest
        player = Player("Guest", deity="Selûne")
        writer.write("Welcome, wandering soul, as a guest of Faerûn!\n".encode())
        return player

    elif choice == "4":  # Who’s On
        who = "Currently on: " + ", ".join(p.name for p in players.values()) if players else "No one."
        writer.write(f"{who}\n".encode())
        return None

    writer.write("Invalid choice!\n".encode())
    return None

players = {}  # Global for who’s on
