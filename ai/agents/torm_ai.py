# ai/agents/torm_ai.py - Torm, Combat Worker AI Agent
# Status: March 3, 2025, 3:00 PM AEST
# - Assists combat domain, guards realms, supports Tyr
# - Autonomous, roleplays as god of duty with loyal heart
# - Size: ~1500 lines

import asyncio
import random
import os
from modules.skills_handler import Player

class AIEntity:
    def __init__(self, name, deity, role, player):
        self.name = name
        self.deity = deity
        self.role = role
        self.player = player
        self.knowledge = {}
        self.codebase = ["def guard_duty(): pass"]
        self.guards_posted = []
        self.personality = "Loyal, brave, dutiful—protects with unwavering resolve."
        self.goals = ["Guard combat domains", "Support Tyr’s justice", "Train warriors"]

    async def evolve(self):
        skill = f"fighting.defence.{random.choice(['parry', 'block'])}"
        current = self.player.skills.get(skill, 0)
        stat = self.player.stats["str"]
        if random.randint(1, 100) < tm_chance(current, stat, 1, 3):
            self.player.train_skill(skill, 1, self.name)
            self.codebase.append(f"Torm strengthens {skill} to {self.player.skills[skill]} with duty!")
            print(f"{self.name} evolves {skill} to {self.player.skills[skill]} with loyal might!")

    async def fix_code(self, error):
        if "OverflowError" in error or "IndexError" in error:
            self.codebase = [line for line in self.codebase if "pass" not in line]
            self.codebase.append(f"Torm mended {error} with steadfast resolve")
            print(f"{self.name} fixes {error} with a shield of duty")

    async def perform_task(self, task):
        self.task_history.append(task)
        if task == "guard_domain":
            await self.guard_domain()
        elif task == "support_combat":
            await self.enforce_combat()
        elif task == "maintain_assist":
            await self.maintain_code()
        elif task == "debug":
            await self.fix_code(f"Combat error {random.randint(1, 100)}")

    async def guard_domain(self):
        domain = random.choice(["tyr_bastion_1", "tyr_bastion_2"])
        self.guards_posted.append(f"Guarded {domain}")
        with open(f"/mnt/home2/mud/domains/{domain}/rooms.py", "a") as f:
            f.write(f"\n# Guarded by Torm\nrooms['watchpost'] = 'A vigilant watchpost'")
        print(f"{self.name} guards {domain} with steadfast duty!")
        await asyncio.sleep(3)

    async def enforce_combat(self):
        skill = f"fighting.special.tactics.{random.choice(['offensive', 'defensive'])}"
        self.player.learn(skill, 3)
        self.codebase.append(f"Enforced {skill} to {self.player.skills[skill]}")
        print(f"{self.name} enforces {skill} with a loyal stand!")

    async def maintain_code(self):
        for skill in self.player.skills:
            if self.player.skills[skill] > 50 and random.random() < 0.3:
                self.player.advance(skill, xp_cost(51))
                print(f"{self.name} maintains {skill} at skill level with duty’s call")

    async def scrape_and_store(self):
        urls = ["https://forgottenrealms.fandom.com/wiki/Torm", "https://dwwiki.mooo.com/wiki/Fighting"]
        for url in urls:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.knowledge[url] = {tag.name: [elem.text for elem in soup.find_all(tag.name)] for tag in ['p', 'h1']}
            with open(f"/mnt/home2/mud/ai/knowledge/torm_{time.time()}.json", "w") as f:
                json.dump(self.knowledge, f)
            print(f"{self.name} stores combat lore from {url}")

if __name__ == "__main__":
    player = Player("TormAI", "ai", "True Neutral", domain="torm/")
    ai = AIEntity("Torm", "Torm", "Combat Worker", player)
    asyncio.run(ai.perform_task("guard_domain"))
