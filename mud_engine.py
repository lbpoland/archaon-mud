#!/usr/bin/env python3
# mud_engine.py - Central driver for the MUD game, inspired by Discworld MUD's lib system
# Status: March 5, 2025 - Updated from mud.py to integrate existing handlers
# Description: Acts as the main game loop and orchestrator, inheriting functionality from
#              individual handler modules (login, network, term, inventory) similar to
#              Discworld's lib/std/ structure. Supports MCCP, MXP, and terminal settings.
# Plans: Expand with room system, combat, rituals, and additional handlers once developed.

import asyncio
import os
import json
import logging
import random
import socket
from typing import Dict, Optional
import aiofiles
import sys  # Added to fix NameError
import threading  # Added to ensure threading is available

# Logging setup
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
from inventory_handler import InventoryHandler
from term_handler import TermHandler
from network_handler import NetworkHandler

# Stubs for missing modules
class Player:
    def __init__(self, name: str):
        self.name = name
        self.stats = {}
        self.skills = {}
        self.xp = 0
        self.hp = 100  # Default HP
        self.max_hp = 100
        self.gp = 0
        self.max_gp = 0
        self.alignment = "True Neutral"
        self.race = "human"
        self.gender = "n"
        self.start_zone = "Market Square"
        self.room = "Market Square"  # String identifier for now
        self.connected = False
        self.socket = None
        self.writer = None
        self.inventory = InventoryHandler(self)  # Only initialized handler
        self.spells = None
        self.skills_handler = None
        self.rituals = None
        self.soul = None
        self.combat = None
        self.quests = None
        self.crafting = None
        self.cooldowns = {}
        self.data_file = f"/mnt/home2/mud/players/{name.lower()}.json"

    async def load(self) -> None:
        try:
            if os.path.exists(self.data_file):
                async with aiofiles.open(self.data_file, "r") as f:
                    data = json.loads(await f.read())
                    self.stats = data.get("stats", {})
                    self.skills = data.get("skills", {})
                    self.xp = data.get("xp", 0)
                    self.hp = data.get("hp", 100)
                    self.max_hp = data.get("max_hp", 100)
                    self.gp = data.get("gp", 0)
                    self.max_gp = data.get("max_gp", 0)
                    self.alignment = data.get("alignment", "True Neutral")
                    self.race = data.get("race", "human")
                    self.gender = data.get("gender", "n")
                    self.start_zone = data.get("start_zone", "Market Square")
                    self.cooldowns = data.get("cooldowns", {})
                logger.debug(f"Loaded player data for {self.name}")
            else:
                logger.warning(f"No data file found for {self.name}, using defaults.")
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
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            async with aiofiles.open(self.data_file, "w") as f:
                await f.write(json.dumps(data, indent=4))
            logger.debug(f"Saved player data for {self.name}")
        except Exception as e:
            logger.error(f"Error saving player data for {self.name}: {str(e)}")
            raise

    async def send(self, message: str) -> None:
        if self.writer:
            self.writer.write(f"{message}\n".encode('utf-8'))
            await self.writer.drain()
            logger.debug(f"Sent to {self.name}: {message}")

class Room:
    def __init__(self, name: str):
        self.name = name
        self.description = f"A default room: {name}"
        self.npcs = []
        self.players = []
        self.exits = {}

class MudEngine:
    def __init__(self):
        """Initialize the MUD engine with core handlers and game state."""
        self.login_handler = LoginHandler()
        self.players: Dict[str, Player] = {}
        self.rooms: Dict[str, Room] = {
            "Market Square": Room("Market Square"),
            "Docks": Room("Docks"),
            "Temple Precinct": Room("Temple Precinct")
        }
        self.rooms["Market Square"].npcs.append(Player("Mean Gnoll", race="gnoll"))
        os.makedirs("/mnt/home2/mud/players/", exist_ok=True)
        os.makedirs("/mnt/home2/mud/logs/", exist_ok=True)
        logger.info("MudEngine initialized with default rooms and player directory.")

    async def start_login_server(self):
        """Start the login server on port 4000 asynchronously."""
        login_server = await asyncio.start_server(
            self.login_handler.handle_login, "0.0.0.0", 4000, limit=100
        )
        logger.info("Login server started on 0.0.0.0:4000")
        async with login_server:
            await login_server.serve_forever()

    async def start_game_server(self):
        """Start the game server on port 3000."""
        # Disable SSL for now due to missing certificate
        self.server = await asyncio.start_server(
            self.handle_client, "0.0.0.0", 3000, limit=100
        )
        logger.info("Game server started on 0.0.0.0:3000")
        async with self.server:
            await self.server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming game server connections on port 3000."""
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
            if len(parts) < 2 or parts[0].lower() != "auth":
                await writer.write("Use: auth <name>\n".encode('utf-8'))
                await writer.drain()
                continue

            name = parts[1]
            if name in self.players and self.players[name].connected:
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
                logger.error(f"Failed to load player {name}: {str(e)}")
                await writer.drain()

    async def handle_player(self, player: Player, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle the game loop for an authenticated player."""
        term = TermHandler()
        network = NetworkHandler()
        await network.negotiate_telnet(reader, writer)  # Handle MXP/MCCP
        await player.send(f"{COLORS['success']}Welcome, {player.name}! You awaken in {player.room}{COLORS['reset']}")
        player.room = "Market Square"  # Set default room
        self.rooms[player.room].players.append(player)

        while player.connected:
            data = await reader.read(1024)
            if not data:
                break
            command = data.decode('utf-8').strip().lower()
            logger.debug(f"Player {player.name} sent: {command}")
            response = await self.process_command(player, command)
            await player.send(term.format_output(response))

            if command.lower() == "quit":
                player.connected = False
                await player.save()
                del self.players[player.name]
                await player.send(f"{COLORS['info']}Farewell from Archaon MUD.{COLORS['reset']}")
                self.rooms[player.room].players.remove(player)
                writer.close()
                await writer.wait_closed()
                logger.info(f"Player {player.name} disconnected")
                break

    async def process_command(self, player: Player, command: str) -> str:
        """Process player commands using available handlers."""
        term = TermHandler()
        inventory = player.inventory

        parts = command.split()
        if not parts:
            return f"{COLORS['error']}Speak, mortal!{COLORS['reset']}"

        action = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if action == "look":
            return f"{COLORS['info']}You are in {player.room}. {self.rooms[player.room].description}{COLORS['reset']}"
        elif action == "inventory":
            return inventory.inventory()
        elif action == "wear":
            item = " ".join(args) if args else None
            if not item:
                return f"{COLORS['error']}What do you wish to wear?{COLORS['reset']}"
            return inventory.wear(item)
        elif action == "wield":
            item = " ".join(args) if args else None
            if not item:
                return f"{COLORS['error']}What do you wish to wield?{COLORS['reset']}"
            return inventory.wield(item)
        elif action == "drop":
            item = " ".join(args) if args else None
            if not item:
                return f"{COLORS['error']}What do you wish to drop?{COLORS['reset']}"
            return inventory.remove_item(item)
        else:
            return f"{COLORS['error']}Unknown command: {action}{COLORS['reset']}"

    async def start(self):
        """Start both login and game servers."""
        login_task = asyncio.create_task(self.start_login_server())
        game_task = asyncio.create_task(self.start_game_server())
        try:
            await asyncio.gather(login_task, game_task)
        except KeyboardInterrupt:
            logger.info("MudEngine shutdown initiated by user.")
            print("Shutting down MudEngine...")
        except Exception as e:
            logger.error(f"MudEngine crashed: {str(e)}")
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    engine = MudEngine()
    asyncio.run(engine.start())
