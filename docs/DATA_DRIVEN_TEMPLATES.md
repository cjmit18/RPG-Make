# 📊 Data-Driven Template System

**Project Focus:** JSON-Driven Content Creation
**Last Updated:** July 26, 2025

This document explains how the RPG engine uses JSON templates to create characters, achievements, and future content in a completely data-driven manner.

---

## 🎯 **Template System Overview**

### **Core Principle: Everything is Data-Driven**
All game content (characters, achievements, items, skills, spells) is defined in JSON files, making the system:
- **Easily Moddable** - Players can create content without coding
- **Designer Friendly** - Non-programmers can balance and create content
- **Version Controlled** - All content changes are tracked in git
- **Validatable** - JSON schemas ensure data integrity

---

## 📊 **Stat System Architecture**

### **Three-Layer Stat System**

#### 1. **Base Stats** (Character Template)
```json
"base_stats": {
  "strength": 16,      // Starting strength value
  "constitution": 14,  // Starting constitution value
  "intelligence": 8    // Starting intelligence value
}
```

#### 2. **Growth Rates** (Character Template) 
```json
"growth_rates": {
  "strength": 1.3,     // +1.3 strength per level
  "constitution": 1.2, // +1.2 constitution per level  
  "intelligence": 0.7  // +0.7 intelligence per level
}
```

#### 3. **Derived Stat Formulas** (Global Config)
```json
"derived_stat_formulas": {
  "health": 10.0,      // constitution × 10.0 = health points
  "mana": 10.0,        // intelligence × 10.0 = mana points
  "attack": 1.5        // strength × 1.5 = attack power
}
```

### **Example Calculation**
```
Warrior at Level 1:
- Base Constitution: 14
- Health = 14 × 10.0 = 140 HP

Warrior at Level 10:
- Constitution: 14 + (1.2 × 9 levels) = 24.8
- Health = 24.8 × 10.0 = 248 HP
```

---

## 📁 **Template File Structure**

### **Current Template Files**
```
data/
├── character_templates.json    # Character classes and builds
├── achievements.json          # Achievement definitions
├── items.json                # Equipment and consumables (planned)
├── skills.json               # Abilities and spells (planned)
└── quests.json               # Story content (planned)
```

### **Configuration Files**
```
default_settings.json          # Global game mechanics
config/
├── balance.json              # Damage/healing values (planned)
├── progression.json          # Leveling curves (planned)
└── world_settings.json       # Environmental settings (planned)
```

---

## 🛠️ **Character Template Format**

### **Required Fields**
```json
{
  "character_templates": {
    "template_id": {
      "id": "unique_identifier",
      "name": "Display Name",
      "description": "Flavor text description",
      "character_class": "Warrior",
      "rarity": "COMMON|UNCOMMON|RARE|EPIC|LEGENDARY|MYTHIC|DIVINE",
      "grade": "ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN",
      
      "base_stats": {
        "strength": number,
        "dexterity": number,
        "vitality": number,
        "intelligence": number,
        "wisdom": number,
        "constitution": number,
        "luck": number,
        "agility": number,
        "charisma": number
      },
      
      "growth_rates": {
        "strength": number,    // Stat gain per level
        "dexterity": number,
        // ... etc
      }
    }
  }
}
```

### **Optional Fields**
```json
"starting_equipment": ["item_id1", "item_id2"],
"starting_skills": ["skill_id1", "skill_id2"],
"background": "soldier|scholar|merchant|noble",
"appearance": {
  "hair_color": "brown",
  "eye_color": "blue",
  "skin_tone": "fair",
  "height": "tall|medium|short",
  "build": "muscular|average|slim"
}
```

---

## 🏆 **Achievement Template Format**

### **Achievement Structure**
```json
{
  "achievements": {
    "category_name": {
      "achievement_id": {
        "name": "Achievement Name",
        "description": "What the player accomplished",
        "points": number,
        "icon": "icon_filename.png",
        "hidden": boolean,
        "requirements": {
          "type": "character_creation|level_up|stat_threshold|combat",
          "conditions": {
            // Specific conditions based on type
          }
        },
        "rewards": {
          "experience": number,
          "items": ["item_id1"],
          "titles": ["title_id1"]
        }
      }
    }
  }
}
```

