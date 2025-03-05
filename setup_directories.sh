# setup_directories.py
import os

BASE_DIR = "/mnt/home2/mud"

DIRECTORIES = [
    "std", "modules", "modules/spell_handler.py/spells/generic", "modules/spell_handler.py/spells/racial/drow",
    "modules/spell_handler.py/spells/racial/elf", "modules/spell_handler.py/spells/class/wizard",
    "modules/spell_handler.py/spells/class/cleric", "modules/ritual_handler.py/rituals",
    "modules/crafting_handler.py/crafts/smithing", "modules/crafting_handler.py/crafts/mining",
    "modules/crafting_handler.py/crafts/culinary", "modules/classes.py/generic",
    "modules/classes.py/racial/drow", "modules/classes.py/racial/elf", "modules/commands",
    "domains/sword_coast/waterdeep/docks", "domains/sword_coast/waterdeep/market",
    "domains/sword_coast/waterdeep/castle", "domains/sword_coast/neverwinter",
    "domains/sword_coast/baldur_gate", "domains/sword_coast/candlekeep", "domains/sword_coast/daggerford",
    "domains/sword_coast/luskan", "domains/sword_coast/phandalin", "domains/underdark/menzoberranzan/houses/house_baenre",
    "domains/underdark/menzoberranzan/houses/house_noquar", "domains/underdark/ched_nasad",
    "domains/underdark/gracklstugh", "domains/underdark/sshamath", "domains/cormanthor/villages/elventree",
    "domains/cormanthor/villages/tangled_trees", "domains/icewind_dale/ten_towns/bryn_shander",
    "domains/icewind_dale/ten_towns/targos", "domains/calimshan/calimport", "domains/calimshan/memnon",
    "domains/vast_swamp/villages/mossbridge", "domains/damara/heliogabalus",
    "domains/damara/villages/bloodstone", "domains/anauroch", "domains/high_forest/settlements/star_mount",
    "domains/world", "players", "logs", "ai", "website/marketing/banners", "docs"
]

for dir_path in DIRECTORIES:
    full_path = os.path.join(BASE_DIR, dir_path)
    os.makedirs(full_path, exist_ok=True)
    print(f"Created directory: {full_path}")

with open(os.path.join(BASE_DIR, "tasks.txt"), "w") as f:
    f.write("# Add tasks (e.g., 'mystra create_spell fireball [high]')\n")
print("Created tasks.txt")

with open(os.path.join(BASE_DIR, "WEBSITE_LINKS.txt"), "w") as f:
    f.write("# Discworld Links\nhttps://discworld.starturtle.net/\nhttps://dwwiki.mooo.com/wiki/Ankh-Morpork\n# Forgotten Realms Links\nhttps://forgottenrealms.fandom.com/wiki/Faer%C3%BBn\nhttps://forgottenrealms.fandom.com/wiki/Category:Spells\n")
print("Created WEBSITE_LINKS.txt")
