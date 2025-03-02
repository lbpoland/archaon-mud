# deities.py - Archaon MUD Divine System
# Status: March 3, 2025, 02:00 AM AEST
# - Discworld MUD 2025 deity mechanics, Forgotten Realms flavor
# - Features: ~50 deities, worship, favor, alignment, benefits
# - Goal: ~5000 lines of divine depth

DEITIES = {
    "Mystra": {
        "desc": "Goddess of Magic, Keeper of the Weave",
        "alignment_range": ["Neutral Good", "Chaotic Good", "True Neutral"],
        "benefits": {"magic.points": 5, "gp_bonus": 10},
        "restrictions": {"covert.manipulation.stealing": -10},
        "domains": ["waterdeep/", "cormanthor/"],
        "lore": "Mystra shapes the Weave, gifting mortals with magic’s spark..."
    },
    "Tyr": {
        "desc": "God of Justice, the Maimed Lord",
        "alignment_range": ["Lawful Good", "Lawful Neutral"],
        "benefits": {"fighting.defence.dodge": 5, "hp_bonus": 10},
        "restrictions": {"covert.stealth.shadow": -15},
        "domains": ["baldursgate/", "neverwinter/"],
        "lore": "Tyr weighs all with his blind justice..."
    },
    "Lolth": {
        "desc": "Spider Queen, Sovereign of the Drow",
        "alignment_range": ["Chaotic Evil"],
        "benefits": {"covert.manipulation.stealing": 5, "poison_bonus": 3},
        "restrictions": {"faith.rituals.curing.self": -10},
        "race_favor": ["drow"],
        "domains": ["menzoberranzan/", "underdark/"],
        "lore": "Lolth ensnares all in her web of deceit..."
    },
    "Selûne": {
        "desc": "Goddess of the Moon, Our Lady of Silver",
        "alignment_range": ["Chaotic Good", "Neutral Good"],
        "benefits": {"adventuring.perception.visual": 5, "regen_bonus": 2},
        "restrictions": {"covert.stealth.shadow": -5},
        "domains": ["silverymoon/", "waterdeep/"],
        "lore": "Selûne’s light guides the lost..."
    },
    # Add 46+ more (e.g., Bane, Tempus, Corellon)
}

class DeitySystem:
    def __init__(self, player):
        self.player = player
        self.deity = None
        self.favor = 0  # -100 (furious) to 100 (exalted)

    def worship(self, deity):
        if deity not in DEITIES:
            return f"No altar honors {deity} in Faerûn!"
        deity_data = DEITIES[deity]
        if "race_favor" in deity_data and self.player.race not in deity_data["race_favor"]:
            return f"{deity} rejects {self.player.name}’s unworthy lineage!"
        if self.player.alignment not in deity_data["alignment_range"]:
            return f"{self.player.name}’s heart defies {deity}’s will!"
        self.deity = deity
        self.favor = 50
        return f"{self.player.name} pledges fealty at {deity}’s shrine!"

    def check_favor(self):
        if not self.deity:
            return
        deity_data = DEITIES[self.deity]
        if self.player.alignment in deity_data["alignment_range"]:
            self.favor = min(100, self.favor + 5)
        else:
            self.favor = max(-100, self.favor - 10)

    def apply_benefits(self):
        if not self.deity or self.favor < 0:
            return
        deity_data = DEITIES[self.deity]
        for skill, bonus in deity_data["benefits"].items():
            if skill in self.player.skills:
                self.player.skills[skill] += bonus
        self.player.max_hp += deity_data.get("hp_bonus", 0)
        self.player.max_gp += deity_data.get("gp_bonus", 0)
        # Add poison_bonus, regen_bonus hooks for combat.py, skills_handler.py

    def score(self):
        if not self.deity:
            return "Worship: None"
        favor = self.favor
        mood = "exalted" if favor > 75 else "pleased" if favor > 25 else "neutral" if favor > -25 else "displeased" if favor > -75 else "furious"
        return f"Worship: {self.deity} ({DEITIES[self.deity]['desc']})\nFavor: {mood} ({favor}/100)"

# Expansion to ~5000 lines:
# - Add 50+ deities with lore, domains, rituals
# - Favor actions (e.g., +10 for slaying foes of deity’s alignment)
# - Altar mechanics tied to domains (e.g., "menzoberranzan/lolth_altar")
