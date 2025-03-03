# master_ai_handler.py - Unified AI system for Archaon MUD
# Updated: March 3, 2025, 04:10 AM AEST
# Changes:
# - Fixed KeyError: 'ao' by awaiting load_agents before other tasks in run_all
# - Pre-populated knowledge_base["progress"] in __init__ for all agents
# - Added try-finally to ensure session cleanup
# - Enhanced logging for initialization steps
# Status: Stable, background-ready, aligned with PLAN.md

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
import time
import logging.handlers

# Dependencies: pip install aiohttp aiofiles beautifulsoup4 torch sentence-transformers tenacity numpy
# ANSI color codes (for console if needed)
RED = "\033[31m"
BLUE = "\033[34m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
RESET = "\033[0m"

# Setup logging with rotation
logger = logging.getLogger('MasterAI')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

handlers = {
    "errors": logging.handlers.RotatingFileHandler('/mnt/home2/mud/logs/errors.log', maxBytes=1024*1024, backupCount=3),
    "tasks": logging.handlers.RotatingFileHandler('/mnt/home2/mud/logs/tasks.log', maxBytes=1024*1024, backupCount=3),
    "completed": logging.handlers.RotatingFileHandler('/mnt/home2/mud/logs/completed.log', maxBytes=1024*1024, backupCount=3),
    "edited": logging.handlers.RotatingFileHandler('/mnt/home2/mud/logs/edited.log', maxBytes=1024*1024, backupCount=3),
    "scraped": logging.handlers.RotatingFileHandler('/mnt/home2/mud/logs/scraped.log', maxBytes=1024*1024, backupCount=3)
}

