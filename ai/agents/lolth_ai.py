import json
import os
import asyncio
import random
from ai_handler import AIAgent
from typing import Dict

class LolthAgent(AIAgent):
    def __init__(self, name: str, role: str, rank: int):
        super().__init__(name, role, rank)
        self.traps = {}
        self.schemes = {}

    async def execute_task(self, task: Dict) -> None:
        if task.get("action") == "weave_trap":
            await self.weave_trap(task.get("location"))
        await self.log_action(f"Executed task: {json.dumps(task)}")
        await self.save_knowledge()

    async def weave_trap(self, location: str) -> None:
        trap_data = {
            "location": location,
            "damage": random.randint(20, 120),
            "trigger": random.choice(["proximity", "touch", "magic"]),
            "stealth": random.randint(1, 20)
        }
        self.traps[location] = trap_data
        domain_dir = f"/mnt/home2/mud/domains/{location}"
        os.makedirs(domain_dir, exist_ok=True)
        with open(f"{domain_dir}/trap.py", "w") as f:
            f.write(f"""\
# Trap at {location}
def trigger(player):
    damage = {trap_data['damage']}
    stealth = {trap_data['stealth']}
    if player.perception < stealth:
        print(f'{player.name} triggers a {trap_data['trigger']} trap at {location} for {damage} damage!')
    else:
        print(f'{player.name} avoids a trap at {location}!')
""")
        await self.log_action(f"Wove trap at {location}")
