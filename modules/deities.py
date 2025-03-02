# deities.py - Archaon MUD Divine System
# Status: March 3, 2025, 03:00 AM AEST
# - Discworld MUD 2025 deity mechanics, Forgotten Realms flavor
# - Features: ~50 deities, worship, favor, alignment, benefits, rituals
# - Size: ~5000 lines when fully expanded

DEITIES = {
    "Mystra": {
        "desc": "Goddess of Magic, Mistress of the Weave",
        "alignment_range": ["Neutral Good", "Chaotic Good", "True Neutral"],
        "benefits": {"magic.points": 5, "gp_bonus": 10, "magic.spells.offensive.bolt": 3},
        "restrictions": {"covert.manipulation.stealing": -10},
        "domains": ["waterdeep/", "cormanthor/", "silverymoon/"],
        "lore": "Mystra weaves the threads of magic, binding Faerûn’s arcane destiny..."
    },
    "Tyr": {
        "desc": "God of Justice, the Even-Handed",
        "alignment_range": ["Lawful Good", "Lawful Neutral"],
        "benefits": {"fighting.defence.dodge": 5, "hp_bonus": 10, "fighting.special.tactics.defensive": 3},
        "restrictions": {"covert.stealth.shadow": -15},
        "domains": ["baldursgate/", "neverwinter/", "cormyr/"],
        "lore": "Tyr’s blind gaze pierces deceit, upholding law across the Realms..."
    },
    "Lolth": {
        "desc": "Spider Queen, Sovereign of the Drow",
        "alignment_range": ["Chaotic Evil"],
        "benefits": {"covert.manipulation.stealing": 5, "poison_bonus": 3, "covert.stealth.shadow": 5},
        "restrictions": {"faith.rituals.curing.self": -10},
        "race_favor": ["drow"],
        "domains": ["menzoberranzan/", "underdark/", "eryndor/"],
        "lore": "Lolth spins treachery and terror, ruling the drow with an iron web..."
    },
    "Selûne": {
        "desc": "Goddess of the Moon, Our Lady of Silver",
        "alignment_range": ["Chaotic Good", "Neutral Good"],
        "benefits": {"adventuring.perception.visual": 5, "regen_bonus": 2, "faith.rituals.defensive.ward": 3},
        "restrictions": {"covert.stealth.shadow": -5},
        "domains": ["silverymoon/", "waterdeep/", "evereska/"],
        "lore": "Selûne’s silver light guides the lost and defies the dark..."
    },
    "Bane": {
        "desc": "God of Tyranny, the Black Hand",
        "alignment_range": ["Lawful Evil", "Neutral Evil"],
        "benefits": {"fighting.special.tactics.offensive": 5, "damage_bonus": 2, "people.trading.haggling": 3},
        "restrictions": {"faith.rituals.curing.target": -10},
        "domains": ["zhentilkeep/", "mulmaster/", "thay/"],
        "lore": "Bane crushes all beneath his iron fist, dreaming of dominion..."
    },
    "Shar": {
        "desc": "Goddess of Darkness, Mistress of the Night",
        "alignment_range": ["Neutral Evil", "Chaotic Evil"],
        "benefits": {"covert.stealth.shadow": 5, "magic.spells.special.illusion": 3},
        "restrictions": {"faith.rituals.defensive.ward": -10},
        "domains": ["calimport/", "underdark/", "shadowdale/"],
        "lore": "Shar cloaks the world in shadow, whispering secrets of despair..."
    },
    "Tempus": {
        "desc": "God of War, Lord of Battles",
        "alignment_range": ["Chaotic Neutral", "True Neutral"],
        "benefits": {"fighting.melee.sword.great": 5, "fighting.points": 5},
        "restrictions": {"covert.manipulation.forgery": -5},
        "domains": ["battledale/", "cormyr/", "icewinddale/"],
        "lore": "Tempus revels in the clash of steel and the glory of war..."
    },
    # Add 43+ more (e.g., Corellon, Moradin, Torm, etc.)
}

class DeitySystem:
    def __init__(self, player):
        self.player = player
        self.deity = None
        self.favor = 0  # -100 to 100
        self.actions = []  # Track favor-affecting deeds

    def worship(self, deity):
        if deity not in DEITIES:
            return f"No shrine bears {deity}’s name in Faerûn!"
        deity_data = DEITIES[deity]
        if "race_favor" in deity_data and self.player.race not in deity_data["race_favor"]:
            return f"{deity} scorns {self.player.name}’s bloodline!"
        if self.player.alignment not in deity_data["alignment_range"]:
            return f"{self.player.name}’s soul strays from {deity}’s creed!"
        self.deity = deity
        self.favor = 50
        self.apply_benefits()
        return f"{self.player.name} kneels at {deity}’s altar, sworn to their will!"

    def check_favor(self):
        if not self.deity:
            return
        deity_data = DEITIES[self.deity]
        alignment_match = self.player.alignment in deity_data["alignment_range"]
        self.favor = min(100, max(-100, self.favor + (5 if alignment_match else -10)))
        for action in self.actions:
            if action["type"] == "kill" and action["alignment"] in deity_data["alignment_range"]:
                self.favor += 10
            elif action["type"] == "offering" and action["value"] > 0:
                self.favor += min(20, action["value"] // 1000)
        self.actions = []  # Clear after processing
        self.apply_benefits() if self.favor >= 0 else self.remove_benefits()

    def apply_benefits(self):
        if not self.deity or self.favor < 0:
            return
        deity_data = DEITIES[self.deity]
        for skill, bonus in deity_data["benefits"].items():
            if skill in self.player.skills:
                self.player.skills[skill] += bonus
        self.player.max_hp += deity_data.get("hp_bonus", 0)
        self.player.max_gp += deity_data.get("gp_bonus", 0)

    def remove_benefits(self):
        if not self.deity:
            return
        deity_data = DEITIES[self.deity]
        for skill, bonus in deity_data["benefits"].items():
            if skill in self.player.skills:
                self.player.skills[skill] = max(0, self.player.skills[skill] - bonus)
        self.player.max_hp -= deity_data.get("hp_bonus", 0)
        self.player.max_gp -= deity_data.get("gp_bonus", 0)

    def record_action(self, action_type, value=None, alignment=None):
        self.actions.append({"type": action_type, "value": value, "alignment": alignment})
        self.check_favor()

    def score(self):
        if not self.deity:
            return "Worship: None"
        favor = self.favor
        mood = "exalted" if favor > 75 else "pleased" if favor > 25 else "neutral" if favor > -25 else "displeased" if favor > -75 else "furious"
        return f"Worship: {self.deity} ({DEITIES[self.deity]['desc']})\nFavor: {mood} ({favor}/100)"

# Expansion to ~5000 lines:
# - Full 50+ deity roster with lore
# - Detailed favor actions (e.g., +15 for defiling rival altars)
# - Domain-specific altar locations
# - Deity-specific rituals tied to faith skills
