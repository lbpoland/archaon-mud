import sys
import os
import asyncio
import json
import logging
import random
import socket
import ssl
from datetime import datetime
from typing import Dict, List, Optional
import aiofiles

# Dependencies: pip install aiofiles (already installed)
logging.basicConfig(filename='/mnt/home2/mud/logs/server.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
mud_error_handler = logging.FileHandler('/mnt/home2/mud/logs/mud_errors.log')
mud_error_handler.setLevel(logging.ERROR)
mud_error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger('MudServer')
logger.handlers = [mud_error_handler]

# Import existing modules
sys.path.append("/mnt/home2/mud/modules")
from login_handler import LoginHandler
#from spell_handler import SpellHandler
#from combat_handler import CombatHandler
#from skills_handler import SkillHandler
#from ritual_handler import RitualHandler
from inventory_handler import InventoryHandler
#from soul_handler import SoulHandler
from term_handler import TermHandler
from network_handler import NetworkHandler
#from quests_handler import QuestHandler
#from crafting_handler import CraftingHandler
#from weapons import Weapons
#from armors import Armors
#from clothing import Clothing
#from classes import Classes
#from races import Races
#from organizations import Organizations

sys.path.append("/mnt/home2/mud/std")
#from object import Object
#from living import Living
#from room import Room
#from wearable import Wearable
#from container import Container
#from command import Command

# Server configuration
HOST = "0.0.0.0"
PORT = 3000  # Main game server, login_handler.py uses 4000
MAX_CONNECTIONS = 100
START_ROOM = "/mnt/home2/mud/domains/sword_coast/waterdeep/rooms.py"

# Player class aligned with login_handler.py
class Player:
    def __init__(self, name: str):
        self.name = name
        self.stats = {}
        self.skills = {}
        self.xp = 0
        self.hp = 0
        self.max_hp = 0
        self.gp = 0
        self.max_gp = 0
        self.alignment = ""
        self.race = ""
        self.gender = "n"
        self.start_zone = ""
        self.room = None
        self.connected = False
        self.socket = None
        self.writer = None
        self.inventory = InventoryHandler()
        self.spells = SpellHandler()
        self.skills_handler = SkillHandler()
        self.rituals = RitualHandler()
        self.soul = SoulHandler()
        self.combat = CombatHandler()
        self.quests = QuestHandler()
        self.crafting = CraftingHandler()
        self.cooldowns = {}
        self.data_file = f"/mnt/home2/mud/players/{name.lower()}.json"

    async def load(self) -> None:
        try:
            async with aiofiles.open(self.data_file, "r") as f:
                data = json.loads(await f.read())
                self.stats = data["stats"]
                self.skills = data["skills"]
                self.xp = data["xp"]
                self.hp = data["hp"]
                self.max_hp = data["max_hp"]
                self.gp = data["gp"]
                self.max_gp = data["max_gp"]
                self.alignment = data["alignment"]
                self.race = data["race"]
                self.gender = data["gender"]
                self.start_zone = data["start_zone"]
                self.room = Room(START_ROOM)
                self.cooldowns = data.get("cooldowns", {})
                logger.debug(f"Loaded player data for {self.name}")
        except FileNotFoundError:
            logger.error(f"Player data file {self.data_file} not found")
            raise
        except Exception as e:
            logger.error(f"Error loading player data for {self.name}: {str(e)}")
            raise

    async def save(self) -> None:
        data = {
            "name": self.name,
            "stats": self.stats,
            "skills": self.skills,
            "xp": self.xp,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "gp": self.gp,
            "max_gp": self.max_gp,
            "alignment": self.alignment,
            "race": self.race,
            "gender": self.gender,
            "start_zone": self.start_zone,
            "cooldowns": self.cooldowns
        }
        async with aiofiles.open(self.data_file, "w") as f:
            await f.write(json.dumps(data, indent=4))
        logger.debug(f"Saved player data for {self.name}")

    async def send(self, message: str) -> None:
        if self.writer:
            self.writer.write(f"{message}\n".encode('utf-8'))
            await self.writer.drain()
            logger.debug(f"Sent to {self.name}: {message}")

class MudServer:
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.rooms: Dict[str, Room] = {}
        self.login_server = LoginHandler()
        self.server = None

    async def start(self) -> None:
        # Start login server on port 4000 in a separate thread
        login_loop = asyncio.new_event_loop()
        Thread(target=lambda: asyncio.set_event_loop(login_loop) or login_loop.run_until_complete(self.login_server.main()), daemon=True).start()
        logger.info("Login server started on port 4000")

        # Start game server on port 3000
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.server = await asyncio.start_server(
            self.handle_client, HOST, PORT, ssl=context, limit=MAX_CONNECTIONS
        )
        logger.info(f"Game server started on {HOST}:{PORT}")
        async with self.server:
            await self.server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info('peername')
        logger.info(f"New connection from {addr}")
        await writer.write("Connecting to Archaon MUD - Please login at port 4000 first, then reconnect here.\n".encode('utf-8'))
        await writer.drain()

        while True:
            data = await reader.read(1024)
            if not data:
                break
            command = data.decode('utf-8').strip()
            logger.debug(f"Received from {addr}: {command}")

            parts = command.split()
            if len(parts) < 2 or parts[0] != "auth":
                await writer.write("Use: auth <name>\n".encode('utf-8'))
                await writer.drain()
                continue

            name = parts[1]
            if name in self.players:
                await writer.write("Player already logged in.\n".encode('utf-8'))
                await writer.drain()
                continue

            player_file = f"/mnt/home2/mud/players/{name.lower()}.json"
            if not os.path.exists(player_file):
                await writer.write("No such player exists. Please create a character on port 4000.\n".encode('utf-8'))
                await writer.drain()
                continue

            player = Player(name)
            try:
                await player.load()
                player.connected = True
                player.writer = writer
                self.players[name] = player
                await self.handle_player(player, reader, writer)
            except Exception as e:
                await writer.write(f"Login failed: {str(e)}\n".encode('utf-8'))
                await writer.drain()
                logger.error(f"Failed to load player {name}: {str(e)}")

    async def handle_player(self, player: Player, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        await player.send(f"Welcome, {player.name}! You awaken in {player.room.path}")
        while player.connected:
            data = await reader.read(1024)
            if not data:
                break
            command = data.decode('utf-8').strip()
            logger.debug(f"Player {player.name} sent: {command}")
            if command.lower() == "quit":
                player.connected = False
                await player.save()
                del self.players[player.name]
                await writer.write("Farewell from Archaon MUD.\n".encode('utf-8'))
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                logger.info(f"Player {player.name} disconnected")
                break
            else:
                await player.send(f"Echo: {command} (commands coming soon!)")

async def main():
    server = MudServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
