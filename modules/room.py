# room.py - Stub file for room definitions in Archaon MUD
# Status: March 5, 2025 - Basic stub to support mud_engine.py
# Description: Defines the Room class for zones, to be expanded with Discworld-inspired features.
# Plans: Add exits, NPCs, items, and environmental effects.

class Room:
    def __init__(self, name: str):
        """Initialize a room with basic properties."""
        self.name = name
        self.description = f"A default room in Faerûn: {name}"
        self.npcs = []  # To be populated by future npc_handler.py
        self.players = []
        self.exits = {}  # Dictionary of exit directions to room names

    def add_player(self, player):
        """Add a player to the room."""
        self.players.append(player)

    def remove_player(self, player):
        """Remove a player from the room."""
        if player in self.players:
            self.players.remove(player)

    def __str__(self):
        """Return a string representation of the room."""
        return f"Room: {self.name} - {self.description}"
