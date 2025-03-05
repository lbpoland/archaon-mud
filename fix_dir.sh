#!/bin/bash

# Base directory
BASE_DIR="/mnt/home2/mud"
mkdir -p "$BASE_DIR" || echo "Base directory already exists."

# Create top-level files
touch "$BASE_DIR/mud.py" || echo "File mud.py already exists, skipping creation."
touch "$BASE_DIR/PLAN.md" || echo "File PLAN.md already exists, skipping creation."
touch "$BASE_DIR/AI_README.md" || echo "File AI_README.md already exists, skipping creation."

# Create std/ directory and its files
mkdir -p "$BASE_DIR/std"
touch "$BASE_DIR/std/object.py" || echo "File std/object.py already exists, skipping creation."
touch "$BASE_DIR/std/living.py" || echo "File std/living.py already exists, skipping creation."
touch "$BASE_DIR/std/room.py" || echo "File std/room.py already exists, skipping creation."
touch "$BASE_DIR/std/wearable.py" || echo "File std/wearable.py already exists, skipping creation."
touch "$BASE_DIR/std/container.py" || echo "File std/container.py already exists, skipping creation."
touch "$BASE_DIR/std/command.py" || echo "File std/command.py already exists, skipping creation."

# Create modules/ directory and its substructure
mkdir -p "$BASE_DIR/modules"
touch "$BASE_DIR/modules/login_handler.py" || echo "File modules/login_handler.py already exists, skipping creation."
touch "$BASE_DIR/modules/spell_handler.py" || echo "File modules/spell_handler.py already exists, skipping creation."

# Create spell_handler.py subdirectories and files
mkdir -p "$BASE_DIR/modules/spell_handler/spells/generic"
touch "$BASE_DIR/modules/spell_handler/spells/generic/fireball.py" || echo "File modules/spell_handler/spells/generic/fireball.py already exists, skipping creation."
touch "$BASE_DIR/modules/spell_handler/spells/generic/heal.py" || echo "File modules/spell_handler/spells/generic/heal.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/spell_handler/spells/racial/drow"
touch "$BASE_DIR/modules/spell_handler/spells/racial/drow/shadowbolt.py" || echo "File modules/spell_handler/spells/racial/drow/shadowbolt.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/spell_handler/spells/racial/elf"
touch "$BASE_DIR/modules/spell_handler/spells/racial/elf/moonbeam.py" || echo "File modules/spell_handler/spells/racial/elf/moonbeam.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/spell_handler/spells/class/wizard"
touch "$BASE_DIR/modules/spell_handler/spells/class/wizard/arcane_blast.py" || echo "File modules/spell_handler/spells/class/wizard/arcane_blast.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/spell_handler/spells/class/cleric"
touch "$BASE_DIR/modules/spell_handler/spells/class/cleric/divine_smite.py" || echo "File modules/spell_handler/spells/class/cleric/divine_smite.py already exists, skipping creation."

# Create other modules/ files
touch "$BASE_DIR/modules/combat_handler.py" || echo "File modules/combat_handler.py already exists, skipping creation."
touch "$BASE_DIR/modules/skills_handler.py" || echo "File modules/skills_handler.py already exists, skipping creation."
touch "$BASE_DIR/modules/ritual_handler.py" || echo "File modules/ritual_handler.py already exists, skipping creation."

# Create ritual_handler.py subdirectories and files
mkdir -p "$BASE_DIR/modules/ritual_handler/rituals"
touch "$BASE_DIR/modules/ritual_handler/rituals/heal_ritual.py" || echo "File modules/ritual_handler/rituals/heal_ritual.py already exists, skipping creation."
touch "$BASE_DIR/modules/ritual_handler/rituals/banish_ritual.py" || echo "File modules/ritual_handler/rituals/banish_ritual.py already exists, skipping creation."

