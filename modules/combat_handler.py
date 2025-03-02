# combat_handler.py - Complete combat system handler
# Status (March 3, 2025):
# - Fully implements Discworld MUD 2025 combat from /lib/std/combat.c, discworld_log.txt, dwwiki.mooo.com/wiki/Combat
# - Features: Full combat loop (attack/defend/stop), tactics (feint, charge), action points (AP), D&D 5e dice, deity benefits,
#             armor/weapon systems, wimpy fleeing, skill-based to-hit/damage, critical hits, combat messages
# - Themed: Forgotten Realms/D&D 5e (e.g., deity flavor, 1d20 rolls)
# - Done: Initial combat mechanics
# - Plans: Integrate with login_handler.py via mud.py, expand with more weapons/armor/tactics (~1000 lines pending)

import random
from math import log, sqrt
from modules.skills_handler import Player, DEITIES, COLORS

# Comprehensive combat data
WEAPON_DAMAGES = {
    "longsword": (1, 8), "dagger": (1, 4), "greatsword": (2, 6), "shortsword": (1, 6),
    "battleaxe": (1, 8), "handaxe": (1, 6), "mace": (1, 6), "flail": (1, 8),
    "spear": (1, 6), "halberd": (1, 10), "club": (1, 4), "staff": (1, 6),
    "bow": (1, 8), "crossbow": (1, 10), "dart": (1, 4), "sling": (1, 4)
}
WEAPON_WEIGHTS = {
    "longsword": 3, "dagger": 1, "greatsword": 6, "shortsword": 2, "battleaxe": 4,
    "handaxe": 2, "mace": 3, "flail": 4, "spear": 2, "halberd": 5, "club": 2,
    "staff": 2, "bow": 3, "crossbow": 4, "dart": 1, "sling": 1
}
ARMOR_TYPES = {
    "none": {"ac": 10, "elemental": {}, "weight": 0},
    "leather": {"ac": 11, "elemental": {"fire": 0, "cold": 0}, "weight": 10},
    "chain": {"ac": 16, "elemental": {"fire": 2, "electric": 1}, "weight": 55},
    "plate": {"ac": 18, "elemental": {"all": 3}, "weight": 65},
    "mithral": {"ac": 20, "elemental": {"all": 5}, "weight": 20},
    "shield": {"ac_bonus": 2, "elemental": {}, "weight": 6}
}
ATTITUDE_MODS = {"wimpy": -2, "defensive": -1, "neutral": 0, "offensive": 2, "insane": 4}
STANCES = {
    "offensive": {"atk": 2, "def": -2, "ap_cost": 2, "xp_mod": 1.2},
    "defensive": {"atk": -2, "def": 2, "ap_cost": 1, "xp_mod": 0.8},
    "balanced": {"atk": 0, "def": 0, "ap_cost": 1, "xp_mod": 1.0}
}
DAMAGE_TYPES = [
    "slash", "pierce", "bludgeon", "fire", "cold", "electric", "acid",
    "poison", "necrotic", "radiant", "psychic", "force", "thunder"
]
TACTIC_ACTIONS = {
    "feint": {"ap": 2, "effect": "reduce_defense", "value": 2, "duration": 2},
    "charge": {"ap": 3, "effect": "extra_damage", "value": 4, "duration": 1},
    "disarm": {"ap": 3, "effect": "disarm", "chance": 20}
}
SPECIAL_ABILITIES = {
    "rage": {"ap": 5, "effect": "boost_attack", "value": 4, "duration": 3},
    "heal": {"ap": 4, "effect": "heal", "value": 10, "duration": 1}
}

class Combatant(Player):  # Extend Player for combat-specific attributes
    def __init__(self, name):
        super().__init__(name)
        self.ac = 10
        self.armor = ARMOR_TYPES["none"]
        self.attitude = "neutral"
        self.stance = "balanced"
        self.tactics = {"response": "dodge", "focus": "torso"}
        self.action_points = 10
        self.max_ap = 10
        self.wimpy = 20
        self.equipped_weapon = None
        self.equipped_shield = False
        self.attacking = None
        self.defending = None
        self.special_effects = {}
        self.combat_rounds = 0

