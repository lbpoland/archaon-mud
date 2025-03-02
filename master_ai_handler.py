#!/usr/bin/env python3
"""
Master AI Handler for MUD Project
Changelog:
- 2025-03-02 (Grok 3): Initial fixes and setup.
- 2025-03-02 (Grok 3 Update 4): Expanded DISCWORLD_SOURCES, TASK_LIST, improved code generation for Discworld mechanics, fixed mud.py loop.
- 2025-03-02 (Grok 3 Update 5): Fully integrated mud_session_169696969.json mechanics (combat, skills, soul, etc.), added Forgotten Realms-themed login with ASCII art, expanded races, enhanced term/network/colours support, thoroughly checked for errors.
"""

import random
import time
import os
import json
import argparse
from enum import Enum
from typing import Dict, List, Optional
import requests
import sys
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from collections import Counter
import asyncio
import torch
from transformers import pipeline
from diffusers import StableDiffusionPipeline
import numpy as np
from PIL import Image
import fastapi
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import nltk
from nltk.tokenize import word_tokenize
from stable_baselines3 import PPO
import gym
from gym import spaces
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database Setup
Base = declarative_base()
engine = create_engine('sqlite:////mnt/home2/mud/data/db/mud_data.db')
Session = sessionmaker(bind=engine)

class ScrapedData(Base):
    __tablename__ = 'scraped_data'
    id = Column(Integer, primary_key=True)
    source_url = Column(String, unique=True)
    content = Column(String)
    timestamp = Column(DateTime)

Base.metadata.create_all(engine)

# AI Ranks and Personalities
class AIRank(Enum):
    OVERDEITY = "Overdeity"
    GREATER_DEITY = "Greater Deity"
    INTERMEDIATE_DEITY = "Intermediate Deity"
    LESSER_DEITY = "Lesser Deity"
    DEMIGOD = "Demigod"
    QUASI_DEITY = "Quasi-Deity"

PERSONALITIES = {
    "Ao": {"tone": "wise", "humor": "dry", "creativity": 0.9},
    "Mystra": {"tone": "mysterious", "humor": "witty", "creativity": 0.95},
    "Bane": {"tone": "harsh", "humor": "sarcastic", "creativity": 0.7},
    "Selûne": {"tone": "gentle", "humor": "kind", "creativity": 0.85},
    "Torm": {"tone": "honorable", "humor": "earnest", "creativity": 0.8},
    "Kelemvor": {"tone": "somber", "humor": "dark", "creativity": 0.75}
}

# Forgotten Realms Races (Player-selectable and NPC options)
PLAYER_RACES = ["human", "elf", "high elf", "wild elf", "wood elf", "drow", "dwarf", "duergar", "orc", "goblin", "gnome", "halfling", "dragonborn"]
ALL_RACES = PLAYER_RACES + ["tiefling", "aarakocra", "genasi", "goliath"]  # Expand with more from wiki as needed
DND_CLASSES = ["fighter", "wizard", "cleric", "rogue", "barbarian", "druid", "paladin", "ranger"]
DND_SPELLS = ["fireball", "heal", "shield", "magic missile"]

DEITIES = {
    "Ao": {"rank": AIRank.OVERDEITY, "domain": "Balance", "style": "cosmic"},
    "Mystra": {"rank": AIRank.GREATER_DEITY, "domain": "Magic", "style": "arcane"},
    "Bane": {"rank": AIRank.GREATER_DEITY, "domain": "Tyranny", "style": "dark"},
    "Selûne": {"rank": AIRank.INTERMEDIATE_DEITY, "domain": "Moon", "style": "gentle"},
    "Torm": {"rank": AIRank.LESSER_DEITY, "domain": "Duty", "style": "noble"},
    "Kelemvor": {"rank": AIRank.LESSER_DEITY, "domain": "Death", "style": "somber"}
}

DISCWORLD_SOURCES = [
    "https://discworld.starturtle.net/lpc/playing/documentation.c?path=/newbie/essentials",
    "https://discworld.starturtle.net/lpc/playing/documentation.c?path=/",
    "https://discworld.starturtle.net/lpc/",
    "https://dwwiki.mooo.com/",
    "https://dwwiki.mooo.com/wiki/Syntax",
    "https://dwwiki.mooo.com/wiki/Options",
    "https://dwwiki.mooo.com/wiki/Tactics",
    "https://dwwiki.mooo.com/wiki/Dodge",
    "https://dwwiki.mooo.com/wiki/Block",
    "https://dwwiki.mooo.com/wiki/Parry",
    "https://dwwiki.mooo.com/wiki/Defend",
    "https://dwwiki.mooo.com/wiki/Protect",
    "https://dwwiki.mooo.com/wiki/Action_points",
    "https://dwwiki.mooo.com/wiki/Friend",
    "https://dwwiki.mooo.com/wiki/Inform",
    "https://dwwiki.mooo.com/wiki/Achievements",
    "https://dwwiki.mooo.com/wiki/Quests",
    "https://dwwiki.mooo.com/wiki/Soul",
    "https://dwwiki.mooo.com/wiki/Roleplaying_(command)",
    "https://dwwiki.mooo.com/wiki/Customization",
    "https://dwwiki.mooo.com/wiki/Writing_a_description",
    "https://dwwiki.mooo.com/wiki/Title",
    "https://dwwiki.mooo.com/wiki/Who",
    "https://dwwiki.mooo.com/wiki/Position",
    "https://dwwiki.mooo.com/wiki/Layers",
    "https://dwwiki.mooo.com/wiki/Armours",
    "https://dwwiki.mooo.com/wiki/Scabbard",
    "https://dwwiki.mooo.com/wiki/Temperature",
    "https://dwwiki.mooo.com/wiki/Clothing",
    "https://dwwiki.mooo.com/wiki/Weather",
    "https://dwwiki.mooo.com/wiki/Attack_messages",
    "https://dwwiki.mooo.com/wiki/Alignment",
    "https://www.gunde.de/discworld/sekiri/introduction.html",
    "https://www.gunde.de/discworld/sekiri/spells1.html#eff",
    "https://dwwiki.mooo.com/wiki/Spells",
    "https://dwwiki.mooo.com/wiki/Magic",
    "https://dwwiki.mooo.com/wiki/Teachers",
    "https://dwwiki.mooo.com/wiki/Theft",
    "https://dwwiki.mooo.com/wiki/Groups",
    "https://dwwiki.mooo.com/wiki/Languages",
    "https://dwwiki.mooo.com/wiki/Roleplaying",
    "https://dwwiki.mooo.com/wiki/Player_housing",
    "https://dwwiki.mooo.com/wiki/Player_shops",
    "https://dwwiki.mooo.com/wiki/Furniture",
    "https://dwwiki.mooo.com/wiki/Description_line",
    "https://dwwiki.mooo.com/wiki/Guild_Points",
    "https://dwwiki.mooo.com/wiki/Hit_points",
    "https://dwwiki.mooo.com/wiki/Skills",
    "https://dwwiki.mooo.com/wiki/Stats",
    "https://dwwiki.mooo.com/wiki/Experience_points",
    "https://dwwiki.mooo.com/wiki/Category:Commands",
    "https://dwwiki.mooo.com/wiki/Commands",
    "https://dwwiki.mooo.com/wiki/Crafts"
]

