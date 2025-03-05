#!/usr/bin/env python3
# mud_engine.py - Driver for Archaon MUD, inspired by Discworld MUD's structure
# Status: March 5, 2025 - Simplified to act as a bootstrap driver, delegates all handling
# Description: Boots up the MUD servers and integrates modules for login, game logic, etc.
#              Delegates all specific handling (login, rooms, NPCs, commands) to modules.
#              Mirrors Discworld's design with MCCP, MXP, and terminal support.
# Plans: Integrate and expand modules (login_handler.py, room.py, etc.) one by one.

import asyncio
import os
import logging
import sys

# Logging setup
logging.basicConfig(filename='/mnt/home2/mud/logs/server.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
mud_error_handler = logging.FileHandler('/mnt/home2/mud/logs/mud_errors.log')
mud_error_handler.setLevel(logging.ERROR)
mud_error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger('MudServer')
logger.handlers = [mud_error_handler]

# Import modules from correct paths (to be populated as modules are developed)
sys.path.append("/mnt/home2/mud/std")
sys.path.append("/mnt/home2/mud/modules")

class MudEngine:
    def __init__(self):
        """Initialize the MUD engine as a driver, setting up basic directories."""
        os.makedirs("/mnt/home2/mud/players/", exist_ok=True)
        os.makedirs("/mnt/home2/mud/logs/", exist_ok=True)
        logger.info("MudEngine initialized as driver with player and log directories.")

    def create_login_server(self):
        """Create and return the login server, delegating to login_handler.py."""
        from modules.login_handler import LoginHandler
        return asyncio.start_server(LoginHandler().handle_login, "0.0.0.0", 4000, limit=100)

    def create_game_server(self):
        """Create and return the game server (to be implemented in future modules)."""
        # Placeholder for game server, to be replaced with a protocol or handler
        async def placeholder_handler(reader, writer):
            logger.info("Game server placeholder active - awaiting module implementation")
            writer.write("Game server not yet implemented. Connect to port 4000 for login.\n".encode('utf-8'))
            await writer.drain()
        return asyncio.start_server(placeholder_handler, "0.0.0.0", 3000, limit=100)

    async def start(self):
        """Start both login and game servers."""
        login_server = await self.create_login_server()
        game_server = await self.create_game_server()

        logger.info("Login server started on 0.0.0.0:4000")
        logger.info("Game server started on 0.0.0.0:3000 (placeholder)")

        async with login_server, game_server:
            await asyncio.gather(login_server.serve_forever(), game_server.serve_forever())

    async def start_servers(self):
        """Wrapper to start servers with proper context."""
        try:
            await self.start()
        except KeyboardInterrupt:
            logger.info("MudEngine shutdown initiated by user.")
            print("Shutting down MudEngine...")
        except Exception as e:
            logger.error(f"MudEngine crashed: {str(e)}")
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    engine = MudEngine()
    asyncio.run(engine.start_servers())