### **Achievement Types**
```json
// Character Creation
"requirements": {
  "type": "character_creation",
  "conditions": {
    "count": 1,
    "classes": ["any"] // or specific classes
  }
}

// Level Milestone
"requirements": {
  "type": "level_up", 
  "conditions": {
    "level": 10,
    "class": "any" // or specific class
  }
}

// Stat Threshold
"requirements": {
  "type": "stat_threshold",
  "conditions": {
    "stat": "strength",
    "value": 100
  }
}
```

---

## 🔮 **Future Template Types**

### **Item Templates** (Planned)
```json
{
  "items": {
    "item_id": {
      "name": "Item Name",
      "type": "weapon|armor|consumable|misc",
      "rarity": "COMMON|RARE|etc",
      "stats": {
        "attack": 10,
        "defense": 5
      },
      "requirements": {
        "level": 5,
        "class": ["Warrior", "Paladin"]
      }
    }
  }
}
```

### **Skill Templates** (Planned)
```json
{
  "skills": {
    "skill_id": {
      "name": "Skill Name",
      "description": "What the skill does",
      "type": "active|passive",
      "cost": {
        "mana": 10,
        "stamina": 5
      },
      "effects": [
        {
          "type": "damage",
          "formula": "strength * 1.5 + weapon_damage"
        }
      ]
    }
  }
}
```

---

## 📊 **Template Loading System**

### **Loading Order**
1. **Global Configuration** - Load balance and formulas first
2. **Character Templates** - Load all available character types
3. **Achievement Templates** - Load progression tracking
4. **Content Templates** - Load items, skills, quests as needed

### **Validation System**
- **JSON Schema Validation** - Ensure all required fields
- **Reference Validation** - Check that referenced IDs exist
- **Balance Validation** - Warn about potential balance issues
- **Consistency Checks** - Ensure templates work together

### **Hot Reloading** (Development)
- Templates can be reloaded without restarting the game
- Changes are validated before applying
- Backup system prevents corrupted data

---

## 🎮 **Usage Examples**

### **Creating a New Character Class**
1. Add template to `data/character_templates.json`
2. Define base stats and growth rates
3. Test in game - system automatically loads new template
4. No code changes required!

### **Adding an Achievement**
1. Add achievement to `data/achievements.json`
2. Define trigger conditions and rewards
3. System automatically tracks the new achievement
4. No code changes required!

### **Balancing Changes**
1. Modify `derived_stat_formulas` in `default_settings.json`
2. Changes apply to all characters immediately
3. Can A/B test different balance approaches
4. Version control tracks all balance changes

---

## 🔧 **Development Tools**

### **Template Validator** (Planned)
```bash
python tools/validate_templates.py
# Checks all JSON files for errors
```

### **Balance Analyzer** (Planned)
```bash
python tools/analyze_balance.py
# Shows power curves and balance issues
```

### **Template Generator** (Planned)
```bash
python tools/generate_template.py --type character
# Interactive template creation
```

---

## 📝 **Best Practices**

### **Naming Conventions**
- **IDs**: `snake_case` (e.g., `fire_mage_basic`)
- **Names**: `Title Case` (e.g., `"Fire Mage"`)
- **Files**: `snake_case.json`

### **Balance Guidelines**
- **Total Base Stats**: 90-110 for balanced characters
- **Growth Rates**: 0.5-1.5 per level for balanced progression
- **Derived Stats**: Use config formulas, don't hardcode values

### **Template Organization**
- **Group by Type**: All warriors together, all mages together
- **Difficulty Progression**: Basic → Advanced → Master templates
- **Clear Dependencies**: Document what items/skills are referenced

This data-driven approach makes the RPG engine extremely flexible and moddable while maintaining balance and consistency across all content.
