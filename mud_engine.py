#!/usr/bin/env python3
# mud_engine.py - Central driver for the MUD game, inspired by Discworld MUD's lib system
# Status: March 5, 2025 - Initial standalone driver integrating existing modules
# Description: Acts as the main game loop and orchestrator, inheriting functionality from
#              individual handler modules (e.g., login, network, term, inventory) similar
#              to Discworld's lib/std/ structure. Supports MCCP, MXP, and terminal settings.
# Plans: Expand with room system, NPC AI, and additional handlers (combat, ritual, etc.)

import asyncio
import os
import json
import logging
from typing import Dict, Optional
from modules.login_handler import LoginHandler
from modules.network_handler import NetworkHandler
from modules.term_handler import TermHandler
from modules.inventory_handler import InventoryHandler
from modules.skills_handler import Player
from modules.combat_handler import CombatHandler  # Placeholder stub
from modules.deities import DEITIES  # Placeholder stub
from modules.soul_handler import SoulHandler  # Placeholder stub
from modules.ritual_handler import RitualHandler  # Placeholder stub

# Set up logging
logging.basicConfig(filename="/mnt/home2/mud/mud_engine.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.npcs = []
        self.players = []
        self.exits = {}

class MudEngine:
    def __init__(self):
        """Initialize the MUD engine with core handlers and game state."""
        self.login_handler = LoginHandler()
        self.players: Dict[str, dict] = {}  # {player_name: {"player": Player, "writer": StreamWriter, ...}}
        self.rooms = {
            "Market Square": Room("Market Square", "A bustling trade hub in Waterdeep."),
            "Docks": Room("Docks", "A gritty port with salty air."),
            "Temple Precinct": Room("Temple Precinct", "A sacred ground bathed in divine light.")
        }
        self.rooms["Market Square"].npcs.append(Player("Mean Gnoll", race="gnoll"))
        # Ensure player directory exists
        os.makedirs("/mnt/home2/mud/players/", exist_ok=True)
        logging.info("MudEngine initialized with default rooms and player directory.")

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle individual client connections, managing login and game loop."""
        logging.info("New client connection established.")
        try:
            player = await self.login_handler.handle_login(reader, writer)
            if player:
                # Initialize additional handlers for the player
                inventory = InventoryHandler(player)
                inventory.init_inventory()  # Set up starting items based on race
                combat = CombatHandler(player)  # Placeholder
                network = NetworkHandler(self.login_handler)
                term = TermHandler(self.login_handler)
                soul = SoulHandler(player)  # Placeholder
                ritual = RitualHandler(player)  # Placeholder

                # Store player data
                self.players[player.name] = {
                    "player": player,
                    "writer": writer,
                    "inventory": inventory,
                    "combat": combat,
                    "network": network,
                    "term": term,
                    "soul": soul,
                    "ritual": ritual
                }
                player.domain = "Market Square"  # Default starting room
                self.rooms[player.domain].players.append(player)

                # Negotiate telnet options (MXP/MCCP)
                await network.negotiate_telnet(reader, writer)
                welcome_msg = f"{COLORS['success']}Welcome, {player.name}, to Faerûn’s Shattered Legacy!{COLORS['reset']}"
                writer.write(term.format_output(welcome_msg).encode())
                await writer.drain()

                # Enter game loop
                await self.game_loop(player, reader, writer)
            else:
                writer.write(term.format_output(f"{COLORS['error']}Login failed. Disconnecting.{COLORS['reset']}").encode())
                await writer.drain()
        except Exception as e:
            error_msg = f"{COLORS['error']}Connection error: {str(e)}. Disconnecting.{COLORS['reset']}"
            writer.write(term.format_output(error_msg).encode())
            logging.error(f"Client error: {str(e)}")
            await writer.drain()
        finally:
            self.cleanup_player(player)
            writer.close()
            logging.info(f"Client {player.name if player else 'unknown'} disconnected.")

    async def game_loop(self, player: Player, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Main game loop for a connected player."""
        handlers = self.players[player.name]
        term = handlers["term"]
        network = handlers["network"]
        inventory = handlers["inventory"]
        combat = handlers["combat"]
        soul = handlers["soul"]
        ritual = handlers["ritual"]
        current_room = self.rooms[player.domain]

        while True:
            try:
                writer.write(term.prompt.encode())
                await writer.drain()
                data = await reader.read(100)
                if not data:
                    break
                command = data.decode().strip().lower()
                logging.info(f"Player {player.name} issued command: {command}")
                response = await self.process_command(player, command, current_room, handlers)
                writer.write(term.format_output(response).encode())
                await writer.drain()
            except Exception as e:
                error_msg = f"{COLORS['error']}Command error: {str(e)}. Try again.{COLORS['reset']}"
                writer.write(term.format_output(error_msg).encode())
                logging.error(f"Command error for {player.name}: {str(e)}")
                await writer.drain()

    async def process_command(self, player: Player, command: str, room: Room, handlers: dict) -> str:
        """Process player commands and route to appropriate handlers."""
        term = handlers["term"]
        inventory = handlers["inventory"]
        combat = handlers["combat"]
        soul = handlers["soul"]
        ritual = handlers["ritual"]

        parts = command.split()
        if not parts:
            return f"{COLORS['error']}Speak, mortal!{COLORS['reset']}"

        action = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if action == "look":
            return f"{COLORS['info']}{room.name}: {room.description}\nExits: {', '.join(room.exits.keys())}\nNPCs: {', '.join(n.name for n in room.npcs)}{COLORS['reset']}"
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
        elif action == "kill":
            target = " ".join(args) if args else None
            if not target:
                return f"{COLORS['error']}Whom do you strike?{COLORS['reset']}"
            return combat.kill(target, room)
        elif action == "say":
            msg = " ".join(args) if args else None
            if not msg:
                return f"{COLORS['error']}What do you wish to say?{COLORS['reset']}"
            result = soul.perform("say", msg, None, room, self.players)
            return self.broadcast(player, result, term)
        elif action == "perform":
            ritual_name = args[0] if args else None
            target = args[1] if len(args) > 1 else None
            if not ritual_name:
                return f"{COLORS['error']}What ritual do you wish to perform?{COLORS['reset']}"
            return ritual.perform(ritual_name, target, room)
        elif action == "score":
            return player.score() if hasattr(player, "score") else f"{COLORS['info']}No score data available yet.{COLORS['reset']}"
        elif action == "quit":
            return f"{COLORS['info']}Goodbye, {player.name}.{COLORS['reset']}"
        else:
            return f"{COLORS['error']}Unknown command: {action}{COLORS['reset']}"

    def broadcast(self, player: Player, messages: dict, term: TermHandler) -> str:
        """Broadcast messages to all players in the same room."""
        room = self.rooms[player.domain]
        for p_data in self.players.values():
            if p_data["player"] in room.players and p_data["player"] != player:
                p_data["writer"].write(term.format_output(messages["room"]).encode())
                asyncio.ensure_future(p_data["writer"].drain())
        return messages["self"]

    def cleanup_player(self, player: Optional[Player]):
        """Remove player from game state and room."""
        if player and player.name in self.players:
            room = self.rooms.get(player.domain)
            if room and player in room.players:
                room.players.remove(player)
            del self.players[player.name]
            logging.info(f"Player {player.name} cleaned up from game state.")

async def main():
    """Start the MUD server."""
    engine = MudEngine()
    try:
        server = await asyncio.start_server(engine.handle_client, "127.0.0.1", 4000)
        logging.info("MUD Engine started on 127.0.0.1:4000")
        print("MUD Engine running on 127.0.0.1:4000. Press Ctrl+C to stop.")
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        logging.info("MUD Engine shutdown initiated by user.")
        print("Shutting down MUD Engine...")
    except Exception as e:
        logging.error(f"MUD Engine crashed: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