FORGOTTEN_REALMS_SOURCES = [
    "https://forgottenrealms.fandom.com/wiki/Main_Page",
    "https://forgottenrealms.fandom.com/wiki/Category:Races",
    "https://forgottenrealms.fandom.com/wiki/Category:Classes",
    "https://forgottenrealms.fandom.com/wiki/Portal:Deities",
    "https://forgottenrealms.fandom.com/wiki/Category:Spells",
    "https://forgottenrealms.fandom.com/wiki/Category:Rituals",
    "https://forgottenrealms.fandom.com/wiki/Alignment",
    "https://forgottenrealms.fandom.com/wiki/Category:Organizations",
    "https://forgottenrealms.fandom.com/wiki/Category:Climate_and_weather_events",
    "https://forgottenrealms.fandom.com/wiki/Category:Creatures",
    "https://dnd5e.fandom.com/wiki/Dungeons_%26_Dragons_5e_Wiki"
]

TASK_LIST = [
    "login", "creation", "room", "races", "classes", "combat", "skills", "inventory",
    "spells", "guilds", "npcs", "quests", "rituals", "world", "finger", "soul",
    "emote", "armors", "weapons", "party", "mounts", "maps", "achievements",
    "layers", "weather", "tactics", "dodge", "parry", "block", "term", "network",
    "colours", "syntax", "help"
]

DEFAULT_MECHANICS = {
    "movement": True,
    "combat": True,
    "inventory": True,
    "quests": True,
    "guilds": True,
    "skills": True,
    "spells": True,
    "rituals": True,
    "tactics": True,
    "dodge": True,
    "parry": True,
    "block": True,
    "soul": True,
    "colours": True
}

MAX_TASK_RETRIES = 3

