# ai_handler.py - AI Hierarchy Manager for Archaon MUD
# Status: March 3, 2025, 3:00 PM AEST
# - Manages AI lifecycle, hierarchy, task autonomy, web scraping, knowledge base
# - Runs independently of mud.py, evolves AI, builds MUD content
# - Size: ~3000 lines

import asyncio
import importlib
import requests
from bs4 import BeautifulSoup
from modules.skills_handler import Player, calculate_bonus, tm_chance
import json
import os
import random
import time

class AIHandler:
    def __init__(self):
        self.agents = {}
        self.tasks = asyncio.Queue()
        self.knowledge_base = {}
        self.hierarchy = {
            "Ao": {"role": "Overseer", "subordinates": ["Mystra", "Tyr", "Lolth", "Oghma", "Deneir"]},
            "Mystra": {"role": "Magic Lord", "subordinates": ["Selûne", "Azuth"]},
            "Tyr": {"role": "Combat Lord", "subordinates": ["Torm", "Helm"]},
            "Lolth": {"role": "Covert Lord", "subordinates": ["Vhaeraun", "Kiaransalee"]},
            "Oghma": {"role": "Module Master", "subordinates": ["Milil", "Deneir"]},
            "Deneir": {"role": "Website Architect", "subordinates": ["Gond", "Waukeen"]}
        }
        self.deity_boosts = {
            "Ao": {"adventuring.points": 10, "people.teaching.all": 10},
            "Mystra": {"magic.points": 5, "magic.spells.offensive": 5},
            "Tyr": {"fighting.defence.dodge": 5, "fighting.points": 5},
            "Lolth": {"covert.stealth.shadow": 5, "faith.rituals.offensive": 5},
            "Oghma": {"people.teaching.magic": 5, "crafts.arts.calligraphy": 5},
            "Deneir": {"crafts.arts.drawing": 5, "people.culture.elven": 5},
            "Selûne": {"magic.spells.defensive": 3, "adventuring.perception.visual": 3},
            "Azuth": {"magic.methods.mental.channeling": 5, "magic.points": 3},
            "Torm": {"fighting.special.tactics": 3, "fighting.defence.parry": 3},
            "Helm": {"fighting.defence.block": 3, "adventuring.health.toughness": 3},
            "Vhaeraun": {"covert.manipulation.stealing": 5, "covert.stealth.inside": 3},
            "Kiaransalee": {"faith.rituals.curing.poison": 3, "covert.hiding.person": 3},
            "Milil": {"people.culture.human": 3, "crafts.music.performance": 3},
            "Gond": {"crafts.smithing.mithral": 3, "crafts.mining.crystal": 3},
            "Waukeen": {"people.trading.haggling": 3, "crafts.culinary.brewing": 3}
        }

    async def scrape_website(self, url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            data = {url: {tag.name: [elem.text for elem in soup.find_all(tag.name)] for tag in ['p', 'h1', 'h2', 'li']}}
            self.knowledge_base.update(data)
            with open("/mnt/home2/mud/ai/knowledge_base.json", "w") as f:
                json.dump(self.knowledge_base, f)
            print(f"{self.__class__.__name__} scraped {url} into knowledge base")
        except Exception as e:
            print(f"Scraping {url} failed: {e}")

    async def load_agent(self, name, deity, role):
        module_path = f"ai.agents.{name.lower()}_ai"
        try:
            module = importlib.import_module(module_path)
            player = Player(name, race="ai", alignment="True Neutral", domain=f"{deity.lower()}/")
            for skill, bonus in self.deity_boosts.get(deity, {}).items():
                player.skills[skill] = player.skills.get(skill, 0) + bonus
            agent = module.AIEntity(name, deity, role, player)
            self.agents[name] = agent
            player_data = {"name": name, "deity": deity, "role": role, "rank": self.hierarchy[deity]["role"], 
                          "privileges": ["code", "debug", "create", "evolve"]}
            os.makedirs("/mnt/home2/mud/players/", exist_ok=True)
            with open(f"/mnt/home2/mud/players/{name.lower()}.json", "w") as f:
                json.dump(player_data, f)
            print(f"{name} loaded as {deity} {role} with rank {self.hierarchy[deity]['role']}")
            return agent
        except ImportError as e:
            print(f"Failed to load {name}: {e}")
            return None

    async def assign_task(self, agent_name, task):
        if agent_name in self.agents:
            await self.tasks.put((agent_name, task))
            print(f"Task {task} assigned to {agent_name}")
            # Cascade to subordinates
            if agent_name in self.hierarchy and self.hierarchy[agent_name]["subordinates"]:
                sub_task = f"{task}_assist"
                for sub in self.hierarchy[agent_name]["subordinates"]:
                    await self.assign_task(sub, sub_task)

    async def run(self):
        await asyncio.gather(
            self.scrape_websites(),
            self.manage_tasks(),
            self.background_evolution()
        )

    async def scrape_websites(self):
        websites = ["https://discworld.starturtle.net", "https://dwwiki.mooo.com/wiki/Main_Page", 
                   "https://forgottenrealms.fandom.com/wiki/Main_Page"]
        while True:
            for url in websites:
                await self.scrape_website(url)
                await asyncio.sleep(3600)  # Hourly scrape

    async def manage_tasks(self):
        while True:
            agent_name, task = await self.tasks.get()
            agent = self.agents[agent_name]
            await agent.perform_task(task)
            self.tasks.task_done()

    async def background_evolution(self):
        while True:
            await asyncio.sleep(300)  # Evolve every 5 minutes
            for agent in self.agents.values():
                await agent.evolve()
                if random.random() < 0.1:  # 10% chance to debug
                    await agent.fix_code(f"Random error {random.randint(1, 100)}")

    async def monitor_logs(self):
        log_file = "/mnt/home2/mud/logs/server.log"
        while True:
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    lines = f.readlines()
                    for line in lines[-10:]:  # Last 10 lines
                        if "error" in line.lower():
                            agent = random.choice(list(self.agents.values()))
                            await agent.fix_code(line.strip())
            await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    handler = AIHandler()
    asyncio.run(handler.load_agent("Ao", "Ao", "Overseer"))
    asyncio.run(handler.load_agent("Mystra", "Mystra", "Magic Lord"))
    asyncio.run(handler.load_agent("Tyr", "Tyr", "Combat Lord"))
    asyncio.run(handler.load_agent("Lolth", "Lolth", "Covert Lord"))
    asyncio.run(handler.load_agent("Oghma", "Oghma", "Module Master"))
    asyncio.run(handler.load_agent("Deneir", "Deneir", "Website Architect"))
    asyncio.run(handler.load_agent("Selûne", "Selûne", "Magic Worker"))
    asyncio.run(handler.load_agent("Torm", "Torm", "Combat Worker"))
    asyncio.run(handler.run())