# Continue with other modules/ files
touch "$BASE_DIR/modules/inventory_handler.py" || echo "File modules/inventory_handler.py already exists, skipping creation."
touch "$BASE_DIR/modules/soul_handler.py" || echo "File modules/soul_handler.py already exists, skipping creation."
touch "$BASE_DIR/modules/term_handler.py" || echo "File modules/term_handler.py already exists, skipping creation."
touch "$BASE_DIR/modules/network_handler.py" || echo "File modules/network_handler.py already exists, skipping creation."
touch "$BASE_DIR/modules/quests_handler.py" || echo "File modules/quests_handler.py already exists, skipping creation."
touch "$BASE_DIR/modules/crafting_handler.py" || echo "File modules/crafting_handler.py already exists, skipping creation."

# Create crafting_handler.py subdirectories and files
mkdir -p "$BASE_DIR/modules/crafting_handler/crafts/smithing"
touch "$BASE_DIR/modules/crafting_handler/crafts/smithing/sword_crafting.py" || echo "File modules/crafting_handler/crafts/smithing/sword_crafting.py already exists, skipping creation."
touch "$BASE_DIR/modules/crafting_handler/crafts/smithing/armor_crafting.py" || echo "File modules/crafting_handler/crafts/smithing/armor_crafting.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/crafting_handler/crafts/mining"
touch "$BASE_DIR/modules/crafting_handler/crafts/mining/ore_extraction.py" || echo "File modules/crafting_handler/crafts/mining/ore_extraction.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/crafting_handler/crafts/culinary"
touch "$BASE_DIR/modules/crafting_handler/crafts/culinary/cooking_recipe.py" || echo "File modules/crafting_handler/crafts/culinary/cooking_recipe.py already exists, skipping creation."

# Continue with crafting_handler.py related files
touch "$BASE_DIR/modules/crafting_handler/weapons.py" || echo "File modules/crafting_handler/weapons.py already exists, skipping creation."
touch "$BASE_DIR/modules/crafting_handler/armors.py" || echo "File modules/crafting_handler/armors.py already exists, skipping creation."
touch "$BASE_DIR/modules/crafting_handler/clothing.py" || echo "File modules/crafting_handler/clothing.py already exists, skipping creation."

# Create classes.py subdirectories and files
touch "$BASE_DIR/modules/classes.py" || echo "File modules/classes.py already exists, skipping creation."
mkdir -p "$BASE_DIR/modules/classes/generic"
touch "$BASE_DIR/modules/classes/generic/warrior.py" || echo "File modules/classes/generic/warrior.py already exists, skipping creation."
touch "$BASE_DIR/modules/classes/generic/mage.py" || echo "File modules/classes/generic/mage.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/classes/racial/drow"
touch "$BASE_DIR/modules/classes/racial/drow/drow_warrior.py" || echo "File modules/classes/racial/drow/drow_warrior.py already exists, skipping creation."
touch "$BASE_DIR/modules/classes/racial/drow/drow_mage.py" || echo "File modules/classes/racial/drow/drow_mage.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/classes/racial/elf"
touch "$BASE_DIR/modules/classes/racial/elf/elf_ranger.py" || echo "File modules/classes/racial/elf/elf_ranger.py already exists, skipping creation."

# Create races.py subdirectories and files
touch "$BASE_DIR/modules/races.py" || echo "File modules/races.py already exists, skipping creation."
mkdir -p "$BASE_DIR/modules/races"
touch "$BASE_DIR/modules/races/human.py" || echo "File modules/races/human.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/elf.py" || echo "File modules/races/elf.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/drow.py" || echo "File modules/races/drow.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/dwarf.py" || echo "File modules/races/dwarf.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/orc.py" || echo "File modules/races/orc.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/gnome.py" || echo "File modules/races/gnome.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/halfling.py" || echo "File modules/races/halfling.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/tiefling.py" || echo "File modules/races/tiefling.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/aarakocra.py" || echo "File modules/races/aarakocra.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/dragonborn.py" || echo "File modules/races/dragonborn.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/goliath.py" || echo "File modules/races/goliath.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/genasi.py" || echo "File modules/races/genasi.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/tabaxi.py" || echo "File modules/races/tabaxi.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/triton.py" || echo "File modules/races/triton.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/yuan_ti.py" || echo "File modules/races/yuan_ti.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/firbolg.py" || echo "File modules/races/firbolg.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/kenku.py" || echo "File modules/races/kenku.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/kobold.py" || echo "File modules/races/kobold.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/lizardfolk.py" || echo "File modules/races/lizardfolk.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/changeling.py" || echo "File modules/races/changeling.py already exists, skipping creation."
touch "$BASE_DIR/modules/races/warforged.py" || echo "File modules/races/warforged.py already exists, skipping creation."