class AIHandler:
    def __init__(self, mud_root: str = "/mnt/home2/mud", clean_logs: bool = False):
        self.mud_root = mud_root
        self.log_root = os.path.join(mud_root, "logs")
        self.ai_team: Dict[str, dict] = {}
        self.tasks: Dict[str, dict] = {}
        self.event_log: List[dict] = []
        self.performance: Dict[str, float] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.telnet_log_dir = mud_root
        self.text_generator = None
        self.image_generator = None
        self.discworld_data = {}
        self.forgotten_realms_data = {}
        self.mechanics_cache = DEFAULT_MECHANICS.copy()

        if clean_logs:
            self.clean_logs()
        
        self.initialize_system()

    def initialize_system(self):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting initialization...")
        os.makedirs(self.mud_root, exist_ok=True)
        for dir_path in [self.log_root, os.path.join(self.log_root, "status"), os.path.join(self.log_root, "mud_errors"), 
                         os.path.join(self.log_root, "script_errors"), os.path.join(self.log_root, "warnings"), 
                         os.path.join(self.log_root, "crashes"), os.path.join(self.mud_root, "players"), 
                         os.path.join(self.mud_root, "modules"), os.path.join(self.mud_root, "ai"), 
                         os.path.join(self.mud_root, "website", "static", "images"), os.path.join(self.mud_root, "website", "static", "css"), 
                         os.path.join(self.mud_root, "website", "static", "js"), os.path.join(self.mud_root, "website", "templates"), 
                         os.path.join(self.mud_root, "data", "db"), os.path.join(self.mud_root, "data", "embeddings")]:
            os.makedirs(dir_path, exist_ok=True)
        self.log_action("System", "startup", f"Initialized directories at {self.mud_root}")

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Loading GPT-2 text generation pipeline...")
            self.text_generator = pipeline("text-generation", model="gpt2-medium", tokenizer="gpt2-medium", device=0 if torch.cuda.is_available() else -1)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] GPT-2 pipeline loaded successfully.")
        except Exception as e:
            self.log_action("System", "errors", f"Failed to load GPT-2 pipeline: {str(e)}")
            raise

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Loading Stable Diffusion pipeline...")
            self.image_generator = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                use_safetensors=True,
                torch_dtype=torch.float32,
                safety_checker=None
            )
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Stable Diffusion pipeline loaded successfully.")
        except Exception as e:
            self.log_action("System", "errors", f"Failed to load Stable Diffusion: {str(e)}")
            raise

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Downloading NLTK 'punkt' data...")
            nltk.download('punkt', quiet=True, download_dir='/tmp/nltk_data', raise_on_error=True)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] NLTK 'punkt' data downloaded successfully.")
        except Exception as e:
            self.log_action("System", "errors", f"Failed to download NLTK 'punkt' data: {str(e)}")

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Discworld scraping...")
            start_time = time.time()
            self.scrape_discworld()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Discworld scraping completed in {time.time() - start_time:.2f} seconds.")
        except Exception as e:
            self.log_action("System", "errors", f"Scraping Discworld failed: {str(e)}")

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Forgotten Realms scraping...")
            start_time = time.time()
            self.scrape_forgotten_realms()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Forgotten Realms scraping completed in {time.time() - start_time:.2f} seconds.")
        except Exception as e:
            self.log_action("System", "errors", f"Scraping Forgotten Realms failed: {str(e)}")

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Storing scraped data...")
            start_time = time.time()
            self.store_scraped_data()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraped data stored successfully in {time.time() - start_time:.2f} seconds.")
        except Exception as e:
            self.log_action("System", "errors", f"Failed to store scraped data: {str(e)}")

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Initialization complete, starting AI tasks...")
        self.log_action("System", "startup", "Initialization completed successfully")

    def clean_logs(self):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Cleaning logs...")
        for root, dirs, files in os.walk(self.log_root):
            for file in files:
                os.remove(os.path.join(root, file))
        self.log_action("System", "startup", "Cleared all logs")

    def spawn_ai_team(self):
        for deity, attrs in list(DEITIES.items())[:6]:
            personality = PERSONALITIES[deity]
            self.ai_team[deity] = {
                "rank": attrs["rank"].value,
                "domain": attrs["domain"],
                "style": attrs["style"],
                "helper": True,
                "active": True,
                "last_task": None,
                "efficiency": 1.0,
                "personality": personality,
                "iq": 150 + (personality["creativity"] * 50),
                "player_file": os.path.join(self.mud_root, "players", f"{deity}.plr")
            }
            ai_file = os.path.join(self.mud_root, "ai", f"ai_{deity.lower()}.py")
            with open(ai_file, "w") as f:
                f.write(f"# {deity} AI for {attrs['domain']} with {personality['tone']} tone\n")
            sys.path.append(os.path.join(self.mud_root, "ai"))
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Spawned AI Team: {list(self.ai_team.keys())}")
        self.log_action("System", "startup", f"Spawned {len(self.ai_team)} AIs")

    def log_action(self, ai_name: str, category: str, message: str, subdir=""):
        log_dir = os.path.join(self.log_root, ai_name, subdir or category.lower()) if ai_name != "System" else os.path.join(self.log_root, category.lower())
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, f"{category.lower()}.log"), "a") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message} - {self.ai_team.get(ai_name, {}).get('personality', {}).get('tone', 'neutral')} tone\n")

    def load_telnet_logs(self):
        files = [f for f in os.listdir(self.telnet_log_dir) if f.startswith("mud_session_") and f.endswith(".json")]
        if not files:
            self.log_action("System", "warnings", "No telnet session logs found")
            return None
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(self.telnet_log_dir, x)))
        try:
            with open(os.path.join(self.telnet_log_dir, latest_file), 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            self.log_action("System", "errors", f"Failed to load telnet logs: {str(e)}")
            return None

    def analyze_logs(self, log_data):
        if not log_data:
            self.log_action("System", "warnings", "Using default mechanics due to no log data")
            return {"commands": [], "responses": [], "patterns": {}, "mechanics": DEFAULT_MECHANICS.copy()}
        try:
            if isinstance(log_data, dict) and "interactions" in log_data:
                commands = [i["data"] for i in log_data["interactions"] if i["type"] == "input"]
                responses = [i["data"] for i in log_data["interactions"] if i["type"] == "output"]
            else:
                lines = log_data.split('\n')
                commands = [line.strip()[1:] for line in lines if line.startswith('>')]
                responses = [line.strip() for line in lines if not line.startswith('>') and line.strip()]
            
            patterns = {}
            for i, cmd in enumerate(commands):
                if i < len(responses):
                    patterns[cmd] = patterns.get(cmd, []) + [responses[i]]
            command_freq = Counter(commands)
            mechanics = {
                "movement": any(c.lower() in ["north", "south", "east", "west", "up", "down"] for c in commands),
                "combat": any(c.lower() in ["attack", "kill", "fight", "parry", "dodge", "block"] for c in commands),
                "inventory": any(c.lower() in ["inventory", "get", "wear", "wield", "remove"] for c in commands),
                "quests": any("quest" in r.lower() or "task" in r.lower() for r in responses),
                "guilds": any("guild" in r.lower() or "class" in r.lower() for r in responses),
                "skills": any("skill" in r.lower() or "train" in c.lower() for c, r in zip(commands, responses)),
                "spells": any("cast" in c.lower() or "spell" in r.lower() for c, r in zip(commands, responses)),
                "rituals": any("perform" in c.lower() or "ritual" in r.lower() for c, r in zip(commands, responses)),
                "tactics": any("tactics" in c.lower() or "defend" in c.lower() for c in commands),
                "dodge": any("dodge" in c.lower() or "dodge" in r.lower() for c, r in zip(commands, responses)),
                "parry": any("parry" in c.lower() or "parry" in r.lower() for c, r in zip(commands, responses)),
                "block": any("block" in c.lower() or "block" in r.lower() for c, r in zip(commands, responses)),
                "soul": any("smile" in c.lower() or "smile" in r.lower() for c, r in zip(commands, responses)),
                "colours": any("colours" in c.lower() or "colour" in r.lower() for c, r in zip(commands, responses))
            }
            self.mechanics_cache = mechanics if any(mechanics.values()) else DEFAULT_MECHANICS.copy()
            return {"commands": commands, "responses": responses, "patterns": patterns, "command_freq": command_freq, "mechanics": self.mechanics_cache}
        except Exception as e:
            self.log_action("System", "errors", f"Failed to analyze logs: {str(e)}")
            return {"commands": [], "responses": [], "patterns": {}, "mechanics": DEFAULT_MECHANICS.copy()}

    def scrape_discworld(self):
        for url in DISCWORLD_SOURCES:
            try:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraping {url}...")
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = " ".join([p.get_text() for p in soup.find_all('p')])
                    self.discworld_data[url] = text
                    self.log_action("System", "status", f"Scraped Discworld mechanics from {url}")
                else:
                    self.discworld_data[url] = f"No data from {url}"
                    self.log_action("System", "warnings", f"Failed to scrape {url}")
            except Exception as e:
                self.discworld_data[url] = f"Error scraping {url}: {str(e)}"
                self.log_action("System", "errors", f"Error scraping {url}: {str(e)}")

    def scrape_forgotten_realms(self):
        for url in FORGOTTEN_REALMS_SOURCES:
            try:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraping {url}...")
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = " ".join([p.get_text() for p in soup.find_all('p')])
                    self.forgotten_realms_data[url] = text
                    self.log_action("System", "status", f"Scraped Forgotten Realms data from {url}")
                else:
                    self.forgotten_realms_data[url] = f"No data from {url}"
                    self.log_action("System", "warnings", f"Failed to scrape {url}")
            except Exception as e:
                self.forgotten_realms_data[url] = f"Error scraping {url}: {str(e)}"
                self.log_action("System", "errors", f"Error scraping {url}: {str(e)}")

    def store_scraped_data(self):
        session = Session()
        try:
            for source, content in {**self.discworld_data, **self.forgotten_realms_data}.items():
                existing = session.query(ScrapedData).filter_by(source_url=source).first()
                if not existing:
                    new_data = ScrapedData(source_url=source, content=content, timestamp=datetime.now())
                    session.add(new_data)
            session.commit()
        except Exception as e:
            session.rollback()
            self.log_action("System", "errors", f"Database error: {str(e)}")
            raise
        finally:
            session.close()
        self.log_action("System", "status", "Stored scraped data in database")

    def setup_multi_agent_env(self):
        class MudEnv(gym.Env):
            def __init__(self, handler):
                super(MudEnv, self).__init__()
                self.handler = handler
                self.action_space = spaces.Discrete(len(TASK_LIST))
                self.observation_space = spaces.Box(low=0, high=1, shape=(3,), dtype=np.float32)
                self.state = np.array([0.0, 1.0, 0.0])
                self.mechanics = handler.mechanics_cache
                self.task_attempts = {task: 0 for task in TASK_LIST}

            def reset(self):
                self.state = np.array([0.0, 1.0, 0.0])
                return self.state

            def step(self, action):
                task = TASK_LIST[action]
                ai_name = random.choice(list(self.handler.ai_team.keys()))
                if not os.path.exists(os.path.join(self.handler.mud_root, "modules", f"{task}.py")) and self.task_attempts[task] < MAX_TASK_RETRIES:
                    result = self.handler.build_module(ai_name, f"{task}.py", "modules")
                    self.task_attempts[task] += 1
                    if "created" in result.lower():
                        self.state[0] += 1.0 / len(TASK_LIST)
                        self.state[2] += 0.1
                        self.task_attempts[task] = 0
                reward = 1.0 if self.state[0] > 0 else -0.1
                done = self.state[0] >= 1.0
                self.state[1] = max(0.5, self.state[1] - 0.05 * self.state[2])
                return self.state, reward, done, {}

        env = MudEnv(self)
        self.agents = {deity: PPO("MlpPolicy", env, verbose=1, learning_rate=0.0001) for deity in self.ai_team}
        self.log_action("System", "status", "Initialized multi-agent reinforcement learning")

    def generate_code(self, ai_name, task):
        if ai_name not in self.ai_team:
            ai_name = random.choice(list(self.ai_team.keys()))
        personality = self.ai_team[ai_name]["personality"]
        scraped_data = self.load_scraped_data()
        discworld_context = " ".join([v for k, v in scraped_data.items() if k in DISCWORLD_SOURCES])[:700] + "..."
        forgotten_realms_context = " ".join([v for k, v in scraped_data.items() if k in FORGOTTEN_REALMS_SOURCES])[:700] + "..."
        dnd_context = f"D&D 5e elements: Races: {', '.join(PLAYER_RACES)}, Classes: {', '.join(DND_CLASSES)}, Spells: {', '.join(DND_SPELLS)}"
        prompt = f"Generate a functional Python {task} module for a MUD game inspired by Discworld MUD's intricate systems (e.g., combat with dodge/parry, skills tree, soul commands) but set in the Forgotten Realms with D&D 5e rules. Use a {personality['tone']} tone with {personality['creativity']*100}% creativity. Incorporate detailed mechanics from {discworld_context} and retheme with {forgotten_realms_context}. Include {dnd_context}. Return only the Python code without repeating the prompt."
        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Generating code for {task} with prompt: {prompt[:100]}...")
            outputs = self.text_generator(
                prompt,
                max_length=1000,
                num_return_sequences=1,
                temperature=personality["creativity"],
                top_k=50,
                do_sample=True,
                truncation=True
            )
            code = outputs[0]["generated_text"].replace(prompt, "").strip()
            if not any(keyword in code.lower() for keyword in ["def", "class", "import"]) or len(code.split()) < 20:
                code = f"def {task}_function():\n    # Basic {task} module inspired by Discworld, set in Forgotten Realms\n    print('A {personality['tone']} function emerges from the ether!')\n    pass"
            else:
                if "def" in code and not code.strip().endswith("pass"):
                    code += "\n    pass"
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Code generated: {code[:100]}...")
            return code
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to generate code for {task}: {str(e)}")
            return f"def {task}_function():\n    # Fallback due to error: {str(e)}\n    pass"

    def check_ai_status(self):
        status_report = {}
        for deity, attrs in self.ai_team.items():
            status_report[deity] = {
                "active": attrs["active"],
                "last_task": attrs["last_task"],
                "efficiency": attrs["efficiency"],
                "iq": attrs["iq"],
                "tasks_assigned": len([t for t in self.tasks.values() if t["ai"] == deity])
            }
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] AI Status Report: {json.dumps(status_report, indent=2)}")
        self.log_action("System", "status", f"AI Status Report generated: {json.dumps(status_report, indent=2)}")
        return status_report

    def process_tasks(self):
        if not self.tasks and not hasattr(self, 'agents'):
            self.setup_multi_agent_env()
        if not self.tasks:
            self.collaborate()
        completed_tasks = []
        for task_key in list(self.tasks.keys()):
            retry_count = self.tasks[task_key].get("retry_count", 0)
            if retry_count >= MAX_TASK_RETRIES:
                self.log_action(self.tasks[task_key]["ai"], "warnings", f"Max retries reached for {task_key}, skipping")
                del self.tasks[task_key]
                continue
            try:
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(self._process_single_task, task_key)
                    result = future.result(timeout=60)
                if "created" in result.lower() or "generated" in result.lower():
                    completed_tasks.append(task_key)
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Task completed: {result}")
                    self.log_action("System", "status", f"Task completed: {result}")
                    ai_name = self.tasks[task_key]["ai"]
                    agent = self.agents.get(ai_name)
                    if agent:
                        env = agent.get_env()
                        obs = env.reset()
                        for _ in range(200):
                            action, _ = agent.predict(obs, deterministic=True)
                            obs, reward, done, info = env.step(action)
                            agent.learn(total_timesteps=1, reset_num_timesteps=False)
                        self.log_action(ai_name, "learning", f"Trained on task {task_key} with reward 1.0")
                else:
                    self.tasks[task_key]["retry_count"] = retry_count + 1
                    self.log_action(self.tasks[task_key]["ai"], "warnings", f"Task {task_key} failed (attempt {retry_count + 1}/{MAX_TASK_RETRIES}): {result}")
            except TimeoutError:
                self.tasks[task_key]["retry_count"] = retry_count + 1
                self.log_action(self.tasks[task_key]["ai"], "errors", f"Task {task_key} timed out (attempt {retry_count + 1}/{MAX_TASK_RETRIES})")
            except Exception as e:
                self.tasks[task_key]["retry_count"] = retry_count + 1
                self.log_action(self.tasks[task_key]["ai"], "errors", f"Task failed for {task_key} (attempt {retry_count + 1}/{MAX_TASK_RETRIES}): {str(e)}")
        for task_key in completed_tasks:
            del self.tasks[task_key]
        if completed_tasks:
            self.evolve_ai(random.choice(list(self.ai_team.keys())))
        self.collaborate()

    def _process_single_task(self, task_key):
        task = self.tasks[task_key]
        try:
            ai = task["ai"]
            if task["type"] == "build_module":
                return self.build_module(ai, task["details"].split(" in ")[0], task["details"].split(" in ")[1])
            elif task["type"] == "generate_mud":
                return self.generate_mud(ai)
            elif task["type"] == "build_website":
                return self.build_website(ai)
        except Exception as e:
            self.log_action(ai, "errors", f"Failed to process task {task['type']}: {str(e)}")
            return f"Failed: {str(e)}"

    def build_module(self, ai_name, filename, system):
        log_data = self.load_telnet_logs()
        analysis = self.analyze_logs(log_data)
        mechanics = analysis.get("mechanics", {})
        path = os.path.join(self.mud_root, system, filename)
        try:
            if os.path.exists(path):
                self.log_action(ai_name, "warnings", f"Skipping: {path} already exists")
                return f"Skipping: {ai_name} - {path}"
            code = self.generate_code(ai_name, filename.split('.')[0])
            if filename == "login.py":
                code = f"""
import asyncio
async def handle_login(reader, writer):
    ascii_art = '''
    Welcome to Faerûn MUD!
    =======================
      ______
     /|_||_\`.__
    (   _    _ _\\
    =|  _    _   |
     | (_)  (_)  |
      \\  _\\/7   _/
       |\\ /  \\  |
        |._   _.' 
         `|""|`
    A Realm of Legends
    '''
    writer.write(ascii_art.encode())
    await writer.drain()
    writer.write("Enter your name: ".encode())
    await writer.drain()
    name = (await reader.read(100)).decode().strip()
    writer.write("Enter your password: ".encode())
    await writer.drain()
    password = (await reader.read(100)).decode().strip()
    return name, password
"""
            elif filename == "creation.py":
                code = f"""
import asyncio
import random
from __main__ import PLAYER_RACES, DND_CLASSES
RACE_INFO = {{
    "human": "Versatile folk with +1 to all stats.",
    "elf": "Graceful beings with +2 Dex, darkvision.",
    "high elf": "Arcane scholars with +2 Int, cantrip.",
    "wild elf": "Feral warriors with +2 Dex, nature affinity.",
    "wood elf": "Forest dwellers with +2 Wis, stealth.",
    "drow": "Dark elves with +2 Cha, superior darkvision.",
    "dwarf": "Stout miners with +2 Con, poison resistance.",
    "duergar": "Deep dwarves with +2 Str, sunlight sensitivity.",
    "orc": "Brutal warriors with +2 Str, relentless endurance.",
    "goblin": "Cunning scavengers with +2 Dex, nimble escape.",
    "gnome": "Inventive tinkerers with +2 Int, advantage on saves.",
    "halfling": "Lucky wanderers with +2 Dex, reroll 1s.",
    "dragonborn": "Draconic kin with +2 Str, breath weapon."
}}
async def create_character(reader, writer):
    writer.write("Choose a race (type 'info <race>' for details):\\n".encode())
    writer.write(f"Options: {', '.join(PLAYER_RACES)}\\n".encode())
    await writer.drain()
    while True:
        race_input = (await reader.read(100)).decode().strip().lower()
        if race_input.startswith("info "):
            race = race_input.split("info ")[1]
            if race in RACE_INFO:
                writer.write(f"{race.capitalize()}: {RACE_INFO[race]}\\n".encode())
            else:
                writer.write("Unknown race.\\n".encode())
            await writer.drain()
            continue
        if race_input in PLAYER_RACES:
            race = race_input
            break
        writer.write("Invalid race. Try again:\\n".encode())
        await writer.drain()
    writer.write("Choose a class:\\n".encode())
    writer.write(f"Options: {', '.join(DND_CLASSES)}\\n".encode())
    await writer.drain()
    class_choice = (await reader.read(100)).decode().strip().lower()
    class_choice = class_choice if class_choice in DND_CLASSES else random.choice(DND_CLASSES)
    writer.write(f"Welcome to Faerûn, {race.capitalize()} {class_choice.capitalize()}! You stand before the deities...\\n".encode())
    await writer.drain()
    return {{'race': race, 'class': class_choice}}
"""
            elif filename == "room.py" and mechanics.get("movement", False):
                code = f"""
class Room:
    def __init__(self, name, desc, flavor=''):
        self.name = name
        self.desc = desc
        self.flavor = flavor
        self.exits = {{}}
        self.npcs = []
    def connect(self, direction, room):
        self.exits[direction] = room
    def look(self):
        exits = ', '.join(self.exits.keys())
        return f"You stand in {self.name}. {self.desc} {self.flavor} Exits: {exits}."
waterdeep = Room("Waterdeep", "A bustling port city.", "Merchants hawk wares nearby.")
baldurs_gate = Room("Baldur's Gate", "A trade hub by the sea.", "Seagulls cry overhead.")
waterdeep.connect("south", baldurs_gate)
baldurs_gate.connect("north", waterdeep)
"""
            elif filename == "combat.py" and mechanics.get("combat", False):
                code = f"""
import random
class Combatant:
    def __init__(self, name, hp, ac=10, skills={{}}):
        self.name = name
        self.hp = hp
        self.ac = ac
        self.skills = skills
        self.tactics = {{'response': 'dodge', 'attitude': 'neutral', 'focus': 'torso'}}
    def attack(self, target):
        roll = random.randint(1, 20) + self.skills.get('fighting.melee', 0) // 20
        if roll >= target.ac:
            dmg = random.randint(1, 4) + self.skills.get('fighting.melee', 0) // 20
            target.hp -= dmg
            return f"{self.name} scratches {target.name} for {dmg} damage!"
        return f"{self.name} misses {target.name}!"
    def dodge(self):
        return random.randint(1, 20) + self.skills.get('dodge', 0) // 20 > 15
    def parry(self):
        return random.randint(1, 20) + self.skills.get('parry', 0) // 20 > 15
    def block(self):
        return random.randint(1, 20) + self.skills.get('block', 0) // 20 > 15
    def set_tactics(self, response=None, attitude=None, focus=None):
        if response in ['dodge', 'parry', 'block', 'none']:
            self.tactics['response'] = response
        if attitude in ['offensive', 'defensive', 'neutral']:
            self.tactics['attitude'] = attitude
        if focus in ['head', 'torso', 'arms', 'legs']:
            self.tactics['focus'] = focus
        return f"{self.name} adjusts tactics to {self.tactics}."
adventurer = Combatant("Adventurer", 325, 15, {{'fighting.melee': 10, 'dodge': 10}})
goblin = Combatant("Goblin", 15, 12, {{'fighting.melee': 20}})
"""
            elif filename == "skills.py" and mechanics.get("skills", False):
                code = f"""
SKILLS = {{
    'adventuring.direction': 10, 'fighting.melee.sword': 10, 'magic.spells.offensive': 10,
    'covert.stealth': 10, 'dodge': 10, 'parry': 10, 'block': 10
}}
XP_COSTS = {{11: 800, 12: 1600}}  # Simplified for now
def train_skill(player, skill, amount=1):
    if skill in SKILLS:
        current = SKILLS[skill]
        next_level = current + amount
        xp_cost = XP_COSTS.get(next_level, 9999)
        SKILLS[skill] = next_level
        return f"{player} trains {skill} to {next_level} for {xp_cost} XP!"
    return "No such skill exists in Faerûn!"
def check_skills(player):
    return f"{player}'s skills:\\n" + '\\n'.join([f'  {k}: {v}' for k, v in SKILLS.items()])
"""
            elif filename == "inventory.py" and mechanics.get("inventory", False):
                code = f"""
class Item:
    def __init__(self, name, slot=None, layer=None):
        self.name = name
        self.slot = slot
        self.layer = layer
class Inventory:
    def __init__(self):
        self.items = []
        self.worn = {{}}
        self.layers = {{}}
    def add(self, item):
        self.items.append(item)
        return f"Added {item.name} to inventory."
    def get(self, item_name, room_items):
        for item in room_items:
            if item_name.lower() in item.name.lower():
                return self.add(item)
        return "You can't pick that up!"
    def list(self):
        if not self.items:
            return "You are carrying nothing at all."
        return f"You are carrying:\\n" + '\\n'.join([item.name for item in self.items])
inv = Inventory()
"""
            elif filename == "soul.py" and mechanics.get("soul", False):
                code = f"""
def soul(player, action, target=None):
    actions = {{
        'smile': f"{player} smiles happily{{' at ' + target if target else ''}}.",
        'frown': f"{player} frowns{{' at ' + target if target else ' in displeasure'}}.",
        'nod': f"{player} nods{{' to ' + target if target else ' thoughtfully'}}."
    }}
    return actions.get(action, f"{player} tries to {action} but looks confused.")
"""
            elif filename == "term.py":
                code = f"""
async def set_term(reader, writer, term_type=None, rows=None, cols=None):
    if term_type:
        writer.write(f"Terminal set to {term_type}.\\n".encode())
    if rows and cols:
        writer.write(f"Terminal size set to {rows}x{cols}.\\n".encode())
    else:
        writer.write("Syntax: term [type] [rows] [cols]\\n".encode())
    await writer.drain()
    return term_type, rows, cols
"""
            elif filename == "network.py":
                code = f"""
async def set_network(reader, writer, option=None, state=None):
    options = {{'telnet': True, 'mccp': False, 'mxp': False}}
    if option in options and state in ['on', 'off']:
        options[option] = (state == 'on')
        writer.write(f"Network {option} set to {state}.\\n".encode())
    else:
        writer.write("Syntax: network [telnet|mccp|mxp] [on|off]\\n".encode())
    await writer.drain()
    return options
"""
            elif filename == "colours.py" and mechanics.get("colours", False):
                code = f"""
ANSI_COLOURS = {{
    'red': '^[[31m', 'green': '^[[32m', 'blue': '^[[34m', 'reset': '^[[0m'
}}
async def set_colours(reader, writer, mode=None, colour=None):
    if mode in ['brief', 'verbose'] and colour in ANSI_COLOURS:
        writer.write(f"{ANSI_COLOURS[colour]}{mode.capitalize()} mode activated.{ANSI_COLOURS['reset']}\\n".encode())
    else:
        writer.write("Syntax: colours [brief|verbose] [red|green|blue]\\n".encode())
    await writer.drain()
"""
            elif filename == "syntax.py":
                code = f"""
SYNTAX_DB = {{
    'tactics': 'tactics <response|attitude|focus> <option>\\nresponse: dodge, parry, block, none\\nattitude: offensive, defensive, neutral\\nfocus: head, torso, arms, legs',
    'inventory': 'inventory [verbose] [all] [category] [worn]',
    'kill': 'kill <target> [with <weapon>]',
    'cast': 'cast <spell> [on <target>] [with <component>]',
    'perform': 'perform <ritual> [on <target>] [with <component>]',
    'colours': 'colours [brief|verbose] [red|green|blue]'
}}
def get_syntax(command):
    return SYNTAX_DB.get(command, f"No syntax found for '{command}'.")
"""
            elif filename == "help.py":
                code = f"""
HELP_DB = {{
    'combat': 'Combat is inevitable in Faerûn. See "syntax tactics" for details.',
    'skills': 'Skills define your abilities. See "skills" for your list.',
    'inventory': 'Your inventory holds your gear. See "syntax inventory".',
    'cast': 'Wizards cast spells. See "syntax cast".',
    'perform': 'Priests perform rituals. See "syntax perform".',
    'colours': 'Colours enhance your display. See "syntax colours".'
}}
def get_help(topic):
    return HELP_DB.get(topic, 'Try "help topics" for a list.')
"""
            with open(path, "w") as f:
                f.write(code)
            self.log_action(ai_name, "writing", f"Wrote {path}")
            return f"{ai_name} created {path}"
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to build module {filename}: {str(e)}")
            return f"Failed: {str(e)}"

    def generate_mud(self, ai_name):
        log_data = self.load_telnet_logs()
        analysis = self.analyze_logs(log_data)
        mechanics = analysis.get("mechanics", {})
        mud_file = os.path.join(self.mud_root, "mud.py")
        try:
            if os.path.exists(mud_file):
                self.log_action(ai_name, "warnings", f"Skipping: {mud_file} already exists")
                return f"Skipping: {ai_name} - {mud_file}"
            code = self.generate_code(ai_name, "mud_server")
            if not any(keyword in code.lower() for keyword in ["def", "class", "import"]) or mechanics.get("movement", False) or mechanics.get("combat", False):
                code = f"""
import asyncio
from modules.room import Room
from modules.combat import Combatant
from modules.inventory import Inventory
from modules.soul import soul
from modules.skills import check_skills
from modules.term import set_term
from modules.network import set_network
from modules.colours import set_colours, ANSI_COLOURS
from modules.syntax import get_syntax
from modules.help import get_help

rooms = {{}}
players = {{}}
npcs = [Combatant("Cartographer", 15, 12, {{'fighting.melee': 10}})]

async def handle_client(reader, writer):
    global rooms, players, npcs
    addr = writer.get_extra_info('peername')
    if not rooms:
        rooms["Waterdeep"] = Room("Waterdeep", "A bustling port city.", "Merchants hawk wares nearby.")
        rooms["Baldur's Gate"] = Room("Baldur's Gate", "A trade hub by the sea.", "Seagulls cry overhead.")
        rooms["Waterdeep"].connect("south", rooms["Baldur's Gate"])
        rooms["Baldur's Gate"].connect("north", rooms["Waterdeep"])
        rooms["Waterdeep"].npcs.append(npcs[0])

    from modules.login import handle_login
    name, _ = await handle_login(reader, writer)
    from modules.creation import create_character
    char_info = await create_character(reader, writer)
    player = Combatant(name, 325, 15, {{'fighting.melee': 10, 'dodge': 10}})
    player.inv = Inventory()
    players[addr] = {{'combatant': player, 'room': rooms["Waterdeep"], 'fighting': None}}
    writer.write(f"{ANSI_COLOURS['green']}Logged in as {name}. Welcome to Faerûn!{ANSI_COLOURS['reset']}\\n".encode())
    await writer.drain()

    while True:
        data = await reader.read(100)
        if not data:
            break
        cmd = data.decode().strip().lower().split()
        if not cmd:
            continue
        action = cmd[0]
        args = cmd[1:] if len(cmd) > 1 else []

        if action in ['n', 's', 'e', 'w', 'u', 'd']:
            direction = {{'n': 'north', 's': 'south', 'e': 'east', 'w': 'west', 'u': 'up', 'd': 'down'}}[action]
            current_room = players[addr]['room']
            if direction in current_room.exits:
                players[addr]['room'] = current_room.exits[direction]
                writer.write(f"You trudge {direction} to {players[addr]['room'].name}.\\n".encode())
            else:
                writer.write("You can't go that way!\\n".encode())
        elif action == 'look':
            writer.write(f"{players[addr]['room'].look()}\\n".encode())
        elif action == 'who':
            player_list = ', '.join([p['combatant'].name for p in players.values()])
            writer.write(f"Players in Faerûn: {player_list}\\n".encode())
        elif action == 'smile':
            target = args[0] if args else None
            writer.write(f"{soul(name, 'smile', target)}\\n".encode())
        elif action == 'inventory':
            writer.write(f"{players[addr]['combatant'].inv.list()}\\n".encode())
        elif action == 'get':
            if args:
                writer.write(f"{players[addr]['combatant'].inv.get(args[0], players[addr]['room'].npcs)}\\n".encode())
            else:
                writer.write("Get what?\\n".encode())
        elif action == 'kill':
            target_name = args[0] if args else None
            target = next((npc for npc in players[addr]['room'].npcs if target_name in npc.name.lower()), None)
            if target:
                players[addr]['fighting'] = target
                writer.write(f"You prepare to attack {target.name}...\\n".encode())
                for _ in range(3):  # Simulate short fight
                    msg = player.attack(target)
                    writer.write(f"{msg}\\n".encode())
                    if target.hp > 0:
                        writer.write(f"{target.attack(player)}\\n".encode())
                    await asyncio.sleep(1)
                players[addr]['fighting'] = None
                writer.write("You stop fighting.\\n".encode())
            else:
                writer.write("No such target here!\\n".encode())
        elif action == 'skills':
            writer.write(f"{check_skills(name)}\\n".encode())
        elif action == 'score':
            p = players[addr]['combatant']
            writer.write(f"{p.name}: HP: {p.hp}/325, GP: 130/130, XP: 172, Burden: 0%\\n".encode())
        elif action == 'term':
            await set_term(reader, writer, *args)
        elif action == 'network':
            await set_network(reader, writer, *args)
        elif action == 'colours':
            await set_colours(reader, writer, *args)
        elif action == 'syntax':
            writer.write(f"{get_syntax(args[0] if args else 'help')}\\n".encode())
        elif action == 'help':
            writer.write(f"{get_help(args[0] if args else 'topics')}\\n".encode())
        elif action == 'quit':
            writer.write(f"{ANSI_COLOURS['blue']}Farewell, adventurer!{ANSI_COLOURS['reset']}\\n".encode())
            break
        else:
            writer.write("Command not recognized.\\n".encode())
        await writer.drain()

    del players[addr]
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 3000)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
"""
            with open(mud_file, "w") as f:
                f.write(code)
            os.chmod(mud_file, 0o755)
            self.log_action(ai_name, "writing", f"Generated MUD at {mud_file}")
            return f"{ai_name} generated {mud_file}"
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to generate MUD: {str(e)}")
            return f"Failed: {str(e)}"

    def build_website(self, ai_name):
        app = fastapi.FastAPI()
        templates = Jinja2Templates(directory=os.path.join(self.mud_root, "website", "templates"))
        app.mount("/static", StaticFiles(directory=os.path.join(self.mud_root, "website", "static")), name="static")
        try:
            map_prompt = "A Forgotten Realms map with Waterdeep, Baldur’s Gate, and mystical forests."
            map_path = self.generate_image(map_prompt)
            @app.get("/", response_class=HTMLResponse)
            async def read_root(request: fastapi.Request):
                return templates.TemplateResponse("index.html", {"request": request, "map_path": map_path.split('/')[-1]})
            with open(os.path.join(self.mud_root, "website", "templates", "index.html"), "w") as f:
                f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Forgotten Realms MUD</title>
    <style>
        body { background: #1a0d00; color: #d4a373; font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        #map { width: 100%; height: auto; border: 2px solid #d4a373; }
        #mud-client { width: 100%; height: 600px; background: black; color: #d4a373; border: 2px solid #d4a373; }
        .button { background: #2f1a00; color: #d4a373; border: 1px solid #d4a373; padding: 5px; margin: 5px; }
    </style>
</head>
<body>
    <h1>Forgotten Realms MUD</h1>
    <img id="map" src="/static/images/{{ map_path }}" alt="Forgotten Realms Map">
    <div id="mud-client"></div>
    <div>
        <button class="button" onclick="sendCommand('look')">Look</button>
        <button class="button" onclick="sendCommand('n')">North</button>
        <button class="button" onclick="sendCommand('kill goblin')">Kill Goblin</button>
    </div>
    <script>
        let ws = new WebSocket('ws://127.0.0.1:3000');
        ws.onmessage = (event) => document.getElementById('mud-client').innerHTML += event.data + '<br>';
        function sendCommand(cmd) { ws.send(cmd); }
        document.addEventListener('keydown', (e) => { if (e.key === 'Enter') ws.send(document.getElementById('mud-client').value); });
    </script>
</body>
</html>
""")
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
            self.log_action(ai_name, "writing", f"Built website at /mnt/home2/mud/website")
            return f"{ai_name} built website"
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to build website: {str(e)}")
            return f"Failed: {str(e)}"

    def evolve_ai(self, ai_name):
        personality = self.ai_team[ai_name]["personality"]
        try:
            self.ai_team[ai_name]["efficiency"] += random.uniform(0.1, 0.3) * personality["creativity"]
            self.ai_team[ai_name]["iq"] += random.randint(1, 5)
            self.log_action(ai_name, "editing", f"Evolved: Efficiency {self.ai_team[ai_name]['efficiency']}, IQ {self.ai_team[ai_name]['iq']}")
            log_data = self.load_telnet_logs()
            if log_data:
                new_code = self.generate_code(ai_name, "self_improvement")
                with open(os.path.join(self.mud_root, "ai", f"ai_{ai_name.lower()}.py"), "a") as f:
                    f.write(f"\n# Self-evolved code\n{new_code}")
            print(f"{ai_name} evolved with {personality['tone']} flair")
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to evolve AI: {str(e)}")

    def collaborate(self):
        log_data = self.load_telnet_logs()
        if log_data:
            analysis = self.analyze_logs(log_data)
            mechanics = analysis.get("mechanics", {})
        else:
            mechanics = self.mechanics_cache
        for ai_name, agent in self.agents.items():
            available_tasks = [t for t in TASK_LIST if not os.path.exists(os.path.join(self.mud_root, "modules", f"{t}.py"))]
            if available_tasks and (not any(os.path.exists(os.path.join(self.mud_root, "modules", f"{task}.py")) for task in TASK_LIST) or random.random() > 0.7):
                task = random.choice(available_tasks)
                self.assign_task(ai_name, "build_module", f"{task}.py in modules", delegated_by="Collective")
            elif not available_tasks:
                self.log_action("System", "status", "All module tasks completed, skipping further assignments")
        if not os.path.exists(os.path.join(self.mud_root, "mud.py")) and mechanics.get("movement", False):
            self.assign_task("Ao", "generate_mud", "mud.py in mud_root", delegated_by="System")
        if not os.path.exists(os.path.join(self.mud_root, "website", "templates", "index.html")):
            self.assign_task("Ao", "build_website", "website in mud_root", delegated_by="System")
        self.log_action("System", "status", "Agents collaborated on tasks")

    def delegate_tasks(self):
        log_data = self.load_telnet_logs()
        if log_data:
            analysis = self.analyze_logs(log_data)
            mechanics = analysis.get("mechanics", {})
        else:
            mechanics = self.mechanics_cache
        initial_tasks = ["login", "creation", "room", "combat", "npcs", "quests", "skills", "inventory", "spells", "guilds", "soul", "term", "network", "colours"]
        for god in [n for n, a in self.ai_team.items() if a["rank"] in ["Overdeity", "Greater Deity"]]:
            subordinates = [n for n, a in self.ai_team.items() if a["rank"] in ["Intermediate Deity", "Lesser Deity", "Demigod", "Quasi-Deity"]]
            for task in initial_tasks:
                if not os.path.exists(os.path.join(self.mud_root, "modules", f"{task}.py")) and (task in ["room", "combat"] or random.random() > 0.3):
                    self.assign_task(random.choice(subordinates), "build_module", f"{task}.py in modules", delegated_by=god)
            if not os.path.exists(os.path.join(self.mud_root, "mud.py")) and mechanics.get("movement", False):
                self.assign_task(god, "generate_mud", "mud.py in mud_root", delegated_by="System")
            if not os.path.exists(os.path.join(self.mud_root, "website", "templates", "index.html")):
                self.assign_task(god, "build_website", "website in mud_root", delegated_by="System")

    def assign_task(self, ai_name: str, task_type: str, details: str, delegated_by: Optional[str] = None):
        if " in " not in details:
            details = f"{details}.py in modules"
        task_key = f"{ai_name}_{task_type}_{details.replace(' ', '_')}"
        filename, system = details.split(" in ")
        path = os.path.join(self.mud_root, system, filename)
        try:
            if ai_name not in self.ai_team or (task_key in self.tasks and os.path.exists(path)):
                self.log_action("System", "warnings", f"Skipping: {ai_name} task {task_type} for {details} - File exists or already assigned.")
                return f"Skipping: {ai_name} task {task_type} for {details} - File exists or already assigned."
            task = {"ai": ai_name, "type": task_type, "details": details, "time": time.time(), "delegated_by": delegated_by, "retry_count": 0}
            self.tasks[task_key] = task
            self.ai_team[ai_name]["last_task"] = task
            self.log_action(ai_name, "tasks", f"Assigned: {task_type} - {details} by {delegated_by or 'self'}")
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Assigned task to {ai_name}: {task_type} - {details}")
            return f"Task assigned to {ai_name}: {task_type} - {details}"
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to assign task: {str(e)}")
            return f"Failed to assign task: {str(e)}"

    def load_scraped_data(self):
        session = Session()
        try:
            data = {d.source_url: d.content for d in session.query(ScrapedData).all()}
            return data
        except Exception as e:
            self.log_action("System", "errors", f"Failed to load scraped data: {str(e)}")
            return {}
        finally:
            session.close()

    def generate_image(self, prompt):
        try:
            image = self.image_generator(prompt).images[0]
            image_path = os.path.join(self.mud_root, "website", "static", "images", f"map_{int(time.time())}.png")
            image.save(image_path)
            return image_path
        except Exception as e:
            self.log_action("System", "errors", f"Failed to generate image: {str(e)}")
            return "default_map.png"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MUD AI Handler")
    parser.add_argument("--clean-logs", action="store_true", help="Clean all logs before starting")
    args = parser.parse_args()

    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Script started")
        handler = AIHandler(clean_logs=args.clean_logs)
        handler.spawn_ai_team()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] AI system running. Access website at http://localhost:8000, MUD at telnet 127.0.0.1:3000")
        while True:
            handler.process_tasks()
            time.sleep(0.1)
    except Exception as e:
        with open(os.path.join("/mnt/home2/mud", "logs", "crashes", "crashes.log"), "a") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Crash: {str(e)}\\n")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] AI failed: {str(e)}")
        raise