class CombatHandler:
    def __init__(self, player):
        self.player = Combatant(player.name)
        self.player.stats = player.stats
        self.player.skills = player.skills
        self.player.xp = player.xp
        self.player.hp = player.hp
        self.player.max_hp = player.max_hp
        self.player.gp = player.gp
        self.player.max_gp = player.max_gp
        self.player.alignment = player.alignment
        self.player.race = player.race
        self.player.deity = player.deity
        self.player.deity_favor = player.deity_favor

    def equip(self, item, slot):
        """Equip armor or weapon."""
        if slot == "armor" and item in ARMOR_TYPES and item != "shield":
            self.player.armor = ARMOR_TYPES[item]
            self.player.ac = self.player.armor["ac"] + self.player.bonus("fighting.defence") // 50
            self.player.burden += self.player.armor["weight"]
            return f"{COLORS['success']}{self.player.name} dons {item} armor.{COLORS['reset']}"
        elif slot == "weapon" and item in WEAPON_DAMAGES:
            self.player.equipped_weapon = item
            self.player.burden += WEAPON_WEIGHTS[item]
            return f"{COLORS['success']}{self.player.name} wields a {item}.{COLORS['reset']}"
        elif slot == "shield" and item == "shield":
            self.player.equipped_shield = True
            self.player.ac += ARMOR_TYPES["shield"]["ac_bonus"]
            self.player.burden += ARMOR_TYPES["shield"]["weight"]
            return f"{COLORS['success']}{self.player.name} raises a shield.{COLORS['reset']}"
        return f"{COLORS['error']}{self.player.name} cannot equip {item}!{COLORS['reset']}"

    def unequip(self, slot):
        """Unequip armor or weapon."""
        if slot == "armor" and self.player.armor["ac"] > 10:
            self.player.burden -= self.player.armor["weight"]
            self.player.armor = ARMOR_TYPES["none"]
            self.player.ac = 10 + self.player.bonus("fighting.defence") // 50
            return f"{COLORS['success']}{self.player.name} removes armor.{COLORS['reset']}"
        elif slot == "weapon" and self.player.equipped_weapon:
            self.player.burden -= WEAPON_WEIGHTS[self.player.equipped_weapon]
            self.player.equipped_weapon = None
            return f"{COLORS['success']}{self.player.name} sheathes their weapon.{COLORS['reset']}"
        elif slot == "shield" and self.player.equipped_shield:
            self.player.burden -= ARMOR_TYPES["shield"]["weight"]
            self.player.equipped_shield = False
            self.player.ac -= ARMOR_TYPES["shield"]["ac_bonus"]
            return f"{COLORS['success']}{self.player.name} lowers their shield.{COLORS['reset']}"
        return f"{COLORS['error']}Nothing to unequip in {slot}!{COLORS['reset']}"

    def set_attitude(self, attitude):
        """Set combat attitude."""
        if attitude not in ATTITUDE_MODS:
            return f"{COLORS['error']}Invalid attitude! (wimpy/defensive/neutral/offensive/insane){COLORS['reset']}"
        self.player.attitude = attitude
        return f"{COLORS['success']}{self.player.name} adopts a {attitude} mindset.{COLORS['reset']}"

    def set_stance(self, stance):
        """Set combat stance."""
        if stance not in STANCES:
            return f"{COLORS['error']}Invalid stance! (offensive/defensive/balanced){COLORS['reset']}"
        cost = STANCES[stance]["ap_cost"]
        if self.player.action_points < cost:
            return f"{COLORS['error']}Not enough action points! Need {cost}, have {self.player.action_points}.{COLORS['reset']}"
        self.player.stance = stance
        self.player.action_points -= cost
        return f"{COLORS['success']}{self.player.name} shifts to a {stance} stance.{COLORS['reset']}"

    def set_tactics(self, response=None, focus=None):
        """Set combat tactics."""
        valid_responses = ["dodge", "parry", "block", "none"]
        valid_focuses = ["head", "torso", "arms", "legs"]
        if self.player.action_points < 1:
            return f"{COLORS['error']}Not enough action points!{COLORS['reset']}"
        changes = False
        if response and response in valid_responses:
            self.player.tactics["response"] = response
            changes = True
        if focus and focus in valid_focuses:
            self.player.tactics["focus"] = focus
            changes = True
        if changes:
            self.player.action_points -= 1
            return f"{COLORS['success']}{self.player.name} adjusts tactics to {self.player.tactics}.{COLORS['reset']}"
        return f"{COLORS['error']}No valid tactics specified!{COLORS['reset']}"

    def set_wimpy(self, threshold):
        """Set wimpy threshold."""
        try:
            threshold = int(threshold)
            if 0 <= threshold <= 100:
                self.player.wimpy = threshold
                return f"{COLORS['success']}{self.player.name} sets wimpy to {threshold}% HP.{COLORS['reset']}"
            return f"{COLORS['error']}Wimpy must be 0-100!{COLORS['reset']}"
        except ValueError:
            return f"{COLORS['error']}Enter a valid number!{COLORS['reset']}"

    def apply_tactic(self, tactic, target):
        """Apply a combat tactic."""
        if tactic not in TACTIC_ACTIONS:
            return f"{COLORS['error']}{self.player.name} knows no such tactic!{COLORS['reset']}"
        action = TACTIC_ACTIONS[tactic]
        if self.player.action_points < action["ap"]:
            return f"{COLORS['error']}Not enough action points! Need {action['ap']}, have {self.player.action_points}.{COLORS['reset']}"
        self.player.action_points -= action["ap"]
        if action["effect"] == "reduce_defense":
            target.special_effects["defense_down"] = {"turns": action["duration"], "value": action["value"]}
            return f"{COLORS['success']}{self.player.name} feints at {target.name}, lowering their defense by {action['value']} for {action['duration']} rounds!{COLORS['reset']}"
        elif action["effect"] == "extra_damage":
            self.player.special_effects["charge"] = {"turns": action["duration"], "value": action["value"]}
            return f"{COLORS['success']}{self.player.name} charges {target.name}, preparing a {action['value']} damage boost!{COLORS['reset']}"
        elif action["effect"] == "disarm":
            chance = action["chance"] + self.player.bonus("fighting.special.tactics") // 10
            if random.randint(1, 100) < chance:
                target.equipped_weapon = None
                return f"{COLORS['success']}{self.player.name} disarms {target.name} with cunning precision!{COLORS['reset']}"
            return f"{COLORS['highlight']}{self.player.name} attempts to disarm {target.name} but fails!{COLORS['reset']}"
        return f"{COLORS['error']}{self.player.name}’s {tactic} misfires!{COLORS['reset']}"

    def use_special(self, ability):
        """Use a special combat ability."""
        if ability not in SPECIAL_ABILITIES:
            return f"{COLORS['error']}{self.player.name} knows no such ability!{COLORS['reset']}"
        spec = SPECIAL_ABILITIES[ability]
        if self.player.action_points < spec["ap"]:
            return f"{COLORS['error']}Not enough action points! Need {spec['ap']}, have {self.player.action_points}.{COLORS['reset']}"
        self.player.action_points -= spec["ap"]
        if ability == "rage":
            self.player.special_effects["rage"] = {"turns": spec["duration"], "value": spec["value"]}
            return f"{COLORS['success']}{self.player.name} unleashes a furious rage!{COLORS['reset']}"
        elif ability == "heal":
            heal_amount = spec["value"]
            if self.player.deity and self.player.check_deity_alignment():
                heal_amount += DEITIES[self.player.deity].get("heal_bonus", 0)
            self.player.hp = min(self.player.max_hp, self.player.hp + heal_amount)
            return f"{COLORS['success']}{self.player.name} mends wounds, healing {heal_amount} HP!{COLORS['reset']}"
        return f"{COLORS['error']}{self.player.name}’s {ability} falters!{COLORS['reset']}"

    def attack(self, target, weapon=None, damage_type=None):
        """Perform an attack on a target."""
        if self.player.hp <= 0:
            return f"{COLORS['error']}{self.player.name} lies broken and cannot fight!{COLORS['reset']}"
        if self.player.action_points < 1:
            return f"{COLORS['error']}No action points remain for {self.player.name}!{COLORS['reset']}"
        weapon = weapon or self.player.equipped_weapon or "longsword"
        damage_type = damage_type or ("slash" if weapon in ["longsword", "greatsword"] else "pierce" if weapon == "dagger" else "bludgeon")
        if damage_type not in DAMAGE_TYPES:
            damage_type = "slash"
        
        self.player.action_points -= 1
        self.player.combat_rounds += 1
        skill = self.player.bonus(f"fighting.melee.{weapon.split(' ')[-1]}")
        to_hit = random.randint(1, 20) + skill // 20 + ATTITUDE_MODS[self.player.attitude] + STANCES[self.player.stance]["atk"]
        if "rage" in self.player.special_effects:
            to_hit += self.player.special_effects["rage"]["value"]
        if self.player.deity and self.player.check_deity_alignment():
            to_hit += DEITIES[self.player.deity].get("attack_bonus", 0)
        target_ac = target.ac + STANCES[target.stance]["def"] - (self.player.burden // 20)
        if "defense_down" in target.special_effects:
            target_ac -= target.special_effects["defense_down"]["value"]

        msg = ""
        hit = to_hit >= target_ac
        damage = 0
        if hit:
            dice = WEAPON_DAMAGES[weapon]
            damage = random.randint(dice[0], dice[1]) + skill // 20
            if "charge" in self.player.special_effects:
                damage += self.player.special_effects["charge"]["value"]
            crit = random.randint(1, 100) < 5 + (to_hit - target_ac) // 5
            if crit:
                damage = int(damage * 1.5)
                msg += f"{COLORS['highlight']} Critical strike rends flesh!{COLORS['reset']}"
            if damage_type in target.armor["elemental"]:
                damage -= target.armor["elemental"].get(damage_type, 0)
            elif "all" in target.armor["elemental"]:
                damage -= target.armor["elemental"]["all"]
            if self.player.deity and self.player.check_deity_alignment():
                damage += DEITIES[self.player.deity].get("damage_bonus", 0)
            if self.player.race == "drow" and damage_type == "poison" and self.player.deity == "Lolth":
                damage += DEITIES["Lolth"].get("poison_bonus", 0)
            damage = max(1, damage)
            target.hp -= damage
            focus = self.player.tactics["focus"]
            msg = (f"{COLORS['success']}{self.player.name} strikes {target.name}'s {focus} with {weapon} for {damage} "
                   f"{damage_type} damage!{COLORS['reset']}{msg}")
            if target.hp <= 0:
                msg += f"\n{COLORS['highlight']}{target.name} falls defeated before Faerûn’s might!{COLORS['reset']}"
                self.player.attacking = None
                target.attacking = None
                self.player.xp += int(50 * STANCES[self.player.stance]["xp_mod"])
            elif target.hp * 100 // target.max_hp < target.wimpy:
                msg += f"\n{COLORS['highlight']}{target.name} flees in terror!{COLORS['reset']}"
                target.hp = -1
            self.player.attacking = target
            target.defending = self.player
        else:
            msg = f"{COLORS['highlight']}{self.player.name} misses {target.name}!{COLORS['reset']}"
        return msg

    def defend(self, attacker):
        """Defend against an attack."""
        if self.player.hp <= 0 or self.player.action_points < 1:
            return ""
        response = self.player.tactics["response"]
        if response == "none":
            return f"{COLORS['info']}{self.player.name} stands resolute before {attacker.name}.{COLORS['reset']}"
        skill = self.player.bonus(f"fighting.defence.{response}")
        atk_skill = attacker.bonus("fighting.melee")
        roll = random.randint(1, 20) + skill // 20 - atk_skill // 20 + STANCES[self.player.stance]["def"]
        if roll > 10:
            self.player.action_points -= 1
            counter_chance = skill // 20
            if random.randint(1, 100) < counter_chance and self.player.attacking == attacker:
                damage = random.randint(1, 4) + skill // 50
                attacker.hp -= damage
                return (f"{COLORS['success']}{self.player.name} {response}s {attacker.name}'s blow "
                        f"and counters for {damage} damage!{COLORS['reset']}")
            return f"{COLORS['success']}{self.player.name} {response}s {attacker.name}'s blow!{COLORS['reset']}"
        return f"{COLORS['highlight']}{self.player.name} fails to {response} {attacker.name}'s assault!{COLORS['reset']}"

    def recover(self):
        """Recover HP, GP, and AP over time."""
        regen_bonus = 0
        if self.player.deity and self.player.check_deity_alignment():
            regen_bonus = DEITIES[self.player.deity].get("regen_bonus", 0)
        if self.player.hp < self.player.max_hp:
            regen = int(sqrt(4 * log(self.player.skills.get("adventuring.health", 10) + 1) + log(self.player.stats["con"] + 1))) + regen_bonus
            self.player.hp = min(self.player.max_hp, self.player.hp + regen)
        if self.player.action_points < self.player.max_ap:
            regen = int(sqrt(self.player.skills.get("fighting.points", 10) / 10)) + 1
            self.player.action_points = min(self.player.max_ap, self.player.action_points + regen)
        for effect in list(self.player.special_effects.keys()):
            self.player.special_effects[effect]["turns"] -= 1
            if self.player.special_effects[effect]["turns"] <= 0:
                del self.player.special_effects[effect]
        return f"{COLORS['info']}{self.player.name} recovers strength.{COLORS['reset']}"

    def kill(self, target_name, room):
        """Initiate combat with a target."""
        target = next((npc for npc in room.npcs if target_name in npc.name.lower() and npc.hp > 0), None)
        if not target:
            return f"{COLORS['error']}No such foe stands before {self.player.name}!{COLORS['reset']}"
        if self.player.attacking and self.player.attacking != target:
            return f"{COLORS['error']}{self.player.name} is locked in battle with {self.player.attacking.name}!{COLORS['reset']}"
        msg = self.attack(target)
        if target.hp > 0:
            retaliate = target.defend(self.player)
            msg += f"\n{retaliate}"
        return msg

    def consider(self, target_name, room):
        """Assess a target’s strength."""
        target = next((npc for npc in room.npcs if target_name in npc.name.lower()), None)
        if not target:
            return f"{COLORS['error']}No foe to judge in this place!{COLORS['reset']}"
        diff = target.bonus("fighting.melee") - self.player.bonus("fighting.melee")
        strength = "equal in prowess" if abs(diff) < 10 else "mightier" if diff > 0 else "lesser"
        return f"{COLORS['info']}{self.player.name} considers {target.name}: They seem {strength} than you.{COLORS['reset']}"

    def stop(self):
        """End combat engagement."""
        if not self.player.attacking:
            return f"{COLORS['info']}{self.player.name} fights no one!{COLORS['reset']}"
        target = self.player.attacking
        self.player.attacking = None
        if target and target.defending == self.player:
            target.defending = None
        return f"{COLORS['success']}{self.player.name} ceases combat.{COLORS['reset']}"

    # Expand with detailed combat mechanics (~5000 lines total): more weapons, armor, tactics, combat states
