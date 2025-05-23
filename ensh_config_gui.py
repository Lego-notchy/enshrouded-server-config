import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import shutil
from datetime import datetime
import sys
import re
import random 

# --- Constants ---
JSON_FILE = "enshrouded_server.json"
README_FILE = "enshrouded_server_readme.txt" 
BACKUP_DIR = "old"
LOG_LEVEL = "INFO" 
FALLBACK_GAME_VERSION = "Unknown (Readme not found/parsable)"
APP_TITLE_BASE = "Enshrouded Server Config Editor"

NANOSECONDS_PER_SECOND = 1_000_000_000
SECONDS_PER_MINUTE = 60
NANOSECONDS_PER_MINUTE = NANOSECONDS_PER_SECOND * SECONDS_PER_MINUTE

# --- Path Definitions ---
DAY_DURATION_PATH = ["gameSettings", "dayTimeDuration"]
NIGHT_DURATION_PATH = ["gameSettings", "nightTimeDuration"]
HUNGER_TO_STARVING_PATH = ["gameSettings", "fromHungerToStarving"]
TOMBSTONE_MODE_PATH = ["gameSettings", "tombstoneMode"]
TAMING_STARTLE_PATH = ["gameSettings", "tamingStartleRepercussion"]
WEATHER_FREQUENCY_PATH = ["gameSettings", "weatherFrequency"]
CURSE_MODIFIER_PATH = ["gameSettings", "curseModifier"]
GAME_PRESET_PATH = ["gameSettingsPreset"] 
VOICE_CHAT_MODE_PATH = ["voiceChatMode"] 
RANDOM_SPAWNER_PATH = ["gameSettings", "randomSpawnerAmount"]
AGGRO_POOL_PATH = ["gameSettings", "aggroPoolAmount"]

# --- Setting Type Configurations (Path, Min/Max, Normal values) ---
DURATION_SETTINGS_CONFIG = {
    "dayTimeDuration": {"min_minutes": 2, "max_minutes": 60, "path": DAY_DURATION_PATH, "normal_minutes": 30},
    "nightTimeDuration": {"min_minutes": 2, "max_minutes": 60, "path": NIGHT_DURATION_PATH, "normal_minutes": 12},
    "fromHungerToStarving": {"min_minutes": 5, "max_minutes": 20, "path": HUNGER_TO_STARVING_PATH, "normal_minutes": 10000}, 
}

STRING_CHOICE_SETTINGS_CONFIG = {
    "tombstoneMode": {"path": TOMBSTONE_MODE_PATH, "options": ["AddBackpackMaterials", "Everything", "NoTombstone"], "normal": "AddBackpackMaterials"},
    "tamingStartleRepercussion": {"path": TAMING_STARTLE_PATH, "options": ["KeepProgress", "LoseSomeProgress", "LoseAllProgress"], "normal": "LoseSomeProgress"},
    "weatherFrequency": {"path": WEATHER_FREQUENCY_PATH, "options": ["Disabled", "Rare", "Normal", "Often"], "normal": "Normal"},
    "curseModifier": {"path": CURSE_MODIFIER_PATH, "options": ["Easy", "Normal", "Hard"], "normal": "Normal"},
    "gameSettingsPreset": {"path": GAME_PRESET_PATH, "options": ["Default", "Relaxed", "Hard", "Survival", "Custom"], "normal": "Default"},
    "voiceChatMode": {"path": VOICE_CHAT_MODE_PATH, "options": ["Proximity", "Global"], "normal": "Proximity"},
    "randomSpawnerAmount": {"path": RANDOM_SPAWNER_PATH, "options": ["Few", "Normal", "Many", "Extreme"], "normal": "Normal"},
    "aggroPoolAmount": {"path": AGGRO_POOL_PATH, "options": ["Few", "Normal", "Many", "Extreme"], "normal": "Normal"},
}

FACTOR_SETTINGS_CONFIG = { 
    "playerHealthFactor": {"path": ["gameSettings", "playerHealthFactor"], "min_float": 0.25, "max_float": 4.0, "normal_float": 1.0, "impact_score_hard": -2, "tooltip_hint": "Player max health multiplier."},
    "playerStaminaFactor": {"path": ["gameSettings", "playerStaminaFactor"], "min_float": 0.25, "max_float": 4.0, "normal_float": 1.0, "impact_score_hard": -1, "tooltip_hint": "Player max stamina multiplier."},
    "playerManaFactor": {"path": ["gameSettings", "playerManaFactor"], "min_float": 0.25, "max_float": 4.0, "normal_float": 1.0, "impact_score_hard": -1, "tooltip_hint": "Player max mana multiplier."},
    "playerBodyHeatFactor": {"path": ["gameSettings", "playerBodyHeatFactor"], "min_float": 0.5, "max_float": 2.0, "normal_float": 1.0, "tooltip_hint": "Player resistance to cold."},
    "foodBuffDurationFactor": {"path": ["gameSettings", "foodBuffDurationFactor"], "min_float": 0.5, "max_float": 2.0, "normal_float": 1.0, "tooltip_hint": "How long food buffs last."},
    "shroudTimeFactor": {"path": ["gameSettings", "shroudTimeFactor"], "min_float": 0.5, "max_float": 2.0, "normal_float": 1.0, "impact_score_hard": -2, "tooltip_hint": "Time allowed in Shroud."},
    "miningDamageFactor": {"path": ["gameSettings", "miningDamageFactor"], "min_float": 0.5, "max_float": 2.0, "normal_float": 1.0, "tooltip_hint": "Damage dealt by mining tools."},
    "plantGrowthSpeedFactor": {"path": ["gameSettings", "plantGrowthSpeedFactor"], "min_float": 0.25, "max_float": 2.0, "normal_float": 1.0, "tooltip_hint": "How fast plants grow."},
    "resourceDropStackAmountFactor": {"path": ["gameSettings", "resourceDropStackAmountFactor"], "min_float": 0.25, "max_float": 2.0, "normal_float": 1.0, "impact_score_hard": -2, "tooltip_hint": "Amount of resources dropped."},
    "factoryProductionSpeedFactor": {"path": ["gameSettings", "factoryProductionSpeedFactor"], "min_float": 0.25, "max_float": 2.0, "normal_float": 1.0, "tooltip_hint": "Crafting speed at workstations."},
    "perkUpgradeRecyclingFactor": {"path": ["gameSettings", "perkUpgradeRecyclingFactor"], "min_float": 0.0, "max_float": 1.0, "normal_float": 0.5, "tooltip_hint": "Runes returned when salvaging."},
    "perkCostFactor": {"path": ["gameSettings", "perkCostFactor"], "min_float": 0.25, "max_float": 2.0, "normal_float": 1.0, "tooltip_hint": "Cost to upgrade weapons."},
    "experienceCombatFactor": {"path": ["gameSettings", "experienceCombatFactor"], "min_float": 0.25, "max_float": 2.0, "normal_float": 1.0, "impact_score_hard": -1, "tooltip_hint": "XP gained from combat."},
    "experienceMiningFactor": {"path": ["gameSettings", "experienceMiningFactor"], "min_float": 0.0, "max_float": 2.0, "normal_float": 1.0, "impact_score_hard": -1, "tooltip_hint": "XP gained from mining."},
    "experienceExplorationQuestsFactor": {"path": ["gameSettings", "experienceExplorationQuestsFactor"], "min_float": 0.25, "max_float": 2.0, "normal_float": 1.0, "impact_score_hard": -1, "tooltip_hint": "XP from exploration/quests."},
    "enemyDamageFactor": {"path": ["gameSettings", "enemyDamageFactor"], "min_float": 0.25, "max_float": 5.0, "normal_float": 1.0, "impact_score_hard": 2, "tooltip_hint": "Damage dealt by non-boss enemies."},
    "enemyHealthFactor": {"path": ["gameSettings", "enemyHealthFactor"], "min_float": 0.25, "max_float": 4.0, "normal_float": 1.0, "impact_score_hard": 2, "tooltip_hint": "Health of non-boss enemies."},
    "enemyStaminaFactor": {"path": ["gameSettings", "enemyStaminaFactor"], "min_float": 0.5, "max_float": 2.0, "normal_float": 1.0, "tooltip_hint": "Stamina of non-boss enemies (stun resistance)."},
    "enemyPerceptionRangeFactor": {"path": ["gameSettings", "enemyPerceptionRangeFactor"], "min_float": 0.5, "max_float": 2.0, "normal_float": 1.0, "tooltip_hint": "How far enemies can see/hear."},
    "bossDamageFactor": {"path": ["gameSettings", "bossDamageFactor"], "min_float": 0.2, "max_float": 5.0, "normal_float": 1.0, "impact_score_hard": 1, "tooltip_hint": "Damage dealt by bosses."},
    "bossHealthFactor": {"path": ["gameSettings", "bossHealthFactor"], "min_float": 0.2, "max_float": 5.0, "normal_float": 1.0, "impact_score_hard": 1, "tooltip_hint": "Health of bosses."},
    "threatBonus": {"path": ["gameSettings", "threatBonus"], "min_float": 0.25, "max_float": 4.0, "normal_float": 1.0, "tooltip_hint": "Player threat generation modifier."},
}