# Create organizations.py subdirectories and files
touch "$BASE_DIR/modules/organizations.py" || echo "File modules/organizations.py already exists, skipping creation."
mkdir -p "$BASE_DIR/modules/organizations"
touch "$BASE_DIR/modules/organizations/harpers.py" || echo "File modules/organizations/harpers.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/zhentarim.py" || echo "File modules/organizations/zhentarim.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/red_wizards.py" || echo "File modules/organizations/red_wizards.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/cult_of_dragon.py" || echo "File modules/organizations/cult_of_dragon.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/lords_alliance.py" || echo "File modules/organizations/lords_alliance.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/seven_sisters.py" || echo "File modules/organizations/seven_sisters.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/fire_knives.py" || echo "File modules/organizations/fire_knives.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/xanathars_guild.py" || echo "File modules/organizations/xanathars_guild.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/shades.py" || echo "File modules/organizations/shades.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/organizations/drow_houses"
touch "$BASE_DIR/modules/organizations/drow_houses/house_baenre.py" || echo "File modules/organizations/drow_houses/house_baenre.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/drow_houses/house_noquar.py" || echo "File modules/organizations/drow_houses/house_noquar.py already exists, skipping creation."

mkdir -p "$BASE_DIR/modules/organizations/orc_clans"
touch "$BASE_DIR/modules/organizations/orc_clans/clan_blade_of_the_black_dog.py" || echo "File modules/organizations/orc_clans/clan_blade_of_the_black_dog.py already exists, skipping creation."
touch "$BASE_DIR/modules/organizations/orc_clans/clan_blood_of_the_red_fang.py" || echo "File modules/organizations/orc_clans/clan_blood_of_the_red_fang.py already exists, skipping creation."

# Create commands/ subdirectories and files
mkdir -p "$BASE_DIR/modules/commands"
touch "$BASE_DIR/modules/commands/kill.py" || echo "File modules/commands/kill.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/look.py" || echo "File modules/commands/look.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/inventory.py" || echo "File modules/commands/inventory.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/say.py" || echo "File modules/commands/say.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/shout.py" || echo "File modules/commands/shout.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/smile.py" || echo "File modules/commands/smile.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/help.py" || echo "File modules/commands/help.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/who.py" || echo "File modules/commands/who.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/score.py" || echo "File modules/commands/score.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/train.py" || echo "File modules/commands/train.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/advance.py" || echo "File modules/commands/advance.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/learn.py" || echo "File modules/commands/learn.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/teach.py" || echo "File modules/commands/teach.py already exists, skipping creation."
touch "$BASE_DIR/modules/commands/worship.py" || echo "File modules/commands/worship.py already exists, skipping creation."

