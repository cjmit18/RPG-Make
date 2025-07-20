# Spell and Enchantment Elemental System

## Overview

This document explains the implementation of elemental damage effects for both enchantments and spells, ensuring they interact properly with enemy resistances and weaknesses.

## Key Components

### 1. Damage Types

All damage in the system is associated with a DamageType:
- PHYSICAL
- FIRE
- ICE
- LIGHTNING
- POISON
- ARCANE
- HOLY
- DARK
- MAGIC

### 2. Resistances and Weaknesses

Enemies can have resistances and weaknesses to specific damage types:
- Resistances reduce incoming damage (e.g., 50% fire resistance = half damage)
- Weaknesses increase incoming damage (e.g., 50% ice weakness = 50% more damage)

### 3. Enchantment System

Weapon enchantments:
- Add elemental damage (fire, ice, lightning)
- Set the weapon's damage_type property
- Provide stat boosts related to the element

### 4. Spell System

Spells have specific damage types:
- Fireball uses FIRE damage
- Ice Shard uses ICE damage
- Magic Missile uses MAGIC damage

## Implementation Details

### Enemy Setup

Different enemy types have appropriate resistances and weaknesses:
- Dragons: Resist fire (75%), weak to ice (50%)
- Orcs: Resist physical (40%), weak to fire (30%)
- Goblins: Weak to fire/lightning (40%), poison (25%)

### Weapon Attacks

1. When a player attacks with an enchanted weapon:
   - The weapon's damage_type is used for the attack
   - Enemy resistance/weakness is applied
   - Combat log shows appropriate messages

### Spell Casting

1. When a player casts a spell:
   - The spell's damage_type is determined (FIRE for Fireball, ICE for Ice Shard)
   - Enemy resistance/weakness is applied
   - Combat log shows appropriate messages

## User Interface

The user receives clear feedback about elemental interactions:
1. Weapon attacks show: "[Player] attacks [Enemy] with [Weapon] for X [Element] damage!"
2. Spells show: "[Player] casts [Spell] for X [Element] damage!"
3. Resistance messages: "The [Enemy] resists [Element]! (-X% damage)"
4. Weakness messages: "The [Enemy] is weak to [Element]! (+X% damage)"

## Future Improvements

1. Add more complex elemental interactions (e.g., fire melts ice)
2. Implement visual indicators for resistances/weaknesses
3. Add player resistances/weaknesses to enemy attacks
4. Introduce equipment that provides resistances
