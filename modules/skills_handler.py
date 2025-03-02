# skills_handler.py - Archaon MUD Skills System
# Status: March 3, 2025, 02:00 AM AEST
# - Discworld MUD 2025 mechanics, Forgotten Realms/D&D 5e flavor
# - Features: ~1000 skills, XP/TM, bonuses, regen, racial/guild/environment effects
# - Goal: ~5000 lines of epic mechanics
# - Syncs with: login_handler.py, combat.py, spells.py, deities.py

import random
from math import log, sqrt

# Expanded skill tree (~1000 skills when fully fleshed out)
SKILL_TREE = {
    "adventuring": {
        "direction": {"base": 10, "max": 300, "desc": "Chart Faerûn’s wild paths"},
        "movement": {
            "climbing": {
                "rock": {"base": 10, "max": 300, "desc": "Scale craggy heights"},
                "rope": {"base": 10, "max": 300, "desc": "Ascend ropes with grace"},
                "tree": {"base": 10, "max": 300, "desc": "Climb Mirkwood’s boughs"},
                "ice": {"base": 10, "max": 300, "desc": "Defy frozen faces"},
                "cliff": {"base": 10, "max": 300, "desc": "Conquer sheer drops"},
                "wall": {"base": 10, "max": 300, "desc": "Breach stone fortifications"}
            },
            "swimming": {
                "river": {"base": 10, "max": 300, "desc": "Ford the Dessarin"},
                "sea": {"base": 10, "max": 300, "desc": "Brave the Sea of Swords"},
                "lake": {"base": 10, "max": 300, "desc": "Cross Moonsea’s depths"},
                "underground": {"base": 10, "max": 300, "desc": "Dive Underdark pools"}
            },
            "riding": {
                "horse": {"base": 10, "max": 300, "desc": "Ride Cormyr’s chargers"},
                "camel": {"base": 10, "max": 300, "desc": "Cross Calimshan sands"},
                "wyvern": {"base": 10, "max": 300, "desc": "Tame savage wyverns"},
                "griffon": {"base": 10, "max": 300, "desc": "Soar with elven griffons"}
            },
            # Expand: flying, journey (~50+ sub-skills)
        },
        "perception": {
            "visual": {"base": 10, "max": 300, "desc": "Spot drow in shadows"},
            "auditory": {"base": 10, "max": 300, "desc": "Hear goblins’ whispers"},
            "tactile": {"base": 10, "max": 300, "desc": "Feel trap triggers"},
            "olfactory": {"base": 10, "max": 300, "desc": "Smell orc stench"},
            "magical": {"base": 10, "max": 300, "desc": "Sense Weave ripples"}
        },
        # Expand: health, evaluate, acrobatics (~100+ sub-skills)
        "points": {"base": 10, "max": 300, "desc": "Vitality for Faerûn’s trials"}
    },
    "fighting": {
        "melee": {
            "sword": {
                "long": {"base": 10, "max": 300, "desc": "Wield blades of Neverwinter"},
                "short": {"base": 10, "max": 300, "desc": "Strike with drow stilettos"},
                "great": {"base": 10, "max": 300, "desc": "Swing barbarian claymores"},
                "rapier": {"base": 10, "max": 300, "desc": "Duel with Waterdhavian steel"},
                "scimitar": {"base": 10, "max": 300, "desc": "Dance with Calishite curves"}
            },
            "dagger": {
                "stabbing": {"base": 10, "max": 300, "desc": "Plunge into foes"},
                "throwing": {"base": 10, "max": 300, "desc": "Hurl with deadly aim"},
                # Expand: parrying, concealed
            },
            # Expand: axe, mace, flail, polearm (~150+ sub-skills)
        },
        "range": {
            "bow": {
                "long": {"base": 10, "max": 300, "desc": "Loose elven longbows"},
                "short": {"base": 10, "max": 300, "desc": "Fire wood elf shortbows"},
                # Expand: composite, recurve
            },
            # Expand: crossbow, thrown (~50+ sub-skills)
        },
        # Expand: unarmed, defence, special (~200+ sub-skills)
        "points": {"base": 10, "max": 300, "desc": "Endurance for war"}
    },
    "magic": {
        "spells": {
            "offensive": {
                "area": {"base": 10, "max": 300, "desc": "Unleash Netherese fire"},
                "target": {"base": 10, "max": 300, "desc": "Strike with arcane bolts"},
                "bolt": {"base": 10, "max": 300, "desc": "Hurl lightning"},
                # Expand: blast, curse
            },
            # Expand: defensive, misc, special (~100+ sub-skills)
        },
        "methods": {
            "mental": {
                "channeling": {"base": 10, "max": 300, "desc": "Draw from the Weave"},
                # Expand: charming, convoking
            },
            # Expand: physical, elemental (~100+ sub-skills)
        },
        "points": {"base": 10, "max": 300, "desc": "Arcane reserves"}
    },
    "faith": {
        "rituals": {
            "offensive": {
                "smite": {"base": 10, "max": 300, "desc": "Invoke divine wrath"},
                # Expand: area, target, banish
            },
            # Expand: defensive, curing, misc (~100+ sub-skills)
        },
        "points": {"base": 10, "max": 300, "desc": "Favor of the gods"}
    },
    "covert": {
        "stealth": {
            "shadow": {"base": 10, "max": 300, "desc": "Meld with Underdark gloom"},
            "crowd": {"base": 10, "max": 300, "desc": "Vanish in Baldur’s Gate throngs"},
            # Expand: inside, outside, underwater
        },
        # Expand: hiding, lockpick, manipulation (~150+ sub-skills)
        "points": {"base": 10, "max": 300, "desc": "Cunning reserves"}
    },
    # Expand: crafts, people (~200+ sub-skills each)
}

