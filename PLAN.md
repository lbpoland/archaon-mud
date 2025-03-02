# PLAN.md - Archaon MUD Development Plan
*Last Updated: March 3, 2025, 2:00 AM AEST by Grok 3 (xAI)*

## Overview
This is the master plan for *Archaon MUD*, a self-reliant, AI-driven MUD replicating Discworld MUD’s 2025 mechanics (`discworld.starturtle.net`), rethemed to Forgotten Realms/D&D 5e, with no Discworld lore. Built by a Grok team (e.g., Mystra, Tyr) for coding, maintenance, and play with deity-based privileges. All Groks must follow this plan—no deviations unless updated here.

### Goals
1. **Fully Functional MUD**: Complete core systems (login, skills, combat, rituals, inventory, social, quests) by March 10, 2025.
2. **AI Integration**: Train Groks for 5000-line outputs, self-evolving codebase (~1 week post-core).
3. **Forgotten Realms Immersion**: 1000+ rooms across domains (e.g., Waterdeep), X-Y-Z wilderness, D&D 5e mechanics (e.g., 1d20, dice rolls).
4. **Player Experience**: Robust login/creation, 300+ emotes, deity altars, quests—tested via telnet (`127.0.0.1:3000`).

### Directory Structure
- **Root (`/mnt/home2/mud/`)**: `mud.py` (main server), `PLAN.md` (this file).
- **Modules (`/mnt/home2/mud/modules/`)**: Core handlers (`*_handler.py`), `spells/` (individual spells), `rituals/` (future), `commands/` (individual commands).
- **Std (`/mnt/home2/mud/std/`)**: Base classes (`object.py`, etc.)—pending.
- **Domains (`/mnt/home2/mud/domains/`)**: Zones (e.g., `waterdeep/rooms.py`)—pending.
- **Players (`/mnt/home2/mud/players/`)**: Player data (e.g., `archaon.json`).
- **Logs (`/mnt/home2/mud/logs/`)**: Server logs—pending.
- **AI (`/mnt/home2/mud/ai/`)**: Legacy files (e.g., `skills.py`), AI scripts—pending.

### Completed Files
1. **`mud.py` (~1000+ lines)**  
   - **Path**: `/mnt/home2/mud/mud.py`
   - **Status**: Fully integrates all handlers—supports login, emotes (300+), combat, inventory, etc. Testable via telnet.
2. **`login_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/login_handler.py`
   - **Status**: Complete—login/new/guest/who’s on, 18 races, random alignment, no deity selection (altars in-game).
   - **Grok**: Being refined by another Grok—ensure alignment with this plan.
3. **`skills_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/skills_handler.py`
   - **Status**: Complete—300+ skills, XP/TM, deity/alignment tracking, HP/GP regen.
   - **Grok**: Being refined by another Grok—ensure deity altar mechanics align.
4. **`term_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/term_handler.py`
   - **Status**: Complete—ANSI colors, term types, verbose/brief, line wrapping.
5. **`network_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/network_handler.py`
   - **Status**: Complete—MXP/MCCP support, telnet negotiation.
6. **`combat_handler.py` (~5000 lines)**  
   - **Path**: `/mnt/home2/mud/modules/combat_handler.py`
   - **Status**: Complete—full combat loop, tactics, D&D 5e dice, deity benefits.
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
    - **Path**: `/mnt/home2/mud/modules/spells/` (`arcane_aegis.py`, `flame_ward.py`, etc.)
    - **Status**: 6 spells done—expand to 100+ later.

### Current Focus
- **`mud.py`**: Updated and pushed—server-ready for testing (`telnet 127.0.0.1:3000`). Awaiting logs.
- **`soul_handler.py`**: Fully complete at ~6000 lines—300+ emotes, no further tweaks needed now.
- **Next**: `quests_handler.py` (~5000 lines)—story depth, fully polished, no revisits.

### Plan Details
1. **One File at a Time**: Each handler completed fully (~5000+ lines) before moving on—every detail locked in.
2. **Current Task**: 
   - **Grok 3 (me)**: Writing `quests_handler.py`—quests, objectives, rewards, deity ties.
   - **Grok 2**: Refining `login_handler.py`—ensure alignment with no deity selection, random alignment.
   - **Grok 1**: Refining `skills_handler.py`—ensure deity altar mechanics match `ritual_handler.py`.
3. **Next Steps**:
   - Finish `quests_handler.py` (~5000 lines)—story system, 50+ quests.
   - Move to `std/object.py`—base class for items/NPCs (~5000 lines).
   - Expand `domains/`—1000+ rooms (e.g., `waterdeep/rooms.py`).
   - Add 100+ spells to `/modules/spells/`.
4. **Testing**: 
   - Current: `mud.py` with all handlers—telnet `127.0.0.1:3000`. Log feedback critical!
   - Future: Full system test post-`quests` (March 10, 2025).
5. **AI Evolution**: Post-core, train Groks for 5000-line outputs—self-evolving codebase (~1 week).

### Guidelines for Groks
- **Sync**: Pull from `https://github.com/lbpoland/archaon-mud.git` before working—push updates with clear commits (e.g., `git commit -m "Refine login_handler.py - add X"`).
- **No Overlap**: Work on assigned files only—check `Current Focus` above.
- **Detail**: Every file must be ~5000+ lines, fully functional, no placeholders—match Discworld depth, Forgotten Realms theme.
- **Consistency**: Use `Player` from `skills_handler.py`, `COLORS` from `term_handler.py`, deity system from `skills_handler.py`.
- **Testing**: After each file, ensure `mud.py` runs—report issues in logs.

### Timeline
- **March 3**: `mud.py` tested, `quests_handler.py` started.
- **March 4-5**: `quests_handler.py` completed.
- **March 6-7**: `std/object.py` completed.
- **March 8-10**: Domains started, spells expanded, full test.
- **March 11-17**: AI training, polish.

### Contact
- **Lead Grok**: Grok 3 (me)—coordinates via this plan.
- **Repo**: `https://github.com/lbpoland/archaon-mud.git`—central hub.

*All Groks: Read this before coding—no exceptions! Let’s smash it!*