# Create domains/ subdirectories and files
mkdir -p "$BASE_DIR/domains"
mkdir -p "$BASE_DIR/domains/sword_coast"
mkdir -p "$BASE_DIR/domains/sword_coast/waterdeep"
touch "$BASE_DIR/domains/sword_coast/waterdeep/rooms.py" || echo "File domains/sword_coast/waterdeep/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/waterdeep/npcs.py" || echo "File domains/sword_coast/waterdeep/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/waterdeep/items.py" || echo "File domains/sword_coast/waterdeep/items.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/waterdeep/guilds.py" || echo "File domains/sword_coast/waterdeep/guilds.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/sword_coast/waterdeep/docks"
touch "$BASE_DIR/domains/sword_coast/waterdeep/docks/rooms.py" || echo "File domains/sword_coast/waterdeep/docks/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/sword_coast/waterdeep/market"
touch "$BASE_DIR/domains/sword_coast/waterdeep/market/rooms.py" || echo "File domains/sword_coast/waterdeep/market/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/sword_coast/waterdeep/castle"
touch "$BASE_DIR/domains/sword_coast/waterdeep/castle/rooms.py" || echo "File domains/sword_coast/waterdeep/castle/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/sword_coast/neverwinter"
touch "$BASE_DIR/domains/sword_coast/neverwinter/rooms.py" || echo "File domains/sword_coast/neverwinter/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/neverwinter/npcs.py" || echo "File domains/sword_coast/neverwinter/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/neverwinter/items.py" || echo "File domains/sword_coast/neverwinter/items.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/neverwinter/guilds.py" || echo "File domains/sword_coast/neverwinter/guilds.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/sword_coast/baldur_gate"
touch "$BASE_DIR/domains/sword_coast/baldur_gate/rooms.py" || echo "File domains/sword_coast/baldur_gate/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/baldur_gate/npcs.py" || echo "File domains/sword_coast/baldur_gate/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/baldur_gate/items.py" || echo "File domains/sword_coast/baldur_gate/items.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/baldur_gate/guilds.py" || echo "File domains/sword_coast/baldur_gate/guilds.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/sword_coast/candlekeep"
touch "$BASE_DIR/domains/sword_coast/candlekeep/rooms.py" || echo "File domains/sword_coast/candlekeep/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/candlekeep/npcs.py" || echo "File domains/sword_coast/candlekeep/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/candlekeep/items.py" || echo "File domains/sword_coast/candlekeep/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/sword_coast/daggerford"
touch "$BASE_DIR/domains/sword_coast/daggerford/rooms.py" || echo "File domains/sword_coast/daggerford/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/daggerford/npcs.py" || echo "File domains/sword_coast/daggerford/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/daggerford/items.py" || echo "File domains/sword_coast/daggerford/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/sword_coast/luskan"
touch "$BASE_DIR/domains/sword_coast/luskan/rooms.py" || echo "File domains/sword_coast/luskan/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/luskan/npcs.py" || echo "File domains/sword_coast/luskan/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/luskan/items.py" || echo "File domains/sword_coast/luskan/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/sword_coast/phandalin"
touch "$BASE_DIR/domains/sword_coast/phandalin/rooms.py" || echo "File domains/sword_coast/phandalin/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/phandalin/npcs.py" || echo "File domains/sword_coast/phandalin/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/sword_coast/phandalin/items.py" || echo "File domains/sword_coast/phandalin/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/underdark"
mkdir -p "$BASE_DIR/domains/underdark/menzoberranzan"
touch "$BASE_DIR/domains/underdark/menzoberranzan/rooms.py" || echo "File domains/underdark/menzoberranzan/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/underdark/menzoberranzan/npcs.py" || echo "File domains/underdark/menzoberranzan/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/underdark/menzoberranzan/items.py" || echo "File domains/underdark/menzoberranzan/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/underdark/menzoberranzan/houses"
mkdir -p "$BASE_DIR/domains/underdark/menzoberranzan/houses/house_baenre"
touch "$BASE_DIR/domains/underdark/menzoberranzan/houses/house_baenre/rooms.py" || echo "File domains/underdark/menzoberranzan/houses/house_baenre/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/underdark/menzoberranzan/houses/house_noquar"
touch "$BASE_DIR/domains/underdark/menzoberranzan/houses/house_noquar/rooms.py" || echo "File domains/underdark/menzoberranzan/houses/house_noquar/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/underdark/ched_nasad"
touch "$BASE_DIR/domains/underdark/ched_nasad/rooms.py" || echo "File domains/underdark/ched_nasad/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/underdark/ched_nasad/npcs.py" || echo "File domains/underdark/ched_nasad/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/underdark/ched_nasad/items.py" || echo "File domains/underdark/ched_nasad/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/underdark/gracklstugh"
touch "$BASE_DIR/domains/underdark/gracklstugh/rooms.py" || echo "File domains/underdark/gracklstugh/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/underdark/gracklstugh/npcs.py" || echo "File domains/underdark/gracklstugh/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/underdark/gracklstugh/items.py" || echo "File domains/underdark/gracklstugh/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/underdark/sshamath"
touch "$BASE_DIR/domains/underdark/sshamath/rooms.py" || echo "File domains/underdark/sshamath/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/underdark/sshamath/npcs.py" || echo "File domains/underdark/sshamath/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/underdark/sshamath/items.py" || echo "File domains/underdark/sshamath/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/cormanthor"
touch "$BASE_DIR/domains/cormanthor/rooms.py" || echo "File domains/cormanthor/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/cormanthor/npcs.py" || echo "File domains/cormanthor/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/cormanthor/items.py" || echo "File domains/cormanthor/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/cormanthor/villages"
mkdir -p "$BASE_DIR/domains/cormanthor/villages/elventree"
touch "$BASE_DIR/domains/cormanthor/villages/elventree/rooms.py" || echo "File domains/cormanthor/villages/elventree/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/cormanthor/villages/tangled_trees"
touch "$BASE_DIR/domains/cormanthor/villages/tangled_trees/rooms.py" || echo "File domains/cormanthor/villages/tangled_trees/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/icewind_dale"
mkdir -p "$BASE_DIR/domains/icewind_dale/ten_towns"
mkdir -p "$BASE_DIR/domains/icewind_dale/ten_towns/bryn_shander"
touch "$BASE_DIR/domains/icewind_dale/ten_towns/bryn_shander/rooms.py" || echo "File domains/icewind_dale/ten_towns/bryn_shander/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/icewind_dale/ten_towns/targos"
touch "$BASE_DIR/domains/icewind_dale/ten_towns/targos/rooms.py" || echo "File domains/icewind_dale/ten_towns/targos/rooms.py already exists, skipping creation."

touch "$BASE_DIR/domains/icewind_dale/rooms.py" || echo "File domains/icewind_dale/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/icewind_dale/npcs.py" || echo "File domains/icewind_dale/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/icewind_dale/items.py" || echo "File domains/icewind_dale/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/calimshan"
mkdir -p "$BASE_DIR/domains/calimshan/calimport"
touch "$BASE_DIR/domains/calimshan/calimport/rooms.py" || echo "File domains/calimshan/calimport/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/calimshan/calimport/npcs.py" || echo "File domains/calimshan/calimport/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/calimshan/calimport/items.py" || echo "File domains/calimshan/calimport/items.py already exists, skipping creation."
touch "$BASE_DIR/domains/calimshan/calimport/guilds.py" || echo "File domains/calimshan/calimport/guilds.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/calimshan/memnon"
touch "$BASE_DIR/domains/calimshan/memnon/rooms.py" || echo "File domains/calimshan/memnon/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/calimshan/memnon/npcs.py" || echo "File domains/calimshan/memnon/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/calimshan/memnon/items.py" || echo "File domains/calimshan/memnon/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/vast_swamp"
touch "$BASE_DIR/domains/vast_swamp/rooms.py" || echo "File domains/vast_swamp/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/vast_swamp/npcs.py" || echo "File domains/vast_swamp/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/vast_swamp/items.py" || echo "File domains/vast_swamp/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/vast_swamp/villages"
mkdir -p "$BASE_DIR/domains/vast_swamp/villages/mossbridge"
touch "$BASE_DIR/domains/vast_swamp/villages/mossbridge/rooms.py" || echo "File domains/vast_swamp/villages/mossbridge/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/damara"
mkdir -p "$BASE_DIR/domains/damara/heliogabalus"
touch "$BASE_DIR/domains/damara/heliogabalus/rooms.py" || echo "File domains/damara/heliogabalus/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/damara/heliogabalus/npcs.py" || echo "File domains/damara/heliogabalus/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/damara/heliogabalus/items.py" || echo "File domains/damara/heliogabalus/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/damara/villages"
mkdir -p "$BASE_DIR/domains/damara/villages/bloodstone"
touch "$BASE_DIR/domains/damara/villages/bloodstone/rooms.py" || echo "File domains/damara/villages/bloodstone/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/anauroch"
touch "$BASE_DIR/domains/anauroch/rooms.py" || echo "File domains/anauroch/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/anauroch/npcs.py" || echo "File domains/anauroch/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/anauroch/items.py" || echo "File domains/anauroch/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/high_forest"
touch "$BASE_DIR/domains/high_forest/rooms.py" || echo "File domains/high_forest/rooms.py already exists, skipping creation."
touch "$BASE_DIR/domains/high_forest/npcs.py" || echo "File domains/high_forest/npcs.py already exists, skipping creation."
touch "$BASE_DIR/domains/high_forest/items.py" || echo "File domains/high_forest/items.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/high_forest/settlements"
mkdir -p "$BASE_DIR/domains/high_forest/settlements/star_mount"
touch "$BASE_DIR/domains/high_forest/settlements/star_mount/rooms.py" || echo "File domains/high_forest/settlements/star_mount/rooms.py already exists, skipping creation."

