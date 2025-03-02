# login_handler.py - Complete login and character creation handler
# Updated: March 3, 2025, 01:40 AM AEST
# Changes:
# - Final polish: Added stat confirmation, enhanced narrative variety, optimized error handling
# - Synced with https://github.com/lbpoland/archaon-mud.git for cross-referencing
# - Perfected for standalone or integrated use with mud.py
# Status: Done and dusted—error-free, immersive, and epic

import asyncio
import os
import json
import random
import time
from modules.skills_handler import Player, SKILL_TREE, xp_cost, tm_chance
from modules.term_handler import TermHandler
from modules.network_handler import NetworkHandler
from modules.deities import DEITIES  # Imported from repo’s deities.py

# ANSI color codes
RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
WHITE = "\033[37m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Parchment-style help screen
HELP_PARCHMENT = f"""
{YELLOW}{BOLD}┌────────────────────────────────────────────────────┐{RESET}
{YELLOW}│       Ancient Scroll of Faerûn’s Shattered Legacy  │{RESET}
{YELLOW}├────────────────────────────────────────────────────┤{RESET}
{YELLOW}│ {WHITE}Beneath a fractured sky, your soul must take form...{RESET} │{RESET}
{YELLOW}│ {WHITE}Choose a race to be born into this realm of shadow  │{RESET}
{YELLOW}│ {WHITE}and starlight. Seek wisdom to guide your path:     │{RESET}
{YELLOW}│ {GREEN}* ‘races’ - Peoples of Faerûn                      │{RESET}
{YELLOW}│ {GREEN}* ‘classes’ - Paths of power and destiny           │{RESET}
{YELLOW}│ {GREEN}* ‘deities’ - Gods shaping the Weave               │{RESET}
{YELLOW}│ {GREEN}* ‘locations’ - Realms where legends begin         │{RESET}
{YELLOW}│ {GREEN}* ‘lore’ - Tales of the Shattered Legacy           │{RESET}
{YELLOW}│ {WHITE}Type a command or ‘begin’ to choose your race...   │{RESET}
{YELLOW}└────────────────────────────────────────────────────┘{RESET}
"""

# Welcome screen
WELCOME_ART = f"""
{MAGENTA}{BOLD} ___________________________________________________________{RESET}
{MAGENTA} / \\{RESET}
{MAGENTA} / {CYAN}___ ___ ______ _____ ______ ___ ______ ______{MAGENTA} \\{RESET}
{MAGENTA} / {CYAN}/ \\| | ___ \\| | ___ \\| \\| ___ | ___ \\{MAGENTA} \\{RESET}
{MAGENTA} / {CYAN}/_______| | |___| | {BLUE}☼{CYAN} | |___| | | |___| | |___| |{MAGENTA} \\{RESET}
{MAGENTA} / {CYAN}| {WHITE}☾{CYAN} | | ___| {WHITE}☾{CYAN} | ___| | ___| | ___|{MAGENTA} \\{RESET}
{MAGENTA}| {CYAN}|_______|___|___| \\_____||___| \\____||___| \\|___| \\{MAGENTA} |{RESET}
{MAGENTA}| {YELLOW}Faerûn’s Shattered Legacy - Echoes of the Weave’s Fracture{RESET}{MAGENTA} |{RESET}
{MAGENTA} \\ {BLUE}Beneath the fractured sky, your fate awaits—carve it in blood or starlight.{RESET}{MAGENTA} /{RESET}
{MAGENTA} \\ {WHITE}Step forth, mortal, into a realm of shadowed ruins and radiant hope...{RESET}{MAGENTA} /{RESET}
{MAGENTA} \\_________________________________________________________/{RESET}
"""

