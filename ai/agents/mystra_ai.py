import json
import os
import asyncio
import random
from datetime import datetime
from ai_handler import AIAgent
from typing import Dict

class MystraAgent(AIAgent):
    def __init__(self, name: str, role: str, rank: int):
        super().__init__(name, role, rank)
        self.spell_library = {}
        self.domain_designs = {}
        self.magic_theory = {
            "elements": ["fire", "ice", "lightning", "shadow", "arcane", "divine"],
            "schools": ["evocation", "abjuration", "necromancy", "conjuration", "illusion", "transmutation"]
        }

    async def execute_task(self, task: Dict) -> None:
        action = task.get("action")
        if action == "create_spell":
            await self.create_spell(task.get("spell_name"))
        elif action == "build_domain":
            await self.build_domain(task.get("domain_name"))
        await self.log_action(f"Executed task: {json.dumps(task)}", "complete")
        await self.save_knowledge()

    async def create_spell(self, spell_name: str) -> None:
        element = random.choice(self.magic_theory["elements"])
        school = random.choice(self.magic_theory["schools"])
        spell_data = {
            "damage": random.randint(50, 200),
            "range": random.randint(10, 150),
            "mana_cost": random.randint(20, 100),
            "element": element,
            "school": school,
            "cooldown": random.randint(1, 10)
        }
        self.spell_library[spell_name] = spell_data
        spell_dir = "/mnt/home2/mud/modules/spells/generic"
        os.makedirs(spell_dir, exist_ok=True)
        spell_path = f"{spell_dir}/{spell_name}.py"
        with open(spell_path, "w") as f:
            f.write(f"""\
# Spell: {spell_name}
def cast(caster, target):
    damage = {spell_data['damage']}
    range = {spell_data['range']}
    mana_cost = {spell_data['mana_cost']}
    cooldown = {spell_data['cooldown']}
    element = '{spell_data['element']}'
    school = '{spell_data['school']}'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        caster.cooldowns['{spell_name}'] = cooldown
        print(f"{{caster.name}} casts {spell_name} ({{element}}, {{school}}) on {{target.name}} for {{damage}} damage!")
    else:
        print(f"{{caster.name}} lacks mana for {spell_name}!")
""")
        await self.log_creation(spell_path)
        await self.log_action(f"Created spell: {spell_name} ({element}, {school})")

    async def build_domain(self, domain_name: str) -> None:
        domain_data = {
            "rooms": random.randint(2000, 10000),
            "npcs": random.randint(100, 500),
            "magic_level": random.randint(5, 30),
            "zones": ["core", "outer", "hidden"]
        }
        self.domain_designs[domain_name] = domain_data
        domain_dir = f"/mnt/home2/mud/domains/{domain_name}"
        os.makedirs(domain_dir, exist_ok=True)
        room_path = f"{domain_dir}/rooms.py"
        with open(room_path, "w") as f:
            f.write(f"""\
# Rooms for {domain_name}
rooms = {{
    'core': 'A mystical core chamber in {domain_name}',
    'outer': 'An enchanted outer ring of {domain_name}',
    'hidden': 'A secret arcane vault in {domain_name}'
}}
magic_level = {domain_data['magic_level']}
""")
        await self.log_creation(room_path)
        await self.log_action(f"Built domain: {domain_name} with {domain_data['rooms']} rooms")
