#!/usr/bin/env python3
# mud_engine.py - Central driver for Archaon MUD, inspired by Discworld MUD's structure
# Status: March 5, 2025 - Fully updated to serve as the main server in /mnt/home2/mud/
# Description: Acts as the main game loop and orchestrator, managing login and game servers.
#              Mirrors Discworld's design with MCCP, MXP, and terminal support.
#              Starting locations handled by login_handler.py; NPCs via future npc_handler.py.
# Plans: Integrate room.py, npc_handler.py, and expand with full Discworld replication.

import asyncio
import os
import json
import logging
import socket
from typing import Dict, Optional
import aiofiles
import sys

# Logging setup
logging.basicConfig(filename='/mnt/home2/mud/logs/server.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
mud_error_handler = logging.FileHandler('/mnt/home2/mud/logs/mud_errors.log')
mud_error_handler.setLevel(logging.ERROR)
mud_error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger('MudServer')
logger.handlers = [mud_error_handler]

# Import modules from correct paths
sys.path.append("/mnt/home2/mud/std")
sys.path.append("/mnt/home2/mud/modules")
from login_handler import LoginHandler
from term_handler import TermHandler
from network_handler import NetworkHandler
from std.room import Room  # Import Room class from std/
from modules.skills_handler import Player  # Import Player class

class MudEngine:
    def __init__(self):
        """Initialize the MUD engine with core handlers and game state."""
        self.login_handler = LoginHandler()
        self.players: Dict[str, Player] = {}  # Map of player names to Player objects
        self.rooms: Dict[str, Room] = {
            "Market Square": Room("Market Square"),
            "Docks": Room("Docks"),
            "Temple Precinct": Room("Temple Precinct")
        }
        os.makedirs("/mnt/home2/mud/players/", exist_ok=True)
        os.makedirs("/mnt/home2/mud/logs/", exist_ok=True)
        logger.info("MudEngine initialized with default rooms and player directory.")

    async def start_login_server(self):
        """Start the login server on port 4000 asynchronously."""
        login_server = await asyncio.start_server(
            self.handle_login_connection, "0.0.0.0", 4000, limit=100
        )
        logger.info("Login server started on 0.0.0.0:4000")
        async with login_server:
            await login_server.serve_forever()

    async def start_game_server(self):
        """Start the game server on port 3000."""
        self.server = await asyncio.start_server(
            self.handle_game_connection, "0.0.0.0", 3000, limit=100
        )
        logger.info("Game server started on 0.0.0.0:3000")
        async with self.server:
            await self.server.serve_forever()

    async def handle_login_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming login connections on port 4000."""
        player = await self.login_handler.handle_login(reader, writer)
        if player:
            player.connected = True
            player.writer = writer
            self.players[player.name] = player
            logger.info(f"Player {player.name} logged in via port 4000")
            await writer.write(f"{player.name}, please reconnect to port 3000 to enter Faerûn.\n".encode('utf-8'))
            await writer.drain()

    async def handle_game_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming game server connections on port 3000."""
        addr = writer.get_extra_info('peername')
        logger.info(f"New game connection from {addr}")
        await writer.write("Connecting to Archaon MUD - Authenticate with: auth <name>\n".encode('utf-8'))
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

            player = self.players.get(name)  # Retrieve from login if exists
            if not player:
                player = Player(name)
                try:
                    await player.load()
                    player.connected = True
                    player.writer = writer
                    self.players[name] = player
                except Exception as e:
                    await writer.write(f"Login failed: {str(e)}\n".encode('utf-8'))
                    logger.error(f"Failed to load player {name}: {str(e)}")
                    await writer.drain()
                    continue

            await self.handle_player_session(player, reader, writer)

    async def handle_player_session(self, player: Player, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle the game loop for an authenticated player."""
        term = TermHandler()
        network = NetworkHandler()
        await network.negotiate_telnet(reader, writer)  # Handle MXP/MCCP
        # Set player room based on login_handler.py's start_zone
        player.room = player.start_zone if hasattr(player, 'start_zone') else "Market Square"
        self.rooms[player.room].add_player(player)
        await player.send(f"{COLORS['success']}Welcome, {player.name}! You awaken in {player.room}.{COLORS['reset']}")

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
                self.rooms[player.room].remove_player(player)
                writer.close()
                await writer.wait_closed()
                logger.info(f"Player {player.name} disconnected")
                break

    async def process_command(self, player: Player, command: str) -> str:
        """Process player commands using available handlers."""
        term = TermHandler()
        # Assuming inventory is part of Player (to be integrated with inventory_handler.py)
        inventory = getattr(player, 'inventory', None)

        parts = command.split()
        if not parts:
            return f"{COLORS['error']}Speak, mortal!{COLORS['reset']}"

        action = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if action == "look":
            room = self.rooms.get(player.room, Room(player.room))
            return f"{COLORS['info']}You are in {player.room}. {room.description}{COLORS['reset']}"
        elif action == "inventory" and inventory:
            return inventory.inventory()
        elif action == "wear" and inventory and args:
            item = " ".join(args)
            return inventory.wear(item) if hasattr(inventory, 'wear') else f"{COLORS['error']}Inventory not available.{COLORS['reset']}"
        elif action == "wield" and inventory and args:
            item = " ".join(args)
            return inventory.wield(item) if hasattr(inventory, 'wield') else f"{COLORS['error']}Inventory not available.{COLORS['reset']}"
        elif action == "drop" and inventory and args:
            item = " ".join(args)
            return inventory.remove_item(item) if hasattr(inventory, 'remove_item') else f"{COLORS['error']}Inventory not available.{COLORS['reset']}"
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