# --- Menu Definitions (path_keys, label_text, tooltip_text) ---
general_settings_menu_def = {
    1: (["name"], "Server Name", "The name displayed in the server browser."),
    2: (["saveDirectory"], "Save Directory", "Folder where game saves are stored (e.g., ./savegame)."),
    3: (["logDirectory"], "Log Directory", "Folder where server logs are stored (e.g., ./logs)."),
    4: (["ip"], "IP Address", "Server IP address. '0.0.0.0' binds to all available network interfaces."), 
    5: (["queryPort"], "Query Port", "Port for server browser queries (Default: 15637). Firewall must allow this port."), 
    6: (["slotCount"], "Slot Count", "Maximum concurrent players (e.g., 1-16)."), 
    7: (["enableTextChat"], "Enable Text Chat", "Allow players to use text chat."),
    8: (["enableVoiceChat"], "Enable Voice Chat", "Allow players to use voice chat."),
    9: (VOICE_CHAT_MODE_PATH, "Voice Chat Mode", f"Voice chat type: {', '.join(STRING_CHOICE_SETTINGS_CONFIG['voiceChatMode']['options'])}."), 
}
player_settings_menu_def = {
    1: (FACTOR_SETTINGS_CONFIG["playerHealthFactor"]["path"], "Player Health", FACTOR_SETTINGS_CONFIG["playerHealthFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['playerHealthFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['playerHealthFactor']['max_float']*100)}%."),
    2: (FACTOR_SETTINGS_CONFIG["playerStaminaFactor"]["path"], "Player Stamina", FACTOR_SETTINGS_CONFIG["playerStaminaFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['playerStaminaFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['playerStaminaFactor']['max_float']*100)}%."),
    3: (FACTOR_SETTINGS_CONFIG["playerManaFactor"]["path"], "Player Mana", FACTOR_SETTINGS_CONFIG["playerManaFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['playerManaFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['playerManaFactor']['max_float']*100)}%."),
    4: (FACTOR_SETTINGS_CONFIG["playerBodyHeatFactor"]["path"], "Player Body Heat", FACTOR_SETTINGS_CONFIG["playerBodyHeatFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['playerBodyHeatFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['playerBodyHeatFactor']['max_float']*100)}%."),
    5: (["gameSettings", "enableDurability"], "Enable Item Durability", "If true, weapons and tools take durability damage."),
    6: (["gameSettings", "enableStarvingDebuff"], "Enable Starving Debuff", "If true, players suffer debuffs when starving."),
    7: (FACTOR_SETTINGS_CONFIG["foodBuffDurationFactor"]["path"], "Food Buff Duration", FACTOR_SETTINGS_CONFIG["foodBuffDurationFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['foodBuffDurationFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['foodBuffDurationFactor']['max_float']*100)}%."),
    8: (HUNGER_TO_STARVING_PATH, "Time to Starvation", f"Time in minutes before starving starts. Range: {DURATION_SETTINGS_CONFIG['fromHungerToStarving']['min_minutes']}-{DURATION_SETTINGS_CONFIG['fromHungerToStarving']['max_minutes']} min."),
}
world_settings_menu_def = {
    1: (GAME_PRESET_PATH, "Game Difficulty Preset", f"Overall game difficulty preset: {', '.join(STRING_CHOICE_SETTINGS_CONFIG['gameSettingsPreset']['options'])}. If not 'Custom', individual settings below might be ignored by the game."), 
    2: (TOMBSTONE_MODE_PATH, "Tombstone Mode", f"What players drop on death: {', '.join(STRING_CHOICE_SETTINGS_CONFIG['tombstoneMode']['options'])}."),     
    3: (DAY_DURATION_PATH, "Day Duration", f"Length of daytime in minutes. Range: {DURATION_SETTINGS_CONFIG['dayTimeDuration']['min_minutes']}-{DURATION_SETTINGS_CONFIG['dayTimeDuration']['max_minutes']} min."),
    4: (NIGHT_DURATION_PATH, "Night Duration", f"Length of nighttime in minutes. Range: {DURATION_SETTINGS_CONFIG['nightTimeDuration']['min_minutes']}-{DURATION_SETTINGS_CONFIG['nightTimeDuration']['max_minutes']} min."),
    5: (["gameSettings", "enableGliderTurbulences"], "Glider Turbulences", "If true, gliders are affected by air turbulence."),
    6: (WEATHER_FREQUENCY_PATH, "Weather Frequency", f"How often weather changes: {', '.join(STRING_CHOICE_SETTINGS_CONFIG['weatherFrequency']['options'])}."), 
    7: (FACTOR_SETTINGS_CONFIG["shroudTimeFactor"]["path"], "Shroud Time", FACTOR_SETTINGS_CONFIG["shroudTimeFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['shroudTimeFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['shroudTimeFactor']['max_float']*100)}%."),
    8: (CURSE_MODIFIER_PATH, "Shroud Curse Modifier", f"Chance of Shroud curse: {', '.join(STRING_CHOICE_SETTINGS_CONFIG['curseModifier']['options'])}. Easy turns it off."), 
}
enemy_settings_menu_def = {
    1: (FACTOR_SETTINGS_CONFIG["enemyHealthFactor"]["path"], "Enemy Health", FACTOR_SETTINGS_CONFIG["enemyHealthFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['enemyHealthFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['enemyHealthFactor']['max_float']*100)}%."),
    2: (FACTOR_SETTINGS_CONFIG["enemyDamageFactor"]["path"], "Enemy Damage", FACTOR_SETTINGS_CONFIG["enemyDamageFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['enemyDamageFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['enemyDamageFactor']['max_float']*100)}%."),
    3: (FACTOR_SETTINGS_CONFIG["enemyStaminaFactor"]["path"], "Enemy Stun Modifier", FACTOR_SETTINGS_CONFIG["enemyStaminaFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['enemyStaminaFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['enemyStaminaFactor']['max_float']*100)}%."),
    4: (FACTOR_SETTINGS_CONFIG["enemyPerceptionRangeFactor"]["path"], "Enemy Perception", FACTOR_SETTINGS_CONFIG["enemyPerceptionRangeFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['enemyPerceptionRangeFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['enemyPerceptionRangeFactor']['max_float']*100)}%."),
    5: (FACTOR_SETTINGS_CONFIG["bossHealthFactor"]["path"], "Boss Health", FACTOR_SETTINGS_CONFIG["bossHealthFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['bossHealthFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['bossHealthFactor']['max_float']*100)}%."),
    6: (FACTOR_SETTINGS_CONFIG["bossDamageFactor"]["path"], "Boss Damage", FACTOR_SETTINGS_CONFIG["bossDamageFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['bossDamageFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['bossDamageFactor']['max_float']*100)}%."),
    7: (["gameSettings", "pacifyAllEnemies"], "Pacify All Enemies", "If true, enemies (not bosses) won't attack until provoked."),
    8: (FACTOR_SETTINGS_CONFIG["threatBonus"]["path"], "Enemy Attacks Modifier", FACTOR_SETTINGS_CONFIG["threatBonus"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['threatBonus']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['threatBonus']['max_float']*100)}%."),
    9: (RANDOM_SPAWNER_PATH, "Enemy Amount", f"Controls density of enemies: {', '.join(STRING_CHOICE_SETTINGS_CONFIG['randomSpawnerAmount']['options'])}."), 
    10: (AGGRO_POOL_PATH, "Simultaneous Enemy Attacks", f"How many enemies can attack at once: {', '.join(STRING_CHOICE_SETTINGS_CONFIG['aggroPoolAmount']['options'])}."), 
    11: (TAMING_STARTLE_PATH, "Taming Startle Repercussion", f"Penalty for startling creatures during taming: {', '.join(STRING_CHOICE_SETTINGS_CONFIG['tamingStartleRepercussion']['options'])}."), 
}
resource_settings_menu_def = {
    1: (FACTOR_SETTINGS_CONFIG["miningDamageFactor"]["path"], "Mining Effectiveness", FACTOR_SETTINGS_CONFIG["miningDamageFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['miningDamageFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['miningDamageFactor']['max_float']*100)}%."),
    2: (FACTOR_SETTINGS_CONFIG["plantGrowthSpeedFactor"]["path"], "Plant Growth Speed", FACTOR_SETTINGS_CONFIG["plantGrowthSpeedFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['plantGrowthSpeedFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['plantGrowthSpeedFactor']['max_float']*100)}%."),
    3: (FACTOR_SETTINGS_CONFIG["resourceDropStackAmountFactor"]["path"], "Resources Gain", FACTOR_SETTINGS_CONFIG["resourceDropStackAmountFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['resourceDropStackAmountFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['resourceDropStackAmountFactor']['max_float']*100)}%."),
    4: (FACTOR_SETTINGS_CONFIG["factoryProductionSpeedFactor"]["path"], "Workstation Effectiveness", FACTOR_SETTINGS_CONFIG["factoryProductionSpeedFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['factoryProductionSpeedFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['factoryProductionSpeedFactor']['max_float']*100)}%."),
    5: (FACTOR_SETTINGS_CONFIG["perkUpgradeRecyclingFactor"]["path"], "Weapon Recycling Yield", FACTOR_SETTINGS_CONFIG["perkUpgradeRecyclingFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['perkUpgradeRecyclingFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['perkUpgradeRecyclingFactor']['max_float']*100)}%."),
    6: (FACTOR_SETTINGS_CONFIG["perkCostFactor"]["path"], "Weapon Upgrading Costs", FACTOR_SETTINGS_CONFIG["perkCostFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['perkCostFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['perkCostFactor']['max_float']*100)}%."),
}
experience_settings_menu_def = {
    1: (FACTOR_SETTINGS_CONFIG["experienceCombatFactor"]["path"], "Combat Experience", FACTOR_SETTINGS_CONFIG["experienceCombatFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['experienceCombatFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['experienceCombatFactor']['max_float']*100)}%."),
    2: (FACTOR_SETTINGS_CONFIG["experienceMiningFactor"]["path"], "Mining Experience", FACTOR_SETTINGS_CONFIG["experienceMiningFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['experienceMiningFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['experienceMiningFactor']['max_float']*100)}%."),
    3: (FACTOR_SETTINGS_CONFIG["experienceExplorationQuestsFactor"]["path"], "Exploration/Quest XP", FACTOR_SETTINGS_CONFIG["experienceExplorationQuestsFactor"]["tooltip_hint"] + f" Range: {int(FACTOR_SETTINGS_CONFIG['experienceExplorationQuestsFactor']['min_float']*100)}-{int(FACTOR_SETTINGS_CONFIG['experienceExplorationQuestsFactor']['max_float']*100)}%."),
}
user_groups_settings_def_template = { 
    1: (["name"], "Group Name", "Identifier for this user group."),
    2: (["password"], "Password", "Password for this group. IMPORTANT: Change default passwords for security!"),
    3: (["canKickBan"], "Can Kick/Ban", "Allows group members to kick or ban other players."),
    4: (["canAccessInventories"], "Can Access Inventories", "Allows group members to access others' inventories/chests."),
    5: (["canEditBase"], "Can Edit Base", "Allows group members to modify player bases."),
    6: (["canExtendBase"], "Can Extend Base", "Allows group members to extend player bases."),
    7: (["reservedSlots"], "Reserved Slots", "Number of server slots reserved for this group."),
}

# --- Utility Functions ---
def log_message_gui(message, level="INFO", status_var=None):
    log_entry = f"[{level}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}"
    print(log_entry) 
    if status_var: status_var.set(message)

def nanoseconds_to_minutes_gui(ns):
    if not isinstance(ns, (int, float)) or ns < 0: return "N/A" 
    return int(ns // NANOSECONDS_PER_MINUTE)

def minutes_to_nanoseconds_gui(minutes_str):
    try:
        minutes = int(minutes_str)
        if minutes < 0: return None 
        return int(minutes * NANOSECONDS_PER_MINUTE)
    except ValueError: return None

def float_to_percent_str(f_val):
    if not isinstance(f_val, (int, float)): return "N/A"
    return str(int(round(f_val * 100)))

def percent_str_to_float(p_str):
    try:
        percent = float(p_str.rstrip('%')) 
        return round(percent / 100.0, 6) 
    except ValueError: return None

def get_setting_config_by_path(path_keys):
    for _, config in DURATION_SETTINGS_CONFIG.items():
        if config["path"] == path_keys: return "duration", config
    for _, config in STRING_CHOICE_SETTINGS_CONFIG.items():
        if config["path"] == path_keys: return "string_choice", config
    for _, config in FACTOR_SETTINGS_CONFIG.items():
        if config["path"] == path_keys: return "factor", config
    return None, None

# --- Tooltip Class ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None): # pylint: disable=unused-argument
        if not self.text or not self.text.strip(): return 
        x, y, _, _ = self.widget.bbox("insert") if isinstance(self.widget, (tk.Entry, ttk.Entry, tk.Text)) else self.widget.bbox()
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="lightyellow", relief="solid", borderwidth=1, wraplength=350, justify=tk.LEFT)
        label.pack(ipadx=2, ipady=2)

    def leave(self, event=None): # pylint: disable=unused-argument
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = None

# --- SettingsManager Class ---
class SettingsManager:
    def __init__(self, status_var=None):
        self.settings = {}
        self.game_version = FALLBACK_GAME_VERSION
        self.status_var = status_var
        self.readme_defaults = None
        self.initialize_or_update_settings_file()

    def _log(self, message, level="INFO"): log_message_gui(message, level, self.status_var)
    def _load_json(self, fp):
        try:
            with open(fp, "r", encoding="utf-8") as f: return json.load(f)
        except Exception as e: self._log(f"Error loading '{fp}': {e}", "ERROR"); return None
    def _save_json(self, data, fp):
        try:
            with open(fp, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)
            self._log(f"Successfully saved to '{fp}'."); return True
        except Exception as e: self._log(f"Error saving to '{fp}': {e}", "ERROR"); return False

    def _get_hardcoded_defaults(self):
        self._log("Using hardcoded fallback default settings.", "WARNING")
        defaults = {
            "name": "Enshrouded Server", "saveDirectory": "./savegame", "logDirectory": "./logs",
            "ip": "0.0.0.0", "queryPort": 15637, "slotCount": 16,
            "enableVoiceChat": False, "enableTextChat": False,
        }
        defaults["gameSettings"] = {}
        for key, conf in DURATION_SETTINGS_CONFIG.items():
            defaults["gameSettings"][key] = minutes_to_nanoseconds_gui(str(conf["normal_minutes"]))
        
        for key_conf_name, conf in STRING_CHOICE_SETTINGS_CONFIG.items():
            target_key = conf["path"][-1]
            if conf["path"][0] == "gameSettings": defaults["gameSettings"][target_key] = conf["normal"]
            else: defaults[target_key] = conf["normal"]
        
        for key_conf_name, conf in FACTOR_SETTINGS_CONFIG.items():
            target_key = conf["path"][-1]
            defaults["gameSettings"][target_key] = conf.get("normal_float", 1.0)

        defaults["userGroups"] = [
            {"name": "Admin", "password": "AdminPassword", "canKickBan": True, "canAccessInventories": True, "canEditBase": True, "canExtendBase": True, "reservedSlots": 0},
            {"name": "Friend", "password": "FriendPassword", "canKickBan": False, "canAccessInventories": True, "canEditBase": True, "canExtendBase": False, "reservedSlots": 0},
            {"name": "Guest", "password": "GuestPassword", "canKickBan": False, "canAccessInventories": False, "canEditBase": False, "canExtendBase": False, "reservedSlots": 0}
        ]
        return defaults

    def parse_readme(self): 
        try:
            with open(README_FILE, "r", encoding="utf-8") as f: readme_content = f.read()
        except Exception as e: self._log(f"Error reading readme: {e}", "ERROR"); return None, FALLBACK_GAME_VERSION
        version = FALLBACK_GAME_VERSION
        v_match = re.search(r"^Version:\s*(\S+)", readme_content, re.MULTILINE)
        if v_match: version = v_match.group(1)
        json_match = re.search(r"DEFAULT enshrouded_server\.json(?: / VERSION \S+)?\s*(\{[\s\S]*?\n\})", readme_content, re.MULTILINE)
        if json_match:
            try: return json.loads(json_match.group(1)), version
            except json.JSONDecodeError as e: self._log(f"Error decoding JSON from readme: {e}", "ERROR"); return None, version
        self._log("Could not find default JSON block in readme.", "WARNING"); return None, version
    
    def _recursive_merge(self, default, existing):
        for key, val in default.items():
            if key not in existing: existing[key] = val
            elif isinstance(val, dict) and isinstance(existing.get(key), dict): self._recursive_merge(val, existing[key])

    def _find_structural_differences(self, current, default, path=""):
        diffs = []
        for k, v_curr in current.items():
            p = f"{path}.{k}" if path else k
            if k not in default:
                diffs.append(f"Obsolete/Custom Key: '{p}'")
            elif isinstance(v_curr, dict) and isinstance(default.get(k), dict):
                diffs.extend(self._find_structural_differences(v_curr, default[k], p))
            elif default.get(k) is not None and type(v_curr) != type(default[k]):
                if not (isinstance(v_curr, (int, float)) and isinstance(default[k], (int, float))):
                    diffs.append(f"Type Mismatch: '{p}' (User: {type(v_curr).__name__}, Default: {type(default[k]).__name__})")
        return diffs

    def initialize_or_update_settings_file(self):
        self.readme_defaults, self.game_version = self.parse_readme()
        if self.readme_defaults is None:
            self.readme_defaults = self._get_hardcoded_defaults()

        if not os.path.exists(JSON_FILE):
            self._log(f"'{JSON_FILE}' not found. Creating with defaults.")
            if self._save_json(self.readme_defaults, JSON_FILE):
                self.settings = json.loads(json.dumps(self.readme_defaults))
            else:
                self._log("Failed to create default config. Exiting.", "FATAL")
                messagebox.showerror("Fatal Error", "Could not create default configuration file. Exiting.")
                sys.exit(1)
            return

        existing_settings = self._load_json(JSON_FILE)
        if existing_settings is None: 
            self._log(f"Could not load '{JSON_FILE}'. It might be corrupted.", "WARNING")
            if messagebox.askyesno("Corrupted File", f"Could not load '{JSON_FILE}'. Replace with defaults?"):
                self.backup_file(JSON_FILE, reason="corrupted_original_gui")
                if self._save_json(self.readme_defaults, JSON_FILE):
                    self.settings = json.loads(json.dumps(self.readme_defaults))
                    self._log("Replaced corrupted file with defaults.")
                else: messagebox.showerror("Error", "Failed to replace corrupted file."); sys.exit(1)
            else: messagebox.showinfo("Exiting", f"Please check '{JSON_FILE}' manually."); sys.exit(1)
            return
        
        original_existing_settings_copy = json.loads(json.dumps(existing_settings)) # For accurate comparison after merge
        merged_settings = json.loads(json.dumps(existing_settings)) 
        self._recursive_merge(self.readme_defaults, merged_settings) 

        diffs = self._find_structural_differences(original_existing_settings_copy, self.readme_defaults) 
        new_keys_added = (merged_settings != original_existing_settings_copy)

        if diffs or new_keys_added:
            if diffs : # Structural issues found in user's config compared to overlapping parts of default
                title = "Configuration Notice"
                msg = "Please note: Some differences were found between your current configuration and the application's default template:\n\n" + \
                      "\n".join(f"- {d}" for d in diffs) + \
                      "\n\nThis can happen if your file contains older settings, custom additions, or if a setting's expected type has changed in the template." + \
                      "\nNew settings from the template (if any) have been merged. Your values for existing settings are preserved." + \
                      "\nIt's recommended to review your settings, especially those listed above."
                messagebox.showwarning(title, msg)
            elif new_keys_added: # Only new keys added, no other diffs
                title = "Configuration Updated"
                msg = "Your configuration has been updated with new default settings from the latest template. " + \
                      "Your existing customizations have been preserved. You may want to review new options available."
                messagebox.showinfo(title, msg)
            
            if new_keys_added: # If merge resulted in changes (even if no "diffs" were found, e.g. adding brand new keys)
                if self._save_json(merged_settings, JSON_FILE):
                    self.settings = merged_settings
                    self._log("Configuration updated and merged with new defaults.")
                else: 
                    self.settings = original_existing_settings_copy
                    self._log("Failed to save merged configuration. Using original settings.", "ERROR")
            else: # No changes from merge, but there might have been structural diffs reported
                self.settings = original_existing_settings_copy
        else: # No structural diffs and no changes from merge
            self.settings = existing_settings
        self._log(f"Settings loaded. Detected game version: {self.game_version}")

    def get_setting_value(self, path_keys, default_value=None, target_dict=None):
        val = target_dict if target_dict is not None else self.settings
        try:
            for key in path_keys:
                if isinstance(val, list) and isinstance(key, int):
                    if 0 <= key < len(val): val = val[key]
                    else: return default_value 
                elif isinstance(val, dict): val = val[key] 
                else: return default_value 
            return val
        except (KeyError, IndexError, TypeError): return default_value

    def set_setting_value(self, path_keys, new_value, target_dict=None):
        s = target_dict if target_dict is not None else self.settings
        for i, key in enumerate(path_keys[:-1]):
            if isinstance(key, int): 
                while len(s) <= key: s.append({}) 
                if not isinstance(s[key], (dict, list)): s[key] = {} 
                s = s[key]
            else: 
                if key not in s or not isinstance(s[key], (dict, list)):
                    next_key_is_int = i + 1 < len(path_keys) and isinstance(path_keys[i+1], int)
                    s[key] = [] if next_key_is_int else {}
                s = s[key]
        last_key = path_keys[-1]
        if isinstance(last_key, int):
             while len(s) <= last_key: s.append(None) 
             s[last_key] = new_value
        else: s[last_key] = new_value

    def save_all_settings(self):
        if self.backup_file(JSON_FILE, reason="before_gui_save"):
            if self._save_json(self.settings, JSON_FILE):
                self._log("All settings saved successfully."); messagebox.showinfo("Save", "Settings saved successfully!"); return True
            else: messagebox.showerror("Save Error", "Failed to save settings to file.")
        else: 
            if messagebox.askyesno("Backup Failed", "Backup failed. Still save changes?"):
                 if self._save_json(self.settings, JSON_FILE):
                    self._log("All settings saved (backup failed)."); messagebox.showwarning("Save", "Settings saved, but backup failed."); return True
                 else: messagebox.showerror("Save Error", "Failed to save settings to file.")
            else: self._log("Save cancelled due to failed backup.")
        return False

    def backup_file(self, file_to_backup, reason=""):
        if not os.path.exists(file_to_backup): self._log(f"File '{file_to_backup}' not found. Nothing to backup.", "INFO"); return False
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            rs = f"_{reason.replace(' ', '_')}" if reason else ""
            base, _ = os.path.splitext(os.path.basename(file_to_backup))
            backup_filename = f"{base}_{ts}{rs}.old" 
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
            shutil.copy2(file_to_backup, backup_path)
            self._log(f"File '{file_to_backup}' backed up to '{backup_path}'."); return backup_path
        except Exception as e: self._log(f"Backup failed for '{file_to_backup}': {e}", "ERROR"); return False

    def revert_to_defaults_from_readme(self):
        if not self.readme_defaults: self._log("No readme defaults available.", "ERROR"); messagebox.showerror("Error", "Readme defaults not available."); return False
        msg = f"Replace current settings with defaults from Readme (Version: {self.game_version})?\nA backup will be made."
        if messagebox.askyesno("Revert to Defaults", msg):
            if self.backup_file(JSON_FILE, reason="before_revert_to_readme_defaults"):
                defaults_copy = json.loads(json.dumps(self.readme_defaults))
                if self._save_json(defaults_copy, JSON_FILE):
                    self.settings = defaults_copy 
                    self._log("Settings reverted to Readme defaults."); messagebox.showinfo("Success", "Settings reverted."); return True
                else: messagebox.showerror("Error", "Failed to save reverted settings.")
            else: messagebox.showwarning("Backup Failed", "Revert cancelled: backup failed.")
        return False

    def list_backup_files(self):
        if not os.path.exists(BACKUP_DIR): return []
        backups = []
        try:
            for fname in os.listdir(BACKUP_DIR):
                if fname.startswith(os.path.splitext(JSON_FILE)[0]) and fname.endswith(".old"):
                    match = re.search(r'_(\d{8}_\d{6})', fname); dt = datetime.min
                    if match:
                        try: dt = datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
                        except ValueError: 
                            try: dt = datetime.fromtimestamp(os.path.getmtime(os.path.join(BACKUP_DIR, fname)))
                            except: pass 
                    else: 
                        try: dt = datetime.fromtimestamp(os.path.getmtime(os.path.join(BACKUP_DIR, fname)))
                        except: pass 
                    backups.append((fname, dt))
            backups.sort(key=lambda item: item[1], reverse=True)
            return backups
        except Exception as e: self._log(f"Error listing backups: {e}", "ERROR"); return []

    def restore_from_backup_file(self, backup_filename):
        backup_filepath = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_filepath): self._log(f"Backup file '{backup_filename}' not found.", "ERROR"); messagebox.showerror("Error", f"Backup file '{backup_filename}' not found."); return False
        reason_suffix = f"before_restoring_{os.path.splitext(backup_filename)[0]}"
        if self.backup_file(JSON_FILE, reason=reason_suffix):
            try:
                shutil.copy2(backup_filepath, JSON_FILE)
                restored = self._load_json(JSON_FILE)
                if restored:
                    self.settings = restored
                    self._log(f"Restored '{backup_filename}'."); messagebox.showinfo("Restore Success", f"Restored from '{backup_filename}'."); return True
                else: messagebox.showerror("Restore Error", "Failed to load settings after restoring.")
            except Exception as e: self._log(f"Error restoring: {e}", "ERROR"); messagebox.showerror("Restore Error", f"Failed: {e}")
        else: messagebox.showwarning("Backup Failed", "Restore cancelled: backup of current settings failed.")
        return False
    
    def add_user_group(self):
        if 'userGroups' not in self.settings or not isinstance(self.settings['userGroups'], list):
            self.settings['userGroups'] = [] 
        
        new_group_name = f"NewGroup{len(self.settings['userGroups']) + 1}"
        new_group = { 
            "name": new_group_name, "password": "Password",
            "canKickBan": False, "canAccessInventories": False,
            "canEditBase": False, "canExtendBase": False, "reservedSlots": 0
        }
        self.settings['userGroups'].append(new_group)
        self._log(f"Added new user group placeholder: {new_group_name}")
        return True 

    def delete_user_group(self, group_index):
        user_groups = self.settings.get('userGroups', [])
        if isinstance(user_groups, list) and 0 <= group_index < len(user_groups):
            group_name = user_groups[group_index].get('name', f"Group at index {group_index}")
            if messagebox.askyesno("Delete Group", f"Are you sure you want to delete group: '{group_name}'?"):
                del user_groups[group_index] 
                self._log(f"Deleted user group: {group_name}")
                return True 
        else:
            self._log(f"Failed to delete user group at index {group_index}. Invalid index or data.", "ERROR")
            messagebox.showerror("Error", "Could not delete group. Invalid index or data.")
        return False


# --- Tkinter GUI Application ---
class EnshroudedConfigEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE_BASE)
        self.settings_changed = False 
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing) 


        try:
            self.style = ttk.Style(); available_themes = self.style.theme_names()
            if "clam" in available_themes: self.style.theme_use("clam")
            elif "alt" in available_themes: self.style.theme_use("alt")
        except tk.TclError: print("TTK themes not fully available.")

        self.status_var = tk.StringVar()
        self.settings_manager = SettingsManager(status_var=self.status_var)
        self.update_title() 

        self.tk_vars = {}; self.path_to_description_map = {}
        self.tab_preset_labels = {} 

        self._create_menu()
        self._create_notebook_with_tabs() 
        self._create_status_bar()
        self._create_action_buttons()
        self.load_settings_into_gui() 
        self.status_var.set(f"Settings loaded. Game Version: {self.settings_manager.game_version}")
        self.settings_changed = False 
        self.update_title()


    def _on_closing(self):
        if self.settings_changed:
            response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Save before exiting?")
            if response is True: 
                if self.save_all_gui_settings(): self.root.destroy()
            elif response is False: self.root.destroy()
        else: self.root.destroy()

    def mark_settings_changed(self, event=None, path_keys_modified=None): 
        if not self.settings_changed:
            self.settings_changed = True
            self.update_title()
        
        # If a gameSetting is changed (i.e., path_keys_modified starts with "gameSettings"),
        # and preset is not "Custom", set it to "Custom"
        if path_keys_modified and len(path_keys_modified) > 0 and path_keys_modified[0] == "gameSettings":
            preset_path_str = ".".join(GAME_PRESET_PATH)
            preset_var = self.tk_vars.get(preset_path_str)
            if preset_var and preset_var.get() != "Custom":
                preset_var.set("Custom") # This will trigger its own trace and call on_preset_changed
                self.settings_manager._log("Individual game setting changed, preset automatically set to 'Custom'.", "INFO")
                # No need to call self.on_preset_changed() directly if the Combobox trace does it.
                # However, if other widgets change gameSettings, a direct call might be needed,
                # or ensure their trace also considers this.
                # For safety, explicitly update the label visibility based on the new "Custom" state.
                self.on_preset_changed() 


    def update_title(self):
        title = f"{APP_TITLE_BASE} - v{self.settings_manager.game_version}"
        if self.settings_changed: title += " *"
        self.root.title(title)

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save Settings", command=self.save_all_gui_settings)
        filemenu.add_separator(); filemenu.add_command(label="Exit", command=self._on_closing) 
        menubar.add_cascade(label="File", menu=filemenu)
        actionmenu = tk.Menu(menubar, tearoff=0)
        actionmenu.add_command(label="Load Defaults (from Readme)", command=self.load_defaults_gui)
        actionmenu.add_command(label="Manual Backup Current Settings", command=self.manual_backup_gui)
        actionmenu.add_command(label="Restore Specific Backup...", command=self.restore_backup_gui)
        menubar.add_cascade(label="Actions", menu=actionmenu)
        self.root.config(menu=menubar)

    def _refresh_notebook_and_vars(self):
        if hasattr(self, 'notebook') and self.notebook.winfo_exists(): self.notebook.destroy()
        self.tk_vars.clear(); self.path_to_description_map.clear(); self.tab_preset_labels.clear()
        self._create_notebook_with_tabs() 
        self.load_settings_into_gui() 
        self.settings_changed = False; self.update_title() 

    def _create_notebook_with_tabs(self): 
        if hasattr(self, 'notebook') and self.notebook.winfo_exists(): pass 
        else: self.notebook = ttk.Notebook(self.root); self.notebook.pack(expand=True, fill="both", padx=10, pady=5)
        
        if hasattr(self, 'notebook') and self.notebook.winfo_exists():
            for i in reversed(range(len(self.notebook.tabs()))): self.notebook.forget(i)
        self.tk_vars.clear(); self.path_to_description_map.clear(); self.tab_preset_labels.clear()


        self.tabs_config = {
            "General": general_settings_menu_def, "Player": player_settings_menu_def,
            "World": world_settings_menu_def, "Enemy": enemy_settings_menu_def,
            "Resources": resource_settings_menu_def, "Experience": experience_settings_menu_def,
            "Server Roles": "user_groups_tab" 
        }
        for tab_name, menu_def in self.tabs_config.items():
            tab_frame_container = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(tab_frame_container, text=tab_name)
            
            # Add Preset Override Warning Label placeholder to relevant tabs
            if tab_name in ["Player", "World", "Enemy", "Resources", "Experience"]:
                preset_label = ttk.Label(tab_frame_container, text="", foreground="blue", font=('TkDefaultFont', 9, 'italic'))
                preset_label.pack(pady=(0,5), anchor="nw", fill="x") # Fill x to allow text to wrap
                self.tab_preset_labels[tab_name] = preset_label 

                random_btn = ttk.Button(tab_frame_container, text=f"Randomize Settings on This Tab", 
                                        command=lambda tn=tab_name, md=menu_def: self._randomize_tab_settings(tn, md))
                random_btn.pack(pady=(0,10), anchor="nw") 

            if menu_def == "user_groups_tab": self._populate_user_groups_tab(tab_frame_container) 
            else: self._populate_tab(tab_frame_container, menu_def) 
        
        self.on_preset_changed() # Call after all tabs and their labels are created


    def on_preset_changed(self, event=None): 
        preset_path_str = ".".join(GAME_PRESET_PATH)
        preset_var = self.tk_vars.get(preset_path_str)

        if not preset_var: return # Should not happen if GUI is built correctly

        is_custom = preset_var.get() == "Custom"
        
        for tab_name_iter, label_widget in self.tab_preset_labels.items():
            if label_widget and label_widget.winfo_exists(): 
                if not is_custom:
                    label_widget.config(text="Info: Individual game settings might be overridden by the selected preset if not 'Custom'.")
                else:
                    label_widget.config(text="") 
        
        # Only mark as changed if it's a user interaction (event is not None)
        # or if explicitly called after an automatic change.
        if event is not None or (event is None and self.settings_changed is False) : # Avoid re-triggering if already marked by another setting
             self.mark_settings_changed(path_keys_modified=GAME_PRESET_PATH)



    def _create_scrollable_frame(self, parent):
        canvas = tk.Canvas(parent); scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
        return scrollable_frame

    def _populate_tab(self, parent_tab_frame, menu_def): 
        
        # Find first non-button child to determine where to insert scrollable frame
        insert_after_widget = None
        for child in parent_tab_frame.winfo_children():
            if not isinstance(child, tk.Canvas): # Assuming buttons/labels are packed before canvas
                insert_after_widget = child
            else: # Found canvas, clear it for repopulation
                child.destroy() 
                break
        
        content_frame = self._create_scrollable_frame(parent_tab_frame) 
        if insert_after_widget:
            content_frame.master.pack_configure(after=insert_after_widget) # Pack canvas after existing buttons/labels
        
        row_idx = 0

        for _, (path_keys, label_text, tooltip_text) in sorted(menu_def.items()): 
            path_str = ".".join(map(str, path_keys))
            self.path_to_description_map[path_str] = label_text 
            
            setting_type, specific_config = get_setting_config_by_path(path_keys)
            current_value = self.settings_manager.get_setting_value(path_keys)
            desc_hint = tooltip_text.lower() # Use tooltip for hints now

            label_widget = ttk.Label(content_frame, text=label_text + ":")
            label_widget.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
            ToolTip(label_widget, tooltip_text)


            widget_frame = ttk.Frame(content_frame)
            widget_frame.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
            content_frame.grid_columnconfigure(1, weight=1)
            
            var = None
            widget_for_binding = None

            if "(path)" in desc_hint: 
                var = tk.StringVar(); entry = ttk.Entry(widget_frame, textvariable=var, width=35)
                entry.pack(side="left", fill="x", expand=True); widget_for_binding = entry
                ttk.Button(widget_frame, text="Browse...", command=lambda v=var: self._browse_directory(v)).pack(side="left", padx=(5,0))
            elif setting_type == "string_choice" and specific_config:
                var = tk.StringVar(); 
                cb = ttk.Combobox(widget_frame, textvariable=var, values=specific_config["options"], state="readonly", width=33)
                cb.pack(side="left", fill="x", expand=True); widget_for_binding = cb
                if path_keys == GAME_PRESET_PATH: 
                    cb.bind("<<ComboboxSelected>>", self.on_preset_changed)

            elif setting_type == "factor" and specific_config:
                var = tk.StringVar() 
                entry = ttk.Entry(widget_frame, textvariable=var, width=10) 
                entry.pack(side="left"); widget_for_binding = entry
                ttk.Label(widget_frame, text=f"% (Range: {int(specific_config['min_float']*100)}-{int(specific_config['max_float']*100)}%)").pack(side="left", padx=(3,0))
            elif "true/false" in desc_hint:
                var = tk.BooleanVar(); cb = ttk.Checkbutton(widget_frame, variable=var); cb.pack(side="left"); widget_for_binding = cb
            elif "integer" in desc_hint or setting_type == "duration" or "float" in desc_hint: 
                var = tk.StringVar(); entry = ttk.Entry(widget_frame, textvariable=var, width=35)
                entry.pack(side="left", fill="x", expand=True); widget_for_binding = entry
            elif "string" in desc_hint or isinstance(current_value, str) or current_value is None:
                var = tk.StringVar(); entry = ttk.Entry(widget_frame, textvariable=var, width=35)
                entry.pack(side="left", fill="x", expand=True); widget_for_binding = entry
            else: 
                var = tk.StringVar(); var.set(str(current_value)[:50]); 
                entry = ttk.Entry(widget_frame, textvariable=var, state="readonly", width=35)
                entry.pack(side="left", fill="x", expand=True) 
            
            if var: self.tk_vars[path_str] = var
            if widget_for_binding and path_keys != GAME_PRESET_PATH: 
                # If it's a gameSetting, mark_settings_changed will handle preset switch
                is_game_setting = path_keys[0] == "gameSettings"
                
                if isinstance(widget_for_binding, ttk.Checkbutton):
                    widget_for_binding.config(command=lambda pk=path_keys: self.mark_settings_changed(path_keys_modified=pk))
                else: 
                    var.trace_add("write", lambda n,i,m,pk=path_keys,v=var: self.mark_settings_changed(path_keys_modified=pk) if hasattr(v, 'get') and v.get() is not None else None)
            row_idx += 1
    
    def _populate_user_groups_tab(self, parent_tab_frame): 
        for widget in parent_tab_frame.winfo_children(): widget.destroy()

        add_group_button = ttk.Button(parent_tab_frame, text="Add New User Group", command=self.add_new_user_group_gui)
        add_group_button.pack(pady=(0,10), anchor="nw") 
        
        content_frame = self._create_scrollable_frame(parent_tab_frame)
        user_groups = self.settings_manager.get_setting_value(["userGroups"], [])
        if not isinstance(user_groups, list):
            ttk.Label(content_frame, text="Error: userGroups is not a list.").pack(); return

        for group_idx, group_data in enumerate(user_groups):
            if not isinstance(group_data, dict): self.settings_manager._log(f"Skipping invalid group at index {group_idx}.", "WARNING"); continue
            
            group_frame_outer = ttk.Frame(content_frame) 
            group_frame_outer.pack(fill="x", expand=True, pady=5)

            group_lf_text = f"Group: {group_data.get('name', f'Group {group_idx+1}')}"
            group_lf = ttk.LabelFrame(group_frame_outer, text=group_lf_text, padding="10")
            group_lf.pack(side="left", fill="x", expand=True)

            del_btn = ttk.Button(group_frame_outer, text="Delete Group", command=lambda idx=group_idx: self.delete_user_group_gui(idx))
            del_btn.pack(side="right", padx=(5,0), anchor="ne")
            ToolTip(del_btn, "Delete this entire user group.")


            row_idx = 0
            for _, (sub_path, label_text, tooltip_text) in sorted(user_groups_settings_def_template.items()):
                full_path = ["userGroups", group_idx] + sub_path
                path_str = ".".join(map(str, full_path))
                
                final_tooltip = tooltip_text
                if sub_path == ["password"]: 
                    final_tooltip += "\n\nReminder: Change default passwords for security!"

                self.path_to_description_map[path_str] = label_text 
                
                label_widget = ttk.Label(group_lf, text=label_text + ":")
                label_widget.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
                ToolTip(label_widget, final_tooltip)
                
                widget_frame = ttk.Frame(group_lf)
                widget_frame.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3); group_lf.grid_columnconfigure(1, weight=1)
                
                var = None; widget_for_binding = None
                if "true/false" in tooltip_text.lower(): 
                    var = tk.BooleanVar(); cb = ttk.Checkbutton(widget_frame, variable=var); cb.pack(side="left"); widget_for_binding = cb
                else: 
                    var = tk.StringVar(); entry = ttk.Entry(widget_frame, textvariable=var, width=30); entry.pack(side="left", fill="x", expand=True); widget_for_binding = entry
                
                if var: self.tk_vars[path_str] = var
                if widget_for_binding:
                    if isinstance(widget_for_binding, ttk.Checkbutton):
                        widget_for_binding.config(command=lambda pk=full_path: self.mark_settings_changed(path_keys_modified=pk))
                    else:
                        var.trace_add("write", lambda n,i,m,pk=full_path,v=var: self.mark_settings_changed(path_keys_modified=pk) if hasattr(v,'get') and v.get() is not None else None)

                row_idx += 1
    
    def add_new_user_group_gui(self):
        if self.settings_manager.add_user_group():
            self._refresh_notebook_and_vars() 
            for i in range(len(self.notebook.tabs())): 
                if self.notebook.tab(i, "text") == "Server Roles": self.notebook.select(i); break
            self.status_var.set("New user group added. Configure and save."); self.mark_settings_changed()

    def delete_user_group_gui(self, group_index):
        if self.settings_manager.delete_user_group(group_index):
            self._refresh_notebook_and_vars() 
            for i in range(len(self.notebook.tabs())): 
                if self.notebook.tab(i, "text") == "Server Roles": self.notebook.select(i); break
            self.status_var.set("User group deleted. Save settings to make permanent."); self.mark_settings_changed()

    def _browse_directory(self, tk_var): directory = filedialog.askdirectory();_ = tk_var.set(directory) if directory else None; self.mark_settings_changed()
    def _create_status_bar(self): ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w").pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)
    def _create_action_buttons(self):
        bf = ttk.Frame(self.root, padding="5"); bf.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(bf, text="Save All Settings", command=self.save_all_gui_settings).pack(side=tk.RIGHT, padx=5)

    def load_settings_into_gui(self):
        for path_str, tk_var in self.tk_vars.items():
            path_keys = [int(p) if p.isdigit() else p for p in path_str.split('.')]
            value = self.settings_manager.get_setting_value(path_keys)
            setting_type, specific_config = get_setting_config_by_path(path_keys)
            try:
                if setting_type == "duration" and isinstance(value, (int, float)): tk_var.set(str(nanoseconds_to_minutes_gui(value)))
                elif setting_type == "factor" and isinstance(value, (int, float)): tk_var.set(float_to_percent_str(value))
                elif isinstance(tk_var, tk.BooleanVar): tk_var.set(bool(value) if value is not None else False)
                else: tk_var.set(str(value) if value is not None else "") 
            except Exception as e:
                self.settings_manager._log(f"Error loading {path_str} into GUI: {value} ({type(value)}). Err: {e}", "ERROR")
                if isinstance(tk_var, tk.StringVar): tk_var.set("") 
                elif isinstance(tk_var, tk.BooleanVar): tk_var.set(False)
        
        self.on_preset_changed() 
        self.settings_changed = False 
        self.update_title()
        self.status_var.set(f"Settings loaded. Game Version: {self.settings_manager.game_version}")


    def save_all_gui_settings(self):
        self.status_var.set("Saving settings...")
        for path_str, tk_var in self.tk_vars.items():
            path_keys = [int(p) if p.isdigit() else p for p in path_str.split('.')]
            gui_val_str = str(tk_var.get()) 
            desc_label = self.path_to_description_map.get(path_str, "") 
            tooltip_text_for_type_hint = "" # Get the full tooltip for type hints
            for menu_collection in [general_settings_menu_def, player_settings_menu_def, world_settings_menu_def, enemy_settings_menu_def, resource_settings_menu_def, experience_settings_menu_def]:
                for _, item_tuple_val in menu_collection.items():
                    if item_tuple_val[0] == path_keys: tooltip_for_type_hint = item_tuple_val[2].lower(); break
                if tooltip_for_type_hint: break
            if not tooltip_for_type_hint and path_keys[0] == "userGroups":
                 for _, item_tuple_val in user_groups_settings_def_template.items():
                     if item_tuple_val[0] == path_keys[2:]: tooltip_for_type_hint = item_tuple_val[2].lower(); break


            setting_type, specific_config = get_setting_config_by_path(path_keys)
            final_value = None
            try:
                if setting_type == "duration":
                    if not gui_val_str.strip(): messagebox.showerror("Input Error", f"Minutes for {desc_label} empty."); return
                    final_value = minutes_to_nanoseconds_gui(gui_val_str)
                    if final_value is None: messagebox.showerror("Input Error", f"Invalid minutes for {desc_label}: '{gui_val_str}'."); return
                    mins = int(gui_val_str)
                    if not (specific_config["min_minutes"] <= mins <= specific_config["max_minutes"]):
                        messagebox.showerror("Input Error", f"{desc_label} ({mins} min) out of range."); return
                elif setting_type == "factor":
                    if not gui_val_str.strip(): messagebox.showerror("Input Error", f"Percentage for {desc_label} empty."); return
                    final_value = percent_str_to_float(gui_val_str)
                    if final_value is None: messagebox.showerror("Input Error", f"Invalid percent for {desc_label}: '{gui_val_str}'."); return
                    min_p, max_p = int(specific_config['min_float']*100), int(specific_config['max_float']*100)
                    if not (specific_config["min_float"] <= final_value <= specific_config["max_float"]): 
                        messagebox.showerror("Input Error", f"{desc_label} ({gui_val_str}%) out of range ({min_p}%-{max_p}%)."); return
                elif isinstance(tk_var, tk.BooleanVar): final_value = bool(tk_var.get()) 
                elif "integer" in tooltip_for_type_hint: final_value = int(gui_val_str) if gui_val_str.strip() else 0 
                elif "float" in tooltip_for_type_hint: final_value = float(gui_val_str) if gui_val_str.strip() else 0.0
                else: final_value = gui_val_str 
                self.settings_manager.set_setting_value(path_keys, final_value)
            except ValueError as e: messagebox.showerror("Input Error", f"Invalid value for {desc_label}: '{gui_val_str}'. Error: {e}"); return
            except Exception as e: messagebox.showerror("Error", f"Processing {desc_label}: {e}"); return
        
        if self.settings_manager.save_all_settings(): 
            self.settings_changed = False; self.update_title()
            self.status_var.set(f"Settings saved! Version: {self.settings_manager.game_version}")
        
    def _randomize_tab_settings(self, tab_name, menu_def):
        self.status_var.set(f"Randomizing settings for {tab_name} tab...")
        randomized_settings_for_assessment = {}

        for _, (path_keys, _, tooltip_text) in sorted(menu_def.items()): # Use tooltip for hints
            path_str = ".".join(map(str, path_keys))
            tk_var = self.tk_vars.get(path_str)
            if not tk_var: continue 

            setting_type, specific_config = get_setting_config_by_path(path_keys)
            original_value_for_assessment = self.settings_manager.get_setting_value(path_keys) 
            
            if path_keys == ["name"] or path_keys == ["saveDirectory"] or \
               path_keys == ["logDirectory"] or path_keys == ["ip"] or \
               path_keys == ["queryPort"]:
                randomized_settings_for_assessment[path_str] = original_value_for_assessment
                continue

            new_value_for_gui = None; actual_new_value = None

            if setting_type == "duration" and specific_config:
                rand_minutes = random.randint(specific_config["min_minutes"], specific_config["max_minutes"])
                new_value_for_gui = str(rand_minutes)
                actual_new_value = minutes_to_nanoseconds_gui(str(rand_minutes))
            elif setting_type == "factor" and specific_config:
                val_range = specific_config["max_float"] - specific_config["min_float"]
                inset = val_range * 0.1 
                rand_min = specific_config["min_float"] + (random.random() * inset)
                rand_max = specific_config["max_float"] - (random.random() * inset)
                if rand_min >= rand_max: 
                    rand_min = specific_config["min_float"]
                    rand_max = specific_config["max_float"]
                rand_float = random.uniform(rand_min, rand_max)
                rand_float = max(specific_config["min_float"], min(specific_config["max_float"], rand_float))
                new_value_for_gui = float_to_percent_str(rand_float)
                actual_new_value = round(rand_float, 6)
            elif setting_type == "string_choice" and specific_config:
                chosen_option = random.choice(specific_config["options"])
                new_value_for_gui = chosen_option; actual_new_value = chosen_option
            elif "true/false" in tooltip_text.lower(): 
                chosen_bool = random.choice([True, False])
                new_value_for_gui = chosen_bool; actual_new_value = chosen_bool
            elif path_keys == ["slotCount"]: 
                actual_new_value = random.randint(1, 16); new_value_for_gui = str(actual_new_value)
            else:
                randomized_settings_for_assessment[path_str] = original_value_for_assessment
                continue 

            if new_value_for_gui is not None:
                tk_var.set(new_value_for_gui)
                randomized_settings_for_assessment[path_str] = actual_new_value
                self.mark_settings_changed(path_keys_modified=path_keys) 
            else: 
                randomized_settings_for_assessment[path_str] = original_value_for_assessment
        
        self._assess_and_warn_difficulty(tab_name, randomized_settings_for_assessment)
        self.status_var.set(f"Settings for {tab_name} randomized. Review and Save.")

    def _assess_and_warn_difficulty(self, tab_name, randomized_values_map):
        if not self.settings_manager.readme_defaults: self.settings_manager._log("Cannot assess: readme_defaults NA.", "WARNING"); return
        normal_settings = self.settings_manager.readme_defaults
        hard_indicators = []; total_impact_score = 0;
        DIFFICULTY_THRESHOLD = 3 

        for path_str, rand_val in randomized_values_map.items():
            path_keys = [int(p) if p.isdigit() else p for p in path_str.split('.')]
            normal_val = self.settings_manager.get_setting_value(path_keys, target_dict=normal_settings) 
            if normal_val is None: continue 

            setting_type, specific_config = get_setting_config_by_path(path_keys)
            impact_score = 0 # Default to neutral

            if setting_type == "factor" and specific_config:
                normal_float = specific_config.get("normal_float", 1.0) # Default normal if not specified
                current_impact = specific_config.get("impact_score_hard", 0) # How much this setting matters

                # If it's a beneficial factor (higher is better for player, or lower is better for enemy stats)
                # A significantly lower random value makes it harder
                if ("player" in path_keys[-1].lower() or "experience" in path_keys[-1].lower() or \
                    "resource" in path_keys[-1].lower() or "shroudTime" in path_keys[-1].lower()) and \
                   not ("cost" in path_keys[-1].lower()): # Higher is good
                    if rand_val < normal_float * 0.60: impact_score = current_impact # current_impact is likely negative
                # If it's a detrimental factor (higher makes game harder for player, like enemy stats)
                elif ("enemy" in path_keys[-1].lower() or "boss" in path_keys[-1].lower() or \
                      "cost" in path_keys[-1].lower()): # Higher is bad
                    if rand_val > normal_float * 1.60: impact_score = current_impact # current_impact is likely positive
            
            elif path_keys == ["gameSettings", "enableStarvingDebuff"] and rand_val is True and normal_val is False: impact_score = 2
            elif path_keys == TOMBSTONE_MODE_PATH and rand_val == "Everything" and normal_val != "Everything": impact_score = 1
            
            if impact_score != 0: # Only add if there's a notable impact
                # For beneficial factors, impact_score_hard is negative. We want to sum absolute difficulties or signed difficulties.
                # If impact_score_hard is negative (player buff), and rand_val is low, this contributes to "harder".
                # If impact_score_hard is positive (enemy buff), and rand_val is high, this contributes to "harder".
                # The current logic `impact_score = current_impact` is okay if current_impact is signed correctly.
                 hard_indicators.append(f"{path_keys[-1].replace('Factor','').replace('Modifier','')} significantly changed (Impact: {impact_score})")
                 total_impact_score += impact_score # Sum signed impacts
        
        # We need to define if positive or negative total_impact_score means harder.
        # Let's assume positive impact_score_hard in FACTOR_SETTINGS_CONFIG means "makes game harder if this factor is high" (e.g. enemy damage)
        # And negative impact_score_hard means "makes game harder if this factor is low" (e.g. player health)
        # So, a large positive total_impact_score means harder. Or a large negative one. Let's use absolute value for thresholding.
        
        # Simplified: if any "hard_indicator" was triggered and total_impact_score (sum of signed values) is e.g. positive and high, or negative and low.
        # For now, let's use a simple threshold for the sum of the "hard-making" direction of impact.
        # If player health impact is -2, and it got triggered, score is -2.
        # If enemy health impact is +2, and it got triggered, score is +2.
        # Total score of +4 or -4 could be a threshold.

        # Redefine how total_impact_score is interpreted for "harder"
        # Let's say positive means harder from detrimental effects, and negative means harder from lack of beneficial effects
        # A simple heuristic: if the sum of scores (where positive means harder) exceeds threshold
        
        effective_difficulty_score = 0
        for path_str_check, rand_val_check in randomized_values_map.items():
            path_keys_check = [int(p) if p.isdigit() else p for p in path_str_check.split('.')]
            normal_val_check = self.settings_manager.get_setting_value(path_keys_check, target_dict=normal_settings)
            if normal_val_check is None: continue
            _, specific_conf_check = get_setting_config_by_path(path_keys_check)

            if specific_conf_check and "impact_score_hard" in specific_conf_check:
                normal_float_check = specific_conf_check.get("normal_float", 1.0)
                impact = specific_conf_check["impact_score_hard"]
                if impact < 0: # Beneficial factor, harder if low
                    if rand_val_check < normal_float_check * 0.6: effective_difficulty_score += abs(impact)
                elif impact > 0: # Detrimental factor, harder if high
                    if rand_val_check > normal_float_check * 1.6: effective_difficulty_score += impact
            # Boolean specific checks
            if path_keys_check == ["gameSettings", "enableStarvingDebuff"] and rand_val_check is True and normal_val_check is False: effective_difficulty_score += 2
            if path_keys_check == TOMBSTONE_MODE_PATH and rand_val_check == "Everything" and normal_val_check != "Everything": effective_difficulty_score += 1


        if effective_difficulty_score >= DIFFICULTY_THRESHOLD:
            warning_message = f"Randomization for '{tab_name}' may make the game substantially harder (Difficulty Score: {effective_difficulty_score}):\n"
            # For brevity, just a general warning. Listing all indicators might be too much.
            warning_message += "- Key settings for player survival or enemy strength have been significantly altered.\n"
            warning_message += "\nReview settings carefully before saving."
            messagebox.showwarning("Difficulty Warning", warning_message)


    def load_defaults_gui(self):
        if self.settings_manager.revert_to_defaults_from_readme(): 
            self._refresh_notebook_and_vars() 
            self.status_var.set("Readme defaults applied. Save to make permanent."); self.mark_settings_changed()
        
    def manual_backup_gui(self):
        if self.settings_manager.backup_file(JSON_FILE, reason="manual_gui_backup"):
            messagebox.showinfo("Backup", "Current settings backed up."); self.status_var.set("Manual backup created.")
        else: messagebox.showerror("Backup Failed", "Could not create manual backup."); self.status_var.set("Manual backup failed.")

    def restore_backup_gui(self):
        backups = self.settings_manager.list_backup_files()
        if not backups: messagebox.showinfo("Restore Backup", "No backup files found."); return
        restore_win = tk.Toplevel(self.root); restore_win.title("Select Backup"); restore_win.geometry("650x400"); restore_win.transient(self.root); restore_win.grab_set()
        tk.Label(restore_win, text="Select backup (newest first):").pack(pady=10)
        lb_frame = ttk.Frame(restore_win); lb_frame.pack(pady=5, padx=10, fill="both", expand=True)
        lb = tk.Listbox(lb_frame, width=90, height=15); scroll = ttk.Scrollbar(lb_frame, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=scroll.set)
        for fname, dt in backups:
            r_match = re.search(r'\d{8}_\d{6}_(.*)\.old$', fname)
            r_disp = f" (Reason: {r_match.group(1).replace('_', ' ') if r_match else 'N/A'})"
            lb.insert(tk.END, f"{fname} ({dt.strftime('%Y-%m-%d %H:%M:%S')}{r_disp})")
        lb.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        def on_restore():
            sel = lb.curselection()
            if not sel: messagebox.showwarning("No Selection", "Please select a backup.", parent=restore_win); return
            fname = lb.get(sel[0]).split(" ")[0]
            if messagebox.askyesno("Confirm Restore", f"Restore from:\n{fname}?\nCurrent settings backed up first.", parent=restore_win):
                if self.settings_manager.restore_from_backup_file(fname):
                    self._refresh_notebook_and_vars(); 
                    self.status_var.set(f"Restored from {fname}."); self.mark_settings_changed() 
                restore_win.destroy()
        btn_frame = ttk.Frame(restore_win); btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Restore Selected", command=on_restore).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=restore_win.destroy).pack(side="left", padx=5)

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = EnshroudedConfigEditorApp(root)
    root.mainloop()