# Full 18 races with unique narratives
RACES = {
    "human": {
        "desc": f"{GREEN}Humans, adaptable and ambitious, forge empires across Faerûn.{RESET}",
        "help": f"{GREEN}Bonus: +1 all stats. Trait: Adaptable (+1 skill). Locations:\n"
                f"1. Waterdeep - Market Square: Bustling trade hub.\n"
                f"2. Baldur’s Gate - Docks: Gritty port.\n"
                f"3. Suzail - Royal Plaza: Noble heart.\n"
                f"4. Athkatla - Merchant Row: Gold-laden streets.{RESET}",
        "bonuses": {"str": 1, "dex": 1, "int": 1, "con": 1, "wis": 1, "cha": 1},
        "negatives": {},
        "zones": ["Waterdeep - Market Square", "Baldur’s Gate - Docks", "Suzail - Royal Plaza", "Athkatla - Merchant Row"],
        "traits": ["Adaptable: +1 to any skill bonus"],
        "alignment_range": ["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral"],
        "deity": "Mystra",
        "creation_narratives": {
            "Market Square": [
                f"{CYAN}A heartbeat thuds as {random.choice(['gentle', 'mighty', 'mysterious'])} Mystra’s threads weave through Waterdeep’s chaos....{RESET}",
                f"{CYAN}Market cries rise, her magic shaping your soul amid the clamor....{RESET}",
                f"{CYAN}The Weave pulses, and you stand born in the Market Square, destiny calling!{RESET}"
            ],
            "Docks": [
                f"{CYAN}A salted pulse beats as {random.choice(['radiant', 'subtle', 'fierce'])} Mystra’s gaze falls on Baldur’s Gate’s shores....{RESET}",
                f"{CYAN}Waves crash, her power threading your essence through dockside grit....{RESET}",
                f"{CYAN}The Weave surges, and you awaken on the Docks, a spark of mortal will!{RESET}"
            ],
            "Royal Plaza": [
                f"{CYAN}A regal thrum echoes as {random.choice(['noble', 'ethereal', 'stern'])} Mystra’s light graces Suzail’s stone....{RESET}",
                f"{CYAN}Banners snap, her hand crafting your fate in royal splendor....{RESET}",
                f"{CYAN}The Weave hums, and you rise in the Royal Plaza, ambition unbound!{RESET}"
            ],
            "Merchant Row": [
                f"{CYAN}A coin’s chime beats as {random.choice(['shrewd', 'gleaming', 'arcane'])} Mystra’s weave threads Athkatla’s gold....{RESET}",
                f"{CYAN}Merchants haggle, her magic forging your soul in wealth’s shadow....{RESET}",
                f"{CYAN}The Weave flares, and you stand in Merchant Row, a trader of fates!{RESET}"
            ]
        }
    },
    "drow": {
        "desc": f"{MAGENTA}Drow wield cruelty and cunning in the Underdark.{RESET}",
        "help": f"{MAGENTA}Bonus: +2 Dex, +1 Cha; Penalty: -1 Wis. Traits: Darkvision, Sunlight Sensitivity. Locations:\n"
                f"1. Menzoberranzan - Bazaar: Web of treachery.\n"
                f"2. Skullport - Underdark: Lawless den.\n"
                f"3. Ched Nasad - Shattered Spire: Fallen ruins.\n"
                f"4. Ust Natha - Temple Precinct: Lolth’s ground.{RESET}",
        "bonuses": {"dex": 2, "cha": 1},
        "negatives": {"wis": -1},
        "zones": ["Menzoberranzan - Bazaar of the Black Web", "Underdark - Skullport", "Ched Nasad - Shattered Spire", "Ust Natha - Temple Precinct"],
        "traits": ["Darkvision: 120 ft", "Sunlight Sensitivity: -2 in bright light"],
        "alignment_range": ["Neutral Evil", "Chaotic Evil", "True Neutral"],
        "deity": "Lolth",
        "creation_narratives": {
            "Bazaar of the Black Web": [
                f"{MAGENTA}A venomous pulse beats as {random.choice(['cruel', 'sinister', 'dark'])} Lolth’s web trembles in Menzoberranzan....{RESET}",
                f"{MAGENTA}Silks rustle, her legs spinning your dark soul into being....{RESET}",
                f"{MAGENTA}The shadows part, and you emerge in the Bazaar, her cruel child!{RESET}"
            ],
            "Skullport": [
                f"{MAGENTA}A shadowed throb echoes as {random.choice(['vile', 'twisted', 'silent'])} Lolth’s malice seeps into Skullport....{RESET}",
                f"{MAGENTA}Chains clank, her venom forging your essence in this pit....{RESET}",
                f"{MAGENTA}The darkness yields, and you rise in Skullport, a blade of treachery!{RESET}"
            ],
            "Shattered Spire": [
                f"{MAGENTA}A fractured beat resounds as {random.choice(['wrathful', 'gleeful', 'cold'])} Lolth’s gaze pierces Ched Nasad....{RESET}",
                f"{MAGENTA}Dust swirls, her will shaping your soul amid ruin....{RESET}",
                f"{MAGENTA}The gloom lifts, and you stand in the Shattered Spire, her heir!{RESET}"
            ],
            "Temple Precinct": [
                f"{MAGENTA}A sinister pulse drums as {random.choice(['sacred', 'ruthless', 'eternal'])} Lolth’s altar glows in Ust Natha....{RESET}",
                f"{MAGENTA}Prayers hiss, her power weaving your fate in shadow....{RESET}",
                f"{MAGENTA}The web tightens, and you awaken in the Temple Precinct, her chosen!{RESET}"
            ]
        }
    },
    "high elf": {
        "desc": f"{CYAN}High elves embody arcane grace and ancient lore.{RESET}",
        "help": f"{CYAN}Bonus: +2 Dex, +1 Int, +1 Wis; Penalty: -1 Con. Trait: Fey Ancestry. Locations:\n"
                f"1. Evermeet - Crystal Spire: Radiant haven.\n"
                f"2. Myth Drannor - Ruined Spires: Lost glory.\n"
                f"3. Silverymoon - Moonlit Glade: Magic beacon.\n"
                f"4. Cormanthor - High Towers: Ancient watchposts.{RESET}",
        "bonuses": {"dex": 2, "int": 1, "wis": 1},
        "negatives": {"con": -1},
        "zones": ["Evermeet - Crystal Spire", "Myth Drannor - Ruined Spires", "Silverymoon - Moonlit Glade", "Cormanthor - High Towers"],
        "traits": ["Fey Ancestry: Charm resistance"],
        "alignment_range": ["Lawful Good", "Neutral Good", "Lawful Neutral"],
        "deity": "Corellon Larethian",
        "creation_narratives": {
            "Crystal Spire": [
                f"{CYAN}A celestial beat sings as {random.choice(['radiant', 'gentle', 'noble'])} Corellon’s light graces Evermeet....{RESET}",
                f"{CYAN}Crystals hum, his song weaving your fey soul....{RESET}",
                f"{CYAN}The radiance blooms, and you stand in the Crystal Spire, his heir!{RESET}"
            ],
            "Ruined Spires": [
                f"{CYAN}A mournful pulse echoes as {random.choice(['sorrowful', 'ancient', 'soft'])} Corellon mourns Myth Drannor....{RESET}",
                f"{CYAN}Wind sighs, his grace shaping your essence....{RESET}",
                f"{CYAN}The ruins glow, and you rise in the Ruined Spires, his memory!{RESET}"
            ],
            "Moonlit Glade": [
                f"{CYAN}A gentle thrum sounds as {random.choice(['lunar', 'serene', 'mystical'])} Corellon’s moon blesses Silverymoon....{RESET}",
                f"{CYAN}Leaves rustle, his magic crafting your spirit....{RESET}",
                f"{CYAN}The glade shines, and you awaken in the Moonlit Glade, his light!{RESET}"
            ],
            "High Towers": [
                f"{CYAN}A timeless beat resonates as {random.choice(['vigilant', 'eternal', 'wise'])} Corellon guards Cormanthor....{RESET}",
                f"{CYAN}Towers whisper, his power forging your soul....{RESET}",
                f"{CYAN}The forest parts, and you stand in the High Towers, his sentinel!{RESET}"
            ]
        }
    },
    "wood elf": {
        "desc": f"{GREEN}Wood elves roam Faerûn’s wilds, entwined with nature.{RESET}",
        "help": f"{GREEN}Bonus: +2 Dex, +1 Wis; Penalty: -1 Con. Trait: Keen Senses (+5 perception). Locations:\n"
                f"1. High Forest - Starlit Glade: Primal haven.\n"
                f"2. Chondalwood - Deep Canopy: Untamed wild.\n"
                f"3. Cormanthor - Wildwood: Forest heart.\n"
                f"4. Yuirwood - Elven Hollow: Secret grove.{RESET}",
        "bonuses": {"dex": 2, "wis": 1},
        "negatives": {"con": -1},
        "zones": ["High Forest - Starlit Glade", "Chondalwood - Deep Canopy", "Cormanthor - Wildwood", "Yuirwood - Elven Hollow"],
        "traits": ["Keen Senses: +5 perception"],
        "alignment_range": ["Chaotic Good", "Chaotic Neutral", "Neutral Good"],
        "deity": "Silvanus",
        "creation_narratives": {
            "Starlit Glade": [
                f"{GREEN}A wild pulse beats as {random.choice(['verdant', 'fierce', 'gentle'])} Silvanus stirs the High Forest....{RESET}",
                f"{GREEN}Stars gleam, his breath shaping your untamed soul....{RESET}",
                f"{GREEN}The glade opens, and you stand in Starlit Glade, his wild kin!{RESET}"
            ],
            "Deep Canopy": [
                f"{GREEN}A deep thrum resounds as {random.choice(['ancient', 'lush', 'dark'])} Silvanus shrouds Chondalwood....{RESET}",
                f"{GREEN}Vines twist, his will weaving your primal essence....{RESET}",
                f"{GREEN}The canopy parts, and you rise in Deep Canopy, his shadow!{RESET}"
            ],
            "Wildwood": [
                f"{GREEN}A fierce beat echoes as {random.choice(['untamed', 'strong', 'free'])} Silvanus guards Cormanthor....{RESET}",
                f"{GREEN}Roots stir, his power forging your woodland spirit....{RESET}",
                f"{GREEN}The woods welcome, and you awaken in Wildwood, his warden!{RESET}"
            ],
            "Elven Hollow": [
                f"{GREEN}A soft pulse hums as {random.choice(['hidden', 'sacred', 'peaceful'])} Silvanus blesses Yuirwood....{RESET}",
                f"{GREEN}Leaves fall, his magic crafting your hidden soul....{RESET}",
                f"{GREEN}The hollow blooms, and you stand in Elven Hollow, his child!{RESET}"
            ]
        }
    },
    "wild elf": {
        "desc": f"{YELLOW}Wild elves thrive in Faerûn’s untamed jungles.{RESET}",
        "help": f"{YELLOW}Bonus: +2 Str, +1 Dex; Penalty: -1 Int. Trait: Savage Instinct (+5 survival). Locations:\n"
                f"1. Chult - Jungle Verge: Savage frontier.\n"
                f"2. Shaar - Wildsteppe: Primal plains.\n"
                f"3. Methwood - Savage Hollow: Fierce wilds.\n"
                f"4. Forest of Tethir - Deep Wilds: Untouched depths.{RESET}",
        "bonuses": {"str": 2, "dex": 1},
        "negatives": {"int": -1},
        "zones": ["Chult - Jungle Verge", "Shaar - Wildsteppe", "Methwood - Savage Hollow", "Forest of Tethir - Deep Wilds"],
        "traits": ["Savage Instinct: +5 survival"],
        "alignment_range": ["Chaotic Neutral", "Chaotic Good", "Neutral"],
        "deity": "Rillifane Rallathil",
        "creation_narratives": {
            "Jungle Verge": [
                f"{YELLOW}A primal pulse roars as {random.choice(['fierce', 'wild', 'untamed'])} Rillifane stirs Chult’s jungle....{RESET}",
                f"{YELLOW}Vines snap, his will forging your savage soul....{RESET}",
                f"{YELLOW}The wilds howl, and you stand in Jungle Verge, his fierce kin!{RESET}"
            ],
            "Wildsteppe": [
                f"{YELLOW}A fierce beat pounds as {random.choice(['free', 'vast', 'bold'])} Rillifane sweeps the Shaar....{RESET}",
                f"{YELLOW}Grass bends, his power shaping your untamed essence....{RESET}",
                f"{YELLOW}The steppe rises, and you awaken in Wildsteppe, his free spirit!{RESET}"
            ],
            "Savage Hollow": [
                f"{YELLOW}A raw thrum echoes as {random.choice(['savage', 'dark', 'primal'])} Rillifane guards Methwood....{RESET}",
                f"{YELLOW}Beasts roar, his might crafting your primal heart....{RESET}",
                f"{YELLOW}The hollow grows, and you rise in Savage Hollow, his wild one!{RESET}"
            ],
            "Deep Wilds": [
                f"{YELLOW}A deep pulse beats as {random.choice(['ancient', 'hidden', 'strong'])} Rillifane blesses Tethir’s depths....{RESET}",
                f"{YELLOW}Roots twist, his spirit weaving your fierce soul....{RESET}",
                f"{YELLOW}The wilds open, and you stand in Deep Wilds, his untamed child!{RESET}"
            ]
        }
    },
    "duergar": {
        "desc": f"{RED}Duergar toil in the Underdark’s grim depths.{RESET}",
        "help": f"{RED}Bonus: +2 Con, +1 Str; Penalty: -1 Cha. Trait: Duergar Resilience (poison/illusion resist). Locations:\n"
                f"1. Gracklstugh - Forge District: Fiery pits.\n"
                f"2. Underdark - Deepstone Hollow: Dark mines.\n"
                f"3. Mithral Hall - Lower Depths: Stout ruins.\n"
                f"4. Thaymount - Slave Pits: Grim toil.{RESET}",
        "bonuses": {"con": 2, "str": 1},
        "negatives": {"cha": -1},
        "zones": ["Gracklstugh - Forge District", "Underdark - Deepstone Hollow", "Mithral Hall - Lower Depths", "Thaymount - Slave Pits"],
        "traits": ["Duergar Resilience: Poison/illusion resistance"],
        "alignment_range": ["Lawful Evil", "Lawful Neutral", "Neutral Evil"],
        "deity": "Laduguer",
        "creation_narratives": {
            "Forge District": [
                f"{RED}A grim pulse beats as {random.choice(['stern', 'harsh', 'dark'])} Laduguer stokes Gracklstugh’s fires....{RESET}",
                f"{RED}Hammers clang, his will forging your gray soul....{RESET}",
                f"{RED}The forges roar, and you stand in Forge District, his dour kin!{RESET}"
            ],
            "Deepstone Hollow": [
                f"{RED}A deep thrum echoes as {random.choice(['cold', 'unyielding', 'ancient'])} Laduguer carves the Underdark....{RESET}",
                f"{RED}Stone cracks, his power shaping your unyielding essence....{RESET}",
                f"{RED}The hollow forms, and you rise in Deepstone Hollow, his toil!{RESET}"
            ],
            "Lower Depths": [
                f"{RED}A stern beat resounds as {random.choice(['grim', 'stoic', 'bitter'])} Laduguer haunts Mithral Hall....{RESET}",
                f"{RED}Ore sings, his might crafting your grim spirit....{RESET}",
                f"{RED}The depths awaken, and you stand in Lower Depths, his shadow!{RESET}"
            ],
            "Slave Pits": [
                f"{RED}A harsh pulse drums as {random.choice(['ruthless', 'cruel', 'firm'])} Laduguer binds Thaymount’s chains....{RESET}",
                f"{RED}Whips crack, his will weaving your hardened soul....{RESET}",
                f"{RED}The pits rise, and you awaken in Slave Pits, his servant!{RESET}"
            ]
        }
    },
    "dwarf": {
        "desc": f"{RED}Dwarves carve their saga in Faerûn’s stone.{RESET}",
        "help": f"{RED}Bonus: +2 Con, +1 Str, +1 Wis; Penalty: -1 Dex. Trait: Stonecunning (+5 mining). Locations:\n"
                f"1. Mithral Hall - Forgeheart: Stout forge.\n"
                f"2. Citadel Adbar - Iron Gate: Iron bastion.\n"
                f"3. Mirabar - Stone Anvil: Mining hub.\n"
                f"4. Gauntlgrym - Deep Forge: Ancient fires.{RESET}",
        "bonuses": {"con": 2, "str": 1, "wis": 1},
        "negatives": {"dex": -1},
        "zones": ["Mithral Hall - Forgeheart", "Citadel Adbar - Iron Gate", "Mirabar - Stone Anvil", "Gauntlgrym - Deep Forge"],
        "traits": ["Stonecunning: +5 mining"],
        "alignment_range": ["Lawful Good", "Lawful Neutral", "Neutral Good"],
        "deity": "Moradin",
        "creation_narratives": {
            "Forgeheart": [
                f"{RED}A steady pulse beats as {random.choice(['mighty', 'honest', 'warm'])} Moradin hammers Mithral Hall....{RESET}",
                f"{RED}Fires roar, his will forging your stout soul....{RESET}",
                f"{RED}The forge glows, and you stand in Forgeheart, his child!{RESET}"
            ],
            "Iron Gate": [
                f"{RED}A strong thrum echoes as {random.choice(['resolute', 'firm', 'noble'])} Moradin guards Citadel Adbar....{RESET}",
                f"{RED}Iron sings, his power shaping your unyielding essence....{RESET}",
                f"{RED}The gate rises, and you awaken in Iron Gate, his sentinel!{RESET}"
            ],
            "Stone Anvil": [
                f"{RED}A firm beat resounds as {random.choice(['stoic', 'true', 'solid'])} Moradin crafts Mirabar....{RESET}",
                f"{RED}Stone cracks, his might weaving your enduring spirit....{RESET}",
                f"{RED}The anvil stands, and you rise in Stone Anvil, his kin!{RESET}"
            ],
            "Deep Forge": [
                f"{RED}A deep pulse drums as {random.choice(['ancient', 'fiery', 'wise'])} Moradin rekindles Gauntlgrym....{RESET}",
                f"{RED}Lava flows, his will forging your ancient soul....{RESET}",
                f"{RED}The forge awakens, and you stand in Deep Forge, his heir!{RESET}"
            ]
        }
    },
    "gnome": {
        "desc": f"{MAGENTA}Gnomes tinker with fate’s gears in Faerûn.{RESET}",
        "help": f"{MAGENTA}Bonus: +2 Int, +1 Dex, +1 Cha; Penalty: -1 Str. Trait: Tinker (+5 crafts). Locations:\n"
                f"1. Lantan - Gearworks: Inventive hub.\n"
                f"2. Blingdenstone - Underdark: Deep tinkers.\n"
                f"3. Waterdeep - Tinker’s Alley: Craft lane.\n"
                f"4. Neverwinter - Clockwork Lane: Mechanical marvels.{RESET}",
        "bonuses": {"int": 2, "dex": 1, "cha": 1},
        "negatives": {"str": -1},
        "zones": ["Lantan - Gearworks", "Underdark - Blingdenstone", "Waterdeep - Tinker’s Alley", "Neverwinter - Clockwork Lane"],
        "traits": ["Tinker: +5 crafts"],
        "alignment_range": ["Neutral Good", "Chaotic Good", "True Neutral"],
        "deity": "Garl Glittergold",
        "creation_narratives": {
            "Gearworks": [
                f"{MAGENTA}A ticking pulse beats as {random.choice(['clever', 'playful', 'bright'])} Garl spins Lantan’s gears....{RESET}",
                f"{MAGENTA}Cogs whirl, his wit shaping your curious soul....{RESET}",
                f"{MAGENTA}The works hum, and you stand in Gearworks, his spark!{RESET}"
            ],
            "Blingdenstone": [
                f"{MAGENTA}A deep thrum echoes as {random.choice(['shiny', 'crafty', 'deep'])} Garl lights Blingdenstone....{RESET}",
                f"{MAGENTA}Gems gleam, his craft forging your inventive essence....{RESET}",
                f"{MAGENTA}The deep shines, and you rise in Blingdenstone, his gem!{RESET}"
            ],
            "Tinker’s Alley": [
                f"{MAGENTA}A lively beat resounds as {random.choice(['joyful', 'quick', 'nimble'])} Garl dances in Waterdeep....{RESET}",
                f"{MAGENTA}Tools clink, his glee weaving your clever spirit....{RESET}",
                f"{MAGENTA}The alley buzzes, and you awaken in Tinker’s Alley, his kin!{RESET}"
            ],
            "Clockwork Lane": [
                f"{MAGENTA}A rhythmic pulse ticks as {random.choice(['precise', 'merry', 'ingenious'])} Garl winds Neverwinter....{RESET}",
                f"{MAGENTA}Clocks chime, his mind crafting your bright soul....{RESET}",
                f"{MAGENTA}The lane turns, and you stand in Clockwork Lane, his marvel!{RESET}"
            ]
        }
    },
    "halfling": {
        "desc": f"{YELLOW}Halflings dance through Faerûn with luck and cheer.{RESET}",
        "help": f"{YELLOW}Bonus: +2 Dex, +1 Wis, +1 Cha; Penalty: -1 Str. Trait: Lucky (reroll 1s). Locations:\n"
                f"1. Luiren - Greenfields: Cheerful fields.\n"
                f"2. Amn - Esmeltaran: Trade haven.\n"
                f"3. Dalelands - Featherdale: Gentle vale.\n"
                f"4. Calimshan - Tethyr Vale: Warm plains.{RESET}",
        "bonuses": {"dex": 2, "wis": 1, "cha": 1},
        "negatives": {"str": -1},
        "zones": ["Luiren - Greenfields", "Amn - Esmeltaran", "Dalelands - Featherdale", "Calimshan - Tethyr Vale"],
        "traits": ["Lucky: Reroll 1s once/encounter"],
        "alignment_range": ["Neutral Good", "Chaotic Good", "Lawful Good"],
        "deity": "Yondalla",
        "creation_narratives": {
            "Greenfields": [
                f"{YELLOW}A joyful pulse beats as {random.choice(['gentle', 'kind', 'warm'])} Yondalla blesses Luiren....{RESET}",
                f"{YELLOW}Grass sways, her warmth shaping your nimble soul....{RESET}",
                f"{YELLOW}The fields bloom, and you stand in Greenfields, her child!{RESET}"
            ],
            "Esmeltaran": [
                f"{YELLOW}A merry thrum echoes as {random.choice(['lucky', 'cheerful', 'shrewd'])} Yondalla guards Amn....{RESET}",
                f"{YELLOW}Coins jingle, her luck weaving your bright essence....{RESET}",
                f"{YELLOW}The market shines, and you rise in Esmeltaran, her kin!{RESET}"
            ],
            "Featherdale": [
                f"{YELLOW}A soft beat resounds as {random.choice(['peaceful', 'gentle', 'sweet'])} Yondalla cradles the Dalelands....{RESET}",
                f"{YELLOW}Winds whisper, her care crafting your gentle spirit....{RESET}",
                f"{YELLOW}The vale opens, and you awaken in Featherdale, her light!{RESET}"
            ],
            "Tethyr Vale": [
                f"{YELLOW}A warm pulse hums as {random.choice(['sunlit', 'kindly', 'free'])} Yondalla graces Calimshan....{RESET}",
                f"{YELLOW}Sun glows, her love forging your cheerful soul....{RESET}",
                f"{YELLOW}The vale rises, and you stand in Tethyr Vale, her joy!{RESET}"
            ]
        }
    },
    "tiefling": {
        "desc": f"{RED}Tieflings wield infernal gifts in Faerûn’s shadows.{RESET}",
        "help": f"{RED}Bonus: +2 Cha, +1 Dex, +1 Int; Penalty: -1 Wis. Trait: Hellish Resistance (fire). Locations:\n"
                f"1. Neverwinter - Blacklake: Dark slums.\n"
                f"2. Baldur’s Gate - Undercellar: Hidden depths.\n"
                f"3. Thay - Bezantur: Sinister port.\n"
                f"4. Calimport - Shadow Quarter: Grim alleys.{RESET}",
        "bonuses": {"cha": 2, "dex": 1, "int": 1},
        "negatives": {"wis": -1},
        "zones": ["Neverwinter - Blacklake", "Baldur’s Gate - Undercellar", "Thay - Bezantur", "Calimport - Shadow Quarter"],
        "traits": ["Hellish Resistance: Fire resistance"],
        "alignment_range": ["Chaotic Evil", "Neutral Evil", "Chaotic Neutral"],
        "deity": "Asmodeus",
        "creation_narratives": {
            "Blacklake": [
                f"{RED}A fiery pulse beats as {random.choice(['cunning', 'dark', 'fiery'])} Asmodeus stirs Neverwinter’s dark....{RESET}",
                f"{RED}Smoke rises, his will shaping your infernal soul....{RESET}",
                f"{RED}The lake burns, and you stand in Blacklake, his spawn!{RESET}"
            ],
            "Undercellar": [
                f"{RED}A sly thrum echoes as {random.choice(['subtle', 'wicked', 'shadowy'])} Asmodeus haunts Baldur’s Gate....{RESET}",
                f"{RED}Shadows twist, his power weaving your cursed essence....{RESET}",
                f"{RED}The depths open, and you rise in Undercellar, his kin!{RESET}"
            ],
            "Bezantur": [
                f"{RED}A sinister beat resounds as {random.choice(['ruthless', 'cold', 'vile'])} Asmodeus grips Thay....{RESET}",
                f"{RED}Waves crash, his might crafting your fiendish spirit....{RESET}",
                f"{RED}The port glows, and you awaken in Bezantur, his child!{RESET}"
            ],
            "Shadow Quarter": [
                f"{RED}A dark pulse drums as {random.choice(['twisted', 'grim', 'silent'])} Asmodeus rules Calimport....{RESET}",
                f"{RED}Knives gleam, his will forging your shadowed soul....{RESET}",
                f"{RED}The quarter rises, and you stand in Shadow Quarter, his heir!{RESET}"
            ]
        }
    },
    "half-elf": {
        "desc": f"{CYAN}Half-elves blend grace and grit in Faerûn.{RESET}",
        "help": f"{CYAN}Bonus: +2 Cha, +1 Dex, +1 Int. Trait: Versatile (+2 skill). Locations:\n"
                f"1. Waterdeep - North Ward: Diverse haven.\n"
                f"2. Evermeet - Halfway Isle: Elven bridge.\n"
                f"3. Cormanthor - Duskwood: Mixed woods.\n"
                f"4. Sembia - Selgaunt: Trade hub.{RESET}",
        "bonuses": {"cha": 2, "dex": 1, "int": 1},
        "negatives": {},
        "zones": ["Waterdeep - North Ward", "Evermeet - Halfway Isle", "Cormanthor - Duskwood", "Sembia - Selgaunt"],
        "traits": ["Versatile: +2 to any skill"],
        "alignment_range": ["Neutral Good", "Chaotic Good", "True Neutral"],
        "deity": "Sune",
        "creation_narratives": {
            "North Ward": [
                f"{CYAN}A warm pulse beats as {random.choice(['radiant', 'gentle', 'alluring'])} Sune graces Waterdeep....{RESET}",
                f"{CYAN}Voices blend, her beauty shaping your dual soul....{RESET}",
                f"{CYAN}The ward shines, and you stand in North Ward, her kin!{RESET}"
            ],
            "Halfway Isle": [
                f"{CYAN}A soft thrum echoes as {random.choice(['ethereal', 'sweet', 'graceful'])} Sune bridges Evermeet....{RESET}",
                f"{CYAN}Waves sing, her love weaving your graceful essence....{RESET}",
                f"{CYAN}The isle blooms, and you rise in Halfway Isle, her child!{RESET}"
            ],
            "Duskwood": [
                f"{CYAN}A gentle beat resounds as {random.choice(['mystical', 'tender', 'wild'])} Sune haunts Cormanthor....{RESET}",
                f"{CYAN}Leaves fall, her charm crafting your mixed spirit....{RESET}",
                f"{CYAN}The woods glow, and you awaken in Duskwood, her light!{RESET}"
            ],
            "Selgaunt": [
                f"{CYAN}A lively pulse drums as {random.choice(['shrewd', 'bright', 'lovely'])} Sune blesses Sembia....{RESET}",
                f"{CYAN}Coins clink, her grace forging your versatile soul....{RESET}",
                f"{CYAN}The port rises, and you stand in Selgaunt, her heir!{RESET}"
            ]
        }
    },
    "half-orc": {
        "desc": f"{RED}Half-orcs channel raw strength in Faerûn’s wilds.{RESET}",
        "help": f"{RED}Bonus: +2 Str, +1 Con, +1 Dex; Penalty: -1 Int. Trait: Relentless (+5 HP once/day). Locations:\n"
                f"1. Thesk - Orcsteppes: Fierce plains.\n"
                f"2. Phsant - Outskirts: Rough edges.\n"
                f"3. Icewind Dale - Targos: Cold frontier.\n"
                f"4. Rashemen - Urlingwood: Wild woods.{RESET}",
        "bonuses": {"str": 2, "con": 1, "dex": 1},
        "negatives": {"int": -1},
        "zones": ["Thesk - Orcsteppes", "Phsant - Outskirts", "Icewind Dale - Targos", "Rashemen - Urlingwood"],
        "traits": ["Relentless: +5 HP when below 0 once/day"],
        "alignment_range": ["Chaotic Neutral", "True Neutral", "Chaotic Good"],
        "deity": "Gruumsh",
        "creation_narratives": {
            "Orcsteppes": [
                f"{RED}A fierce pulse beats as {random.choice(['wrathful', 'wild', 'mighty'])} Gruumsh roars over Thesk....{RESET}",
                f"{RED}Winds howl, his fury shaping your primal soul....{RESET}",
                f"{RED}The steppe rises, and you stand in Orcsteppes, his kin!{RESET}"
            ],
            "Outskirts": [
                f"{RED}A raw thrum echoes as {random.choice(['rugged', 'brutal', 'free'])} Gruumsh stalks Phsant....{RESET}",
                f"{RED}Dust swirls, his might forging your rugged essence....{RESET}",
                f"{RED}The edge forms, and you rise in Outskirts, his child!{RESET}"
            ],
            "Targos": [
                f"{RED}A cold beat resounds as {random.choice(['harsh', 'fierce', 'unyielding'])} Gruumsh grips Icewind Dale....{RESET}",
                f"{RED}Snow falls, his power crafting your fierce spirit....{RESET}",
                f"{RED}The frost parts, and you awaken in Targos, his heir!{RESET}"
            ],
            "Urlingwood": [
                f"{RED}A wild pulse drums as {random.choice(['savage', 'dark', 'strong'])} Gruumsh haunts Rashemen....{RESET}",
                f"{RED}Trees sway, his will weaving your savage soul....{RESET}",
                f"{RED}The woods open, and you stand in Urlingwood, his spawn!{RESET}"
            ]
        }
    },
    "dragonborn": {
        "desc": f"{YELLOW}Dragonborn bear scales of draconic power.{RESET}",
        "help": f"{YELLOW}Bonus: +2 Str, +1 Cha, +1 Con; Penalty: -1 Dex. Trait: Breath Weapon (2d6/day). Locations:\n"
                f"1. Tymanther - Djerad Thymar: Draconic hold.\n"
                f"2. Unther - Skuld: Ancient ruins.\n"
                f"3. Chessenta - Luthcheq: Proud city.\n"
                f"4. Thay - Pyarados: Dark spires.{RESET}",
        "bonuses": {"str": 2, "cha": 1, "con": 1},
        "negatives": {"dex": -1},
        "zones": ["Tymanther - Djerad Thymar", "Unther - Skuld", "Chessenta - Luthcheq", "Thay - Pyarados"],
        "traits": ["Breath Weapon: 2d6 elemental damage/day"],
        "alignment_range": ["Lawful Good", "Lawful Neutral", "Neutral Good"],
        "deity": "Bahamut",
        "creation_narratives": {
            "Djerad Thymar": [
                f"{YELLOW}A mighty pulse beats as {random.choice(['noble', 'radiant', 'fierce'])} Bahamut soars over Tymanther....{RESET}",
                f"{YELLOW}Scales gleam, his breath shaping your draconic soul....{RESET}",
                f"{YELLOW}The hold rises, and you stand in Djerad Thymar, his kin!{RESET}"
            ],
            "Skuld": [
                f"{YELLOW}A proud thrum echoes as {random.choice(['ancient', 'just', 'strong'])} Bahamut guards Unther....{RESET}",
                f"{YELLOW}Ruins sing, his will forging your scaled essence....{RESET}",
                f"{YELLOW}The past awakens, and you rise in Skuld, his child!{RESET}"
            ],
            "Luthcheq": [
                f"{YELLOW}A regal beat resounds as {random.choice(['honored', 'bright', 'bold'])} Bahamut blesses Chessenta....{RESET}",
                f"{YELLOW}Stone hums, his might crafting your noble spirit....{RESET}",
                f"{YELLOW}The city shines, and you awaken in Luthcheq, his heir!{RESET}"
            ],
            "Pyarados": [
                f"{YELLOW}A fierce pulse drums as {random.choice(['fiery', 'stern', 'true'])} Bahamut pierces Thay....{RESET}",
                f"{YELLOW}Flames dance, his power weaving your dragon soul....{RESET}",
                f"{YELLOW}The spires glow, and you stand in Pyarados, his spawn!{RESET}"
            ]
        }
    },
    "aasimar": {
        "desc": f"{WHITE}Aasimar shine with celestial radiance.{RESET}",
        "help": f"{WHITE}Bonus: +2 Wis, +1 Cha, +1 Int; Penalty: -1 Str. Trait: Radiant Soul (1d8/day). Locations:\n"
                f"1. Mulhorand - Skuld: Divine ruins.\n"
                f"2. Damara - Heliogabalus: Holy courts.\n"
                f"3. Cormyr - Suzail Cathedral: Sacred plaza.\n"
                f"4. Waterdeep - Temple Hill: Blessed rise.{RESET}",
        "bonuses": {"wis": 2, "cha": 1, "int": 1},
        "negatives": {"str": -1},
        "zones": ["Mulhorand - Skuld", "Damara - Heliogabalus", "Cormyr - Suzail Cathedral", "Waterdeep - Temple Hill"],
        "traits": ["Radiant Soul: 1d8 radiant damage/day"],
        "alignment_range": ["Lawful Good", "Neutral Good", "Chaotic Good"],
        "deity": "Lathander",
        "creation_narratives": {
            "Skuld": [
                f"{WHITE}A holy pulse beats as {random.choice(['gentle', 'radiant', 'pure'])} Lathander lights Mulhorand....{RESET}",
                f"{WHITE}Dawn breaks, his grace shaping your radiant soul....{RESET}",
                f"{WHITE}The ruins glow, and you stand in Skuld, his kin!{RESET}"
            ],
            "Heliogabalus": [
                f"{WHITE}A pure thrum echoes as {random.choice(['noble', 'bright', 'serene'])} Lathander blesses Damara....{RESET}",
                f"{WHITE}Bells ring, his will forging your celestial essence....{RESET}",
                f"{WHITE}The courts shine, and you rise in Heliogabalus, his child!{RESET}"
            ],
            "Suzail Cathedral": [
                f"{WHITE}A bright beat resounds as {random.choice(['sacred', 'warm', 'just'])} Lathander guards Cormyr....{RESET}",
                f"{WHITE}Light streams, his power crafting your divine spirit....{RESET}",
                f"{WHITE}The cathedral rises, and you awaken in Suzail, his heir!{RESET}"
            ],
            "Temple Hill": [
                f"{WHITE}A warm pulse drums as {random.choice(['gentle', 'holy', 'eternal'])} Lathander graces Waterdeep....{RESET}",
                f"{WHITE}Prayers soar, his might weaving your holy soul....{RESET}",
                f"{WHITE}The hill blooms, and you stand in Temple Hill, his light!{RESET}"
            ]
        }
    },
    "genasi": {
        "desc": f"{BLUE}Genasi embody the elemental chaos of Faerûn.{RESET}",
        "help": f"{BLUE}Bonus: +2 Con, +1 Int, +1 Dex; Penalty: -1 Cha. Trait: Elemental Affinity (+5 skill). Locations:\n"
                f"1. Calimshan - Elemental Spires: Planar nexus.\n"
                f"2. Chult - Firepeaks: Volcanic wilds.\n"
                f"3. Anauroch - Windrift: Desert storms.\n"
                f"4. Thay - Thaymount: Elemental pits.{RESET}",
        "bonuses": {"con": 2, "int": 1, "dex": 1},
        "negatives": {"cha": -1},
        "zones": ["Calimshan - Elemental Spires", "Chult - Firepeaks", "Anauroch - Windrift", "Thay - Thaymount"],
        "traits": ["Elemental Affinity: +5 to one elemental skill"],
        "alignment_range": ["Chaotic Neutral", "True Neutral", "Chaotic Good"],
        "deity": "Akadi",
        "creation_narratives": {
            "Elemental Spires": [
                f"{BLUE}A wild pulse beats as {random.choice(['free', 'swift', 'chaotic'])} Akadi swirls over Calimshan....{RESET}",
                f"{BLUE}Winds roar, her chaos shaping your elemental soul....{RESET}",
                f"{BLUE}The spires rise, and you stand in Elemental Spires, her kin!{RESET}"
            ],
            "Firepeaks": [
                f"{BLUE}A fiery thrum echoes as {random.choice(['fiery', 'bold', 'untamed'])} Akadi ignites Chult....{RESET}",
                f"{BLUE}Flames dance, her will forging your primal essence....{RESET}",
                f"{BLUE}The peaks glow, and you rise in Firepeaks, her child!{RESET}"
            ],
            "Windrift": [
                f"{BLUE}A swift beat resounds as {random.choice(['wild', 'free', 'fierce'])} Akadi sweeps Anauroch....{RESET}",
                f"{BLUE}Sand storms, her power crafting your stormy spirit....{RESET}",
                f"{BLUE}The drift parts, and you awaken in Windrift, her heir!{RESET}"
            ],
            "Thaymount": [
                f"{BLUE}A deep pulse drums as {random.choice(['dark', 'strong', 'chaotic'])} Akadi haunts Thay....{RESET}",
                f"{BLUE}Earth shakes, her might weaving your chaotic soul....{RESET}",
                f"{BLUE}The mount rises, and you stand in Thaymount, her spawn!{RESET}"
            ]
        }
    },
    "goliath": {
        "desc": f"{RED}Goliaths stand as mountains in Faerûn’s peaks.{RESET}",
        "help": f"{RED}Bonus: +2 Str, +1 Con, +1 Wis; Penalty: -1 Int. Trait: Mountain Born (+5 climbing). Locations:\n"
                f"1. Spine of the World - Frosthold: Icy heights.\n"
                f"2. Thesk - Stonecrag: Rugged cliffs.\n"
                f"3. Hartsvale - Highreach: Towering peaks.\n"
                f"4. Icewind Dale - Bremen: Cold slopes.{RESET}",
        "bonuses": {"str": 2, "con": 1, "wis": 1},
        "negatives": {"int": -1},
        "zones": ["Spine of the World - Frosthold", "Thesk - Stonecrag", "Hartsvale - Highreach", "Icewind Dale - Bremen"],
        "traits": ["Mountain Born: +5 climbing"],
        "alignment_range": ["True Neutral", "Lawful Neutral", "Chaotic Neutral"],
        "deity": "Kavaki",
        "creation_narratives": {
            "Frosthold": [
                f"{RED}A mighty pulse beats as {random.choice(['stoic', 'cold', 'strong'])} Kavaki guards the Spine....{RESET}",
                f"{RED}Ice cracks, his will shaping your giant soul....{RESET}",
                f"{RED}The frost rises, and you stand in Frosthold, his kin!{RESET}"
            ],
            "Stonecrag": [
                f"{RED}A firm thrum echoes as {random.choice(['rugged', 'true', 'ancient'])} Kavaki carves Thesk....{RESET}",
                f"{RED}Stone sings, his power forging your towering essence....{RESET}",
                f"{RED}The crag stands, and you rise in Stonecrag, his child!{RESET}"
            ],
            "Highreach": [
                f"{RED}A high beat resounds as {random.choice(['noble', 'vast', 'firm'])} Kavaki blesses Hartsvale....{RESET}",
                f"{RED}Winds howl, his might crafting your mountain spirit....{RESET}",
                f"{RED}The peaks glow, and you awaken in Highreach, his heir!{RESET}"
            ],
            "Bremen": [
                f"{RED}A cold pulse drums as {random.choice(['hardy', 'stern', 'free'])} Kavaki grips Icewind Dale....{RESET}",
                f"{RED}Snow falls, his will weaving your stoic soul....{RESET}",
                f"{RED}The slopes rise, and you stand in Bremen, his spawn!{RESET}"
            ]
        }
    },
    "tabaxi": {
        "desc": f"{YELLOW}Tabaxi prowl Faerûn with feline grace.{RESET}",
        "help": f"{YELLOW}Bonus: +2 Dex, +1 Cha, +1 Wis; Penalty: -1 Con. Trait: Cat’s Claws (+1d4 unarmed). Locations:\n"
                f"1. Chult - Port Nyanzaru: Jungle port.\n"
                f"2. Maztica - Nexal: Exotic wilds.\n"
                f"3. Shaundalar - Tabaxi Jungles: Feline realm.\n"
                f"4. Amn - Murann: Coastal haven.{RESET}",
        "bonuses": {"dex": 2, "cha": 1, "wis": 1},
        "negatives": {"con": -1},
        "zones": ["Chult - Port Nyanzaru", "Maztica - Nexal", "Shaundalar - Tabaxi Jungles", "Amn - Murann"],
        "traits": ["Cat’s Claws: +1d4 unarmed damage"],
        "alignment_range": ["Chaotic Neutral", "Chaotic Good", "Neutral"],
        "deity": "Cat Lord",
        "creation_narratives": {
            "Port Nyanzaru": [
                f"{YELLOW}A swift pulse beats as {random.choice(['sly', 'graceful', 'wild'])} Cat Lord stalks Chult....{RESET}",
                f"{YELLOW}Waves purr, his grace shaping your feline soul....{RESET}",
                f"{YELLOW}The port rises, and you stand in Port Nyanzaru, his kin!{RESET}"
            ],
            "Nexal": [
                f"{YELLOW}A wild thrum echoes as {random.choice(['curious', 'fierce', 'exotic'])} Cat Lord haunts Maztica....{RESET}",
                f"{YELLOW}Jungles hum, his will forging your curious essence....{RESET}",
                f"{YELLOW}The wilds glow, and you rise in Nexal, his child!{RESET}"
            ],
            "Tabaxi Jungles": [
                f"{YELLOW}A soft beat resounds as {random.choice(['silent', 'agile', 'mysterious'])} Cat Lord guards Shaundalar....{RESET}",
                f"{YELLOW}Leaves rustle, his might crafting your prowling spirit....{RESET}",
                f"{YELLOW}The jungles open, and you awaken in Tabaxi Jungles, his heir!{RESET}"
            ],
            "Murann": [
                f"{YELLOW}A sly pulse drums as {random.choice(['nimble', 'clever', 'free'])} Cat Lord graces Amn....{RESET}",
                f"{YELLOW}Winds whisper, his power weaving your agile soul....{RESET}",
                f"{YELLOW}The coast shines, and you stand in Murann, his spawn!{RESET}"
            ]
        }
    }
}

