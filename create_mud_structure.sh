
#!/bin/bash
# create_mud_structure.sh - Sets up /mnt/home2/mud/ directory structure

BASE_DIR="/mnt/home2/mud"
mkdir -p "$BASE_DIR"

# Top-level files
touch "$BASE_DIR/mud.py"

# Std directory
mkdir -p "$BASE_DIR/std"
touch "$BASE_DIR/std/object.py" "$BASE_DIR/std/living.py" "$BASE_DIR/std/room.py" \
      "$BASE_DIR/std/wearable.py" "$BASE_DIR/std/container.py" "$BASE_DIR/std/command.py"

# Modules directory
mkdir -p "$BASE_DIR/modules" "$BASE_DIR/modules/spells" "$BASE_DIR/modules/rituals" "$BASE_DIR/modules/commands"
touch "$BASE_DIR/modules/login_handler.py" "$BASE_DIR/modules/spell_handler.py" "$BASE_DIR/modules/combat_handler.py" \
      "$BASE_DIR/modules/skills_handler.py" "$BASE_DIR/modules/ritual_handler.py" "$BASE_DIR/modules/inventory_handler.py" \
      "$BASE_DIR/modules/soul_handler.py" "$BASE_DIR/modules/term_handler.py" "$BASE_DIR/modules/network_handler.py" \
      "$BASE_DIR/modules/quests_handler.py"
touch "$BASE_DIR/modules/spells/arcane_aegis.py" "$BASE_DIR/modules/spells/flame_ward.py" \
      "$BASE_DIR/modules/spells/abyssal_summons.py" "$BASE_DIR/modules/spells/thunder_lance.py" \
      "$BASE_DIR/modules/spells/lunar_wyrm.py" "$BASE_DIR/modules/spells/shadow_gate.py"
touch "$BASE_DIR/modules/commands/kill.py" "$BASE_DIR/modules/commands/look.py" "$BASE_DIR/modules/commands/inventory.py"

# Domains directory (abbreviated - expand as needed)
mkdir -p "$BASE_DIR/domains/sword_coast/waterdeep" "$BASE_DIR/domains/underdark/menzoberranzan" \
         "$BASE_DIR/domains/cormyr/suzail" "$BASE_DIR/domains/dalelands/shadowdale" \
         "$BASE_DIR/domains/icewind_dale/bryn_shander" "$BASE_DIR/domains/amn/athkatla" \
         "$BASE_DIR/domains/thay/eltabbar" "$BASE_DIR/domains/world"
for dir in "$BASE_DIR/domains"/*/ "$BASE_DIR/domains"/*/*/ ; do
    touch "$dir/rooms.py" "$dir/npcs.py" "$dir/items.py"
    [[ $dir =~ /waterdeep/ ]] && touch "$dir/guilds.py"
done
touch "$BASE_DIR/domains/world/terrain.py"

# Players, logs, ai
mkdir -p "$BASE_DIR/players" "$BASE_DIR/logs" "$BASE_DIR/ai"

echo "Directory structure created at $BASE_DIR"
