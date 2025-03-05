# modules/deities.py
# Status: Basic implementation for login_handler.py integration
# Updated: March 5, 2025, 04:15 PM AEST

DEITIES = {
    "Mystra": {"desc": "Goddess of Magic, weaver of the Weave.", "alignment": "Neutral Good"},
    "Lolth": {"desc": "Spider Queen, mistress of drow.", "alignment": "Chaotic Evil"},
    "Corellon Larethian": {"desc": "Elven god of beauty and magic.", "alignment": "Chaotic Good"},
    "Silvanus": {"desc": "God of wild nature.", "alignment": "True Neutral"},
    "Rillifane Rallathil": {"desc": "Wild elf god of the forest.", "alignment": "Chaotic Neutral"},
    "Laduguer": {"desc": "Duergar god of craft and toil.", "alignment": "Lawful Evil"},
    "Moradin": {"desc": "Dwarven god of creation.", "alignment": "Lawful Good"},
    "Garl Glittergold": {"desc": "Gnomish god of trickery.", "alignment": "Chaotic Good"},
    "Yondalla": {"desc": "Halfling goddess of protection.", "alignment": "Lawful Good"},
    "Asmodeus": {"desc": "Lord of the Nine Hells.", "alignment": "Lawful Evil"},
    "Sune": {"desc": "Goddess of love and beauty.", "alignment": "Chaotic Good"},
    "Gruumsh": {"desc": "Orc god of war.", "alignment": "Chaotic Evil"},
    "Bahamut": {"desc": "Platinum Dragon, god of justice.", "alignment": "Lawful Good"},
    "Lathander": {"desc": "Morninglord, god of renewal.", "alignment": "Neutral Good"},
    "Akadi": {"desc": "Goddess of air and freedom.", "alignment": "Chaotic Neutral"},
    "Kavaki": {"desc": "Goliath god of strength.", "alignment": "True Neutral"},
    "Cat Lord": {"desc": "Deity of felines.", "alignment": "Chaotic Neutral"}
}

class Deity:
    @staticmethod
    def random_deity():
        return random.choice(list(DEITIES.keys()))

    def worship(self, player):
        deity = random.choice(list(DEITIES.keys()))
        return f"{player.name} offers praise to {deity}, gaining {DEITIES[deity]['alignment']} favor!"
