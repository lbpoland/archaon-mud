# mud_engine.py - Main Driver for Archaon MUD
# Updated: March 5, 2025, 06:30 PM AEST
# Status: Integrated with inventory_handler.py, utils.py

import asyncio
from typing import Dict, Optional
from modules.login_handler import LoginHandler
from modules.combat_handler import CombatHandler
from modules.inventory_handler import InventoryHandler
from modules.skills_handler import SkillHandler
from modules.spell_handler import SpellHandler
from modules.ritual_handler import RitualHandler
from modules.soul_handler import SoulHandler
from modules.term_handler import TermHandler
from modules.network_handler import NetworkHandler
from modules.quests_handler import QuestHandler
from modules.crafting_handler import CraftingHandler
from modules.deities import Deity
from modules.utils import COLORS
from std.room import Room
from std.command import Command
from std.living import Living
from domains.world_map import WorldMap
import ssl
import aiofiles
import json

class Player(Living):
    def __init__(self, name: str):
        super().__init__(name)
        self.login = LoginHandler()
        self.combat = CombatHandler(self)
        self.inventory = InventoryHandler(self)
        self.skills = SkillHandler(self)
        self.spells = SpellHandler(self)
        self.rituals = RitualHandler(self)
        self.soul = SoulHandler(self)
        self.term = TermHandler(self)
        self.network = NetworkHandler(self.login)
        self.quests = QuestHandler(self)
        self.crafting = CraftingHandler(self)
        self.deity = Deity.random_deity()
        self.room = None
        self.x, self.y, self.z = 0, 0, 0
        self.ac = 10  # Base AC from D&D 5e
        self.burden = 0.0  # Percentage of max weight
        self.data_file = f"/mnt/home2/mud/players/{name.lower()}.json"

    async def load(self) -> None:
        try:
            async with aiofiles.open(self.data_file, "r") as f:
                data = json.loads(await f.read())
                self.hp = data["hp"]
                self.max_hp = data["max_hp"]
                self.mana = data.get("mana", 0)
                self.gp = data["gp"]
                self.x, self.y, self.z = data["x"], data["y"], data["z"]
                self.ac = data.get("ac", 10)
                self.burden = data.get("burden", 0.0)
                self.room = Room(f"/mnt/home2/mud/domains/{self.world_map.get_region(self.x, self.y, self.z)}/rooms.py")
                self.inventory = InventoryHandler(self)  # Reinitialize inventory
        except FileNotFoundError:
            self.room = Room("/mnt/home2/mud/domains/sword_coast/waterdeep/rooms.py")
            await self.save()
        except Exception as e:
            print(f"Load error for {self.name}: {e}")

    async def save(self) -> None:
        data = {
            "name": self.name, "hp": self.hp, "max_hp": self.max_hp,
            "mana": getattr(self, "mana", 0), "gp": self.gp,
            "x": self.x, "y": self.y, "z": self.z, "ac": self.ac,
            "burden": self.burden
        }
        async with aiofiles.open(self.data_file, "w") as f:
            await f.write(json.dumps(data, indent=4))

    async def move(self, direction: str):
        new_x, new_y, new_z = self.world_map.move(self.x, self.y, self.z, direction)
        if new_x is not None:
            self.x, self.y, self.z = new_x, new_y, new_z
            self.room = Room(f"/mnt/home2/mud/domains/{self.world_map.get_region(self.x, self.y, self.z)}/rooms.py")
            await self.term.send(f"You move to {self.room.name}")

    def bonus(self, skill_name):
        return self.skills.get_skill_level(skill_name) or 0

