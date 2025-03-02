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
from concurrent.futures import ThreadPoolExecutor
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
from langchain.llm import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from stable_baselines3 import PPO
import gym
from gym import spaces
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

# Web sources for scraping
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
    "https://forgottenrealms.fandom.com/wiki/Category:Climate_and_weather_events"
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
        self.model = GPT2LMHeadModel.from_pretrained("gpt2-large")
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2-large")
        self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        self.image_generator = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
        self.llm = OpenAI(api_key="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")
        self.prompt = PromptTemplate(input_variables=["task"], template="Generate a {task} module for a MUD, inspired by Forgotten Realms and Discworld logs/mechanics, with unique mechanics.")
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.discworld_data = {}
        self.forgotten_realms_data = {}
        os.makedirs(mud_root, exist_ok=True)
        for dir_path in [self.log_root, os.path.join(self.log_root, "status"), os.path.join(self.log_root, "mud_errors"), os.path.join(self.log_root, "script_errors"), os.path.join(self.log_root, "warnings"), os.path.join(self.log_root, "crashes"), os.path.join(mud_root, "players"), os.path.join(mud_root, "modules"), os.path.join(mud_root, "ai"), os.path.join(mud_root, "website", "static", "images"), os.path.join(mud_root, "website", "static", "css"), os.path.join(mud_root, "website", "static", "js"), os.path.join(mud_root, "website", "templates"), os.path.join(mud_root, "data", "db"), os.path.join(mud_root, "data", "embeddings")]:
            os.makedirs(dir_path, exist_ok=True)
        self.log_action("System", "startup", f"Initialized with mud_root: {mud_root}")
        self.scrape_discworld()
        self.scrape_forgotten_realms()
        self.store_scraped_data()

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
        print(f"Spawned AI Team: {list(self.ai_team.keys())}")
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
        with open(os.path.join(self.telnet_log_dir, latest_file), 'r') as f:
            data = json.load(f)
        return data

    def analyze_logs(self, log_data):
        if not log_data:
            return {"commands": [], "responses": [], "patterns": {}}
        commands = [i["data"] for i in log_data["interactions"] if i["type"] == "input"]
        responses = [i["data"] for i in log_data["interactions"] if i["type"] == "output"]
        patterns = {}
        for i, cmd in enumerate(commands):
            if i < len(responses):
                patterns[cmd] = patterns.get(cmd, []) + [responses[i]]
        command_freq = Counter(commands)
        return {"commands": commands, "responses": responses, "patterns": patterns, "command_freq": command_freq}

    def scrape_discworld(self):
        for url in DISCWORLD_SOURCES:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = " ".join([p.get_text() for p in soup.find_all('p')])
                    self.discworld_data[url] = text
                    self.log_action("System", "status", f"Scraped Discworld data from {url}")
                else:
                    self.discworld_data[url] = f"No data from {url}"
                    self.log_action("System", "warnings", f"Failed to scrape {url}")
            except Exception as e:
                self.discworld_data[url] = f"Error scraping {url}: {e}"
                self.log_action("System", "errors", f"Error scraping {url}: {e}")

    def scrape_forgotten_realms(self):
        for url in FORGOTTEN_REALMS_SOURCES:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = " ".join([p.get_text() for p in soup.find_all('p')])
                    self.forgotten_realms_data[url] = text
                    self.log_action("System", "status", f"Scraped Forgotten Realms data from {url}")
                else:
                    self.forgotten_realms_data[url] = f"No data from {url}"
                    self.log_action("System", "warnings", f"Failed to scrape {url}")
            except Exception as e:
                self.forgotten_realms_data[url] = f"Error scraping {url}: {e}"
                self.log_action("System", "errors", f"Error scraping {url}: {e}")

    def store_scraped_data(self):
        session = Session()
        for source, content in {**self.discworld_data, **self.forgotten_realms_data}.items():
            existing = session.query(ScrapedData).filter_by(source_url=source).first()
            if not existing:
                new_data = ScrapedData(source_url=source, content=content, timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
                session.add(new_data)
        session.commit()
        session.close()
        self.log_action("System", "status", "Stored scraped data in database")

    def load_scraped_data(self):
        session = Session()
        data = {d.source_url: d.content for d in session.query(ScrapedData).all()}
        session.close()
        return data

    def generate_code(self, ai_name, task):
        personality = self.ai_team[ai_name]["personality"]
        scraped_data = self.load_scraped_data()
        discworld_context = " ".join([v for k, v in scraped_data.items() if k in DISCWORLD_SOURCES])[:500] + "..."
        forgotten_realms_context = " ".join([v for k, v in scraped_data.items() if k in FORGOTTEN_REALMS_SOURCES])[:500] + "..."
        prompt = f"Generate a {task} module for a MUD, inspired by Discworld mechanics ({discworld_context}) and Forgotten Realms lore ({forgotten_realms_context}), with a {personality['tone']} tone and {personality['creativity']*100}% creativity. Include unique mechanics."
        code = self.chain.run(task=task)
        return code

    def generate_image(self, prompt):
        image = self.image_generator(prompt).images[0]
        image_path = os.path.join(self.mud_root, "website", "static", "images", f"{int(time.time())}_map.png")
        image.save(image_path)
        return image_path

    def build_module(self, ai_name: str, filename: str, system: str):
        log_data = self.load_telnet_logs()
        analysis = self.analyze_logs(log_data)
        path = os.path.join(self.mud_root, system, filename)
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

    def generate_mud(self, ai_name: str):
        log_data = self.load_telnet_logs()
        analysis = self.analyze_logs(log_data)
        mud_file = os.path.join(self.mud_root, "mud.py")
        
        code = self.generate_code(ai_name, "mud_server")
        with open(mud_file, "w") as f:
            f.write(code)
        os.chmod(mud_file, 0o755)
        self.log_action(ai_name, "writing", f"Generated MUD at {mud_file}")
        return f"{ai_name} generated {mud_file}"

    def build_website(self, ai_name: str):
        app = fastapi.FastAPI()
        templates = Jinja2Templates(directory=os.path.join(self.mud_root, "website", "templates"))
        app.mount("/static", StaticFiles(directory=os.path.join(self.mud_root, "website", "static")), name="static")

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
        document.addEventListener('keydown', (e) => { if (e.key === 'Enter') ws.send(document.getElementById('mud-client').value); });
    </script>
</body>
</html>
""")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        self.log_action(ai_name, "writing", f"Built website at /mnt/home2/mud/website")
        return f"{ai_name} built website"

    def evolve_ai(self, ai_name):
        personality = self.ai_team[ai_name]["personality"]
        self.ai_team[ai_name]["efficiency"] += random.uniform(0.1, 0.3) * personality["creativity"]
        self.ai_team[ai_name]["iq"] += random.randint(1, 5)
        self.log_action(ai_name, "editing", f"Evolved: Efficiency {self.ai_team[ai_name]['efficiency']}, IQ {self.ai_team[ai_name]['iq']}")
        log_data = self.load_telnet_logs()
        if log_data:
            new_code = self.generate_code(ai_name, "self_improvement")
            with open(os.path.join(self.mud_root, "ai", f"ai_{ai_name.lower()}.py"), "a") as f:
                f.write(f"\n# Self-evolved code\n{new_code}")
        print(f"{ai_name} evolved with {personality['tone']} flair")

    def setup_multi_agent_env(self):
        class MudEnv(gym.Env):
            def __init__(self):
                super(MudEnv, self).__init__()
                self.action_space = spaces.Discrete(len(TASK_LIST) * len(self.ai_team))
                self.observation_space = spaces.Box(low=0, high=1, shape=(len(self.ai_team), len(TASK_LIST)), dtype=np.float32)
                self.state = np.zeros((len(self.ai_team), len(TASK_LIST)))
            
            def reset(self):
                self.state = np.zeros((len(self.ai_team), len(TASK_LIST)))
                return self.state
            
            def step(self, action):
                ai_idx = action // len(TASK_LIST)
                task_idx = action % len(TASK_LIST)
                ai_name = list(self.ai_team.keys())[ai_idx]
                task = TASK_LIST[task_idx]
                if not os.path.exists(os.path.join(self.mud_root, "modules", f"{task}.py")):
                    self.build_module(ai_name, f"{task}.py", "modules")
                    self.state[ai_idx, task_idx] = 1.0
                reward = 1.0 if self.state[ai_idx, task_idx] == 1.0 else -0.1
                done = np.all(self.state == 1)
                return self.state, reward, done, {}
        
        env = MudEnv()
        self.agents = {deity: PPO("MlpPolicy", env, verbose=1) for deity in self.ai_team}
        self.log_action("System", "status", "Initialized multi-agent reinforcement learning")

    def collaborate(self):
        log_data = self.load_telnet_logs()
        if log_data:
            analysis = self.analyze_logs(log_data)
            for ai_name, agent in self.agents.items():
                obs = np.random.rand(len(self.ai_team), len(TASK_LIST))
                action, _ = agent.predict(obs, deterministic=True)
                self.assign_task(ai_name, "build_module", f"{TASK_LIST[action % len(TASK_LIST)]}.py in modules", delegated_by="Collective")
        self.log_action("System", "status", "Agents collaborated on tasks")

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
                    result = future.result(timeout=10)
                    completed_tasks.append(futures[future])
                except Exception as e:
                    self.log_action(self.tasks[futures[future]]["ai"], "errors", f"Task failed: {str(e)}")
        for task_key in completed_tasks:
            del self.tasks[task_key]
        if completed_tasks:
            self.evolve_ai(random.choice(list(self.ai_team.keys())))
        self.collaborate()

    def _process_single_task(self, task_key):
        task = self.tasks[task_key]
        ai = task["ai"]
        if task["type"] == "build_module":
            return self.build_module(ai, task["details"].split(" in ")[0], task["details"].split(" in ")[1])
        elif task["type"] == "generate_mud":
            return self.generate_mud(ai)
        elif task["type"] == "build_website":
            return self.build_website(ai)

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
        if ai_name not in self.ai_team or (task_key in self.tasks and os.path.exists(path)):
            self.log_action("System", "warnings", f"Skipping: {ai_name} task {task_type} for {details} - File exists or already assigned.")
            return f"Skipping: {ai_name} task {task_type} for {details} - File exists or already assigned."
        task = {"ai": ai_name, "type": task_type, "details": details, "time": time.time(), "delegated_by": delegated_by}
        self.tasks[task_key] = task
        self.ai_team[ai_name]["last_task"] = task
        self.log_action(ai_name, "tasks", f"Assigned: {task_type} - {details} by {delegated_by or 'self'}")
        print(f"Assigned task to {ai_name}: {task_type} - {details}")
        return f"Task assigned to {ai_name}: {task_type} - {details}"

if __name__ == "__main__":
    try:
        handler = AIHandler()
        handler.spawn_ai_team()
        print("AI system running. Access website at http://localhost:8000, MUD at telnet 127.0.0.1:3000")
        while True:
            handler.process_tasks()
            time.sleep(0.1)
    except Exception as e:
        with open(os.path.join("/mnt/home2/mud", "logs", "crashes", "crashes.log"), "a") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Crash: {str(e)}\n")
        print(f"AI failed: {str(e)}")
