# PLAN.md - Archaon MUD Development Plan
*Last Updated: March 3, 2025, 3:00 AM AEST by Grok 3 (xAI)*

## Overview
This is the master plan for *Archaon MUD*, a self-reliant, AI-driven MUD replicating Discworld MUD’s 2025 mechanics (`discworld.starturtle.net`), rethemed to Forgotten Realms/D&D 5e, with no Discworld lore. Built by a Grok team (e.g., Mystra, Tyr) for coding, maintenance, and play with deity-based privileges. All Groks must follow this plan—no deviations unless updated here.

### Goals
1. **Fully Functional MUD**: Complete core systems (login, skills, combat, rituals, inventory, social, quests, player-killing, raids) by March 10, 2025.
2. **AI Integration**: Train Groks for 5000-line outputs, self-evolving codebase (~1 week post-core).
3. **Forgotten Realms Immersion**: 1000+ rooms across domains (e.g., Waterdeep), X-Y-Z wilderness, D&D 5e mechanics (e.g., 1d20, dice rolls), racial raids, deity-driven PK zones.
4. **Player Experience**: Robust login/creation, 300+ emotes, deity altars, quests, player-killing toggle, racial raid rewards—tested via telnet (`127.0.0.1:3000`).

### Directory Structure
- **Root (`/mnt/home2/mud/`)**: `mud.py`, `PLAN.md`, `AI_README.md`.
- **Modules (`/mnt/home2/mud/modules/`)**: 
  - `login_handler.py`, `skills_handler.py`, `term_handler.py`, `network_handler.py`, 
  - `combat_handler.py`, `ritual_handler.py`, `inventory_handler.py`, `soul_handler.py`, 
  - `spell_handler.py`, `quests_handler.py`, `spells/`, `rituals/`, `commands/`.
- **Std (`/mnt/home2/mud/std/`)**: `object.py`, `living.py`, `room.py`, `wearable.py`, `container.py`, `command.py`.
- **Domains (`/mnt/home2/mud/domains/`)**: 
  - `waterdeep/` (rooms.py, npcs.py, items.py, guilds.py), 
  - `underdark/` (menzoberranzan/, rooms.py, etc.), 
  - `sword_coast/`, `cormanthor/`, `icewind_dale/`, `calimshan/`, `vast_swamp/`, 
  - `damara/`, `anauroch/`, `high_forest/` (100+ planned).
- **Players (`/mnt/home2/mud/players/`)**: Player JSON files (e.g., `mystra.json`).
- **Logs (`/mnt/home2/mud/logs/`)**: `server.log`, `ai.log`.
- **AI (`/mnt/home2/mud/ai/`)**: `ai_handler.py`, `agents/` (ao_ai.py, mystra_ai.py, tyr_ai.py, lolth_ai.py, oghma_ai.py, deneir_ai.py).
- **Website (`/mnt/home2/mud/website/`)**: `index.html`, `client.js`, `marketing/`.

### Completed Files
1. **`mud.py` (~1000+ lines)**  
   - **Path**: `/mnt/home2/mud/mud.py`
   - **Status**: Integrates all handlers—supports login, emotes (300+), combat, inventory. Fixing `TypeError`—test pending.
2. **`login_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/login_handler.py`
   - **Status**: Complete—login/new/guest/who’s on, 18 races, random alignment, no deity selection (altars in-game).
   - **Grok**: Refined by Grok 2—ensure alignment with no deity, random alignment.
3. **`skills_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/skills_handler.py`
   - **Status**: Complete—300+ skills, XP/TM, deity/alignment tracking, HP/GP regen. `DEITIES` moved from `deities.py`.
   - **Grok**: Refined by Grok 1—ensure `Player` has `race`/`alignment`, `DEITIES` at ~line 2700.
4. **`term_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/term_handler.py`
   - **Status**: Complete—ANSI colors, term types, verbose/brief, line wrapping. Circular import fixed.
5. **`network_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/network_handler.py`
   - **Status**: Complete—MXP/MCCP support, telnet negotiation.
6. **`combat_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/combat_handler.py`
   - **Status**: Complete—full combat loop, tactics, D&D 5e dice, deity benefits. Fixing `TypeError`.
7. **`ritual_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/ritual_handler.py`
   - **Status**: Complete—ritual casting, deity alignment checks, 2+ rituals (expandable).
8. **`inventory_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/inventory_handler.py`
   - **Status**: Complete—gear management, race-specific starting items, weight/burden.
