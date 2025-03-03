#!/bin/bash

# Base directories
mkdir -p /mnt/home2/mud/{std,modules,domains,players,logs,ai/agents,ai/knowledge,website/marketing/banners}

# Modules subdirectories
mkdir -p /mnt/home2/mud/modules/spells/{generic,racial/drow,racial/elf,class/wizard,class/cleric}
mkdir -p /mnt/home2/mud/modules/rituals
mkdir -p /mnt/home2/mud/modules/crafts/{smithing,mining,culinary}
mkdir -p /mnt/home2/mud/modules/classes/{generic,racial/drow,racial/elf}
mkdir -p /mnt/home2/mud/modules/races
mkdir -p /mnt/home2/mud/modules/organizations/{drow_houses,orc_clans}
mkdir -p /mnt/home2/mud/modules/commands

# Domains subdirectories
mkdir -p /mnt/home2/mud/domains/sword_coast/waterdeep/{docks,market,castle}
mkdir -p /mnt/home2/mud/domains/sword_coast/{neverwinter,baldur_gate,candlekeep,daggerford,luskan,phandalin}
mkdir -p /mnt/home2/mud/domains/underdark/menzoberranzan/houses/{house_baenre,house_noquar}
mkdir -p /mnt/home2/mud/domains/underdark/{ched_nasad,gracklstugh,sshamath}
mkdir -p /mnt/home2/mud/domains/cormanthor/villages/{elventree,tangled_trees}
mkdir -p /mnt/home2/mud/domains/icewind_dale/ten_towns/{bryn_shander,targos}
mkdir -p /mnt/home2/mud/domains/calimshan/{calimport,memnon}
mkdir -p /mnt/home2/mud/domains/vast_swamp/villages/mossbridge
mkdir -p /mnt/home2/mud/domains/damara/villages/bloodstone
mkdir -p /mnt/home2/mud/domains/anauroch
mkdir -p /mnt/home2/mud/domains/high_forest/settlements/star_mount
mkdir -p /mnt/home2/mud/domains/world

echo "All directories created in /mnt/home2/mud/"
