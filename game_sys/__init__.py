from game_sys.skills.learning import SkillRecord, SkillRegistry

data_path = "game_sys/skills/data/skills.json"
records = SkillRecord.load_from_json_array(data_path)
for rec in records:
    SkillRegistry.register(rec)
