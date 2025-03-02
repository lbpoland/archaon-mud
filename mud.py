# mud.py - Main MUD server
# Status (March 3, 2025):
# - Ties login_handler.py, term_handler.py, network_handler.py together for startup
# - Features: Telnet server, basic command loop
# - Done: Initial server setup
# - Plans: Expand with full command handling after other handlers are complete

import asyncio
from modules.login_handler import LoginHandler
from modules.term_handler import TermHandler
from modules.network_handler import NetworkHandler

async def handle_client(reader, writer):
    handler = LoginHandler()
    term = TermHandler(handler)
    network = NetworkHandler(handler)
    handler.term_handler = term
    handler.network_handler = network
    
    player = await handler.handle_login(reader, writer)
    if not player:
        writer.close()
        return
    
    players[writer] = {"player": player, "room": "waterdeep/market", "term": term, "network": network}
    
    writer.write(term.format_output(f"{COLORS['info']}You’re in Faerûn—type 'score' or 'quit' to begin.{COLORS['reset']}").encode())
    await writer.drain()
    
    while True:
        try:
            cmd = (await reader.read(100)).decode().strip().split()
            if not cmd:
                continue
            action, args = cmd[0].lower(), " ".join(cmd[1:])
            room = players[writer]["room"]

            if action == "score":
                output = term.format_output(player.score())
            elif action == "quit":
                output = term.format_output(f"{COLORS['info']}Farewell, traveler of Faerûn!{COLORS['reset']}")
                writer.write(output.encode())
                await writer.drain()
                break
            else:
                output = term.format_output(f"{COLORS['error']}Unknown command. Try 'score' or 'quit'.{COLORS['reset']}")
            writer.write(output.encode())
            await writer.drain()
        except Exception as e:
            writer.write(term.format_output(f"{COLORS['error']}Error: {str(e)}{COLORS['reset']}").encode())
            await writer.drain()

players = {}
async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 3000)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