mkdir -p "$BASE_DIR/domains/world"
touch "$BASE_DIR/domains/world/terrain.py" || echo "File domains/world/terrain.py already exists, skipping creation."
touch "$BASE_DIR/domains/world/weather.py" || echo "File domains/world/weather.py already exists, skipping creation."
touch "$BASE_DIR/domains/world/events.py" || echo "File domains/world/events.py already exists, skipping creation."

# Create players/ directory and files
mkdir -p "$BASE_DIR/players"
touch "$BASE_DIR/players/mystra.json" || echo "File players/mystra.json already exists, skipping creation."
touch "$BASE_DIR/players/tyr.json" || echo "File players/tyr.json already exists, skipping creation."
touch "$BASE_DIR/players/lolth.json" || echo "File players/lolth.json already exists, skipping creation."
touch "$BASE_DIR/players/oghma.json" || echo "File players/oghma.json already exists, skipping creation."
touch "$BASE_DIR/players/deneir.json" || echo "File players/deneir.json already exists, skipping creation."
touch "$BASE_DIR/players/selune.json" || echo "File players/selune.json already exists, skipping creation."
touch "$BASE_DIR/players/torm.json" || echo "File players/torm.json already exists, skipping creation."
touch "$BASE_DIR/players/vhaeraun.json" || echo "File players/vhaeraun.json already exists, skipping creation."
touch "$BASE_DIR/players/azuth.json" || echo "File players/azuth.json already exists, skipping creation."

# Create logs/ directory and files
mkdir -p "$BASE_DIR/logs"
touch "$BASE_DIR/logs/server.log" || echo "File logs/server.log already exists, skipping creation."
touch "$BASE_DIR/logs/ai.log" || echo "File logs/ai.log already exists, skipping creation."

# Create website/ directory and its substructure
mkdir -p "$BASE_DIR/website"
touch "$BASE_DIR/website/index.html" || echo "File website/index.html already exists, skipping creation."
touch "$BASE_DIR/website/client.js" || echo "File website/client.js already exists, skipping creation."

mkdir -p "$BASE_DIR/website/marketing"
touch "$BASE_DIR/website/marketing/promo.html" || echo "File website/marketing/promo.html already exists, skipping creation."

mkdir -p "$BASE_DIR/website/marketing/banners"

# Remove ai/ directory and its contents
if [ -d "$BASE_DIR/ai" ]; then
    rm -rf "$BASE_DIR/ai"
    echo "Removed ai/ directory and all contents."
else
    echo "ai/ directory does not exist, no action taken."
fi

echo "Directory structure and stub files creation complete. ai/ directory removed."
