# game_sys/effects/factory.py

import re
from typing import Any, Dict
from game_sys.effects.registry import EffectRegistry
from game_sys.effects.base import NullEffect
from game_sys.effects.schemas import validate_effect_definition
from game_sys.logging import effects_logger, log_exception


class EffectFactory:
    """
    Builds Effect instances from either:
      - Full JSON definitions (dicts with 'type' + 'params')
      - Simple ID strings like "flat_2" or "elemental_FIRE_1.2"
    """

    @staticmethod
    @log_exception
    def create(defn: Dict[str, Any]) -> Any:
        """
        Instantiate an effect from a JSON-style dict:
            { "type": str, "params": {...} }
        """
        effects_logger.debug(f"Creating effect from definition: {defn}")
        validate_effect_definition(defn)
        etype = defn["type"]
        params = defn["params"]
        cls = EffectRegistry._registry.get(etype)
        if cls:
            try:
                effect = cls(**params)
                effects_logger.info(
                    f"Created {etype} effect with params: {params}"
                )
                return effect
            except Exception as e:
                effects_logger.warning(
                    f"Failed to create {etype} effect: {e}, "
                    f"falling back to parameterless"
                )
                # fallback to parameterless or NullEffect
                return EffectRegistry.get(etype)
        effects_logger.warning(f"No class registered for effect type: {etype}")
        return EffectRegistry.get(etype)

    @staticmethod
    @log_exception
    def create_from_id(eid: str) -> Any:
        """
        Instantiate effects from ID strings. Supports:
        - flat_X: Flat damage bonus
        - percent_X: Percent damage multiplier  
        - elemental_ELEMENT_X: Elemental damage
        - mana_regen_X: Mana regeneration bonus
        - health_regen_X: Health regeneration bonus
        - stamina_regen_X: Stamina regeneration bonus
        - str_boost_X: Strength stat bonus
        - dex_boost_X: Dexterity stat bonus
        - int_boost_X: Intelligence stat bonus
        - wis_boost_X: Wisdom stat bonus
        - con_boost_X: Constitution stat bonus
        - attack_boost_X: Attack stat bonus
        - defense_boost_X: Defense stat bonus
        - crit_boost_X: Critical hit chance bonus
        - spell_power_X: Spell power bonus
        - spell_accuracy_X: Spell accuracy bonus
        - fire_resist_X: Fire resistance
        - cold_resist_X: Cold resistance
        - lightning_resist_X: Lightning resistance
        - poison_resist_X: Poison resistance
        And fallback to registry for other IDs.
        """
        effects_logger.debug(f"Creating effect from ID: {eid}")
        parts = eid.split("_")
        etype = parts[0]
        
        # Damage modifiers
        if etype == "flat":
            amt = float(parts[1]) if len(parts) > 1 else 0.0
            cls = EffectRegistry._registry.get("flat")
            effects_logger.debug(f"Creating flat damage mod with amount={amt}")
            return cls(amount=amt) if cls else NullEffect()
            
        if etype == "percent":
            mul = float(parts[1]) if len(parts) > 1 else 1.0
            cls = EffectRegistry._registry.get("percent")
            effects_logger.debug(f"Creating percent damage mod with multiplier={mul}")
            return cls(multiplier=mul) if cls else NullEffect()
            
        if etype == "elemental" and len(parts) >= 3:
            elem = parts[1]
            mul = float(parts[2])
            cls = EffectRegistry._registry.get("elemental")
            effects_logger.debug(
                f"Creating elemental damage mod with element={elem}, multiplier={mul}"
            )
            return cls(element=elem, multiplier=mul) if cls else NullEffect()

        # Resource regeneration effects
        if len(parts) >= 3 and parts[1] == "regen":
            amount = float(parts[2])
            if etype == "mana":
                effects_logger.debug(f"Creating mana regeneration: +{amount}/s")
                cls = EffectRegistry._registry.get("regeneration")
                return cls(resource="mana", amount=amount) if cls else NullEffect()
            elif etype == "health":
                effects_logger.debug(f"Creating health regeneration: +{amount}/s") 
                cls = EffectRegistry._registry.get("regeneration")
                return cls(resource="health", amount=amount) if cls else NullEffect()
            elif etype == "stamina":
                effects_logger.debug(f"Creating stamina regeneration: +{amount}/s")
                cls = EffectRegistry._registry.get("regeneration") 
                return cls(resource="stamina", amount=amount) if cls else NullEffect()

        # Primary stat boosts (using EquipmentStatEffect for passive bonuses)
        if len(parts) >= 3 and parts[1] == "boost":
            amount = float(parts[2])
            stat_map = {
                "str": "strength",
                "dex": "dexterity", 
                "int": "intelligence",
                "wis": "wisdom",
                "con": "constitution",
                "attack": "attack",
                "defense": "defense",
                "crit": "critical_chance",
                "spell": "spell_power",
                "accuracy": "accuracy",
                "mana": "max_mana",
                "health": "max_health",
                "stamina": "max_stamina"
            }
            
            if etype in stat_map:
                stat_name = stat_map[etype]
                effects_logger.debug(f"Creating {stat_name} bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name=stat_name, amount=amount) if cls else NullEffect()

        # Special spell effects
        if len(parts) >= 3:
            if etype == "spell" and parts[1] == "power":
                amount = float(parts[2])
                effects_logger.debug(f"Creating spell power bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="spell_power", amount=amount) if cls else NullEffect()
            elif etype == "spell" and parts[1] == "accuracy":
                amount = float(parts[2])
                effects_logger.debug(f"Creating spell accuracy bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="spell_accuracy", amount=amount) if cls else NullEffect()

        # Elemental resistances
        if len(parts) >= 3 and parts[1] == "resist":
            amount = float(parts[2])
            resistance_map = {
                "fire": "fire_resistance",
                "cold": "cold_resistance", 
                "lightning": "lightning_resistance",
                "poison": "poison_resistance",
                "ice": "cold_resistance"
            }
            
            if etype in resistance_map:
                stat_name = resistance_map[etype]
                effects_logger.debug(f"Creating {stat_name}: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name=stat_name, amount=amount) if cls else NullEffect()

        # Additional comprehensive effect patterns for future expansion
        
        # Movement and combat speed effects
        if len(parts) >= 3:
            if etype == "move" and parts[1] == "speed":
                amount = float(parts[2])
                effects_logger.debug(f"Creating movement speed bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="movement_speed", amount=amount) if cls else NullEffect()
            elif etype == "attack" and parts[1] == "speed":
                amount = float(parts[2])
                effects_logger.debug(f"Creating attack speed bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="attack_speed", amount=amount) if cls else NullEffect()
            elif etype == "cast" and parts[1] == "speed":
                amount = float(parts[2])
                effects_logger.debug(f"Creating cast speed bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="cast_speed", amount=amount) if cls else NullEffect()

        # Critical hit and damage effects
        if len(parts) >= 3:
            if etype == "crit" and parts[1] == "chance":
                amount = float(parts[2])
                effects_logger.debug(f"Creating critical hit chance: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="critical_chance", amount=amount) if cls else NullEffect()
            elif etype == "crit" and parts[1] == "damage":
                amount = float(parts[2])
                effects_logger.debug(f"Creating critical damage: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="critical_damage", amount=amount) if cls else NullEffect()

        # Damage type bonuses
        if len(parts) >= 3 and parts[1] == "damage":
            amount = float(parts[2])
            damage_types = ["physical", "magical", "fire", "cold", "lightning", "poison", "holy", "dark"]
            if etype in damage_types:
                stat_name = f"{etype}_damage"
                effects_logger.debug(f"Creating {stat_name} bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name=stat_name, amount=amount) if cls else NullEffect()

        # Resource capacity bonuses
        if len(parts) >= 3 and parts[1] == "capacity":
            amount = float(parts[2])
            resource_map = {
                "health": "max_health",
                "mana": "max_mana",
                "stamina": "max_stamina"
            }
            if etype in resource_map:
                stat_name = resource_map[etype]
                effects_logger.debug(f"Creating {stat_name} bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name=stat_name, amount=amount) if cls else NullEffect()

        # Special combat effects
        if len(parts) >= 3:
            if etype == "block" and parts[1] == "chance":
                amount = float(parts[2])
                effects_logger.debug(f"Creating block chance: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="block_chance", amount=amount) if cls else NullEffect()
            elif etype == "dodge" and parts[1] == "chance":
                amount = float(parts[2])
                effects_logger.debug(f"Creating dodge chance: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="dodge_chance", amount=amount) if cls else NullEffect()
            elif etype == "parry" and parts[1] == "chance":
                amount = float(parts[2])
                effects_logger.debug(f"Creating parry chance: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="parry_chance", amount=amount) if cls else NullEffect()

        # Penetration effects
        if len(parts) >= 3 and parts[1] == "penetration":
            amount = float(parts[2])
            penetration_types = ["armor", "magic", "fire", "cold", "lightning", "poison"]
            if etype in penetration_types:
                stat_name = f"{etype}_penetration"
                effects_logger.debug(f"Creating {stat_name}: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name=stat_name, amount=amount) if cls else NullEffect()

        # Vampiric and lifesteal effects  
        if len(parts) >= 3:
            if etype == "life" and parts[1] == "steal":
                amount = float(parts[2])
                effects_logger.debug(f"Creating life steal: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="life_steal", amount=amount) if cls else NullEffect()
            elif etype == "mana" and parts[1] == "steal":
                amount = float(parts[2])
                effects_logger.debug(f"Creating mana steal: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="mana_steal", amount=amount) if cls else NullEffect()

        # Cooldown and resource cost reduction
        if len(parts) >= 3 and parts[1] == "reduction":
            amount = float(parts[2])
            reduction_map = {
                "cooldown": "cooldown_reduction",
                "mana": "mana_cost_reduction",
                "stamina": "stamina_cost_reduction"
            }
            if etype in reduction_map:
                stat_name = reduction_map[etype]
                effects_logger.debug(f"Creating {stat_name}: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name=stat_name, amount=amount) if cls else NullEffect()

        # Experience and luck bonuses
        if len(parts) >= 3:
            if etype == "exp" and parts[1] == "bonus":
                amount = float(parts[2])
                effects_logger.debug(f"Creating experience bonus: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="exp_bonus", amount=amount) if cls else NullEffect()
            elif etype == "magic" and parts[1] == "find":
                amount = float(parts[2])
                effects_logger.debug(f"Creating magic find: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="magic_find", amount=amount) if cls else NullEffect()
        
        # Simple luck effect (luck_X)
        if etype == "luck" and len(parts) >= 2:
            amount = float(parts[1])
            effects_logger.debug(f"Creating luck bonus: +{amount}")
            cls = EffectRegistry._registry.get("equipment_stat")
            return cls(stat_name="luck", amount=amount) if cls else NullEffect()

        # Range and area effects
        if len(parts) >= 2:
            if etype == "range" and len(parts) >= 2:
                amount = float(parts[1])
                effects_logger.debug(f"Creating range bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="range", amount=amount) if cls else NullEffect()
            elif etype == "aoe" and len(parts) >= 2:
                amount = float(parts[1])
                effects_logger.debug(f"Creating area of effect bonus: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="aoe_size", amount=amount) if cls else NullEffect()

        # Thorns and reflection damage
        if len(parts) >= 2:
            if etype == "thorns":
                amount = float(parts[1])
                effects_logger.debug(f"Creating thorns damage: +{amount}")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="thorns_damage", amount=amount) if cls else NullEffect()
            elif etype == "reflect":
                amount = float(parts[1])
                effects_logger.debug(f"Creating damage reflection: +{amount}%")
                cls = EffectRegistry._registry.get("equipment_stat")
                return cls(stat_name="damage_reflection", amount=amount) if cls else NullEffect()

        # Status effects
        status_effects = {
            'burn', 'poison', 'stun', 'fear', 'slow', 'freeze', 'haste',
            'silence', 'weaken', 'berserk', 'protection', 'invisibility',
            'paralyze', 'sleep'
        }
        
        if etype in status_effects:
            # Parse optional duration parameter
            duration = float(parts[1]) if len(parts) > 1 else None
            cls = EffectRegistry._registry.get(etype)
            effects_logger.debug(f"Creating {etype} status effect with duration={duration}")
            if cls:
                if duration is not None:
                    return cls(duration=duration)
                else:
                    return cls()
            return NullEffect()

        # Fallback: heal, buff, debuff, status, etc.
        effects_logger.debug(f"Delegating effect creation to registry for ID: {eid}")
        return EffectRegistry.get(eid)