# Racial bonuses for 18+ races
RACIAL_BONUSES = {
    "drow": {"covert.stealth.shadow": 5, "magic.spells.offensive.target": 3},
    "high elf": {"magic.points": 5, "adventuring.perception.magical": 3},
    "wood elf": {"fighting.range.bow.long": 5, "adventuring.movement.journey.forest": 3},
    "duergar": {"crafts.smithing.black": 5, "adventuring.health.resistance": 3},
    "human": {"people.trading.haggling": 5, "adventuring.points": 3},
    "wild elf": {"adventuring.movement.journey.forest": 5, "fighting.unarmed.striking": 3},
    # Add 12+ more races (e.g., gnome, halfling, tiefling)
}

# Environmental modifiers (domain-based)
ENVIRONMENTAL_MODIFIERS = {
    "underdark/": {"covert.stealth.shadow": 10, "adventuring.movement.swimming.underground": 5, "adventuring.climbing.ice": -10},
    "waterdeep/": {"people.trading.haggling": 5, "covert.manipulation.stealing": -5},
    "cormanthor/": {"adventuring.movement.journey.forest": 10, "fighting.range.bow": 5},
    # Expand for all domains
}

def xp_cost(level):
    return level * 800 + (max(0, level - 50) * 200) + (max(0, level - 100) * 400) + (max(0, level - 200) * 600)

def tm_chance(level, stat, difficulty=1, env_bonus=0):
    base = sqrt(level * stat) / (10 * difficulty) + env_bonus
    return min(50, int(base))

def calculate_bonus(level, stat, burden=0, env_bonus=0):
    base = level * (log(stat + 1) + 1)
    variance = random.randint(-10, 10)
    return max(0, int(base + variance - burden * 0.1 + env_bonus))

