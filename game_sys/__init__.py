from game_sys.skills.learning import SkillRecord, SkillRegistry
import game_sys.hooks.hooks_setup  # Ensure hooks are registered
from game_sys.effects import damage, heal, status, damage_reduction, statbuff, modify_weapon, instant, unlock
from game_sys.effects.passives import lifesteal
data_path = "game_sys/skills/data/skills.json"
records = SkillRecord.load_from_json_array(data_path)
for rec in records:
    SkillRegistry.register(rec)