for name, handler in handlers.items():
    handler.setLevel(logging.ERROR if name == "errors" else logging.DEBUG if name == "tasks" else logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Redirect TensorFlow warnings to errors.log
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger("tensorflow").addHandler(handlers["errors"])

# Load resources from WEBSITE_LINKS.txt
DISCWORLD_RESOURCES = []
FORGOTTEN_REALMS_RESOURCES = []
TASKS_FILE = "/mnt/home2/mud/tasks.txt"
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
        self.knowledge_base = {"mechanics": {}, "lore": {}, "tasks": [], "projects": {}, "history": [], "embeddings": {}, "health": 100}
        self.tasks = []
        self.active = True
        self.handler = handler

    async def log_action(self, message: str, level: str = "info"):
        levels = {
            "error": logger.error,
            "task": logger.debug,
            "complete": logger.info,
            "edited": logger.info,
            "scraped": logger.info
        }
        levels.get(level, logger.info)(f"{self.name}: {message}")

    async def load_knowledge(self):
        self.knowledge_base = await self.handler.load_knowledge(self.name)

    async def save_knowledge(self):
        await self.handler.save_knowledge(self.name, self.knowledge_base)

    async def record_history(self, task: Dict):
        if "history" not in self.knowledge_base or not isinstance(self.knowledge_base["history"], list):
            self.knowledge_base["history"] = []
        self.knowledge_base["history"].append({"task": task, "timestamp": str(datetime.now())})

    async def get_lore_embedding(self, text: str) -> Optional[np.ndarray]:
        try:
            return embedder.encode(text[:1000], convert_to_numpy=True)
        except Exception as e:
            await self.log_action(f"Embedding failed for {text[:20]}...: {str(e)}", "error")
            return None

    async def check_health(self) -> bool:
        if self.knowledge_base["health"] <= 0:
            self.active = False
            await self.log_action("Agent health depleted, going inactive", "error")
            return False
        self.knowledge_base["health"] -= random.randint(1, 5)
        return True

    async def recover(self):
        if not self.active and self.knowledge_base["health"] < 100:
            await asyncio.sleep(300)  # 5-minute cooldown
            self.active = True
            self.knowledge_base["health"] = min(100, self.knowledge_base["health"] + 50)
            await self.log_action(f"Recovered, health at {self.knowledge_base['health']}", "complete")

    async def collaborate(self, target_agent: str, data: Dict):
        target = self.handler.agents.get(target_agent)
        if target and await target.check_health():
            target.knowledge_base["lore"].update(data.get("lore", {}))
            await target.log_action(f"Received collaboration from {self.name}", "complete")

class AOAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "plan":
            await self.plan_strategy(task["objective"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def plan_strategy(self, objective: str):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
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
        await self.log_action(f"Planned {objective} with {len(strategy['sub_tasks'])} sub-tasks", "complete")

class MystraAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "create_spell":
            await self.create_spell(task["spell_name"], task.get("depends_on"))
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def create_spell(self, spell_name: str, depends_on: str = None):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if depends_on and not any(t["task"]["agent"] == "ao" and t["task"]["action"] == "plan" for t in self.knowledge_base["history"]):
            await self.log_action(f"Waiting for {depends_on} dependency", "task")
            return
        start_time = time.time()
        timeout = max(5, len(spell_name) * 0.1)
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
            execution_time = time.time() - start_time
            await self.log_action(f"Created {spell_name} at {spell_path} (took {execution_time:.2f}s)", "edited")
            if random.random() > 0.7:
                await self.collaborate("oghma", {"lore": {f"{spell_name}_lore": spell_data["element"]}})
        except Exception as e:
            await self.log_action(f"Failed to create {spell_name}: {str(e)}", "error")

class TyrAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "build_battleground":
            await self.build_battleground(task["location"], task.get("depends_on"))
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def build_battleground(self, location: str, depends_on: str = None):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if depends_on and not any(t["task"]["agent"] == "mystra" and t["task"]["action"] == "create_spell" for t in self.knowledge_base["history"]):
            await self.log_action(f"Waiting for {depends_on} dependency", "task")
            return
        start_time = time.time()
        timeout = max(5, len(location) * 0.1)
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
            execution_time = time.time() - start_time
            await self.log_action(f"Built battleground at {bg_path} (took {execution_time:.2f}s)", "edited")
        except Exception as e:
            await self.log_action(f"Failed to build {location}: {str(e)}", "error")

class LolthAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "weave_trap":
            await self.weave_trap(task["location"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def weave_trap(self, location: str):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        start_time = time.time()
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
            execution_time = time.time() - start_time
            await self.log_action(f"Wove trap at {trap_path} (took {execution_time:.2f}s)", "edited")
        except Exception as e:
            await self.log_action(f"Failed to weave trap at {location}: {str(e)}", "error")

class OghmaAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "organize_code":
            await self.organize_code(task["module"])
        elif task["action"] in ("process_mechanics", "process_lore", "analyze_lore"):
            await self.process_data(task.get("data", {}), task.get("source", "unknown"), task["action"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def organize_code(self, module: str):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        start_time = time.time()
        module_path = f"/mnt/home2/mud/modules/{module}"
        try:
            with open(module_path, "a") as f:
                f.write(f"\n# Organized by Oghma - {datetime.now()}\n")
            execution_time = time.time() - start_time
            await self.log_action(f"Organized {module_path} (took {execution_time:.2f}s)", "edited")
        except Exception as e:
            await self.log_action(f"Failed to organize {module_path}: {str(e)}", "error")

    async def process_data(self, data: Dict, source: str, action: str):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        start_time = time.time()
        key = "mechanics" if action == "process_mechanics" else "lore"
        try:
            if action == "analyze_lore" and "content" in data:
                if "embeddings" not in self.knowledge_base or not isinstance(self.knowledge_base["embeddings"], dict):
                    self.knowledge_base["embeddings"] = {}
                embedding = await self.get_lore_embedding(data["content"])
                if embedding is not None and embedding.any():
                    self.knowledge_base["embeddings"][source] = embedding.tolist()
                self.knowledge_base["lore"][source] = {"analyzed": len(data["content"]), "keywords": data["content"][:100]}
                execution_time = time.time() - start_time
                await self.log_action(f"Analyzed lore from {source} ({len(data['content'])} chars) (took {execution_time:.2f}s)", "complete")
                if len(data["content"]) > 5000 and random.random() > 0.5:
                    self.handler.add_task({"agent": "oghma", "action": "analyze_lore", "source": source, "priority": "high"})
            elif "content" in data:
                self.knowledge_base[key][source] = data["content"]
                execution_time = time.time() - start_time
                await self.log_action(f"Processed {key} from {source} ({len(data['content'])} chars) (took {execution_time:.2f}s)", "complete")
        except Exception as e:
            await self.log_action(f"Failed to process {action} from {source}: {str(e)}", "error")

class DeneirAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "design_website":
            await self.design_website(task["page"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def design_website(self, page: str):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        start_time = time.time()
        website_dir = "/mnt/home2/mud/website"
        os.makedirs(website_dir, exist_ok=True)
        page_path = f"{website_dir}/{page}"
        try:
            with open(page_path, "w") as f:
                f.write(f"""\
<html><head><title>Archaon MUD</title></head><body><h1>{page}</h1><p>{datetime.now()}</p></body></html>
""")
            execution_time = time.time() - start_time
            await self.log_action(f"Designed {page_path} (took {execution_time:.2f}s)", "edited")
        except Exception as e:
            await self.log_action(f"Failed to design {page}: {str(e)}", "error")

class SeluneAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "enhance_spell":
            await self.enhance_spell(task["spell_name"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def enhance_spell(self, spell_name: str):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        start_time = time.time()
        spell_path = f"/mnt/home2/mud/modules/spells/generic/{spell_name}.py"
        if os.path.exists(spell_path):
            try:
                with open(spell_path, "a") as f:
                    f.write(f"\n# Enhanced by Selune\ndef lunar_boost():\n    print('Lunar boost applied!')\n")
                execution_time = time.time() - start_time
                await self.log_action(f"Enhanced {spell_path} (took {execution_time:.2f}s)", "edited")
            except Exception as e:
                await self.log_action(f"Failed to enhance {spell_path}: {str(e)}", "error")

class TormAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "guard_zone":
            await self.guard_zone(task["location"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def guard_zone(self, location: str):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        start_time = time.time()
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
            execution_time = time.time() - start_time
            await self.log_action(f"Guarded {guard_path} (took {execution_time:.2f}s)", "edited")
        except Exception as e:
            await self.log_action(f"Failed to guard {location}: {str(e)}", "error")

class VhaeraunAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "steal_knowledge":
            await self.steal_knowledge(task["target"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def steal_knowledge(self, target: str):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        start_time = time.time()
        self.knowledge_base["stolen"] = self.knowledge_base.get("stolen", {})
        target_agent = self.handler.agents.get(target, self)
        lore = target_agent.knowledge_base.get("lore", {})
        value = random.randint(50, 500) + (len(lore) * 10)
        self.knowledge_base["stolen"][target] = {"value": value, "time": str(datetime.now())}
        execution_time = time.time() - start_time
        await self.log_action(f"Stole knowledge from {target} (value: {value}) (took {execution_time:.2f}s)", "complete")
        await self.collaborate("oghma", {"lore": {f"stolen_{target}": str(lore)}})

class AzuthAgent(AIAgent):
    async def execute_task(self, task: Dict):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        if task["action"] == "optimize_spell":
            await self.optimize_spell(task["spell_name"])
        await self.record_history(task)
        await self.log_action(f"Executed {task['action']}", "complete")

    async def optimize_spell(self, spell_name: str):
        if not await self.check_health():
            asyncio.create_task(self.recover())
            return
        start_time = time.time()
        spell_path = f"/mnt/home2/mud/modules/spells/generic/{spell_name}.py"
        if os.path.exists(spell_path):
            try:
                with open(spell_path, "a") as f:
                    f.write(f"\n# Optimized by Azuth\ndef optimize():\n    print('Spell optimized!')\n")
                execution_time = time.time() - start_time
                await self.log_action(f"Optimized {spell_path} (took {execution_time:.2f}s)", "edited")
            except Exception as e:
                await self.log_action(f"Failed to optimize {spell_name}: {str(e)}", "error")

class MasterAIHandler:
    def __init__(self):
        self.agents = {}
        self.task_queue = []
        self.knowledge_dir = "/mnt/home2/mud/ai/knowledge/"
        self.running = False
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=6)
        self.knowledge_base = {
            "mechanics": {}, 
            "lore": {}, 
            "tasks_completed": 0, 
            "progress": {name: {"tasks_completed": 0, "last_active": datetime.now()} for name in HIERARCHY}, 
            "task_history": []
        }
        self.scrape_cache = {}

    async def load_agents(self):
        agent_classes = {
            "ao": AOAgent, "mystra": MystraAgent, "tyr": TyrAgent, "lolth": LolthAgent,
            "oghma": OghmaAgent, "deneir": DeneirAgent, "selune": SeluneAgent,
            "torm": TormAgent, "vhaeraun": VhaeraunAgent, "azuth": AzuthAgent
        }
        for name, cls in agent_classes.items():
            self.agents[name] = cls(name, f"{name}_role", HIERARCHY[name], self)
            await self.agents[name].load_knowledge()
            await self.log_action(f"Loaded {name} (Rank {HIERARCHY[name]})")

    async def start_session(self):
        headers = {"User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15"
        ])}
        self.session = aiohttp.ClientSession(headers=headers)
        await self.log_action("Started aiohttp session")

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
                await self.log_action(f"Scrape failed for {url}: Status {response.status}", "error")
                return None
        except Exception as e:
            await self.log_action(f"Scrape error: {url} - {str(e)}", "error")
            return None

    async def process_task(self, task: Dict):
        agent_name = task.get("agent")
        if agent_name in self.agents and self.agents[agent_name].active:
            await self.log_action(f"Starting {json.dumps(task)}", "task")
            self.knowledge_base["progress"][agent_name]["last_active"] = datetime.now()
            attempt = 0
            max_attempts = 3
            while attempt < max_attempts:
                try:
                    start_time = time.time()
                    timeout = max(5, len(json.dumps(task)) * 0.1)
                    await asyncio.wait_for(self.agents[agent_name].execute_task(task), timeout=timeout)
                    execution_time = time.time() - start_time
                    self.knowledge_base["progress"][agent_name]["tasks_completed"] += 1
                    self.knowledge_base["task_history"].append({"task": task, "agent": agent_name, "time": execution_time, "success": True, "timestamp": str(datetime.now())})
                    self.knowledge_base["tasks_completed"] += 1
                    break
                except asyncio.TimeoutError:
                    attempt += 1
                    await asyncio.sleep(5)
                    await self.log_action(f"Task timeout for {agent_name}: {json.dumps(task)} (Attempt {attempt}/{max_attempts})", "error")
                    if attempt == max_attempts:
                        self.knowledge_base["task_history"].append({"task": task, "agent": agent_name, "time": timeout, "success": False, "timestamp": str(datetime.now())})
                except Exception as e:
                    attempt += 1
                    await asyncio.sleep(5)
                    await self.log_action(f"Task failed for {agent_name}: {str(e)} (Task: {json.dumps(task)}, Attempt {attempt}/{max_attempts})", "error")
                    if attempt == max_attempts:
                        self.knowledge_base["task_history"].append({"task": task, "agent": agent_name, "time": time.time() - start_time, "success": False, "timestamp": str(datetime.now())})
        else:
            await self.log_action(f"Agent {agent_name} unavailable", "error")

    async def run(self):
        self.running = True
        await self.log_action("Master AI started")
        while self.running:
            if self.task_queue:
                healthy_agents = {name: agent for name, agent in self.agents.items() if agent.active and agent.knowledge_base["health"] > 50}
                if healthy_agents:
                    agent_names = list(healthy_agents.keys())
                    self.task_queue.sort(key=lambda x: HIERARCHY.get(x.get("agent", random.choice(agent_names)), 0), reverse=True)
                task = self.task_queue.pop(0)
                await self.process_task(task)
            await asyncio.sleep(0.001)

    def add_task(self, task: Dict):  # Synchronous for external calls
        if "priority" in task and task["priority"] == "high":
            self.task_queue.insert(0, task)
        else:
            self.task_queue.append(task)
        asyncio.create_task(self.log_action(f"Added {json.dumps(task)}", "task"))

    async def save_knowledge(self, agent_name: str, data: Dict):
        os.makedirs(self.knowledge_dir, exist_ok=True)
        file_path = f"{self.knowledge_dir}{agent_name}_knowledge.json"
        backup_path = f"{file_path}.bak"
        try:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
            async with aiofiles.open(file_path, "w") as f:
                await f.write(json.dumps(data, indent=4))
            await self.log_action(f"Saved {agent_name} knowledge")
        except Exception as e:
            await self.log_action(f"Failed to save {agent_name} knowledge: {str(e)}", "error")
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)

    async def load_knowledge(self, agent_name: str) -> Dict:
        file_path = f"{self.knowledge_dir}{agent_name}_knowledge.json"
        default_data = {"mechanics": {}, "lore": {}, "tasks": [], "projects": {}, "history": [], "embeddings": {}, "health": 100}
        try:
            async with aiofiles.open(file_path, "r") as f:
                content = await f.read()
                if not content.strip():
                    await self.log_action(f"{agent_name} knowledge empty - resetting")
                    async with aiofiles.open(file_path, "w") as f:
                        await f.write(json.dumps(default_data, indent=4))
                    return default_data
                loaded_data = json.loads(content)
                for key in default_data:
                    if key not in loaded_data:
                        loaded_data[key] = default_data[key]
                return loaded_data
        except (FileNotFoundError, json.JSONDecodeError):
            await self.log_action(f"Reset {agent_name} knowledge")
            async with aiofiles.open(file_path, "w") as f:
                await f.write(json.dumps(default_data, indent=4))
            return default_data
        except Exception as e:
            await self.log_action(f"Failed to load {agent_name} knowledge: {str(e)}", "error")
            return default_data

    async def log_action(self, message: str, level: str = "info"):
        levels = {
            "error": logger.error,
            "task": logger.debug,
            "complete": logger.info,
            "edited": logger.info,
            "scraped": logger.info
        }
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
            # Read tasks from tasks.txt
            try:
                async with aiofiles.open(TASKS_FILE, "r") as f:
                    lines = await f.readlines()
                for line in lines:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            agent, action = parts[0], parts[1]
                            task_data = {"agent": agent, "action": action}
                            if len(parts) > 2:
                                if action == "create_spell":
                                    task_data["spell_name"] = parts[2]
                                else:
                                    task_data["location"] = parts[2] if action == "build_battleground" else parts[2]
                            if len(parts) > 3 and parts[3].lower() == "[high]":
                                task_data["priority"] = "high"
                            self.add_task(task_data)
            except FileNotFoundError:
                await self.log_action(f"{TASKS_FILE} not found, creating default")
                async with aiofiles.open(TASKS_FILE, "w") as f:
                    await f.write("# Add tasks here (e.g., 'mystra create_spell arcane_100001 [high]')\n")

            # Generate random task
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
        await self.log_action("Bootstrapped AI", "complete")

    async def monitor_agents(self):
        while self.running:
            for name, agent in self.agents.items():
                if not await agent.check_health():
                    asyncio.create_task(agent.recover())
                progress = self.knowledge_base["progress"][name]
                if (datetime.now() - progress["last_active"]).total_seconds() > 120:
                    agent.knowledge_base["health"] = max(0, agent.knowledge_base["health"] - 10)
                    await agent.log_action(f"Low activity, health reduced to {agent.knowledge_base['health']}")
            if self.knowledge_base["tasks_completed"] % 5 == 0:
                await self.log_action(f"Agent Status - Tasks Completed: {self.knowledge_base['tasks_completed']}, Progress: {self.knowledge_base['progress']}", "complete")
            await asyncio.sleep(60)

    async def backup_knowledge(self):
        while self.running:
            if self.knowledge_base["tasks_completed"] % 10 == 0:
                for name, agent in self.agents.items():
                    await agent.save_knowledge()
                await self.log_action("Performed knowledge backup")
            await asyncio.sleep(60)

    async def shutdown(self):
        self.running = False
        for agent in self.agents.values():
            await agent.save_knowledge()
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=False)
        await self.log_action("Master AI shut down")

    async def run_all(self):
        try:
            await self.log_action("Initializing Master AI")
            await self.load_agents()  # Ensure agents are loaded first
            await self.start_session()
            await asyncio.gather(
                self.run(),
                self.generate_tasks(),
                self.scrape_discworld(),
                self.scrape_forgotten_realms(),
                self.bootstrap(),
                self.monitor_agents(),
                self.backup_knowledge()
            )
        finally:
            await self.shutdown()

async def main():
    handler = MasterAIHandler()
    await handler.run_all()

if __name__ == "__main__":
    asyncio.run(main())
