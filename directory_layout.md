Last login: Tue Mar  4 09:56:03 2025 from 192.168.20.12
archaon@archaon:~$ cd /mnt/home2/mud
archaon@archaon:/mnt/home2/mud$ ls -R
.:
ai                          fix_ai_handler_indent.sh      output.log
AI_README.md                fix_ai_handler_log_scrape.sh  PLAN.md
conversation_log_grok1.txt  fix_ai_logs.sh                players
conversation_log_grok2.txt  Groks_ReadMe                  __pycache__
conversation_log_grok3.txt  logs                          std
create_dirs.sh              master_ai_handler.py          tasks.txt
create_mud_structure.sh     modules                       website
data                        mud_logger                    WEBSITE_LINKS.txt
domains                     mud_logger.py                 world_map.txt
fix_ai_errors.sh            mud.py
./ai:
agents              ai_handler.py.bak3  ai_oghma.py   ai_umberlee.py
ai_ao.py            ai_helm.py          ai_selûne.py  knowledge
ai_bane.py          ai_kelemvor.py      ai_tempus.py  __pycache__
ai_handler.py.bak   ai_lathander.py     ai_torm.py
ai_handler.py.bak2  ai_mystra.py        ai_tyr.py
./ai/agents:
ao_ai.py      lolth_ai.py   __pycache__   tyr_ai.py
azuth_ai.py   mystra_ai.py  selune_ai.py  vhaeraun_ai.py
deneir_ai.py  oghma_ai.py   torm_ai.py
./ai/agents/__pycache__:
ao_ai.cpython-311.pyc      oghma_ai.cpython-311.pyc
azuth_ai.cpython-311.pyc   selune_ai.cpython-311.pyc
deneir_ai.cpython-311.pyc  torm_ai.cpython-311.pyc
lolth_ai.cpython-311.pyc   tyr_ai.cpython-311.pyc
mystra_ai.cpython-311.pyc  vhaeraun_ai.cpython-311.pyc
./ai/knowledge:
ao_knowledge.json          oghma_knowledge.json
ao_knowledge.json.bak      oghma_knowledge.json.bak
azuth_knowledge.json       selune_knowledge.json
azuth_knowledge.json.bak   selune_knowledge.json.bak
deneir_knowledge.json      torm_knowledge.json
deneir_knowledge.json.bak  torm_knowledge.json.bak
lolth_knowledge.json       tyr_knowledge.json
lolth_knowledge.json.bak   tyr_knowledge.json.bak
mystra_knowledge.json      vhaeraun_knowledge.json
mystra_knowledge.json.bak  vhaeraun_knowledge.json.bak
./ai/__pycache__:
ai_handler.cpython-311.pyc
./data:
db  embeddings
./data/db:
mud_data.db
./data/embeddings:
./domains:
anauroch   cormanthor  high_forest   sword_coast  vast_swamp
calimshan  damara      icewind_dale  underdark    world
./domains/anauroch:
./domains/calimshan:
calimport  memnon
./domains/calimshan/calimport:
./domains/calimshan/memnon:
./domains/cormanthor:
villages
./domains/cormanthor/villages:
elventree  tangled_trees
./domains/cormanthor/villages/elventree:
./domains/cormanthor/villages/tangled_trees:
./domains/damara:
villages
./domains/damara/villages:
bloodstone
./domains/damara/villages/bloodstone:
./domains/high_forest:
settlements
./domains/high_forest/settlements:
star_mount
./domains/high_forest/settlements/star_mount:
./domains/icewind_dale:
ten_towns
./domains/icewind_dale/ten_towns:
bryn_shander  targos
./domains/icewind_dale/ten_towns/bryn_shander:
./domains/icewind_dale/ten_towns/targos:
./domains/sword_coast:
baldur_gate  daggerford  neverwinter  waterdeep
candlekeep   luskan      phandalin
./domains/sword_coast/baldur_gate:
./domains/sword_coast/candlekeep:
./domains/sword_coast/daggerford:
./domains/sword_coast/luskan:
./domains/sword_coast/neverwinter:
./domains/sword_coast/phandalin:
./domains/sword_coast/waterdeep:
castle  docks  market
./domains/sword_coast/waterdeep/castle:
./domains/sword_coast/waterdeep/docks:
./domains/sword_coast/waterdeep/market:
./domains/underdark:
ched_nasad  gracklstugh  menzoberranzan  sshamath
./domains/underdark/ched_nasad:
./domains/underdark/gracklstugh:
./domains/underdark/menzoberranzan:
houses
./domains/underdark/menzoberranzan/houses:
house_baenre  house_noquar
./domains/underdark/menzoberranzan/houses/house_baenre:
./domains/underdark/menzoberranzan/houses/house_noquar:
./domains/underdark/sshamath:
./domains/vast_swamp:
villages
./domains/vast_swamp/villages:
mossbridge
./domains/vast_swamp/villages/mossbridge:
./domains/world:
./logs:
./modules:
achievements.py    finger.py             organizations      skills.py
armors.py          guilds.py             parry.py           soul_handler.py
block.py           help.py               party.py           soul.py
classes            inventory_handler.py  __pycache__        spell_handler.py
classes.py         inventory.py          quests_handler.py  spells
combat             layers.py             quests.py          spells.py
combat_handler.py  login_handler.py      races              systems
combat.py          login.py              races.py           tactics.py
commands           maps.py               ritual_handler.py  term_handler.py
crafts             mounts.py             rituals            weapons.py
creation.py        mud.py                rituals.py         weather.py
dodge.py           network_handler.py    room.py            world.py
emote.py           npcs.py               skills_handler.py
./modules/classes:
generic  racial
./modules/classes/generic:
./modules/classes/racial:
drow  elf
./modules/classes/racial/drow:
./modules/classes/racial/elf:
./modules/commands:
inventory.py  kill.py  look.py
./modules/crafts:
culinary  mining  smithing
./modules/crafts/culinary:
./modules/crafts/mining:
./modules/crafts/smithing:
./modules/organizations:
drow_houses  orc_clans
./modules/organizations/drow_houses:
./modules/organizations/orc_clans:
./modules/__pycache__:
combat_handler.cpython-311.pyc     ritual_handler.cpython-311.pyc
deities.cpython-311.pyc            skills.cpython-311.pyc
inventory_handler.cpython-311.pyc  skills_handler.cpython-311.pyc
login.cpython-311.pyc              soul_handler.cpython-311.pyc
login_handler.cpython-311.pyc      term_handler.cpython-311.pyc
network_handler.cpython-311.pyc
./modules/races:
./modules/rituals:
./modules/spells:
abyssal_summons.py  fireball.py    lunar_wyrm.py   thunder_lance.py
arcane_aegis.py     flame_ward.py  racial
class               generic        shadow_gate.py
./modules/spells/class:
cleric  wizard
./modules/spells/class/cleric:
./modules/spells/class/wizard:
./modules/spells/generic:
./modules/spells/racial:
drow  elf
./modules/spells/racial/drow:
./modules/spells/racial/elf:
./modules/systems:
combat.py
./mud_logger:
mud_session_001.json
./players:
./__pycache__:
master_ai_handler.cpython-311.pyc  mud.cpython-311.pyc
./std:
command.py  container.py  living.py  object.py  room.py  wearable.py
./website:
marketing
./website/marketing:
banners
./website/marketing/banners:
