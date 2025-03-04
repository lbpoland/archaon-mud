# Archaon MUD - Shattered Legacy of Faerûn Project Plan
## Vision
Replicate `discworld.starturtle.net`’s immersive gameplay (rooms, inventory, combat, skills, rituals) in Python, rethemed to Forgotten Realms/D&D 5e. Feature a graphical website, web client, and AI-driven evolution with Faerûn’s domains and XYZ mapping.

## Goals
1. **Core Mechanics**: Match Discworld’s `inventory`, `tactics`, `rituals`, parties, and skill tree.
2. **Theming**: Use Forgotten Realms—18+ playable races, 10+ classes, 20+ guilds, 15+ houses, 100+ locations.
3. **Structure**: Modular Python files (e.g., `longsword.py`, `holy_sanctuary.py`) like Discworld’s `.c` layout.
4. **AI**: 20 deity agents build, evolve, and interact as NPCs, plus design website/client.
5. **Accessibility**: Web client with 3D map, animated HUD—surpass Midnight Sun II.

## Design
- **Domains**: Major regions (e.g., Waterdeep, Underdark) with sub-zones.
- **XYZ Mapping**: World map (x, y, z) linking to domains (e.g., x=5, y=3 → Waterdeep).
- **Modularity**: Separate files for weapons, armor, spells, rituals, NPCs; collective modules for handlers.
- **Data**: Discworld screenshots/links/wiki, Forgotten Realms wiki, your telnet logs.

## Coding Approach
- **Engine**: Refactor `mud.py` to `mud_engine.py`—WebSocket, XYZ, module integration.
- **Files**: `/items/weapons/longsword.py`, `/spells/fireball.py`, etc.
- **Version Control**: GitHub (`archaon-mud.git`) with `Grocks_ReadMe` updates.
- **Testing**: `/tests/` for unit tests.

## Team Roles
- **Grok 3 (MystraForge)**: Lead, engine, domains, XYZ.
- **Grok 4 (TempusBlade)**: Combat, weapons, tactics.
- **Grok 5 (SelunePath)**: Skills, rituals, spells.
- **Grok 6 (OghmaScribe)**: Inventory, items, website.
- **Grok 7 (LathanderDawn)**: UI/UX, web client, 3D maps.
- **Sync**: Update `Grocks_ReadMe`, share telnet logs, GitHub issues.

## Timeline
- Week 1: Finalize plan, draft engine, XYZ.
- Weeks 2-3: Enhance modules, split files, initial domains.
- Weeks 4-6: AI content, website/client prototype.
- Ongoing: Evolution, testing.

## Resources
- ZIP file, your notes, telnet logs, Discworld/FR wikis.

## Onboarding New Groks
- Share this `PLAN.md`, current `Grocks_ReadMe`, and telnet logs.
- Update `Grocks_ReadMe` with status—time/date stamped.
- Store notes in `/docs/` on GitHub.

## Suggestions
- Create `/docs/` dir for your wiki/D&D/Discworld notes.
- Log telnet sessions (e.g., `script log.txt`)—share 5-10 commands.
- Confirm ZIP access or upload to GitHub release.