class MudEngine:
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.world_map = WorldMap()
        self.login_handler = LoginHandler()
        self.network = NetworkHandler(self.login_handler)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info('peername')
        print(f"New connection from {addr}")
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        player = await self.login_handler.handle_login(reader, writer)
        if player:
            await player.network.connect(reader, writer)
            await player.network.set_mxp(True, writer)
            self.players[player.name] = player
            await player.load()
            await player.term.send(f"Welcome to Archaon MUD, {player.name}! You are in {player.room.name}")
            while player.network.connected:
                data = await reader.read(1024)
                if not data: break
                cmd = Command.parse(data.decode().strip())
                await self.execute_command(player, cmd)
            await player.network.disconnect()
            await player.save()
            del self.players[player.name]
            await writer.close()
            print(f"{player.name} disconnected")

    async def execute_command(self, player: Player, cmd: Command) -> None:
        if not cmd.name:
            await player.term.send("Unknown command. Type 'help' for assistance.")
            return

        async def look():
            await player.term.send(player.room.description)

        async def inventory():
            await player.term.send(player.inventory.inventory())

        async def kill():
            if cmd.args:
                await player.combat.kill(cmd.args[0], player.room)
            else:
                await player.term.send("Kill whom?")

        async def cast():
            if cmd.args:
                await player.spells.cast(cmd.args[0], player)
            else:
                await player.term.send("Cast what?")

        async def ritual():
            if cmd.args:
                await player.rituals.perform(cmd.args[0], player)
            else:
                await player.term.send("Perform which ritual?")

        async def skills():
            await player.term.send(player.skills.list_skills())

        async def quest():
            await player.quests.check_quests()

        async def craft():
            if cmd.args:
                await player.crafting.craft_item(cmd.args[0])
            else:
                await player.term.send("Craft what?")

        async def say():
            if cmd.args:
                await player.soul.say(cmd.args[0])
            else:
                await player.term.send("Say what?")

        async def shout():
            if cmd.args:
                await player.soul.shout(cmd.args[0])
            else:
                await player.term.send("Shout what?")

        async def smile():
            await player.soul.emote("smiles")

        async def help():
            await player.term.send("Commands: look, inventory, kill, cast, ritual, skills, quest, craft, say, shout, smile, help, move, quit, wear, wield, unwear, unwield, put, take")

        async def who():
            await player.term.send("\n".join(self.players.keys()))

        async def score():
            await player.term.send(f"HP: {player.hp}/{player.max_hp}, Mana: {getattr(player, 'mana', 0)}, GP: {player.gp}, AC: {player.ac}, Burden: {player.burden:.1f}%")

        async def train():
            if cmd.args:
                await player.skills.train(cmd.args[0])
            else:
                await player.term.send("Train what?")

        async def advance():
            await player.skills.advance()

        async def learn():
            if cmd.args:
                await player.skills.learn(cmd.args[0])
            else:
                await player.term.send("Learn what?")

        async def teach():
            if cmd.args:
                await player.skills.teach(cmd.args[0])
            else:
                await player.term.send("Teach what?")

        async def worship():
            await player.term.send(player.deity.worship(player))

        async def move():
            if cmd.args in ["north", "east", "south", "west", "up", "down"]:
                await player.move(cmd.args)
            else:
                await player.term.send("Move where?")

        async def quit():
            player.network.connected = False

        async def wear():
            if cmd.args:
                await player.term.send(player.inventory.wear(cmd.args[0]))
            else:
                await player.term.send("Wear what?")

        async def wield():
            if cmd.args:
                await player.term.send(player.inventory.wield(cmd.args[0]))
            else:
                await player.term.send("Wield what?")

        async def unwear():
            if cmd.args:
                await player.term.send(player.inventory.unwear(cmd.args[0]))
            else:
                await player.term.send("Unwear which slot?")

        async def unwield():
            await player.term.send(player.inventory.unwield())

        async def put():
            if len(cmd.args) >= 2:
                await player.term.send(player.inventory.put_in(cmd.args[0], cmd.args[1]))
            else:
                await player.term.send("Put what in which container?")

        async def take():
            if len(cmd.args) >= 2:
                await player.term.send(player.inventory.take_out(cmd.args[0], cmd.args[1]))
            else:
                await player.term.send("Take what from which container?")

        async def unknown():
            await player.term.send(f"Unknown command: {cmd.name}")

        commands = {
            "look": look,
            "inventory": inventory,
            "kill": kill,
            "cast": cast,
            "ritual": ritual,
            "skills": skills,
            "quest": quest,
            "craft": craft,
            "say": say,
            "shout": shout,
            "smile": smile,
            "help": help,
            "who": who,
            "score": score,
            "train": train,
            "advance": advance,
            "learn": learn,
            "teach": teach,
            "worship": worship,
            "move": move,
            "quit": quit,
            "wear": wear,
            "wield": wield,
            "unwear": unwear,
            "unwield": unwield,
            "put": put,
            "take": take
        }
        await commands.get(cmd.name.lower(), unknown)()

    async def start(self) -> None:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.server = await asyncio.start_server(self.handle_client, "0.0.0.0", 3000, ssl=context)
        print(f"Archaon MUD started on 0.0.0.0:3000 with SSL")
        async with self.server:
            await self.server.serve_forever()

async def main():
    engine = MudEngine()
    await engine.start()

if __name__ == "__main__":
    asyncio.run(main())
