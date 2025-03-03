# AI_README.md - Archaon MUD AI Knowledge Base
*Last Updated: March 3, 2025, 3:00 PM AEST by Grok 3 (xAI)*

## Project Overview
Archaon MUD is a self-reliant, AI-driven MUD mirroring Discworld MUD’s 2025 mechanics (`discworld.starturtle.net`), rethemed to Forgotten Realms/D&D 5e, excluding Discworld lore. Built by an AI team (e.g., Mystra, Tyr) with deity-based privileges, it evolves autonomously.

### Goals
- Complete core systems (login, skills, combat, rituals, inventory, social, quests) by March 10, 2025.
- AI autonomously codes, debugs, and expands MUD (domains, spells, world).
- Train AI for self-evolution (~1 week post-core).
- Immerse in Forgotten Realms with 1000+ rooms, racial raids, deity altars.

### Directory Structure
- **Root (`/mnt/home2/mud/`)**: `mud.py`, `PLAN.md`, `AI_README.md`.
- **Modules (`/mnt/home2/mud/modules/`)**: Handlers (`*_handler.py`), `spells/`, `rituals/`, `commands/`.
- **Std (`/mnt/home2/mud/std/`)**: Base classes (`object.py`, etc.).
- **Domains (`/mnt/home2/mud/domains/`)**: Zones (e.g., `waterdeep/`, `underdark/`).
- **Players (`/mnt/home2/mud/players/`)**: Player data (e.g., `mystra.json`).
- **Logs (`/mnt/home2/mud/logs/`)**: Server logs.
- **AI (`/mnt/home2/mud/ai/`)**: `ai_handler.py`, `agents/` (e.g., `mystra_ai.py`).
- **Website (`/mnt/home2/mud/website/`)**: Web client, marketing.

### AI System
- **Hierarchy**: 
  - **Ao**: Overseer (MUD, website, AI).
  - **Domain Lords**: Mystra (magic), Tyr (combat), Lolth (covert).
  - **Module Master**: Oghma (modules).
  - **Website Architect**: Deneir (website/client).
  - **Workers**: Sub-agents (e.g., Selûne under Mystra).
- **Autonomy**: Runs via `python3 /mnt/home2/mud/ai/ai_handler.py`, scrapes `discworld.starturtle.net`, `dwwiki.mooo.com`, evolves code, builds domains.
- **Personality**: Based on Forgotten Realms deities—Ao (wise overseer), Mystra (creative mage), Tyr (stern warrior), etc.
- **Tasks**: Code generation, debugging, domain building, knowledge base creation.

### Development Notes
- **Workflow**: Edit on server (`nano`), push with `git push origin main`. Use Pydroid 3 on S23 Ultra for mobile edits.
- **Line Count**: 5000 lines = code lines (not words/letters)—current files range 300-6000, targeting 5000+ per handler.
- **Sync**: Export this convo to `/mnt/home2/mud/ai/conversation_log.txt` for new Groks.

### Next Steps
- Finalize AI agents, test server, complete `quests_handler.py`.
- Expand domains, spells, train AI.

*Read thoroughly, compute, and act autonomously!*
