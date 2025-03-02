# skills_handler.py - Archaon MUD Ultimate Skills System
# Status: March 3, 2025, 03:00 AM AEST
# - Discworld MUD 2025 mechanics, Forgotten Realms/D&D 5e theme
# - Features: ~1000 skills, XP/TM, bonuses, regen, racial/guild/env effects, synergies
# - Size: ~5000 lines when fully expanded
# - Integrates with: login_handler.py, combat.py, spells.py, deities.py

import random
from math import log, sqrt, floor

# Massive skill tree (~1000 skills)
SKILL_TREE = {
    "adventuring": {
        "direction": {"base": 10, "max": 300, "desc": "Navigate Faerûn’s twisting trails"},
        "movement": {
            "climbing": {
                "rock": {"base": 10, "max": 300, "desc": "Scale the Spine of the World"},
                "rope": {"base": 10, "max": 300, "desc": "Ascend Luskan’s rigging"},
                "tree": {"base": 10, "max": 300, "desc": "Climb High Forest oaks"},
                "ice": {"base": 10, "max": 300, "desc": "Conquer Icewind Dale peaks"},
                "cliff": {"base": 10, "max": 300, "desc": "Defy Greyhawk cliffs"},
                "wall": {"base": 10, "max": 300, "desc": "Breach Baldur’s Gate walls"},
                "ridge": {"base": 10, "max": 300, "desc": "Traverse mountain ridges"},
                "cavern": {"base": 10, "max": 300, "desc": "Climb Underdark stalagmites"}
            },
            "swimming": {
                "river": {"base": 10, "max": 300, "desc": "Ford the River Reaching"},
                "sea": {"base": 10, "max": 300, "desc": "Brave the Trackless Sea"},
                "lake": {"base": 10, "max": 300, "desc": "Cross the Moonsea"},
                "underground": {"base": 10, "max": 300, "desc": "Dive Underdark lakes"},
                "current": {"base": 10, "max": 300, "desc": "Fight raging torrents"},
                "tide": {"base": 10, "max": 300, "desc": "Master coastal tides"}
            },
            "riding": {
                "horse": {"base": 10, "max": 300, "desc": "Ride Cormyrean stallions"},
                "camel": {"base": 10, "max": 300, "desc": "Cross Anauroch dunes"},
                "wyvern": {"base": 10, "max": 300, "desc": "Tame Zhentarim wyverns"},
                "griffon": {"base": 10, "max": 300, "desc": "Soar with elven griffons"},
                "mule": {"base": 10, "max": 300, "desc": "Guide Daggerford mules"},
                "worg": {"base": 10, "max": 300, "desc": "Control orcish worgs"}
            },
            "flying": {
                "broomstick": {"base": 10, "max": 300, "desc": "Ride Netherese brooms"},
                "winged": {"base": 10, "max": 300, "desc": "Fly with aarakocra wings"},
                "carpet": {"base": 10, "max": 300, "desc": "Soar on Calishite rugs"},
                "levitation": {"base": 10, "max": 300, "desc": "Hover via arcane arts"}
            },
            "journey": {
                "plains": {"base": 10, "max": 300, "desc": "Trek the Shaar"},
                "forest": {"base": 10, "max": 300, "desc": "Cross Cormanthor"},
                "mountain": {"base": 10, "max": 300, "desc": "Ascend the Sword Coast peaks"},
                "desert": {"base": 10, "max": 300, "desc": "Survive Calimshan wastes"},
                "swamp": {"base": 10, "max": 300, "desc": "Wade the Vast Swamp"},
                "tundra": {"base": 10, "max": 300, "desc": "Endure Damaran frost"}
            }
        },
        "perception": {
            "visual": {"base": 10, "max": 300, "desc": "Spot Zhent spies"},
            "auditory": {"base": 10, "max": 300, "desc": "Hear drow footsteps"},
            "tactile": {"base": 10, "max": 300, "desc": "Feel trap wires"},
            "olfactory": {"base": 10, "max": 300, "desc": "Smell troll rot"},
            "magical": {"base": 10, "max": 300, "desc": "Sense Weave disturbances"},
            "tracking": {"base": 10, "max": 300, "desc": "Follow ranger trails"}
        },
        "health": {
            "base": {"base": 10, "max": 300, "desc": "Endure Faerûn’s perils"},
            "regen": {"base": 10, "max": 300, "desc": "Heal wounds swiftly"},
            "endurance": {"base": 10, "max": 300, "desc": "Resist exhaustion"},
            "resistance": {"base": 10, "max": 300, "desc": "Defy poison and plague"},
            "toughness": {"base": 10, "max": 300, "desc": "Shrug off blows"}
        },
        "evaluate": {
            "weapons": {"base": 10, "max": 300, "desc": "Judge mithral blades"},
            "armour": {"base": 10, "max": 300, "desc": "Value adamantine plate"},
            "magic": {"base": 10, "max": 300, "desc": "Appraise enchanted rings"},
            "items": {"base": 10, "max": 300, "desc": "Assess merchant wares"},
            "foes": {"base": 10, "max": 300, "desc": "Gauge enemy strength"},
            "terrain": {"base": 10, "max": 300, "desc": "Read battlegrounds"}
        },
        "acrobatics": {
            "balance": {"base": 10, "max": 300, "desc": "Walk Thayan tightropes"},
            "tumble": {"base": 10, "max": 300, "desc": "Roll from falls"},
            "leap": {"base": 10, "max": 300, "desc": "Jump chasms"},
            "vault": {"base": 10, "max": 300, "desc": "Spring over walls"},
            "dodge": {"base": 10, "max": 300, "desc": "Evade sudden strikes"}
        },
        "points": {"base": 10, "max": 300, "desc": "Stamina for heroic deeds"}
    },
    "fighting": {
        "melee": {
            "sword": {
                "long": {"base": 10, "max": 300, "desc": "Wield Silverymoon longswords"},
                "short": {"base": 10, "max": 300, "desc": "Strike with drow shortswords"},
                "great": {"base": 10, "max": 300, "desc": "Swing Rashemi greatswords"},
                "rapier": {"base": 10, "max": 300, "desc": "Fence with Waterdhavian rapiers"},
                "scimitar": {"base": 10, "max": 300, "desc": "Slash with Calishite scimitars"},
                "bastard": {"base": 10, "max": 300, "desc": "Master versatile blades"}
            },
            "dagger": {
                "stabbing": {"base": 10, "max": 300, "desc": "Pierce with precision"},
                "throwing": {"base": 10, "max": 300, "desc": "Hurl deadly knives"},
                "parrying": {"base": 10, "max": 300, "desc": "Deflect with finesse"},
                "concealed": {"base": 10, "max": 300, "desc": "Hide blades in sleeves"}
            },
            "axe": {
                "battle": {"base": 10, "max": 300, "desc": "Cleave with dwarven battleaxes"},
                "hand": {"base": 10, "max": 300, "desc": "Hack with light axes"},
                "throwing": {"base": 10, "max": 300, "desc": "Toss axes at foes"},
                "war": {"base": 10, "max": 300, "desc": "Wield massive waraxes"}
            },
            "mace": {
                "flanged": {"base": 10, "max": 300, "desc": "Crush with flanged maces"},
                "club": {"base": 10, "max": 300, "desc": "Bash with crude clubs"},
                "morningstar": {"base": 10, "max": 300, "desc": "Smash with spiked stars"},
                "hammer": {"base": 10, "max": 300, "desc": "Pound with warhammers"}
            },
            # Expand: flail, polearm, misc (~150+ sub-skills)
        },
        "range": {
            "bow": {
                "long": {"base": 10, "max": 300, "desc": "Loose elven longbows"},
                "short": {"base": 10, "max": 300, "desc": "Fire wild elf shortbows"},
                "composite": {"base": 10, "max": 300, "desc": "Bend composite bows"},
                "recurve": {"base": 10, "max": 300, "desc": "Master recurve precision"}
            },
            "crossbow": {
                "light": {"base": 10, "max": 300, "desc": "Shoot light crossbows"},
                "heavy": {"base": 10, "max": 300, "desc": "Fire heavy bolts"},
                "repeating": {"base": 10, "max": 300, "desc": "Unload repeating volleys"}
            },
            "thrown": {
                "knife": {"base": 10, "max": 300, "desc": "Throw daggers"},
                "dart": {"base": 10, "max": 300, "desc": "Hurl poisoned darts"},
                "javelin": {"base": 10, "max": 300, "desc": "Launch tribal javelins"}
            }
        },
        "unarmed": {
            "striking": {
                "punch": {"base": 10, "max": 300, "desc": "Pummel with fists"},
                "kick": {"base": 10, "max": 300, "desc": "Strike with boots"},
                "elbow": {"base": 10, "max": 300, "desc": "Jab with elbows"},
                "knee": {"base": 10, "max": 300, "desc": "Crush with knees"}
            },
            "grappling": {
                "hold": {"base": 10, "max": 300, "desc": "Pin foes in place"},
                "throw": {"base": 10, "max": 300, "desc": "Toss enemies over"},
                "lock": {"base": 10, "max": 300, "desc": "Twist limbs into submission"},
                "choke": {"base": 10, "max": 300, "desc": "Strangle with might"}
            }
        },
        "defence": {
            "dodge": {
                "evasion": {"base": 10, "max": 300, "desc": "Slip past blows"},
                "leap": {"base": 10, "max": 300, "desc": "Jump from danger"},
                "roll": {"base": 10, "max": 300, "desc": "Tumble from strikes"},
                "sidestep": {"base": 10, "max": 300, "desc": "Shift aside deftly"}
            },
            "parry": {
                "blade": {"base": 10, "max": 300, "desc": "Deflect swords"},
                "staff": {"base": 10, "max": 300, "desc": "Block with staves"},
                "shield": {"base": 10, "max": 300, "desc": "Parry with shields"},
                "unarmed": {"base": 10, "max": 300, "desc": "Turn blows aside"}
            },
            "block": {
                "shield": {"base": 10, "max": 300, "desc": "Raise shield walls"},
                "arm": {"base": 10, "max": 300, "desc": "Brace against hits"},
                "weapon": {"base": 10, "max": 300, "desc": "Block with steel"}
            }
        },
        "special": {
            "tactics": {
                "offensive": {"base": 10, "max": 300, "desc": "Plan devastating assaults"},
                "defensive": {"base": 10, "max": 300, "desc": "Hold lines with cunning"},
                "feint": {"base": 10, "max": 300, "desc": "Deceive with false strikes"},
                "counter": {"base": 10, "max": 300, "desc": "Turn foe’s attacks back"}
            },
            "weapon": {
                "dual": {"base": 10, "max": 300, "desc": "Wield two blades"},
                "precision": {"base": 10, "max": 300, "desc": "Strike vital points"},
                "disarm": {"base": 10, "max": 300, "desc": "Knock weapons free"},
                "flourish": {"base": 10, "max": 300, "desc": "Dazzle with swordplay"}
            }
        },
        "points": {"base": 10, "max": 300, "desc": "Reserves for combat"}
    },
    "magic": {
        "spells": {
            "offensive": {
                "area": {"base": 10, "max": 300, "desc": "Unleash firestorms"},
                "target": {"base": 10, "max": 300, "desc": "Blast with magic missiles"},
                "bolt": {"base": 10, "max": 300, "desc": "Hurl lightning bolts"},
                "blast": {"base": 10, "max": 300, "desc": "Shatter with force"},
                "curse": {"base": 10, "max": 300, "desc": "Afflict with dark magic"}
            },
            "defensive": {
                "area": {"base": 10, "max": 300, "desc": "Raise protective domes"},
                "self": {"base": 10, "max": 300, "desc": "Shield your form"},
                "target": {"base": 10, "max": 300, "desc": "Guard allies"},
                "ward": {"base": 10, "max": 300, "desc": "Repel evil spirits"},
                "barrier": {"base": 10, "max": 300, "desc": "Erect arcane walls"}
            },
            "misc": {
                "utility": {"base": 10, "max": 300, "desc": "Cast light or locks"},
                "travel": {"base": 10, "max": 300, "desc": "Teleport across Faerûn"},
                "detection": {"base": 10, "max": 300, "desc": "Reveal hidden truths"}
            },
            "special": {
                "summon": {"base": 10, "max": 300, "desc": "Call planar allies"},
                "illusion": {"base": 10, "max": 300, "desc": "Weave false visions"},
                "divination": {"base": 10, "max": 300, "desc": "See beyond time"},
                "enchantment": {"base": 10, "max": 300, "desc": "Bend minds"}
            }
        },
        "methods": {
            "mental": {
                "channeling": {"base": 10, "max": 300, "desc": "Tap the Weave’s core"},
                "charming": {"base": 10, "max": 300, "desc": "Sway wills"},
                "convoking": {"base": 10, "max": 300, "desc": "Summon with thought"},
                "animating": {"base": 10, "max": 300, "desc": "Give life to objects"}
            },
            "physical": {
                "dancing": {"base": 10, "max": 300, "desc": "Cast through motion"},
                "singing": {"base": 10, "max": 300, "desc": "Weave spells with song"},
                "gesturing": {"base": 10, "max": 300, "desc": "Shape magic with hands"},
                "scribing": {"base": 10, "max": 300, "desc": "Inscribe runes"}
            },
            "elemental": {
                "fire": {"base": 10, "max": 300, "desc": "Command flames"},
                "water": {"base": 10, "max": 300, "desc": "Control tides"},
                "air": {"base": 10, "max": 300, "desc": "Wield winds"},
                "earth": {"base": 10, "max": 300, "desc": "Shape stone"}
            }
        },
        "points": {"base": 10, "max": 300, "desc": "Arcane reserves"}
    },
    "faith": {
        "rituals": {
            "offensive": {
                "smite": {"base": 10, "max": 300, "desc": "Strike with holy fury"},
                "banish": {"base": 10, "max": 300, "desc": "Exile fiends"},
                "area": {"base": 10, "max": 300, "desc": "Purge wide evil"}
            },
            "defensive": {
                "ward": {"base": 10, "max": 300, "desc": "Shield from darkness"},
                "sanctuary": {"base": 10, "max": 300, "desc": "Create holy ground"},
                "self": {"base": 10, "max": 300, "desc": "Guard your soul"}
            },
            "curing": {
                "self": {"base": 10, "max": 300, "desc": "Heal your wounds"},
                "target": {"base": 10, "max": 300, "desc": "Mend allies"},
                "disease": {"base": 10, "max": 300, "desc": "Cure plagues"},
                "poison": {"base": 10, "max": 300, "desc": "Cleanse venom"}
            },
            "misc": {
                "blessing": {"base": 10, "max": 300, "desc": "Bestow divine favor"},
                "divination": {"base": 10, "max": 300, "desc": "Seek godly insight"}
            }
        },
        "points": {"base": 10, "max": 300, "desc": "Divine favor pool"}
    },
    "covert": {
        "stealth": {
            "shadow": {"base": 10, "max": 300, "desc": "Vanish in Underdark gloom"},
            "crowd": {"base": 10, "max": 300, "desc": "Fade in Waterdeep throngs"},
            "inside": {"base": 10, "max": 300, "desc": "Slip through halls"},
            "outside": {"base": 10, "max": 300, "desc": "Blend with wilds"},
            "underwater": {"base": 10, "max": 300, "desc": "Move unseen in depths"}
        },
        "hiding": {
            "person": {"base": 10, "max": 300, "desc": "Conceal yourself"},
            "object": {"base": 10, "max": 300, "desc": "Hide treasures"},
            "place": {"base": 10, "max": 300, "desc": "Obscure locations"}
        },
        "lockpick": {
            "doors": {"base": 10, "max": 300, "desc": "Open guarded portals"},
            "safes": {"base": 10, "max": 300, "desc": "Crack merchant vaults"},
            "traps": {"base": 10, "max": 300, "desc": "Disarm deadly snares"},
            "chests": {"base": 10, "max": 300, "desc": "Unlock ancient troves"}
        },
        "manipulation": {
            "palming": {"base": 10, "max": 300, "desc": "Slip items unseen"},
            "stealing": {"base": 10, "max": 300, "desc": "Pick pockets deftly"},
            "planting": {"base": 10, "max": 300, "desc": "Frame with evidence"},
            "forgery": {"base": 10, "max": 300, "desc": "Craft false scrolls"}
        },
        "points": {"base": 10, "max": 300, "desc": "Cunning reserves"}
    },
    "crafts": {
        "smithing": {
            "gold": {"base": 10, "max": 300, "desc": "Forge golden trinkets"},
            "silver": {"base": 10, "max": 300, "desc": "Shape silver blades"},
            "black": {"base": 10, "max": 300, "desc": "Work dark iron"},
            "mithral": {"base": 10, "max": 300, "desc": "Craft elven mithral"},
            "adamantine": {"base": 10, "max": 300, "desc": "Forge dwarven adamantine"}
        },
        "mining": {
            "ore": {"base": 10, "max": 300, "desc": "Extract iron veins"},
            "gem": {"base": 10, "max": 300, "desc": "Mine rare jewels"},
            "crystal": {"base": 10, "max": 300, "desc": "Harvest arcane crystals"}
        },
        "hunting": {
            "tracking": {"base": 10, "max": 300, "desc": "Follow beast trails"},
            "trapping": {"base": 10, "max": 300, "desc": "Set snares"},
            "skinning": {"base": 10, "max": 300, "desc": "Harvest hides"}
        },
        "culinary": {
            "cooking": {"base": 10, "max": 300, "desc": "Prepare hearty stews"},
            "baking": {"base": 10, "max": 300, "desc": "Bake elven bread"},
            "brewing": {"base": 10, "max": 300, "desc": "Craft dwarven ale"}
        },
        "points": {"base": 10, "max": 300, "desc": "Crafting stamina"}
    },
    "people": {
        "trading": {
            "buying": {"base": 10, "max": 300, "desc": "Haggle for goods"},
            "selling": {"base": 10, "max": 300, "desc": "Profit from wares"},
            "haggling": {"base": 10, "max": 300, "desc": "Drive hard bargains"},
            "appraisal": {"base": 10, "max": 300, "desc": "Value market items"}
        },
        "culture": {
            "dwarfish": {"base": 10, "max": 300, "desc": "Know dwarven ways"},
            "elven": {"base": 10, "max": 300, "desc": "Grasp elven lore"},
            "human": {"base": 10, "max": 300, "desc": "Understand human customs"},
            "drow": {"base": 10, "max": 300, "desc": "Unravel drow intrigue"}
        },
        "teaching": {
            "adventuring": {"base": 10, "max": 300, "desc": "Teach survival"},
            "fighting": {"base": 10, "max": 300, "desc": "Train warriors"},
            "magic": {"base": 10, "max": 300, "desc": "School mages"},
            "faith": {"base": 10, "max": 300, "desc": "Guide priests"}
        },
        "points": {"base": 10, "max": 300, "desc": "Social endurance"}
    }
}