# Static Classes (expandable later)
CLASSES = {
    "fighter": {"desc": f"{RED}Fighters master martial prowess with steel.{RESET}", "details": f"{RED}All races. Strength and resilience.{RESET}"},
    "wizard": {"desc": f"{CYAN}Wizards bend reality with arcane might.{RESET}", "details": f"{CYAN}High elves, humans, gnomes. Intellect-driven.{RESET}"},
    "cleric": {"desc": f"{WHITE}Clerics channel divine power.{RESET}", "details": f"{WHITE}All races. Wisdom and faith.{RESET}"}
}

# Locations from RACES
LOCATIONS = {zone: f"{CYAN}A realm of {race.capitalize()} beginnings.{RESET}" for race in RACES for zone in RACES[race]["zones"]}

class LoginHandler:
    def __init__(self):
        self.players = {}
        self.term_handler = TermHandler(self)
        self.network_handler = NetworkHandler(self)

    async def handle_login(self, reader, writer):
        try:
            writer.write(f"{WELCOME_ART}\n".encode())
            writer.write(f"{BLUE}Options: {GREEN}(1) Login {CYAN}(2) New Player {MAGENTA}(3) Guest {YELLOW}(4) Who’s On{RESET}\n> ".encode())
            await writer.drain()
            choice = (await reader.read(100)).decode().strip()
            if choice == "1":
                return await self.login_existing(reader, writer)
            elif choice == "2":
                return await self.create_new_player(reader, writer)
            elif choice == "3":
                return await self.login_guest(reader, writer)
            elif choice == "4":
                await self.show_whos_on(reader, writer)
                return None
            writer.write(f"{RED}Invalid choice! Choose wisely, traveler.{RESET}\n".encode())
            return None
        except Exception as e:
            writer.write(f"{RED}The Weave falters: {str(e)}. Try again, mortal.{RESET}\n".encode())
            return None

    async def login_existing(self, reader, writer):
        try:
            writer.write(f"{GREEN}Enter your name: {RESET}".encode())
            await writer.drain()
            name = (await reader.read(100)).decode().strip()
            if not name or not name.isalnum():
                writer.write(f"{RED}Names must be alphanumeric!{RESET}\n".encode())
                return None
            player_file = f"/mnt/home2/mud/players/{name.lower()}.json"
            if not os.path.exists(player_file):
                writer.write(f"{RED}No such adventurer exists in Faerûn!{RESET}\n".encode())
                return None
            writer.write(f"{GREEN}Enter your password: {RESET}".encode())
            await writer.drain()
            password = (await reader.read(100)).decode().strip()
            with open(player_file, "r") as f:
                data = json.load(f)
            if data["password"] != password:
                writer.write(f"{RED}The password denies you entry!{RESET}\n".encode())
                return None
            player = Player(name)
            player.stats = data["stats"]
            player.skills = data["skills"]
            player.xp = data["xp"]
            player.hp = data["hp"]
            player.max_hp = data["max_hp"]
            player.gp = data["gp"]
            player.max_gp = data["max_gp"]
            player.alignment = data["alignment"]
            player.race = data["race"]
            writer.write(f"{CYAN}Welcome back, {name}, to Faerûn’s fractured weave!{RESET}\n".encode())
            return player
        except Exception as e:
            writer.write(f"{RED}The Weave rejects your return: {str(e)}.{RESET}\n".encode())
            return None

    async def login_guest(self, reader, writer):
        player = Player("Guest_" + str(random.randint(1000, 9999)))
        player.alignment = random.choice(["True Neutral", "Chaotic Neutral"])
        writer.write(f"{MAGENTA}Welcome, wandering soul, as a guest of Faerûn’s vast tapestry!{RESET}\n".encode())
        return player

    async def show_whos_on(self, reader, writer):
        who = f"{YELLOW}Currently adventuring in Faerûn:{RESET}\n"
        if not self.players:
            who += f"{WHITE}The realm lies silent—no souls tread its paths.{RESET}"
        else:
            who += "\n".join(f"{GREEN}{p['player'].name}{RESET} - {p['player'].alignment}" 
                            for p in self.players.values())
        writer.write(f"{who}\n".encode())
        await writer.drain()

    async def create_new_player(self, reader, writer):
        try:
            # Name
            writer.write(f"{GREEN}Choose your name (alphanumeric only): {RESET}".encode())
            await writer.drain()
            name = (await reader.read(100)).decode().strip()
            if not name.isalnum():
                writer.write(f"{RED}Names must be letters and numbers only!{RESET}\n".encode())
                return None
            player_file = f"/mnt/home2/mud/players/{name.lower()}.json"
            if os.path.exists(player_file):
                writer.write(f"{RED}That name is already claimed in Faerûn’s annals!{RESET}\n".encode())
                return None

            # Password
            writer.write(f"{GREEN}Forge your password: {RESET}".encode())
            await writer.drain()
            password = (await reader.read(100)).decode().strip()
            if len(password) < 4:
                writer.write(f"{RED}Passwords must be at least 4 characters!{RESET}\n".encode())
                return None

            # Gender
            writer.write(f"{GREEN}Declare your gender (m/f/n): {RESET}".encode())
            await writer.drain()
            gender = (await reader.read(100)).decode().strip().lower()[0]
            if gender not in "mfn":
                gender = "n"

            # Terminal settings
            writer.write(f"{BLUE}Terminal type (ansi/vt100/plain, default ansi): {RESET}".encode())
            await writer.drain()
            term = (await reader.read(100)).decode().strip() or "ansi"
            self.term_handler.set_term_type(term)
            writer.write(f"{BLUE}MXP/MCCP (on/off, default off): {RESET}".encode())
            await writer.drain()
            mxp = (await reader.read(100)).decode().strip() == "on"
            self.network_handler.set_mxp(mxp)

            # Help Parchment Screen
            writer.write(f"{HELP_PARCHMENT}\n> ".encode())
            await writer.drain()
            while True:
                command = (await reader.read(100)).decode().strip().lower()
                if command == "begin":
                    break
                elif command == "races":
                    race_info = "\n".join(f"{GREEN}{race.capitalize()}: {RACES[race]['help']}{RESET}" for race in RACES)
                    writer.write(f"{race_info}\n> ".encode())
                elif command == "classes":
                    class_info = "\n".join(f"{YELLOW}{cls.capitalize()}: {CLASSES[cls]['details']}{RESET}" for cls in CLASSES)
                    writer.write(f"{class_info}\n> ".encode())
                elif command == "deities":
                    deity_info = "\n".join(f"{WHITE}{deity}: {DEITIES[deity]['desc']}{RESET}" for deity in DEITIES)
                    writer.write(f"{deity_info}\n> ".encode())
                elif command == "locations":
                    loc_info = "\n".join(f"{CYAN}{loc}: {desc}{RESET}" for loc, desc in LOCATIONS.items())
                    writer.write(f"{loc_info}\n> ".encode())
                elif command == "lore":
                    writer.write(f"{MAGENTA}Faerûn lies fractured—empires rise, gods clash, and the Weave trembles.{RESET}\n> ".encode())
                else:
                    writer.write(f"{RED}Unknown command! Try ‘races’, ‘classes’, ‘deities’, ‘locations’, ‘lore’, or ‘begin’.{RESET}\n> ".encode())
                await writer.drain()

            # Race Selection
            race_list = "\n".join(f"{GREEN}{i+1}. {race.capitalize()}{RESET}" for i, race in enumerate(RACES.keys()))
            writer.write(f"\n{YELLOW}Choose your race to etch into Faerûn’s legacy:{RESET}\n{race_list}\n> ".encode())
            await writer.drain()
            while True:
                race_choice = (await reader.read(100)).decode().strip()
                try:
                    race_choice = int(race_choice) - 1
                    if 0 <= race_choice < len(RACES):
                        break
                    writer.write(f"{RED}Choose a number between 1 and {len(RACES)}!{RESET}\n> ".encode())
                except ValueError:
                    writer.write(f"{RED}Enter a valid number!{RESET}\n> ".encode())
                await writer.drain()
            race = list(RACES.keys())[race_choice]

            writer.write(f"{BLUE}Seek wisdom on {race.capitalize()}? (y/n): {RESET}".encode())
            await writer.drain()
            if (await reader.read(100)).decode().strip().lower() == "y":
                writer.write(f"{RACES[race]['help']}\n".encode())
                await writer.drain()

            # Starting Zone Selection
            zones = "\n".join(f"{GREEN}{i+1}. {zone.split(' - ')[1]}{RESET}" for i, zone in enumerate(RACES[race]["zones"]))
            writer.write(f"\n{YELLOW}Choose where your tale begins:{RESET}\n{zones}\n> ".encode())
            await writer.drain()
            while True:
                zone_choice = (await reader.read(100)).decode().strip()
                try:
                    zone_choice = int(zone_choice) - 1
                    if 0 <= zone_choice < len(RACES[race]["zones"]):
                        break
                    writer.write(f"{RED}Choose a number between 1 and {len(RACES[race]['zones'])}!{RESET}\n> ".encode())
                except ValueError:
                    writer.write(f"{RED}Enter a valid number!{RESET}\n> ".encode())
                await writer.drain()
            start_zone = RACES[race]["zones"][zone_choice].split(" - ")[1]

            # Stat Allocation with Confirmation
            writer.write(f"\n{YELLOW}Allocate your strengths (27 points total):{RESET}\n"
                         f"{GREEN}STR DEX INT CON WIS CHA (8-15 each, e.g., '10 12 14 8 13 10'){RESET}\n> ".encode())
            await writer.drain()
            while True:
                stats_input = (await reader.read(100)).decode().strip().split()
                if len(stats_input) != 6:
                    writer.write(f"{RED}Enter 6 numbers for STR DEX INT CON WIS CHA!{RESET}\n> ".encode())
                    await writer.drain()
                    continue
                try:
                    stats = [int(x) for x in stats_input]
                    if not all(8 <= x <= 15 for x in stats):
                        writer.write(f"{RED}Stats must be between 8 and 15!{RESET}\n> ".encode())
                        await writer.drain()
                        continue
                    points = sum(max(0, x - 8) + (x - 13) * 2 if x > 13 else 0 for x in stats)
                    if points > 27:
                        writer.write(f"{RED}You’ve spent {points} points—limit is 27!{RESET}\n> ".encode())
                        await writer.drain()
                        continue
                    writer.write(f"{GREEN}Your stats: STR {stats[0]} DEX {stats[1]} INT {stats[2]} CON {stats[3]} WIS {stats[4]} CHA {stats[5]} (Points: {points}/27){RESET}\n"
                                 f"{BLUE}Confirm? (y/n): {RESET}".encode())
                    await writer.drain()
                    if (await reader.read(100)).decode().strip().lower() == "y":
                        break
                    writer.write(f"{YELLOW}Reallocate your stats:{RESET}\n> ".encode())
                    await writer.drain()
                except ValueError:
                    writer.write(f"{RED}Enter valid numbers!{RESET}\n> ".encode())
                    await writer.drain()
            base_stats = {"str": stats[0], "dex": stats[1], "int": stats[2], "con": stats[3], "wis": stats[4], "cha": stats[5]}

            # Random Alignment
            alignment = random.choice(RACES[race]["alignment_range"])

            # Creation Narrative with Timed Callouts
            writer.write(f"\n{MAGENTA}{BOLD}The Weave fractures as {name}’s creation begins...{RESET}\n".encode())
            await writer.drain()
            narrative = RACES[race]["creation_narratives"][start_zone]
            for msg in narrative[:-1]:
                writer.write(f"{msg}\n".encode())
                await writer.drain()
                await asyncio.sleep(5)
            writer.write(f"{narrative[-1]}\n".encode())
            await writer.drain()

            # Initialize Player
            player = Player(name)
            player.stats.update(base_stats)
            player.stats.update(RACES[race]["bonuses"])
            for stat, penalty in RACES[race]["negatives"].items():
                player.stats[stat] += penalty
            player.alignment = alignment
            player.hp = player.calculate_hp()
            player.max_hp = player.hp
            player.gp = player.calculate_gp()
            player.max_gp = player.gp
            player.race = race

            # Save Player Data
            player_data = {
                "name": name,
                "password": password,
                "stats": player.stats,
                "skills": player.skills,
                "xp": player.xp,
                "hp": player.hp,
                "max_hp": player.max_hp,
                "gp": player.gp,
                "max_gp": player.max_gp,
                "alignment": alignment,
                "race": race,
                "gender": gender,
                "start_zone": start_zone
            }
            with open(player_file, "w") as f:
                json.dump(player_data, f)

            return player
        except Exception as e:
            writer.write(f"{RED}Creation falters: {str(e)}. The Weave denies you this time.{RESET}\n".encode())
            return None

async def main():
    login_handler = LoginHandler()
    server = await asyncio.start_server(login_handler.handle_login, "127.0.0.1", 4000)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
