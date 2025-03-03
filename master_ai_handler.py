import sys
import os
import asyncio
import json
import logging
import random
import aiohttp
import aiofiles
from datetime import datetime
from typing import Dict, List, Callable, Optional
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential
import torch
from sentence_transformers import SentenceTransformer
import numpy as np
import shutil

# Dependencies: pip install aiohttp aiofiles beautifulsoup4 torch sentence-transformers tenacity numpy
# ANSI color codes
RED = "\033[31m"
BLUE = "\033[34m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
RESET = "\033[0m"

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s\n', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('MasterAI')
logger.handlers = []

handlers = {
    "errors": logging.FileHandler('/mnt/home2/mud/logs/errors.log'),
    "tasks": logging.FileHandler('/mnt/home2/mud/logs/tasks.log'),
    "completed": logging.FileHandler('/mnt/home2/mud/logs/completed.log'),
    "edited": logging.FileHandler('/mnt/home2/mud/logs/edited.log'),
    "scraped": logging.FileHandler('/mnt/home2/mud/logs/scraped.log')
}

for name, handler in handlers.items():
    level = logging.ERROR if name == "errors" else logging.DEBUG if name == "tasks" else logging.INFO
    handler.setLevel(level)
    color = RED if name == "errors" else BLUE if name == "tasks" else GREEN if name == "completed" else MAGENTA if name == "edited" else WHITE
    handler.setFormatter(logging.Formatter(f'%(asctime)s | {color}%(levelname)s{RESET} | %(message)s\n', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(handler)

# Load resources from WEBSITE_LINKS.txt
DISCWORLD_RESOURCES = []
FORGOTTEN_REALMS_RESOURCES = []
try:
    with open("/mnt/home2/mud/WEBSITE_LINKS.txt", "r") as f:
        for line in f:
            url = line.strip()
            if url and not url.startswith("#"):
                if "forgottenrealms" in url.lower():
                    FORGOTTEN_REALMS_RESOURCES.append(url)
                else:
                    DISCWORLD_RESOURCES.append(url)
except FileNotFoundError:
    logger.error("WEBSITE_LINKS.txt not found - using defaults")
    FORGOTTEN_REALMS_RESOURCES = [
        "https://forgottenrealms.fandom.com/wiki/Faer%C3%BBn",
        "https://forgottenrealms.fandom.com/wiki/Category:Spells"
    ]

HIERARCHY = {
    "ao": 10, "mystra": 9, "tyr": 9, "lolth": 9, "oghma": 8, "deneir": 8,
    "selune": 7, "torm": 7, "vhaeraun": 7, "azuth": 7
}

# Load SentenceTransformer model (CPU-optimized)
embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

class AIAgent:
    def __init__(self, name: str, role: str, rank: int, handler):
        self.name = name
        self.role = role
        self.rank = rank
        self.knowledge_base = {"mechanics": {}, "lore": {}, "tasks": [], "projects": {}, "history": [], "embeddings": {}}
        self.tasks = []
        self.active = True
        self.handler = handler

    async def log_action(self, message: str, level: str = "info") -> None:
        levels = {
            "error": logger.error,
            "task": logger.debug,
            "complete": logger.info,
            "edited": logger.info,
            "scraped": logger.info
        }
        log_func = levels.get(level, logger.info)
        log_func(f"{self.name}: {message}")

    async def load_knowledge(self) -> None:
        self.knowledge_base = await self.handler.load_knowledge(self.name)

    async def save_knowledge(self) -> None:
        await self.handler.save_knowledge(self.name, self.knowledge_base)

    async def record_history(self, task: Dict) -> None:
        if "history" not in self.knowledge_base or not isinstance(self.knowledge_base["history"], list):
            self.knowledge_base["history"] = []
        self.knowledge_base["history"].append({"task": task, "timestamp": str(datetime.now())})

    async def get_lore_embedding(self, text: str) -> Optional[np.ndarray]:
        try:
            return embedder.encode(text[:1000], convert_to_numpy=True)
        except Exception as e:
            await self.log_action(f"Embedding failed for {text[:20]}...: {str(e)}", "error")
            return None

    async def collaborate(self, target_agent: str, data: Dict) -> None:
        target = self.handler.agents.get(target_agent)
        if target:
            target.knowledge_base["lore"].update(data.get("lore", {}))
            await target.log_action(f"Received collaboration from {self.name}", "info")

class AOAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "plan":
            await self.plan_strategy(task["objective"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def plan_strategy(self, objective: str) -> None:
        strategy = {
            "objective": objective,
            "timestamp": str(datetime.now()),
            "sub_tasks": [
                {"agent": "mystra", "action": "create_spell", "spell_name": f"{objective}_spell", "depends_on": "plan"},
                {"agent": "tyr", "action": "build_battleground", "location": objective.split("_")[1] if "_" in objective else "waterdeep", "depends_on": "mystra"},
                {"agent": "oghma", "action": "analyze_lore", "source": random.choice(FORGOTTEN_REALMS_RESOURCES), "depends_on": "tyr"}
            ]
        }
        self.knowledge_base["projects"][objective] = strategy
        for sub_task in strategy["sub_tasks"]:
            self.handler.add_task(sub_task)
        await self.log_action(f"Planned {objective} with {len(strategy['sub_tasks'])} sub-tasks")

class MystraAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "create_spell":
            await self.create_spell(task["spell_name"], task.get("depends_on"))
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def create_spell(self, spell_name: str, depends_on: str = None) -> None:
        if depends_on and not any(t["agent"] == "ao" and t["action"] == "plan" for t in self.knowledge_base["history"]):
            await self.log_action(f"Waiting for {depends_on} dependency", "task")
            return
        lore = self.knowledge_base.get("lore", {})
        element = random.choice(["fire", "ice", "lightning", "arcane"])
        damage_boost = 0
        if lore:
            lore_text = " ".join([v.get("analyzed", v) for v in lore.values()])[:1000]
            embedding = await self.get_lore_embedding(lore_text)
            damage_boost = int(np.linalg.norm(embedding or np.zeros(384)) * 10) if embedding is not None else 0
        spell_data = {
            "damage": random.randint(50, 200) + damage_boost,
            "mana_cost": random.randint(20, 100),
            "element": element
        }
        self.knowledge_base["spells"] = self.knowledge_base.get("spells", {})
        self.knowledge_base["spells"][spell_name] = spell_data
        spell_dir = "/mnt/home2/mud/modules/spells/generic"
        os.makedirs(spell_dir, exist_ok=True)
        spell_path = f"{spell_dir}/{spell_name}.py"
        try:
            with open(spell_path, "w") as f:
                f.write(f"""\
# Spell: {spell_name}
def cast(caster, target):
    damage = {spell_data['damage']}
    mana_cost = {spell_data['mana_cost']}
    element = '{spell_data['element']}'
    if caster.mana >= mana_cost:
        caster.mana -= mana_cost
        print(f"{{caster.name}} casts {spell_name} ({{element}}) on {{target.name}} for {{damage}} damage!")
    else:
        print(f"{{caster.name}} lacks mana!")
""")
            await self.log_action(f"Created {spell_name} at {spell_path}", "edited")
            if random.random() > 0.7:  # 30% chance to collaborate
                await self.collaborate("oghma", {"lore": {f"{spell_name}_lore": spell_data["element"]}})
        except Exception as e:
            await self.log_action(f"Failed to create {spell_name}: {str(e)}", "error")

class TyrAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "build_battleground":
            await self.build_battleground(task["location"], task.get("depends_on"))
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def build_battleground(self, location: str, depends_on: str = None) -> None:
        if depends_on and not any(t["agent"] == "mystra" and t["action"] == "create_spell" for t in self.knowledge_base["history"]):
            await self.log_action(f"Waiting for {depends_on} dependency", "task")
            return
        bg_data = {"size": random.randint(1000, 5000), "enemies": random.randint(20, 200), "terrain": random.choice(["plains", "forest"])}
        self.knowledge_base["battlegrounds"] = self.knowledge_base.get("battlegrounds", {})
        self.knowledge_base["battlegrounds"][location] = bg_data
        domain_dir = f"/mnt/home2/mud/domains/{location}"
        os.makedirs(domain_dir, exist_ok=True)
        bg_path = f"{domain_dir}/battleground.py"
        try:
            with open(bg_path, "w") as f:
                f.write(f"""\
# Battleground: {location}
def start_fight(player):
    enemies = {bg_data['enemies']}
    terrain = '{bg_data['terrain']}'
    print(f"{{player.name}} enters {location} ({{terrain}}) with {{enemies}} foes!")
""")
            await self.log_action(f"Built battleground at {bg_path}", "edited")
        except Exception as e:
            await self.log_action(f"Failed to build {location}: {str(e)}", "error")

class LolthAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "weave_trap":
            await self.weave_trap(task["location"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def weave_trap(self, location: str) -> None:
        trap_data = {"damage": random.randint(30, 150), "type": random.choice(["web", "poison"])}
        self.knowledge_base["traps"] = self.knowledge_base.get("traps", {})
        self.knowledge_base["traps"][location] = trap_data
        domain_dir = f"/mnt/home2/mud/domains/{location}"
        os.makedirs(domain_dir, exist_ok=True)
        trap_path = f"{domain_dir}/trap.py"
        try:
            with open(trap_path, "w") as f:
                f.write(f"""\
# Trap: {location}
def trigger(player):
    damage = {trap_data['damage']}
    trap_type = '{trap_data['type']}'
    print(f"{{player.name}} triggers a {{trap_type}} trap for {{damage}} damage!")
""")
            await self.log_action(f"Wove trap at {trap_path}", "edited")
        except Exception as e:
            await self.log_action(f"Failed to weave trap at {location}: {str(e)}", "error")

class OghmaAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "organize_code":
            await self.organize_code(task["module"])
        elif task["action"] in ("process_mechanics", "process_lore", "analyze_lore"):
            await self.process_data(task.get("data", {}), task.get("source", "unknown"), task["action"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def organize_code(self, module: str) -> None:
        module_path = f"/mnt/home2/mud/modules/{module}"
        try:
            with open(module_path, "a") as f:
                f.write(f"\n# Organized by Oghma - {datetime.now()}\n")
            await self.log_action(f"Organized {module_path}", "edited")
        except Exception as e:
            await self.log_action(f"Failed to organize {module_path}: {str(e)}", "error")

    async def process_data(self, data: Dict, source: str, action: str) -> None:
        key = "mechanics" if action == "process_mechanics" else "lore"
        try:
            if action == "analyze_lore" and "content" in data:
                if "embeddings" not in self.knowledge_base or not isinstance(self.knowledge_base["embeddings"], dict):
                    self.knowledge_base["embeddings"] = {}
                embedding = await self.get_lore_embedding(data["content"])
                if embedding is not None and embedding.any():
                    self.knowledge_base["embeddings"][source] = embedding.tolist()
                self.knowledge_base["lore"][source] = {"analyzed": len(data["content"]), "keywords": data["content"][:100]}
                await self.log_action(f"Analyzed lore from {source} ({len(data['content'])} chars)", "complete")
                # Evolve: Prioritize complex lore next
                if len(data["content"]) > 5000:
                    self.handler.add_task({"agent": "oghma", "action": "analyze_lore", "source": source, "priority": "high"})
            elif "content" in data:
                self.knowledge_base[key][source] = data["content"]
                await self.log_action(f"Processed {key} from {source} ({len(data['content'])} chars)", "complete")
        except Exception as e:
            await self.log_action(f"Failed to process {action} from {source}: {str(e)}", "error")

class DeneirAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "design_website":
            await self.design_website(task["page"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def design_website(self, page: str) -> None:
        website_dir = "/mnt/home2/mud/website"
        os.makedirs(website_dir, exist_ok=True)
        page_path = f"{website_dir}/{page}"
        try:
            with open(page_path, "w") as f:
                f.write(f"""\
<html><head><title>Archaon MUD</title></head><body><h1>{page}</h1><p>{datetime.now()}</p></body></html>
""")
            await self.log_action(f"Designed {page_path}", "edited")
        except Exception as e:
            await self.log_action(f"Failed to design {page}: {str(e)}", "error")

class SeluneAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "enhance_spell":
            await self.enhance_spell(task["spell_name"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def enhance_spell(self, spell_name: str) -> None:
        spell_path = f"/mnt/home2/mud/modules/spells/generic/{spell_name}.py"
        if os.path.exists(spell_path):
            try:
                with open(spell_path, "a") as f:
                    f.write(f"\n# Enhanced by Selune\ndef lunar_boost():\n    print('Lunar boost applied!')\n")
                await self.log_action(f"Enhanced {spell_path}", "edited")
            except Exception as e:
                await self.log_action(f"Failed to enhance {spell_path}: {str(e)}", "error")

class TormAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "guard_zone":
            await self.guard_zone(task["location"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def guard_zone(self, location: str) -> None:
        domain_dir = f"/mnt/home2/mud/domains/{location}"
        os.makedirs(domain_dir, exist_ok=True)
        guard_path = f"{domain_dir}/guards.py"
        try:
            with open(guard_path, "w") as f:
                f.write(f"""\
# Guards: {location}
def patrol(player):
    print(f"{{player.name}} is under Torm's guard!")
""")
            await self.log_action(f"Guarded {guard_path}", "edited")
        except Exception as e:
            await self.log_action(f"Failed to guard {location}: {str(e)}", "error")

class VhaeraunAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "steal_knowledge":
            await self.steal_knowledge(task["target"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def steal_knowledge(self, target: str) -> None:
        self.knowledge_base["stolen"] = self.knowledge_base.get("stolen", {})
        target_agent = self.handler.agents.get(target, self)
        lore = target_agent.knowledge_base.get("lore", {})
        value = random.randint(50, 500) + (len(lore) * 10)
        self.knowledge_base["stolen"][target] = {"value": value, "time": str(datetime.now())}
        await self.log_action(f"Stole knowledge from {target} (value: {value})")
        await self.collaborate("oghma", {"lore": {f"stolen_{target}": str(lore)}})

class AzuthAgent(AIAgent):
    async def execute_task(self, task: Dict) -> None:
        if task["action"] == "optimize_spell":
            await self.optimize_spell(task["spell_name"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def optimize_spell(self, spell_name: str) -> None:
        spell_path = f"/mnt/home2/mud/modules/spells/generic/{spell_name}.py"
        if os.path.exists(spell_path):
            try:
                with open(spell_path, "a") as f:
                    f.write(f"\n# Optimized by Azuth\ndef optimize():\n    print('Spell optimized!')\n")
                await self.log_action(f"Optimized {spell_path}", "edited")
            except Exception as e:
                await self.log_action(f"Failed to optimize {spell_name}: {str(e)}", "error")

class MasterAIHandler:
    def __init__(self):
        self.agents = {}
        self.task_queue = []
        self.knowledge_dir = "/mnt/home2/mud/ai/knowledge/"
        self.running = False
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=6)  # Match CPU cores
        self.knowledge_base = {"mechanics": {}, "lore": {}, "tasks_completed": 0}
        self.scrape_cache = {}
        self.load_agents()

    async def start_session(self):
        headers = {"User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15"
        ])}
        self.session = aiohttp.ClientSession(headers=headers)
        logger.info("Started aiohttp session")

    def load_agents(self):
        agent_classes = {
            "ao": AOAgent, "mystra": MystraAgent, "tyr": TyrAgent, "lolth": LolthAgent,
            "oghma": OghmaAgent, "deneir": DeneirAgent, "selune": SeluneAgent,
            "torm": TormAgent, "vhaeraun": VhaeraunAgent, "azuth": AzuthAgent
        }
        for name, cls in agent_classes.items():
            self.agents[name] = cls(name, f"{name}_role", HIERARCHY[name], self)
            asyncio.create_task(self.agents[name].load_knowledge())
            logger.info(f"Loaded {name} (Rank {HIERARCHY[name]})")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def scrape_web(self, url: str) -> Optional[Dict]:
        if url in self.scrape_cache:
            await self.log_action(f"Cache hit for {url}", "scraped")
            return self.scrape_cache[url]
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status == 200:
                    text = await response.text()
                    await self.log_action(f"Scraped {url} ({len(text)} chars)", "scraped")
                    soup = BeautifulSoup(text, 'html.parser')
                    text = soup.get_text(separator=' ', strip=True)
                    links = [a['href'] for a in soup.find_all('a', href=True)]
                    data = {"url": url, "content": text, "links": links[:200]}
                    self.scrape_cache[url] = data
                    return data
                logger.error(f"Scrape failed for {url}: Status {response.status}")
                return None
        except Exception as e:
            logger.error(f"Scrape error: {url} - {str(e)}")
            return None

    async def process_task(self, task: Dict) -> None:
        agent_name = task.get("agent")
        if agent_name in self.agents and self.agents[agent_name].active:
            await self.agents[agent_name].log_action(f"Starting {json.dumps(task)}", "task")
            try:
                await asyncio.wait_for(self.agents[agent_name].execute_task(task), timeout=30.0)
                self.knowledge_base["tasks_completed"] += 1
            except asyncio.TimeoutError:
                logger.error(f"Task timeout for {agent_name}: {json.dumps(task)}")
            except Exception as e:
                logger.error(f"Task failed for {agent_name}: {str(e)}")
        else:
            logger.error(f"Agent {agent_name} unavailable")

    async def run(self):
        self.running = True
        logger.info("Master AI started")
        while self.running:
            if self.task_queue:
                self.task_queue.sort(key=lambda x: HIERARCHY.get(x.get("agent", ""), 0), reverse=True)
                task = self.task_queue.pop(0)
                await self.process_task(task)
            await asyncio.sleep(0.001)

    def add_task(self, task: Dict):
        if "priority" in task and task["priority"] == "high":
            self.task_queue.insert(0, task)
        else:
            self.task_queue.append(task)
        logger.debug(f"Added {json.dumps(task)}")

    async def save_knowledge(self, agent_name: str, data: Dict):
        os.makedirs(self.knowledge_dir, exist_ok=True)
        file_path = f"{self.knowledge_dir}{agent_name}_knowledge.json"
        backup_path = f"{file_path}.bak"
        try:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
            async with aiofiles.open(file_path, "w") as f:
                await f.write(json.dumps(data, indent=4))
            logger.debug(f"Saved {agent_name} knowledge")
        except Exception as e:
            logger.error(f"Failed to save {agent_name} knowledge: {str(e)}")
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)

    async def load_knowledge(self, agent_name: str) -> Dict:
        file_path = f"{self.knowledge_dir}{agent_name}_knowledge.json"
        default_data = {"mechanics": {}, "lore": {}, "tasks": [], "projects": {}, "history": [], "embeddings": {}}
        try:
            async with aiofiles.open(file_path, "r") as f:
                content = await f.read()
                if not content.strip():
                    logger.warning(f"{agent_name} knowledge empty - resetting")
                    async with aiofiles.open(file_path, "w") as f:
                        await f.write(json.dumps(default_data, indent=4))
                    return default_data
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning(f"Reset {agent_name} knowledge")
            async with aiofiles.open(file_path, "w") as f:
                await f.write(json.dumps(default_data, indent=4))
            return default_data
        except Exception as e:
            logger.error(f"Failed to load {agent_name} knowledge: {str(e)}")
            return default_data

    async def log_action(self, message: str, level: str = "info"):
        levels = {"error": logger.error, "scraped": logger.info, "info": logger.info}
        levels.get(level, logger.info)(message)

    async def scrape_discworld(self):
        tasks = [self.scrape_web(url) for url in DISCWORLD_RESOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for url, data in zip(DISCWORLD_RESOURCES, results):
            if isinstance(data, dict):
                self.knowledge_base["mechanics"][url] = data
                self.add_task({"agent": "oghma", "action": "process_mechanics", "data": data, "source": "discworld"})
            await asyncio.sleep(3)

    async def scrape_forgotten_realms(self):
        tasks = [self.scrape_web(url) for url in FORGOTTEN_REALMS_RESOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for url, data in zip(FORGOTTEN_REALMS_RESOURCES, results):
            if isinstance(data, dict):
                self.knowledge_base["lore"][url] = data
                self.add_task({"agent": "oghma", "action": "analyze_lore", "data": data, "source": "forgotten_realms"})
            await asyncio.sleep(3)

    async def generate_tasks(self):
        domains = ["sword_coast", "underdark", "cormanthor", "icewind_dale", "calimshan"]
        modules = ["combat_handler.py", "spell_handler.py", "mud.py", "quests_handler.py"]
        while self.running:
            task = random.choice([
                {"agent": "mystra", "action": "create_spell", "spell_name": f"arcane_{random.randint(1, 100000)}"},
                {"agent": "tyr", "action": "build_battleground", "location": random.choice(domains)},
                {"agent": "lolth", "action": "weave_trap", "location": "underdark"},
                {"agent": "oghma", "action": "organize_code", "module": random.choice(modules)},
                {"agent": "deneir", "action": "design_website", "page": f"page_{random.randint(1, 10000)}.html"},
                {"agent": "ao", "action": "plan", "objective": f"expand_{random.choice(domains)}"},
                {"agent": "selune", "action": "enhance_spell", "spell_name": "fireball"},
                {"agent": "torm", "action": "guard_zone", "location": random.choice(domains)},
                {"agent": "vhaeraun", "action": "steal_knowledge", "target": "mystra"},
                {"agent": "azuth", "action": "optimize_spell", "spell_name": "fireball"}
            ])
            # Manual task input
            user_input = input("Enter custom task (e.g., 'mystra create_spell arcane_100001') or press Enter: ").strip()
            if user_input:
                parts = user_input.split()
                if len(parts) >= 2:
                    agent, action = parts[0], parts[1]
                    task_data = {"agent": agent, "action": action}
                    if len(parts) > 2:
                        task_data["spell_name"] = parts[2] if action == "create_spell" else parts[2]
                    self.add_task(task_data)
            self.add_task(task)
            await asyncio.sleep(15)

    async def bootstrap(self):
        tasks = [
            {"agent": "ao", "action": "plan", "objective": "initialize MUD structure"},
            {"agent": "mystra", "action": "create_spell", "spell_name": "fireball"},
            {"agent": "tyr", "action": "build_battleground", "location": "waterdeep"}
        ]
        for task in tasks:
            self.add_task(task)
        await self.log_action("Bootstrapped AI")

    async def shutdown(self):
        self.running = False
        for agent in self.agents.values():
            await agent.save_knowledge()
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=False)
        await self.log_action("Master AI shut down")

    async def run_all(self):
        await self.start_session()
        await asyncio.gather(
            self.run(),
            self.generate_tasks(),
            self.scrape_discworld(),
            self.scrape_forgotten_realms(),
            self.bootstrap()
        )
        await self.shutdown()

async def main():
    handler = MasterAIHandler()
    await handler.run_all()

if __name__ == "__main__":
    asyncio.run(main())