class Player:
    def __init__(self, name, race, alignment, domain="waterdeep/"):
        self.name = name
        self.race = race
        self.alignment = alignment
        self.domain = domain  # Current location for env effects
        self.guild = None
        self.skills = self._flatten_skills(SKILL_TREE)
        self.apply_racial_bonuses()
        self.xp = 0
        self.stats = {"str": 8, "dex": 8, "int": 8, "con": 8, "wis": 8, "cha": 8}
        self.hp = self.calculate_hp()
        self.max_hp = self.hp
        self.gp = self.calculate_gp()
        self.max_gp = self.gp
        self.burden = 0
        self.learning_tasks = {}
        self.teaching_tasks = {}

    def _flatten_skills(self, tree, prefix=""):
        flat = {}
        for key, value in tree.items():
            full_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                if "base" in value:
                    flat[full_key] = value["base"]
                flat.update(self._flatten_skills(value, f"{full_key}."))
        return flat

    def apply_racial_bonuses(self):
        for skill, bonus in RACIAL_BONUSES.get(self.race, {}).items():
            if skill in self.skills:
                self.skills[skill] += bonus

    def get_env_bonus(self, skill):
        return ENVIRONMENTAL_MODIFIERS.get(self.domain, {}).get(skill, 0)

    def bonus(self, skill):
        level = self.skills.get(skill, 0)
        stat_map = {
            "fighting": "str", "magic": "int", "covert": "dex", "faith": "wis",
            "adventuring": "con", "crafts": "dex", "people": "cha"
        }
        stat_key = stat_map.get(skill.split(".")[0], "int")
        stat = self.stats[stat_key]
        env_bonus = self.get_env_bonus(skill)
        return calculate_bonus(level, stat, self.burden, env_bonus)

    def calculate_hp(self):
        con = self.stats["con"]
        health = self.skills.get("adventuring.health.base", 10)
        return int(150 + 10 * con + 4 * health)

    def calculate_gp(self):
        points = self.skills.get(f"{self.guild}.points" if self.guild else "magic.points", 10)
        return int(points + 50)

    def train_skill(self, skill, levels=1, teacher=None):
        if skill not in self.skills:
            return f"{self.name} knows not {skill}’s mysteries!"
        current = self.skills[skill]
        next_level = current + levels
        max_level = SKILL_TREE.get(skill.split(".")[0], {}).get("max", 300)
        if next_level > max_level:
            return f"{skill} is honed to perfection!"
        cost = xp_cost(next_level)

        stat_key = {"fighting": "str", "magic": "int", "covert": "dex", "faith": "wis"}.get(skill.split(".")[0], "int")
        stat = self.stats[stat_key]
        env_bonus = self.get_env_bonus(skill)
        if random.randint(1, 100) < tm_chance(current, stat, 1, env_bonus):
            self.skills[skill] = next_level
            self.hp = self.calculate_hp()
            self.gp = self.calculate_gp()
            return f"{self.name} grasps {skill} to {next_level} through instinct (TM)!"

        if self.xp < cost:
            return f"XP runs dry! Need {cost}, have {self.xp}."
        self.xp -= cost
        self.skills[skill] = next_level
        self.hp = self.calculate_hp()
        self.gp = self.calculate_gp()
        teacher_msg = f" with {teacher.name}’s wisdom" if teacher else ""
        return f"{self.name} masters {skill} to {next_level} for {cost} XP{teacher_msg}."

    def advance(self, skill, xp_spent):
        if skill not in self.skills:
            return f"{self.name} is ignorant of {skill}!"
        current = self.skills[skill]
        levels = 0
        total_cost = 0
        max_level = SKILL_TREE.get(skill.split(".")[0], {}).get("max", 300)
        while total_cost <= xp_spent and current + levels < max_level and total_cost + xp_cost(current + levels + 1) <= self.xp:
            levels += 1
            total_cost += xp_cost(current + levels)
        if levels == 0:
            return f"XP too meager! Need {xp_cost(current + 1)}, have {self.xp}."
        self.xp -= total_cost
        self.skills[skill] += levels
        self.hp = self.calculate_hp()
        self.gp = self.calculate_gp()
        return f"{self.name} elevates {skill} to {self.skills[skill]} for {total_cost} XP!"

    def learn(self, skill, attempts=1, difficulty=1):
        if skill not in self.skills:
            self.skills[skill] = 0
        self.learning_tasks[skill] = self.learning_tasks.get(skill, 0) + attempts
        stat_key = {"fighting": "str", "magic": "int", "covert": "dex", "faith": "wis"}.get(skill.split(".")[0], "int")
        stat = self.stats[stat_key]
        env_bonus = self.get_env_bonus(skill)
        if random.randint(1, 100) < tm_chance(self.skills[skill], stat, difficulty, env_bonus):
            self.skills[skill] += 1
            del self.learning_tasks[skill]
            return f"{self.name} learns {skill} to {self.skills[skill]} through toil!"
        return f"{self.name} labors at {skill} ({self.learning_tasks[skill]} attempts left)."

    def teach(self, student, skill, attempts=1):
        if skill not in self.skills or self.skills[skill] < 50:
            return f"{self.name} lacks the mastery to teach {skill}!"
        self.teaching_tasks[skill] = self.teaching_tasks.get(skill, 0) + attempts
        teach_bonus = self.bonus("people.teaching." + skill.split(".")[0])
        student_bonus = student.bonus(skill)
        success_chance = min(75, (teach_bonus - student_bonus) // 10 + 20)
        if random.randint(1, 100) < success_chance:
            student.skills[skill] = student.skills.get(skill, 0) + 1
            self.xp += 50
            return f"{self.name} imparts {skill} to {student.name}, now at {student.skills[skill]}!"
        return f"{self.name} guides {student.name} in {skill} ({self.teaching_tasks[skill]} attempts)."

    def regenerate(self):
        if self.hp < self.max_hp:
            regen = int(sqrt(4 * log(self.skills.get("adventuring.health.regen", 10) + 1) + log(self.stats["con"] + 1)))
            self.hp = min(self.max_hp, self.hp + regen)
        if self.gp < self.max_gp:
            regen = int(sqrt(self.skills.get(f"{self.guild}.points" if self.guild else "magic.points", 10) / 10))
            self.gp = min(self.max_gp, self.gp + regen)
        return f"{self.name} restores their strength."

    def score(self):
        s = f"{self.name}’s tale in Faerûn:\n"
        s += f"HP: {self.hp}/{self.max_hp}  GP: {self.gp}/{self.max_gp}  XP: {self.xp}\n"
        s += f"Stats: STR {self.stats['str']} DEX {self.stats['dex']} INT {self.stats['int']} CON {self.stats['con']} WIS {self.stats['wis']} CHA {self.stats['cha']}\n"
        s += f"Race: {self.race}  Alignment: {self.alignment}  Domain: {self.domain}\n"
        s += f"Burden: {self.burden:.1f}%\n"
        return s

def skills(player):
    s = f"{player.name}’s mastery:\n"
    for skill, level in sorted(player.skills.items()):
        bonus = player.bonus(skill)
        max_level = SKILL_TREE.get(skill.split(".")[0], {}).get("max", 300)
        next_cost = xp_cost(level + 1) if level < max_level else "Max"
        s += f"  {skill:<45} {level:>3}  Bonus: {bonus:>4}  Next: {next_cost:>6}\n"
    s += f"XP Remaining: {player.xp}\n"
    return s

# Expansion to ~5000 lines:
# - Add 700+ skills (e.g., crafts.alchemy.poisons, covert.assassination.traps)
# - Guild-specific trees (e.g., wizards.magic.spells.illusion)
# - Skill decay over time
# - Synergy bonuses (e.g., fighting.melee.sword + fighting.special.tactics)
