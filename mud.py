# mud.py - Main MUD server
import asyncio
from modules.login import handle_login
#from modules.spell_handler import cast
#from modules.combat import kill, consider, stop

async def handle_client(reader, writer):
    player = await handle_login(reader, writer)
    if not player:
        writer.close()
        return
    players[writer] = {"player": player, "room": rooms["waterdeep/market"]}
    
    while True:
        try:
            cmd = (await reader.read(100)).decode().strip().split()
            if not cmd:
                continue
            action, args = cmd[0].lower(), " ".join(cmd[1:])
            room = players[writer]["room"]

            if action == "cast":
                spell, target = args.split(" on ") if " on " in args else (args, None)
                writer.write(f"{cast(player, spell, target, room)}\n".encode())
            elif action == "kill":
                writer.write(f"{kill(player, args, room)}\n".encode())
            elif action == "consider":
                writer.write(f"{consider(player, args, room)}\n".encode())
            elif action == "stop":
                writer.write(f"{stop(player)}\n".encode())
            elif action == "quit":
                writer.write("Farewell, traveler of Faerûn!\n".encode())
                break
            else:
                writer.write("Unknown command. Try 'cast', 'kill', 'consider', 'stop', or 'quit'.\n".encode())
            await writer.drain()
        except Exception as e:
            writer.write(f"Error: {str(e)}\n".encode())
            await writer.drain()

players = {}
rooms = {}  # Populated by domains later
async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 3000)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
