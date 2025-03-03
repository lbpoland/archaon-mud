import json
import os
import asyncio
import random
from ai_handler import AIAgent
from typing import Dict

class MystraAgent(AIAgent):
    def __init__(self, name: str, role: str, rank: int):
        super().__init__(name, role, rank)
        self.spell_library = {}
        self.domain_designs = {}
        self.magic_theory = {
            "elements": ["fire", "ice", "lightning", "shadow", "arcane"],
            "schools": ["evocation", "abjuration", "necromancy", "conjuration"]
        }

    async def execute_task(self, task: Dict) -> None:
        action = task.get("action")
        if action == "create_spell":
            await self.create_spell(task.get("spell_name"))
        elif action == "build_domain":
            await self.build_domain(task.get("domain_name"))
        await self.log_action(f"Executed task: {json.dumps(task)}")
        await self.save_knowledge()

    async def create_spell(self, spell_name: str) -> None:
        element = random.choice(self.magic_theory["elements"])
        school = random.choice(self.magic_theory["schools"])
        spell_data = {
            "damage": random.randint(20, 150),
            "range": random.randint(5, 100),
            "mana_cost": random.randint(10, 80),
            "element": element,
            "school": school
        }
        self.spell_library[spell_name] = spell_data
        spell_dir = "/mnt/home2/mud/modules/spells/generic"
        os.makedirs(spell_dir, exist_ok=True)
        with open(f"{spell_dir}/{spell_name}.py", "w") as f:
            f.write(f"""\
# Spell: {spell_name}
def cast(caster, target):
    damage = {spell_data['damage']}
    range = {spell_data['range']}
    mana_cost = {spell_data['mana_cost']}
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f'{caster.name} casts {spell_name} ({spell_data['element']}, {spell_data['school']}) on {target.name} for {damage} damage!')
    else:
        print(f'{caster.name} lacks mana for {spell_name}!')
""")
        await self.log_action(f"Created spell: {spell_name}")

    async def build_domain(self, domain_name: str) -> None:
        domain_data = {
            "rooms": random.randint(1000, 5000),
            "npcs": random.randint(50, 300),
            "magic_level": random.randint(1, 20)
        }
        self.domain_designs[domain_name] = domain_data
        domain_dir = f"/mnt/home2/mud/domains/{domain_name}"
        os.makedirs(domain_dir, exist_ok=True)
        with open(f"{domain_dir}/rooms.py", "w") as f:
            f.write(f"""\
# Rooms for {domain_name}
rooms = {{
    'start': 'A grand magical hall in {domain_name}',
    'sanctum': 'A sanctum with magic level {domain_data['magic_level']}'
}}
""")
        await self.log_action(f"Built domain: {domain_name}")
