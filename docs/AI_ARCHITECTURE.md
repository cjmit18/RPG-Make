# AI System Architecture Documentation

## Overview

The AI system provides intelligent behavior for enemies and NPCs in the RPG game. It's built on a modular architecture that integrates seamlessly with the existing service layer, ensuring that AI actors use the same game mechanics as players.

## Architecture Components

### 1. AI Service (`ai_service.py`)
**Main coordinator for all AI systems**

- **Purpose**: Central hub that manages all AI actors and coordinates subsystems
- **Key Features**:
  - Actor registration and management
  - Behavior tree execution
  - Difficulty scaling integration
  - Battle simulation capabilities
  - Performance monitoring

```python
# Example usage
ai_service = AIService(combat_service)
ai_service.register_ai_actor(enemy, "aggressive_enemy")
ai_service.set_target_for_actor(enemy, player)
ai_service.update_ai_actors()  # Call each game frame/tick
```

### 2. Combat AI (`combat_ai.py`)
**Intelligent combat decision making**

- **Purpose**: Makes tactical combat decisions based on situational analysis
- **Key Features**:
  - Threat assessment (LOW, MEDIUM, HIGH, CRITICAL)
  - Strategy selection (AGGRESSIVE, DEFENSIVE, BALANCED, OPPORTUNISTIC)
  - Action evaluation and execution
  - Resource management (health, mana, abilities)

```python
# Example combat decision
combat_ai = CombatAI(combat_service)
decision = combat_ai.make_combat_decision(enemy, player)
# Returns: strategy, action_data, threat_level
```

### 3. Behavior Trees (`behavior_tree.py`)
**Flexible AI behavior composition**

- **Purpose**: Provides reusable, hierarchical behavior structures
- **Node Types**:
  - **SequenceNode**: Execute children until one fails
  - **SelectorNode**: Execute children until one succeeds  
  - **ParallelNode**: Execute all children simultaneously
  - **ConditionNode**: Check game state conditions
  - **ActionNode**: Perform game actions
  - **RandomSelectorNode**: Randomly choose child to execute

```python
# Pre-built behavior trees
basic_enemy = CombatBehaviorBuilder.build_basic_enemy()
aggressive_enemy = CombatBehaviorBuilder.build_aggressive_enemy()
defensive_enemy = CombatBehaviorBuilder.build_defensive_enemy()
```

### 4. Difficulty Scaling (`difficulty_scaling.py`)
**Dynamic challenge adjustment**

- **Purpose**: Automatically adjusts game difficulty based on player performance
- **Difficulty Levels**: VERY_EASY → EASY → NORMAL → HARD → VERY_HARD → EXTREME
- **Scaling Factors**:
  - Enemy health/damage/speed multipliers
  - AI aggression levels
  - Spell casting frequency
  - Loot quality and experience rates

```python
# Automatic scaling based on win rate
scaler = DifficultyScaler()
scaler.record_battle_result(player_won=True, battle_duration=45.0)
modifiers = scaler.get_current_modifiers()
scaler.apply_modifiers_to_enemy(enemy)
```

## Integration with Existing Systems

### Service Layer Integration
The AI system uses the same service APIs that the player uses:

```python
# AI uses CombatService for attacks
result = combat_service.perform_attack(ai_actor, target, weapon)

# AI uses CombatService for spells
result = combat_service.cast_spell_at_target(ai_actor, "fireball", target)

# AI uses StatusManager for effects
status_manager.tick(delta_time)
```

### Demo Integration
AI can be easily integrated into the existing demo:

```python
class SimpleGameDemo:
    def setup_game_state(self):
        # ...existing code...
        
        # Initialize AI service
        self.ai_service = AIService(self.combat_service)
        
        # Register enemy for AI control
        if self.enemy:
            self.ai_service.register_ai_actor(self.enemy, "basic_enemy")
            self.ai_service.set_target_for_actor(self.enemy, self.player)
    
    def game_loop_update(self):
        # Update AI actors (call this regularly)
        self.ai_service.update_ai_actors()
        
        # Record battle results for difficulty scaling
        if battle_ended:
            self.ai_service.record_battle_result(
                player_won=player_won,
                battle_duration=battle_time,
                damage_dealt=damage_dealt,
                damage_received=damage_received
            )
```

## Behavior Tree Examples

### Basic Enemy Behavior
```
SelectorNode("EnemyRoot")
├── SequenceNode("SpellCasting")
│   ├── ConditionNode("LowHealth") 
│   ├── ConditionNode("HasSpells")
│   └── ActionNode("CastSpell")
├── SequenceNode("Attack")
│   ├── ConditionNode("HasTarget")
│   └── ActionNode("AttackTarget")
└── ActionNode("Wait")
```

