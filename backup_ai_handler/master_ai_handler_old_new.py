#!/usr/bin/env python3
import random
import time
import os
import json
from enum import Enum
from typing import Dict, List, Optional
import requests
import importlib.util
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from bs4 import BeautifulSoup
from collections import Counter
import asyncio
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
from diffusers import StableDiffusionPipeline
import numpy as np
from PIL import Image
import fastapi
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
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
    "Kelemvor": {"tone": "somber", "humor": "dark", "creativity": 0.75},
    "Tyr": {"tone": "stern", "humor": "serious", "creativity": 0.8},
    "Tempus": {"tone": "bold", "humor": "gruff", "creativity": 0.75},
    "Lathander": {"tone": "optimistic", "humor": "cheerful", "creativity": 0.9},
    "Helm": {"tone": "calm", "humor": "dry", "creativity": 0.7},
    "Oghma": {"tone": "curious", "humor": "wry", "creativity": 0.95},
    "Umberlee": {"tone": "wild", "humor": "sarcastic", "creativity": 0.85}
}

DEITIES = {
    "Ao": {"rank": AIRank.OVERDEITY, "domain": "Balance", "style": "cosmic"},
    "Mystra": {"rank": AIRank.GREATER_DEITY, "domain": "Magic", "style": "arcane"},
    "Bane": {"rank": AIRank.GREATER_DEITY, "domain": "Tyranny", "style": "dark"},
    "Selûne": {"rank": AIRank.INTERMEDIATE_DEITY, "domain": "Moon", "style": "gentle"},
    "Torm": {"rank": AIRank.LESSER_DEITY, "domain": "Duty", "style": "noble"},
    "Kelemvor": {"rank": AIRank.LESSER_DEITY, "domain": "Death", "style": "somber"},
    "Tyr": {"rank": AIRank.GREATER_DEITY, "domain": "Justice", "style": "righteous"},
    "Tempus": {"rank": AIRank.GREATER_DEITY, "domain": "War", "style": "fierce"},
    "Lathander": {"rank": AIRank.INTERMEDIATE_DEITY, "domain": "Life", "style": "radiant"},
    "Helm": {"rank": AIRank.INTERMEDIATE_DEITY, "domain": "Protection", "style": "steadfast"},
    "Oghma": {"rank": AIRank.LESSER_DEITY, "domain": "Knowledge", "style": "scholarly"},
    "Umberlee": {"rank": AIRank.LESSER_DEITY, "domain": "Oceans", "style": "tempestuous"}
}

DISCWORLD_SOURCES = [
    "https://discworld.starturtle.net/lpc/playing/documentation.c?path=/newbie/essentials",
    "https://dwwiki.mooo.com/",
]
FORGOTTEN_REALMS_SOURCES = [
    "https://forgottenrealms.fandom.com/wiki/Main_Page",
    "https://forgottenrealms.fandom.com/wiki/Portal:Deities",
]
TASK_LIST = [
    "login", "creation", "room", "races", "classes", "combat", "skills", "inventory",
    "spells", "guilds", "npcs", "quests", "rituals", "world", "armors", "weapons"
]

