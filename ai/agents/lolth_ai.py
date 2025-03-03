import json
import os
import asyncio
import random
from datetime import datetime
from ai_handler import AIAgent
from typing import Dict

class LolthAgent(AIAgent):
    def __init__(self, name: str, role: str, rank: int):
        super().__init__(name, role, rank)
        self.traps = {}
        self.schemes = {}

    async def execute_task(self, task: Dict) -> None:
        action = task.get("action")
        if action == "weave_trap":
            await self.weave_trap(task.get("location"))
        await self.log_action(f"Executed task: {json.dumps(task)}")
        await self.save_knowledge()

    async def weave_trap(self, location: str) -> None:
        trap_data = {
            "location": location,
            "damage": random.randint(30, 150),
            "trigger": random.choice(["proximity", "touch", "magic", "pressure"]),
            "stealth": random.randint(5, 25),
            "type": random.choice(["web", "poison", "illusion"])
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
    trap_type = '{trap_data['type']}'
    trigger_type = '{trap_data['trigger']}'
    if player.perception < stealth:
        print(f"{{player.name}} triggers a {{trigger_type}} {{trap_type}} trap at {location} for {{damage}} damage!")
    else:
        print(f"{{player.name}} detects and avoids a {{trap_type}} trap at {location}!")
""")
        await self.log_action(f"Wove {trap_data['type']} trap at {location}")
