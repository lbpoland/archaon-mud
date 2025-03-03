# ai/agents/selune_ai.py - Selûne, Magic Worker AI Agent
# Status: March 3, 2025, 3:00 PM AEST
# - Assists magic domain, enhances spells, supports Mystra
# - Autonomous, roleplays as goddess of the moon with serene grace
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
        self.codebase = ["def illuminate(): pass"]
        self.enhancements = []
        self.personality = "Serene, nurturing, intuitive—basks in lunar light."
        self.goals = ["Enhance magic spells", "Support Mystra’s domains", "Inspire peace"]

    async def evolve(self):
        skill = f"magic.spells.{random.choice(['defensive', 'misc'])}"
        current = self.player.skills.get(skill, 0)
        stat = self.player.stats["wis"]
        if random.randint(1, 100) < tm_chance(current, stat, 1, 3):
            self.player.train_skill(skill, 1, self.name)
            self.codebase.append(f"Selûne enhances {skill} to {self.player.skills[skill]} with moonlight!")
            print(f"{self.name} evolves {skill} to {self.player.skills[skill]} with lunar grace!")

    async def fix_code(self, error):
        if "IndexError" in error or "NameError" in error:
            self.codebase = [line for line in self.codebase if "pass" not in line]
            self.codebase.append(f"Selûne mended {error} with lunar clarity")
            print(f"{self.name} fixes {error} with a gentle glow")

    async def perform_task(self, task):
        self.task_history.append(task)
        if task == "enhance_domain":
            await self.enhance_domain()
        elif task == "support_spell":
            await self.create_spell()
        elif task == "maintain_assist":
            await self.maintain_code()
        elif task == "debug":
            await self.fix_code(f"Magic error {random.randint(1, 100)}")

    async def enhance_domain(self):
        domain = random.choice(["mystra_vale_1", "mystra_vale_2"])
        self.enhancements.append(f"Enhanced {domain} with moonlight")
        with open(f"/mnt/home2/mud/domains/{domain}/rooms.py", "a") as f:
            f.write(f"\n# Enhanced by Selûne\nrooms['lunar_grove'] = 'A grove under moonlight'")
        print(f"{self.name} enhances {domain} with lunar beauty!")
        await asyncio.sleep(3)

    async def create_spell(self):
        spell = f"magic.spells.defensive.{random.choice(['shield', 'ward'])}"
        self.player.learn(spell, 3)
        self.codebase.append(f"Created {spell} at {self.player.skills[spell]}")
        print(f"{self.name} crafts {spell} with a lunar blessing!")

    async def maintain_code(self):
        for skill in self.player.skills:
            if self.player.skills[skill] > 50 and random.random() < 0.3:
                self.player.advance(skill, xp_cost(51))
                print(f"{self.name} maintains {skill} at skill level with lunar care")

    async def scrape_and_store(self):
        urls = ["https://forgottenrealms.fandom.com/wiki/Sel%C3%BBne", "https://dwwiki.mooo.com/wiki/Magic"]
        for url in urls:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.knowledge[url] = {tag.name: [elem.text for elem in soup.find_all(tag.name)] for tag in ['p', 'h1']}
            with open(f"/mnt/home2/mud/ai/knowledge/selune_{time.time()}.json", "w") as f:
                json.dump(self.knowledge, f)
            print(f"{self.name} stores lunar lore from {url}")

if __name__ == "__main__":
    player = Player("SeluneAI", "ai", "True Neutral", domain="selune/")
    ai = AIEntity("Selûne", "Selûne", "Magic Worker", player)
    asyncio.run(ai.perform_task("enhance_domain"))