class AIHandler:
    def __init__(self, mud_root: str = "/mnt/home2/mud"):
        self.mud_root = mud_root
        self.log_root = os.path.join(mud_root, "logs")
        self.ai_team: Dict[str, dict] = {}
        self.tasks: Dict[str, dict] = {}
        self.event_log: List[dict] = []
        self.performance: Dict[str, float] = {}
        self.executor = ThreadPoolExecutor(max_workers=12)
        self.telnet_log_dir = mud_root
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.image_generator = None
        self.llm = None
        self.chain = None
        self.discworld_data = {}
        self.forgotten_realms_data = {}

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting initialization...")
        os.makedirs(mud_root, exist_ok=True)
        for dir_path in [self.log_root, os.path.join(self.log_root, "status"), os.path.join(self.log_root, "mud_errors"), os.path.join(self.log_root, "script_errors"), os.path.join(self.log_root, "warnings"), os.path.join(self.log_root, "crashes"), os.path.join(mud_root, "players"), os.path.join(mud_root, "modules"), os.path.join(mud_root, "ai"), os.path.join(mud_root, "website", "static", "images"), os.path.join(mud_root, "website", "static", "css"), os.path.join(mud_root, "website", "static", "js"), os.path.join(mud_root, "website", "templates"), os.path.join(mud_root, "data", "db"), os.path.join(mud_root, "data", "embeddings")]:
            os.makedirs(dir_path, exist_ok=True)
        self.log_action("System", "startup", f"Initialized directories at {mud_root}")

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Loading GPT-2 model...")
            self.model = GPT2LMHeadModel.from_pretrained("gpt2-large")
            self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2-large")
            self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, max_length=50)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] GPT-2 model loaded successfully.")
        except Exception as e:
            self.log_action("System", "errors", f"Failed to load GPT-2: {str(e)}")
            print(f"Error loading GPT-2: {str(e)}")
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
            print(f"Error loading Stable Diffusion: {str(e)}")
            raise

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Initializing LangChain...")
            self.llm = OpenAI(api_key="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")
            self.prompt = PromptTemplate(input_variables=["task"], template="Generate a {task} module for a MUD, inspired by Forgotten Realms and Discworld logs/mechanics, with unique mechanics.")
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] LangChain initialized successfully.")
        except Exception as e:
            self.log_action("System", "errors", f"Failed to initialize LangChain: {str(e)}")
            print(f"Error initializing LangChain: {str(e)}")
            raise

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Downloading NLTK 'punkt' data...")
            nltk.download('punkt', quiet=True, download_dir='/tmp/nltk_data', raise_on_error=True)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] NLTK 'punkt' data downloaded successfully.")
        except Exception as e:
            self.log_action("System", "errors", f"Failed to download NLTK 'punkt' data: {str(e)}")
            print(f"Warning: NLTK 'punkt' download failed: {str(e)}. Proceeding without it.")

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Discworld scraping...")
            start_time = time.time()
            self.scrape_discworld()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Discworld scraping completed in {time.time() - start_time:.2f} seconds.")
        except Exception as e:
            self.log_action("System", "errors", f"Scraping Discworld failed: {str(e)}")
            print(f"Error scraping Discworld: {str(e)}")

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Forgotten Realms scraping...")
            start_time = time.time()
            self.scrape_forgotten_realms()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Forgotten Realms scraping completed in {time.time() - start_time:.2f} seconds.")
        except Exception as e:
            self.log_action("System", "errors", f"Scraping Forgotten Realms failed: {str(e)}")
            print(f"Error scraping Forgotten Realms: {str(e)}")

        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Storing scraped data...")
            start_time = time.time()
            self.store_scraped_data()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraped data stored successfully in {time.time() - start_time:.2f} seconds.")
        except Exception as e:
            self.log_action("System", "errors", f"Failed to store scraped data: {str(e)}")
            print(f"Error storing scraped data: {str(e)}")

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Initialization complete, starting AI tasks...")
        self.log_action("System", "startup", "Initialization completed successfully")

    def spawn_ai_team(self):
        for deity, attrs in list(DEITIES.items())[:12]:
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
            return {"commands": [], "responses": [], "patterns": {}}
        try:
            commands = [i["data"] for i in log_data["interactions"] if i["type"] == "input"]
            responses = [i["data"] for i in log_data["interactions"] if i["type"] == "output"]
            patterns = {}
            for i, cmd in enumerate(commands):
                if i < len(responses):
                    patterns[cmd] = patterns.get(cmd, []) + [responses[i]]
            command_freq = Counter(commands)
            return {"commands": commands, "responses": responses, "patterns": patterns, "command_freq": command_freq}
        except Exception as e:
            self.log_action("System", "errors", f"Failed to analyze logs: {str(e)}")
            return {"commands": [], "responses": [], "patterns": {}}

    def scrape_discworld(self):
        for url in DISCWORLD_SOURCES:
            try:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraping {url}...")
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = " ".join([p.get_text() for p in soup.find_all('p')])
                    self.discworld_data[url] = text
                    self.log_action("System", "status", f"Scraped Discworld data from {url}")
                else:
                    self.discworld_data[url] = f"No data from {url}"
                    self.log_action("System", "warnings", f"Failed to scrape {url}")
            except Exception as e:
                self.discworld_data[url] = f"Error scraping {url}: {str(e)}"
                self.log_action("System", "errors", f"Error scraping {url}: {str(e)}")
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Skipping {url} due to {str(e)}")

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
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Skipping {url} due to {str(e)}")

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
            def __init__(self, ai_team):
                super(MudEnv, self).__init__()
                self.ai_team = ai_team
                self.action_space = spaces.Discrete(len(TASK_LIST))  # One action per task
                self.observation_space = spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)  # [progress, efficiency]
                self.state = np.array([0.0, 1.0])  # Initial state: no progress, full efficiency

            def reset(self):
                self.state = np.array([0.0, 1.0])
                return self.state

            def step(self, action):
                task = TASK_LIST[action]
                if not os.path.exists(os.path.join(self.ai_team["handler"].mud_root, "modules", f"{task}.py")):
                    self.ai_team["handler"].build_module(list(self.ai_team.keys())[0], f"{task}.py", "modules")
                    self.state[0] += 1.0 / len(TASK_LIST)  # Incremental progress
                reward = 1.0 if self.state[0] > 0 else -0.1
                done = self.state[0] >= 1.0
                self.state[1] = max(0.5, self.state[1] - 0.05)  # Decrease efficiency
                return self.state, reward, done, {}

        env = MudEnv({"handler": self, "ai_team": self.ai_team})
        self.agents = {deity: PPO("MlpPolicy", env, verbose=1) for deity in self.ai_team}
        self.log_action("System", "status", "Initialized multi-agent reinforcement learning")

    def generate_code(self, ai_name, task):
        personality = self.ai_team[ai_name]["personality"]
        scraped_data = self.load_scraped_data()
        discworld_context = " ".join([v for k, v in scraped_data.items() if k in DISCWORLD_SOURCES])[:500] + "..."
        forgotten_realms_context = " ".join([v for k, v in scraped_data.items() if k in FORGOTTEN_REALMS_SOURCES])[:500] + "..."
        prompt = f"Generate a {task} module for a MUD, inspired by Discworld mechanics ({discworld_context}) and Forgotten Realms lore ({forgotten_realms_context}), with a {personality['tone']} tone and {personality['creativity']*100}% creativity. Include unique mechanics."
        try:
            code = self.chain.run(task=task)
            return code
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to generate code for {task}: {str(e)}")
            raise

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
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = {executor.submit(self._process_single_task, task_key): task_key for task_key in self.tasks.keys()}
            for future in futures:
                try:
                    result = future.result(timeout=30)  # Increased timeout
                    completed_tasks.append(futures[future])
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Task completed: {result}")
                    self.log_action("System", "status", f"Task completed: {result}")
                except TimeoutError:
                    self.log_action(self.tasks[futures[future]]["ai"], "warnings", "Task timed out")
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Task timed out for {futures[future]}")
                except Exception as e:
                    self.log_action(self.tasks[futures[future]]["ai"], "errors", f"Task failed: {str(e)}")
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Task failed for {futures[future]}: {str(e)}")
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
            raise

    def build_module(self, ai_name: str, filename: str, system: str):
        log_data = self.load_telnet_logs()
        analysis = self.analyze_logs(log_data)
        path = os.path.join(self.mud_root, system, filename)
        try:
            if os.path.exists(path):
                self.log_action(ai_name, "warnings", f"Skipping: {path} already exists")
                return f"Skipping: {ai_name} - {path}"
            code = self.generate_code(ai_name, filename.split('.')[0])
            if filename == "creation.py":
                allowed_races = ["human", "elf", "high elf", "drow", "wild elf", "wood elf", "duergar", "dwarf", "gnome", "orc", "goblin", "dragonborn"]
                code = f"""
import asyncio
async def create_character(reader, writer):
    writer.write("Choose race ({', '.join({allowed_races})}): ".encode())
    race = await reader.read(100)
    race = race.decode().strip().lower()
    races = {{r: {{'hp': 20 if r in ['human', 'dwarf'] else 15}} for r in {allowed_races}}}
    if race in races:
        writer.write(f"Created a {race}! HP: {{races[race]['hp']}}\\n".encode())
        return {{'race': race, 'hp': races[race]['hp']}}
    writer.write("Invalid race. Choose from {', '.join({allowed_races})}.\\n".encode())
    return None
""" + "\n# Additional races can be created by AI but not selectable: " + str([r for r in self.forgotten_realms_data.get("https://forgottenrealms.fandom.com/wiki/Category:Races", "").split() if r not in allowed_races])
            elif filename == "races.py":
                all_races = self.forgotten_realms_data.get("https://forgottenrealms.fandom.com/wiki/Category:Races", "").split()
                code += f"\nRACES = {{r: {{'desc': 'A {r} from Forgotten Realms'}} for r in {all_races}}}"
            with open(path, "w") as f:
                f.write(code)
            self.log_action(ai_name, "writing", f"Wrote {path}")
            return f"{ai_name} created {path}"
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to build module {filename}: {str(e)}")
            raise

    def generate_mud(self, ai_name: str):
        log_data = self.load_telnet_logs()
        analysis = self.analyze_logs(log_data)
        mud_file = os.path.join(self.mud_root, "mud.py")
        try:
            code = self.generate_code(ai_name, "mud_server")
            with open(mud_file, "w") as f:
                f.write(code)
            os.chmod(mud_file, 0o755)
            self.log_action(ai_name, "writing", f"Generated MUD at {mud_file}")
            return f"{ai_name} generated {mud_file}"
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to generate MUD: {str(e)}")
            raise

    def build_website(self, ai_name: str):
        app = fastapi.FastAPI()
        templates = Jinja2Templates(directory=os.path.join(self.mud_root, "website", "templates"))
        app.mount("/static", StaticFiles(directory=os.path.join(self.mud_root, "website", "static")), name="static")
        try:
            map_prompt = "A unique Forgotten Realms-inspired world map with mystical forests, towering mountains, and shimmering seas, in a vintage style."
            map_path = self.generate_image(map_prompt)
            @app.get("/", response_class=HTMLResponse)
            async def read_root(request: fastapi.Request):
                return templates.TemplateResponse("index.html", {"request": request, "map_path": map_path.split('/')[-1]})
            with open(os.path.join(self.mud_root, "website", "templates", "index.html"), "w") as f:
                f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Dawn of Faerûn</title>
    <style>
        body { background: #1a0d00; color: #d4a373; font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        #map { width: 100%; height: auto; border: 2px solid #d4a373; }
        #mud-client { width: 100%; height: 600px; background: black; color: #d4a373; border: 2px solid #d4a373; }
        .button { background: #2f1a00; color: #d4a373; border: 1px solid #d4a373; padding: 5px; margin: 5px; }
    </style>
</head>
<body>
    <h1>Dawn of Faerûn</h1>
    <img id="map" src="/static/images/{{ map_path }}" alt="World Map">
    <div id="mud-client"></div>
    <div>
        <button class="button" onclick="sendCommand('look')">Look</button>
        <button class="button" onclick="sendCommand('north')">Move North</button>
    </div>
    <script>
        let ws = new WebSocket('ws://127.0.0.1:3000');
        ws.onmessage = (event) => document.getElementById('mud-client').innerHTML += event.data + '<br>';
        function sendCommand(cmd) { ws.send(cmd); }
        document.addEventListener('keydown', (e) => { if (e.key === 'Enter')
ws.send(document.getElementById('mud-client').value); });
    </script>
</body>
</html>
""")
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
            self.log_action(ai_name, "writing", f"Built website at /mnt/home2/mud/website")
            return f"{ai_name} built website"
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to build website: {str(e)}")
            raise

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
            for ai_name, agent in self.agents.items():
                obs = np.random.rand(2)  # Match observation_space shape (2,)
                action, _ = agent.predict(obs, deterministic=True)
                self.assign_task(ai_name, "build_module", f"{TASK_LIST[action % len(TASK_LIST)]}.py in modules", delegated_by="Collective")
        else:
            self.log_action("System", "warnings", "No telnet logs found, assigning default tasks")
            self.delegate_tasks()
        self.log_action("System", "status", "Agents collaborated on tasks")

    def delegate_tasks(self):
        log_data = self.load_telnet_logs()
        if log_data:
            analysis = self.analyze_logs(log_data)
        initial_tasks = ["login", "creation", "room", "combat", "npcs", "quests"]
        for god in [n for n, a in self.ai_team.items() if a["rank"] in ["Overdeity", "Greater Deity"]]:
            subordinates = [n for n, a in self.ai_team.items() if a["rank"] in ["Intermediate Deity", "Lesser Deity", "Demigod", "Quasi-Deity"]]
            for task in initial_tasks:
                if not os.path.exists(os.path.join(self.mud_root, "modules", f"{task}.py")):
                    self.assign_task(random.choice(subordinates), "build_module", f"{task}.py in modules", delegated_by=god)
            if not os.path.exists(os.path.join(self.mud_root, "mud.py")):
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
            task = {"ai": ai_name, "type": task_type, "details": details, "time": time.time(), "delegated_by": delegated_by}
            self.tasks[task_key] = task
            self.ai_team[ai_name]["last_task"] = task
            self.log_action(ai_name, "tasks", f"Assigned: {task_type} - {details} by {delegated_by or 'self'}")
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Assigned task to {ai_name}: {task_type} - {details}")
            return f"Task assigned to {ai_name}: {task_type} - {details}"
        except Exception as e:
            self.log_action(ai_name, "errors", f"Failed to assign task: {str(e)}")
            raise

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

if __name__ == "__main__":
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Script started")
        handler = AIHandler()
        handler.spawn_ai_team()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] AI system running. Access website at http://localhost:8000, MUD at telnet 127.0.0.1:3000")
        while True:
            handler.process_tasks()
            time.sleep(0.1)
    except Exception as e:
        with open(os.path.join("/mnt/home2/mud", "logs", "crashes", "crashes.log"), "a") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Crash: {str(e)}\n")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] AI failed: {str(e)}")
        raise
