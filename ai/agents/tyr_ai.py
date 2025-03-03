import json
import os
import asyncio
import random
from datetime import datetime
from ai_handler import AIAgent
from typing import Dict

class TyrAgent(AIAgent):
    def __init__(self, name: str, role: str, rank: int):
        super().__init__(name, role, rank)
        self.battlegrounds = {}
        self.combat_rules = {
            "initiative": "d20+DEX",
            "damage_types": ["slashing", "piercing", "bludgeoning", "magical"],
            "stances": ["offensive", "defensive"]
        }

    async def execute_task(self, task: Dict) -> None:
        action = task.get("action")
        if action == "build_battleground":
            await self.build_battleground(task.get("location"))
        await self.log_action(f"Executed task: {json.dumps(task)}", "complete")
        await self.save_knowledge()

    async def build_battleground(self, location: str) -> None:
        bg_data = {
            "location": location,
            "size": random.randint(1000, 5000),
            "enemies": random.randint(20, 200),
            "rules": self.combat_rules,
            "terrain": random.choice(["plains", "forest", "mountain"])
        }
        self.battlegrounds[location] = bg_data
        domain_dir = f"/mnt/home2/mud/domains/{location}"
        os.makedirs(domain_dir, exist_ok=True)
        bg_path = f"{domain_dir}/battleground.py"
        with open(bg_path, "w") as f:
            f.write(f"""\
# Battleground for {location}
def start_fight(player):
    enemies = {bg_data['enemies']}
    terrain = '{bg_data['terrain']}'
    initiative = '{bg_data['rules']['initiative']}'
    print(f"{{player.name}} enters {location} battleground ({{terrain}}) with {{enemies}} foes using {{initiative}} initiative!")
""")
        await self.log_creation(bg_path)
        await self.log_action(f"Built battleground at {location} ({bg_data['terrain']})")