### Aggressive Enemy Behavior
```
SelectorNode("AggressiveRoot")
├── SequenceNode("AggressiveAttack")
│   ├── ConditionNode("HasTarget")
│   └── ActionNode("AttackTarget")
└── SequenceNode("OffensiveSpells")
    ├── ConditionNode("HasOffensiveSpells")
    └── ActionNode("CastOffensiveSpell")
```

### Defensive Enemy Behavior
```
SelectorNode("DefensiveRoot")
├── SequenceNode("SelfHeal")
│   ├── ConditionNode("LowHealth")
│   ├── ConditionNode("HasHealSpells")
│   └── ActionNode("CastHeal")
├── SequenceNode("CautiousAttack")
│   ├── ConditionNode("HealthyEnough")
│   ├── ConditionNode("HasTarget")
│   └── ActionNode("AttackTarget")
└── SequenceNode("DefensiveSpells")
    ├── ConditionNode("HasDefensiveSpells")
    └── ActionNode("CastDefensiveSpell")
```

## AI Decision Making Flow

1. **Threat Assessment**
   - Analyze relative health, damage potential
   - Calculate threat score (0-5+)
   - Assign threat level (LOW → CRITICAL)

2. **Strategy Selection**
   - Consider threat level and current resources
   - Choose strategy: AGGRESSIVE, DEFENSIVE, BALANCED, OPPORTUNISTIC
   - Factor in difficulty modifiers

3. **Action Selection**
   - Evaluate available actions (attack, spells, abilities)
   - Prioritize based on strategy and situation
   - Consider mana costs and cooldowns

4. **Execution**
   - Use combat service to perform action
   - Apply same game rules as player
   - Handle success/failure appropriately

## Difficulty Scaling Algorithm

### Performance Tracking
- Win rate percentage
- Win/loss streaks
- Battle duration
- Damage ratios
- Resource usage

### Adjustment Triggers
- **Increase Difficulty**: 80%+ win rate OR 8+ win streak
- **Decrease Difficulty**: 50%- win rate OR 5+ loss streak
- **Cooldown**: 5 minutes between adjustments
- **Minimum Data**: 5 battles before first adjustment

### Modifier Application
```python
# Health scaling example
enemy.max_health *= difficulty_modifiers.enemy_health_multiplier
enemy.current_health = enemy.max_health

# Damage scaling
enemy.base_stats['attack'] *= difficulty_modifiers.enemy_damage_multiplier

# AI behavior scaling
enemy.ai_modifiers['aggression'] = difficulty_modifiers.enemy_ai_aggression
```

## Extensibility

### Adding New Behavior Trees
```python
def build_custom_enemy():
    root = SelectorNode("CustomRoot")
    # Add custom logic nodes
    return BehaviorTree("CustomEnemy", root)

ai_service.behavior_trees["custom_enemy"] = build_custom_enemy()
```

### Custom AI Conditions
```python
def custom_condition(actor, context):
    # Custom game state check
    return context.get('special_flag', False)

condition_node = ConditionNode("CustomCondition", custom_condition)
```

### Custom AI Actions
```python
def custom_action(actor, context):
    # Custom action implementation
    # Use existing services for game mechanics
    return NodeStatus.SUCCESS

action_node = ActionNode("CustomAction", custom_action)
```

## Performance Considerations

### Optimization Features
- **Action Cooldowns**: Prevent AI from acting every frame
- **Lazy Evaluation**: Only active AI actors are processed
- **Efficient Tree Traversal**: Early termination on success/failure
- **Resource Pooling**: Reuse behavior tree instances

### Recommended Settings
- **Update Frequency**: 1-2 times per second for turn-based, 10-30 FPS for real-time
- **Action Cooldown**: 1.0 seconds for strategic gameplay
- **Max AI Actors**: 10-20 simultaneously for good performance

## Future Enhancements

### Planned Features
1. **Learning AI**: Adapt to player tactics over time
2. **Personality System**: Unique behavioral traits per character type
3. **Formation AI**: Coordinate multiple AI actors
4. **Dynamic Behavior**: Switch behaviors based on context
5. **Player Modeling**: Customize difficulty per individual player style

### Integration Points
- **Quest System**: AI-driven quest NPCs
- **Social AI**: Non-combat interactions and dialogue
- **Economy AI**: Dynamic pricing and trading behaviors
- **Environmental AI**: Interactive world objects and systems
