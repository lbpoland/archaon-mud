# mud.py
import asyncio
from modules.skills_handler import Player
from modules.term_handler import TermHandler
from modules.network_handler import NetworkHandler
from modules.combat_handler import CombatHandler
from modules.ritual_handler import RitualHandler
from modules.inventory_handler import InventoryHandler
from modules.soul_handler import SoulHandler
from modules.login_handler import LoginHandler  # Moved last to avoid partial init

class Room:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.npcs = [CombatHandler(Player("Goblin"))]
        self.exits = {"north": "waterdeep/tavern"}

rooms = {
    "waterdeep/market": Room("Market Square", "A bustling plaza in Waterdeep thrums with life.")
}

async def handle_client(reader, writer):
    term = TermHandler()  # Init first, no dependency
    network = NetworkHandler(None)  # No login dependency yet
    login_handler = LoginHandler()  # Now safe to init
    login_handler.term_handler = term
    login_handler.network_handler = network
    
    player = await login_handler.handle_login(reader, writer)
    if not player:
        writer.close()
        return
    
    combat = CombatHandler(player)
    ritual = RitualHandler(player)
    inventory = InventoryHandler(player)
    soul = SoulHandler(player)
    
    players[writer] = {
        "player": player, "room": rooms["waterdeep/market"], "term": term, "network": network,
        "combat": combat, "ritual": ritual, "inventory": inventory, "soul": soul
    }
    
    writer.write(term.format_output(f"{COLORS['info']}Welcome to Faerûn, {player.name}! Type 'help' for commands.{COLORS['reset']}").encode())
    await writer.drain()
    
    while True:
        try:
            data = await reader.read(100)
            if not data:
                break
            cmd = data.decode().strip().split()
            if not cmd:
                continue
            action, args = cmd[0].lower(), " ".join(cmd[1:])
            room = players[writer]["room"]

            if action == "help":
                output = term.format_output(
                    f"{COLORS['title']}Commands:{COLORS['reset']}\n"
                    f"  say <msg> - Speak to the room\n"
                    f"  shout <msg> - Yell across Faerûn\n"
                    f"  whisper <target> <msg> - Whisper to someone\n"
                    f"  <emote> [target] - Use a soul gesture (e.g., smile, nod)\n"
                    f"  souls - List all gestures\n"
                    f"  score - View your status\n"
                    f"  kill <target> - Attack an NPC\n"
                    f"  inventory - Check your gear\n"
                    f"  wield <item> - Wield a weapon\n"
                    f"  wear <item> - Wear armor\n"
                    f"  quit - Leave Faerûn"
                )
            elif action == "say":
                result = soul.perform("say", args, None, room, players)
                output = result["self"]
                await broadcast(result["room"], writer, players, room)
            elif action == "shout":
                result = soul.perform("shout", args, None, room, players)
                output = result["self"]
                await broadcast(result["room"], writer, players, room)
                await broadcast_global(result["global"], writer, players)
            elif action == "whisper":
                try:
                    target_name, whisper_msg = args.split(" ", 1)
                    result = soul.perform("whisper", whisper_msg, target_name, room, players)
                    output = result["self"]
                    await broadcast(result["room"], writer, players, room)
                    if result["target"]:
                        await send_to_target(result["target"]["msg"], result["target"]["player"], players)
                except ValueError:
                    output = term.format_output(f"{COLORS['error']}Whisper whom what?{COLORS['reset']}")
            elif action == "souls":
                output = soul.show_actions()
            elif action == "score":
                output = term.format_output(player.score())
            elif action == "kill":
                output = term.format_output(combat.kill(args, room))
            elif action == "inventory":
                output = term.format_output(inventory.inventory())
            elif action == "wield":
                output = term.format_output(inventory.wield(args))
            elif action == "wear":
                output = term.format_output(inventory.wear(args))
            elif action == "quit":
                output = term.format_output(f"{COLORS['info']}Farewell, {player.name}, traveler of Faerûn!{COLORS['reset']}")
                writer.write(output.encode())
                await writer.drain()
                break
            else:
                target_name = args if args else None
                result = soul.perform(action, None, target_name, room, players)
                if "self" in result:
                    output = result["self"]
                    await broadcast(result["room"], writer, players, room)
                    if result.get("target"):
                        await send_to_target(result["target"]["msg"], result["target"]["player"], players)
                    elif result.get("global"):
                        await broadcast_global(result["global"], writer, players)
                else:
                    output = result

            writer.write(output.encode())
            await writer.drain()
        except Exception as e:
            writer.write(term.format_output(f"{COLORS['error']}Error: {str(e)}{COLORS['reset']}").encode())
            await writer.drain()
    
    del players[writer]
    writer.close()

# ... (broadcast functions unchanged)

players = {}
async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 3000)
    print("Server running on 127.0.0.1:3000")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