# Racial bonuses (18+ races)
RACIAL_BONUSES = {
    "drow": {"covert.stealth.shadow": 5, "magic.spells.offensive.bolt": 3},
    "high elf": {"magic.points": 5, "adventuring.perception.magical": 3},
    "wood elf": {"fighting.range.bow.long": 5, "adventuring.movement.journey.forest": 3},
    "duergar": {"crafts.smithing.black": 5, "adventuring.health.resistance": 3},
    "human": {"people.trading.haggling": 5, "adventuring.points": 3},
    "wild elf": {"adventuring.movement.journey.forest": 5, "fighting.unarmed.striking.punch": 3},
    "gnome": {"crafts.mining.gem": 5, "magic.spells.misc.utility": 3},
    "halfling": {"covert.manipulation.palming": 5, "adventuring.acrobatics.tumble": 3},
    "tiefling": {"magic.spells.offensive.blast": 5, "people.culture.human": 3},
    # Add 9+ more (e.g., dwarf, orc, aarakocra)
}

# Environmental modifiers (domain-based)
ENVIRONMENTAL_MODIFIERS = {
    "underdark/": {"covert.stealth.shadow": 10, "adventuring.movement.swimming.underground": 5, "adventuring.climbing.ice": -10},
    "waterdeep/": {"people.trading.haggling": 5, "covert.manipulation.stealing": -5},
    "cormanthor/": {"adventuring.movement.journey.forest": 10, "fighting.range.bow.long": 5},
    "menzoberranzan/": {"covert.stealth.shadow": 15, "adventuring.health.resistance": 5},
    # Expand for 100+ domains
}

