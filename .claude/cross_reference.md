# Cross-Reference System for Plans vs Current Documentation

## Purpose
This file provides a systematic cross-examination system to ensure new plans align with existing documentation and avoid conflicts with established patterns.

## Documentation Categories

### 🏗️ Architecture Documents (docs/)
| Document | Focus Area | When to Consult |
|----------|------------|-----------------|
| `DEMO_README.md` | UI patterns, demo integration | Before any UI work |
| `CONFIG_SYSTEM_README.md` | Configuration patterns | Before config changes |
| `UI_SYSTEM_README.md` | UI architecture guidelines | Before UI modifications |
| `AI_ARCHITECTURE.md` | AI system integration | Before AI feature work |
| `EFFECT_SYSTEM_IMPLEMENTATION.md` | Effect system patterns | Before effect-related work |
| `ELEMENTAL_SYSTEM.md` | Damage type system | Before combat/damage work |
| `COMPREHENSIVE_TESTING_GUIDE.md` | Testing strategies | Before test implementation |

### 🔧 Implementation Summaries (docs/)
| Document | Contains | Cross-Check For |
|----------|----------|-----------------|
| `FINAL_PROJECT_SUMMARY.md` | Current project state | Overall system status |
| `COMPREHENSIVE_FIXES_SUMMARY.md` | Recent fixes and patterns | Avoiding known issues |
| `RPG_STATS_IMPLEMENTATION_SUMMARY.md` | Stats system patterns | Character/stat related work |
| `ENCHANTING_IMPROVEMENTS.md` | Enchantment patterns | Magic/equipment work |
| `INVENTORY_FIXES_README.md` | Inventory patterns | Item/inventory work |

### 📋 Step-by-Step Guides (instructions/)
| Document | Workflow | Use When |
|----------|----------|----------|
| `DEMO_COMPREHENSIVE_IMPROVEMENTS.md` | Demo improvement patterns | Enhancing demo features |
| `STAMINA_USAGE_FOR_COMBAT_ACTIONS.md` | Combat integration patterns | Adding combat features |
| `combo_bar_and_tab_implementation.md` | UI tab patterns | Creating new UI tabs |
| `dual_wield_implementation_guide.md` | Equipment feature patterns | Adding equipment features |

## Cross-Examination Checklist

### Before Starting Any Task:
- [ ] **Identify Primary Area** - Combat, UI, Character, Config, etc.
- [ ] **Find Related Architecture Doc** - Check table above
- [ ] **Find Related Implementation Summary** - Look for recent work in area
- [ ] **Find Related Instructions** - Look for step-by-step guides
- [ ] **Check for Conflicts** - Ensure plan doesn't contradict existing patterns

### Architecture Alignment Check:
- [ ] **Service Layer Pattern** - Does plan follow service-oriented architecture?
- [ ] **Factory Pattern** - Does plan use existing factories for object creation?
- [ ] **Configuration Pattern** - Does plan use ConfigManager and feature toggles?
- [ ] **Event System** - Does plan integrate with existing hook system?
- [ ] **UI Pattern** - Does plan follow tabbed interface and service integration?

### Implementation History Check:
- [ ] **Similar Features** - Has something similar been implemented before?
- [ ] **Known Issues** - Are there documented problems to avoid?
- [ ] **Established Patterns** - What patterns are already in use?
- [ ] **Recent Changes** - What has been modified recently that might conflict?

## Quick Reference Mapping

### By Feature Type:
| Feature Type | Primary Docs | Key Patterns |
|--------------|--------------|--------------|
| **Combat** | ELEMENTAL_SYSTEM.md, STAMINA_USAGE_FOR_COMBAT_ACTIONS.md | CombatService, DamagePacket, Event hooks |
| **UI/Demo** | DEMO_README.md, UI_SYSTEM_README.md, combo_bar_and_tab_implementation.md | Tabbed interface, service calls only |
| **Character/Stats** | RPG_STATS_IMPLEMENTATION_SUMMARY.md | Actor hierarchy, stat derivation |
| **Config/Settings** | CONFIG_SYSTEM_README.md | ConfigManager singleton, feature toggles |
| **Magic/Effects** | EFFECT_SYSTEM_IMPLEMENTATION.md, ENCHANTING_IMPROVEMENTS.md | Effect factory, status manager |
| **Items/Equipment** | INVENTORY_FIXES_README.md, dual_wield_implementation_guide.md | ItemFactory, equipment slots |
| **Testing** | COMPREHENSIVE_TESTING_GUIDE.md | Multiple test approaches, demo integration |

### By System Component:
| Component | Related Docs | Critical Patterns |
|-----------|--------------|-------------------|
| **Actor System** | RPG_STATS_IMPLEMENTATION_SUMMARY.md | Primary/derived stats, template creation |
| **Combat Engine** | ELEMENTAL_SYSTEM.md, STAMINA_USAGE_FOR_COMBAT_ACTIONS.md | Turn-based, service layer |
| **Effect System** | EFFECT_SYSTEM_IMPLEMENTATION.md | Factory creation, temporary effects |
| **Configuration** | CONFIG_SYSTEM_README.md | Hierarchical settings, hot reload |
| **Demo Interface** | DEMO_README.md, combo_bar_and_tab_implementation.md | Tabbed UI, service integration |

## Conflict Detection

### Common Conflict Areas:
1. **Direct State Manipulation** - Check if plan bypasses service layer
2. **Configuration Hardcoding** - Check if plan hardcodes values instead of using config
3. **UI Business Logic** - Check if plan puts business logic in UI
4. **Factory Bypass** - Check if plan creates objects without using factories
5. **Event System Bypass** - Check if plan doesn't use existing hook system

### Resolution Process:
1. **Identify Conflict** - Document specific conflict with existing pattern
2. **Consult Architecture** - Review relevant architecture document
3. **Find Alternative** - Look for pattern-compliant approach
4. **Update Plan** - Modify plan to align with existing patterns
5. **Document Decision** - Add rationale to memory_bank/decisions/

## Validation Gates

### Pre-Implementation:
- [ ] All related docs reviewed
- [ ] No conflicts identified
- [ ] Plan aligns with established patterns
- [ ] Alternative approaches considered

### During Implementation:
- [ ] Following documented patterns
- [ ] Using established services/factories
- [ ] Configuration properly managed
- [ ] Event system properly integrated

### Post-Implementation:
- [ ] Implementation matches documented patterns
- [ ] No new conflicts introduced
- [ ] Documentation updated if patterns extended
- [ ] Lessons learned captured in memory_bank