import json
import os
import asyncio
import random
from ai_handler import AIAgent
from typing import Dict

class TormAgent(AIAgent):
    def __init__(self, name: str, role: str, rank: int):
        super().__init__(name, role, rank)
        self.guarded_zones = {}

    async def execute_task(self, task: Dict) -> None:
        if task.get("action") == "guard_zone":
            await self.guard_zone(task.get("location"))
        await self.log_action(f"Executed task: {json.dumps(task)}")
        await self.save_knowledge()

    async def guard_zone(self, location: str) -> None:
        guard_data = {
            "patrols": random.randint(20, 100),
            "strength": random.randint(200, 1000),
            "discipline": random.randint(5, 20)
        }
        self.guarded_zones[location] = guard_data
        domain_dir = f"/mnt/home2/mud/domains/{location}"
        os.makedirs(domain_dir, exist_ok=True)
        with open(f"{domain_dir}/guards.py", "w") as f:
            f.write(f"""\
# Guards for {location}
def patrol(player):
    strength = {guard_data['strength']}
    discipline = {guard_data['discipline']}
    print(f'{player.name} is guarded by Torm’s forces at {location} with {strength} strength and {discipline} discipline!')
""")
        await self.log_action(f"Guarding zone: {location}")