# Guild-specific skill bonuses
GUILD_BONUSES = {
    "wizards": {"magic.spells.offensive": 5, "magic.points": 10},
    "warriors": {"fighting.melee.sword": 5, "fighting.points": 10},
    "priests": {"faith.rituals.curing": 5, "faith.points": 10},
    "thieves": {"covert.manipulation.stealing": 5, "covert.points": 10},
    # Expand for all guilds
}

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

def xp_cost(level):
    return level * 800 + (max(0, level - 50) * 200) + (max(0, level - 100) * 400) + (max(0, level - 200) * 600)

def tm_chance(level, stat, difficulty=1, env_bonus=0):
    return min(50, int(sqrt(level * stat) / (10 * difficulty) + env_bonus))

def calculate_bonus(level, stat, burden=0, env_bonus=0, guild_bonus=0):
    base = level * (log(stat + 1) + 1)
    variance = random.randint(-10, 10)
    return max(0, int(base + variance - burden * 0.1 + env_bonus + guild_bonus))

def synergy_bonus(player, skill):
    """Calculate bonus from synergistic skills."""
    base_skill = skill.split(".")[0]
    related = [s for s in player.skills if s.startswith(base_skill) and s != skill]
    return sum(floor(player.skills[s] / 50) for s in related)

class Player:
    def __init__(self, name, race="human", alignment="True Neutral", deity=None):
        self.name = name
        self.race = race
        self.alignment = alignment
        self.deity = deity  # Added to align with combat_handler
        self.deity_favor = 0  # Default favor
        self.guild = None
        self.skills = self._flatten_skills(SKILL_TREE)
        self.xp = 0
        self.stats = {"str": 8, "dex": 8, "int": 8, "con": 8, "wis": 8, "cha": 8}
        self.hp = self.calculate_hp()
        self.max_hp = self.hp
        self.gp = self.calculate_gp()
        self.max_gp = self.gp
        self.burden = 0
        self.learning_tasks = {}
        self.teaching_tasks = {}
        self.components = {}  # For rituals/inventory

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

    def apply_guild_bonuses(self):
        if self.guild:
            for skill, bonus in GUILD_BONUSES.get(self.guild, {}).items():
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
        guild_bonus = GUILD_BONUSES.get(self.guild, {}).get(skill, 0)
        synergy = synergy_bonus(self, skill)
        return calculate_bonus(level, stat, self.burden, env_bonus, guild_bonus) + synergy

    def calculate_hp(self):
        con = self.stats["con"]
        health = self.skills.get("adventuring.health.base", 10)
        return int(150 + 10 * con + 4 * health)

    def calculate_gp(self):
        points = self.skills.get(f"{self.guild}.points" if self.guild else "magic.points", 10)
        return int(points + 50)

    def train_skill(self, skill, levels=1, teacher=None):
        if skill not in self.skills:
            return f"{self.name} has no ken of {skill}!"
        current = self.skills[skill]
        next_level = current + levels
        max_level = SKILL_TREE.get(skill.split(".")[0], {}).get("max", 300)
        if next_level > max_level:
            return f"{skill} is forged to its utmost!"
        cost = xp_cost(next_level)

        stat_key = {"fighting": "str", "magic": "int", "covert": "dex", "faith": "wis"}.get(skill.split(".")[0], "int")
        stat = self.stats[stat_key]
        env_bonus = self.get_env_bonus(skill)
        if random.randint(1, 100) < tm_chance(current, stat, 1, env_bonus):
            self.skills[skill] = next_level
            self.hp = self.calculate_hp()
            self.gp = self.calculate_gp()
            self.skill_decay[skill] = 0  # Reset decay timer
            return f"{self.name} masters {skill} to {next_level} by intuition (TM)!"

        if self.xp < cost:
            return f"Glory eludes you! Need {cost} XP, have {self.xp}."
        self.xp -= cost
        self.skills[skill] = next_level
        self.hp = self.calculate_hp()
        self.gp = self.calculate_gp()
        self.skill_decay[skill] = 0
        teacher_msg = f" under {teacher.name}’s eye" if teacher else ""
        return f"{self.name} refines {skill} to {next_level} for {cost} XP{teacher_msg}."

    def advance(self, skill, xp_spent):
        if skill not in self.skills:
            return f"{self.name} knows not {skill}’s secrets!"
        current = self.skills[skill]
        levels = 0
        total_cost = 0
        max_level = SKILL_TREE.get(skill.split(".")[0], {}).get("max", 300)
        while total_cost <= xp_spent and current + levels < max_level and total_cost + xp_cost(current + levels + 1) <= self.xp:
            levels += 1
            total_cost += xp_cost(current + levels)
        if levels == 0:
            return f"XP too scant! Need {xp_cost(current + 1)}, have {self.xp}."
        self.xp -= total_cost
        self.skills[skill] += levels
        self.hp = self.calculate_hp()
        self.gp = self.calculate_gp()
        self.skill_decay[skill] = 0
        return f"{self.name} raises {skill} to {self.skills[skill]} for {total_cost} XP!"

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
            self.skill_decay[skill] = 0
            return f"{self.name} grasps {skill} to {self.skills[skill]} through effort!"
        return f"{self.name} toils at {skill} ({self.learning_tasks[skill]} attempts remain)."

    def teach(self, student, skill, attempts=1):
        if skill not in self.skills or self.skills[skill] < 50:
            return f"{self.name} lacks the prowess to teach {skill}!"
        self.teaching_tasks[skill] = self.teaching_tasks.get(skill, 0) + attempts
        teach_bonus = self.bonus("people.teaching." + skill.split(".")[0])
        student_bonus = student.bonus(skill)
        success_chance = min(75, (teach_bonus - student_bonus) // 10 + 20)
        if random.randint(1, 100) < success_chance:
            student.skills[skill] = student.skills.get(skill, 0) + 1
            self.xp += 50
            student.skill_decay[skill] = 0
            return f"{self.name} enlightens {student.name} in {skill} to {student.skills[skill]}!"
        return f"{self.name} instructs {student.name} in {skill} ({self.teaching_tasks[skill]} attempts)."

    def regenerate(self):
        if self.hp < self.max_hp:
            regen = int(sqrt(4 * log(self.skills.get("adventuring.health.regen", 10) + 1) + log(self.stats["con"] + 1)))
            self.hp = min(self.max_hp, self.hp + regen)
        if self.gp < self.max_gp:
            regen = int(sqrt(self.skills.get(f"{self.guild}.points" if self.guild else "magic.points", 10) / 10))
            self.gp = min(self.max_gp, self.gp + regen)
        return f"{self.name} renews their vigor."

    def decay_skills(self):
        """Decay unused skills over time."""
        for skill in self.skills:
            self.skill_decay[skill] = self.skill_decay.get(skill, 0) + 1
            if self.skill_decay[skill] > 100 and self.skills[skill] > 10:
                self.skills[skill] -= 1
                self.skill_decay[skill] = 0
                return f"{self.name}’s {skill} dulls to {self.skills[skill]} from disuse."

    def score(self):
        s = f"{self.name}’s legend in Faerûn:\n"
        s += f"HP: {self.hp}/{self.max_hp}  GP: {self.gp}/{self.max_gp}  XP: {self.xp}\n"
        s += f"Stats: STR {self.stats['str']} DEX {self.stats['dex']} INT {self.stats['int']} CON {self.stats['con']} WIS {self.stats['wis']} CHA {self.stats['cha']}\n"
        s += f"Race: {self.race}  Alignment: {self.alignment}  Guild: {self.guild or 'None'}  Domain: {self.domain}\n"
        s += f"Burden: {self.burden:.1f}%\n"
        return s

def skills(player):
    s = f"{player.name}’s arsenal of skills:\n"
    for skill, level in sorted(player.skills.items()):
        bonus = player.bonus(skill)
        max_level = SKILL_TREE.get(skill.split(".")[0], {}).get("max", 300)
        next_cost = xp_cost(level + 1) if level < max_level else "Max"
        s += f"  {skill:<45} {level:>3}  Bonus: {bonus:>4}  Next: {next_cost:>6}\n"
    s += f"XP Remaining: {player.xp}\n"
    return s

# Expansion to ~5000 lines:
# - Full 1000 skills with descriptions
# - Detailed synergy tables
# - 100+ environmental modifiers
# - Skill-specific failure/success flavor text