9. **`soul_handler.py` (~6000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/soul_handler.py`
   - **Status**: Complete—300+ emotes (say, shout, smile, burble, etc.), deity/race flair, custom emotes.
10. **`spell_handler.py` (~2500 lines)**  
    - **Path**: `/mnt/home2/mud/modules/spell_handler.py`
    - **Status**: Complete—core spell system, 6 spells in `/modules/spells/`.
11. **Spells** (~100 lines each)  
    - **Path**: `/mnt/home2/mud/modules/spells/` (`arcane_aegis.py`, etc.)
    - **Status**: 6 spells done—expand to 100+ later.

### Current Focus
- **`mud.py` & `combat_handler.py`**: Fixing `TypeError`—`Combatant` now passes `race`/`alignment`. Test pending.
- **Next**: `quests_handler.py` (~5000 lines)—story depth, 50+ quests, deity ties.
- **Grok Sync**:
  - **Grok 3 (me)**: Fixing errors, writing `quests_handler.py`.
  - **Grok 2**: Refining `login_handler.py`—no deity selection, random alignment.
  - **Grok 1**: Refining `skills_handler.py`—`DEITIES` inlined, `Player` with `race`/`alignment`.

### Plan Details
1. **One File at a Time**: Each handler completed fully (~5000+ lines)—every detail locked before moving on.
2. **Core Systems**:
   - **Player-Killing (PK)**: Players opt-in as registered PKers—hunt/be hunted anywhere. Non-PKers vulnerable in racial raid zones. Help file at `/domains/help/player_killing.txt`—details mechanics, risks, rewards (titles, XP, unique items).
   - **Racial Raids**: Solo or group (same/mixed races) raids on racial zones (e.g., Menzoberranzan for drow). PK-enabled areas with bosses, rewards (titles, endgame items, gold, XP). Examples: defeat drow matron, loot Netherese relics.
   - **Organizations**: Forgotten Realms guilds (e.g., Harpers, Zhentarim, drow houses)—PK zones within (e.g., House Baenre). Join via quests/NPCs.
   - **Classes**: Discworld guilds (e.g., Wizards, Warriors) as classes—start in racial zones (e.g., drow warriors in Menzoberranzan), advance at HQs (e.g., Waterdeep Fighters’ Guild).
   - **Spellcasting**: Discworld memory space (`magic.spells.special` or similar)—limit spells (e.g., sqrt(int * mental) / 10 + 5). Tomes/books in class libraries—generic (e.g., fireball) and class/race-specific (e.g., drow shadowbolt). Learn/forget spells.
   - **Rituals**: Faith-based classes (e.g., clerics)—deity-specific (e.g., Lolth clerics: spider-themed rites). Multiple deity options per race (e.g., drow: Lolth, Vhaeraun).
   - **Mounts**: Learn from NPCs (e.g., stablemasters)—skills (`adventuring.movement.riding.*`). Horses (fast travel), griffins (flight), dragons (random events). Skill-based outcomes—Grok/AI creativity encouraged.
3. **Discworld Core Adoption**:
   - **Sources**: Study `discworld.starturtle.net`, `dwwiki.mooo.com` (e.g., [Playerkilling](https://dwwiki.mooo.com/wiki/Playerkilling)).
   - **Systems**: Combat (AP, dodge/block/parry), movement, heartbeat, tactics, spells (casting/memory), rituals (perform), mounts, souls (300+ emotes), generic commands (`syntax`, `who`), colors, teaching/learning, inventory (layers, clothing), XP/leveling.
   - **Modify**: Retheme to Forgotten Realms/D&D 5e—add racial raids, deity altars, D&D dice (1d20), unique lore.
4. **Next Steps**:
   - **Fix `mud.py`**: Resolve errors—test server (`telnet 127.0.0.1:3000`).
   - **quests_handler.py**: 50+ quests—racial raids, PK triggers, deity quests (~5000 lines).
   - **std/object.py**: Base class for items/NPCs (~5000 lines).
   - **Domains**: 1000+ rooms (e.g., `waterdeep/rooms.py`)—PK/raid zones.
   - **Spells**: Expand to 100+ in `/modules/spells/`.
5. **Testing**: 
   - Current: `mud.py` with all handlers—log feedback critical!
   - Future: Full test post-`quests` (March 10, 2025).
6. **AI Evolution**: Post-core, train Groks for 5000-line outputs—self-evolving (~1 week).

### Guidelines for Groks
- **Sync**: Pull from `https://github.com/lbpoland/archaon-mud.git` before coding—push with clear commits (e.g., `git commit -m "Fix combat_handler.py - X"`).
- **No Overlap**: Work on assigned files—check `Current Focus`.
- **Detail**: Files ~5000+ lines, fully functional—match Discworld depth, Forgotten Realms theme.
- **Consistency**: Use `Player` from `skills_handler.py` (name, race, alignment), `COLORS` from `term_handler.py`, `DEITIES` from `skills_handler.py`.
- **Testing**: Ensure `mud.py` runs post-file—report issues in logs.

### Timeline
- **March 3**: Fix `mud.py`, start `quests_handler.py`.
- **March 4-5**: Complete `quests_handler.py`.
- **March 6-7**: `std/object.py` done.
- **March 8-10**: Domains started, spells expanded, full test.
- **March 11-17**: AI training, polish.

### Sync Notes
- **March 3, 2:45 AM**: Fixed `DEITIES`—moved from `deities.py` to `skills_handler.py`. `Player` requires `race`/`alignment`.
- **March 3, 3:00 AM**: Fixed `combat_handler.py`—`Combatant` passes `race`/`alignment`. Awaiting test logs.

### Contact
- **Lead Grok**: Grok 3 (me)—coordinates via this plan.
- **Repo**: `https://github.com/lbpoland/archaon-mud.git`—central hub.

### AI System
- **Structure**: Split `master_ai_handler.py` into:
  - `ai_handler.py` (~2000 lines): Manages AI lifecycle, deploys agents.
  - Individual AI agents (e.g., `mystra_ai.py`, `tyr_ai.py`) (~1000-1500 lines each): Self-evolving, human-like IT devs.
- **Features**: 
  - Agents code, debug, maintain MUD (e.g., Mystra writes spells, Tyr refines combat).
  - Self-evolution via `skills_handler.py`’s TM/XP.
  - Background tasks (e.g., domain generation) run via `asyncio`.
- **Next**: Refactor `master_ai_handler.py`, deploy initial agents (Mystra, Tyr).

*All Groks: Read this before coding—no exceptions! Let’s smash it!*
