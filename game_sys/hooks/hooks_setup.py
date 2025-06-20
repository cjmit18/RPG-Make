# game_sys/core/hooks_setup.py

from game_sys.hooks.hooks import hook_dispatcher
from game_sys.effects.base import Effect
from logs.logs import get_logger

log = get_logger(__name__)

"""
Central hook setup: register listeners for key game events across the codebase.
Import this module once at startup (e.g. in game_sys/__init__.py or your main)
to wire up logging, passive effects, combat hooks, inventory analytics, etc.
"""

# --- Passive Equip/Unequip ------------------------------------------------


def _on_passive_equip(item, user, effect_data):
    """
    When an item is equipped, instantiate & register its passive Effect.
    effect_data must be a dict containing at least 'type' (and ideally 'id').
    """
    try:
        eff = Effect.from_dict(effect_data)
        eff.register(user)
        # ensure actor has passive_effects storage
        if not hasattr(user, "passive_effects"):
            user.passive_effects = {}
        key = effect_data.get("id", effect_data.get("type"))
        user.passive_effects[key] = eff
        log.info(f"Registered passive '{key}' for {user.name} from {item.name}")
    except Exception as e:
        log.error(f"Failed to register passive {effect_data} for {user.name}: {e}")


hook_dispatcher.register("item.passive.equip",   _on_passive_equip)


def _on_passive_unequip(item, user, effect_data):
    """
    When an item is unequipped, unregister & remove its passive Effect.
    """
    key = effect_data.get("id", effect_data.get("type"))
    eff = getattr(user, "passive_effects", {}).pop(key, None)
    if eff:
        try:
            eff.unregister(user)
            log.info(f"Unregistered passive '{key}' for {user.name} removed {item.name}")
        except Exception as e:
            log.error(f"Failed to unregister passive {key} for {user.name}: {e}")


hook_dispatcher.register("item.passive.unequip", _on_passive_unequip)


# --- Inventory Events ------------------------------------------------------

def _on_item_added(inventory, item, quantity, **_):
    log.info(f"Inventory: {inventory.owner.name} gained {quantity}× {item.name}")


hook_dispatcher.register("inventory.item_added", _on_item_added)


def _on_item_removed(inventory, item_id, quantity, **_):
    log.info(f"Inventory: {inventory.owner.name} lost {quantity}× {item_id}")


hook_dispatcher.register("inventory.item_removed", _on_item_removed)


# --- Equip/Unequip Logging ------------------------------------------------

def _on_equip(inventory, slot, item, **_):
    log.info(f"{inventory.owner.name} equipped {item.name} in slot '{slot}'")


hook_dispatcher.register("inventory.equip", _on_equip)


def _on_unequip(inventory, slot, item, **_):
    log.info(f"{inventory.owner.name} unequipped {item.name} from slot '{slot}'")


hook_dispatcher.register("inventory.unequip", _on_unequip)


# --- Combat & Effects ------------------------------------------------------

def _before_effect(effect, caster, target, **_):
    log.debug(f"{caster.name} about to apply effect {effect.get('id')} to {getattr(target,'name','')}")


hook_dispatcher.register("effect.before_apply", _before_effect)


def _after_effect(effect, caster, target, result, **_):
    log.debug(f"{caster.name} applied effect {effect.get('id')} with result {result}")


hook_dispatcher.register("effect.after_apply", _after_effect)


def _before_damage(actor, amount, damage_type, **_):
    log.debug(f"{actor.name} will take {amount} {getattr(damage_type,'name','')} damage")


hook_dispatcher.register("actor.before_damage", _before_damage)


def _after_damage(actor, amount, damage_type, **_):
    log.debug(f"{actor.name} took {amount} {getattr(damage_type,'name','')} damage; HP now {actor.current_health}")


hook_dispatcher.register("actor.after_damage", _after_damage)


# --- Resource & Status -----------------------------------------------------

def _on_heal(actor, amount, **_):
    log.info(f"{actor.name} healed {amount} HP")


hook_dispatcher.register("actor.healed", _on_heal)


def _on_mana(actor, amount, **_):
    log.info(f"{actor.name} used {amount} MP")


hook_dispatcher.register("actor.mana_drained", _on_mana)


def _on_status_added(actor, effect, **_):
    log.info(f"{actor.name} gained status '{effect.name}'")


hook_dispatcher.register("actor.status_added", _on_status_added)


def _on_status_expired(actor, effect, **_):
    log.info(f"{actor.name}'s status '{effect.name}' expired")

    
hook_dispatcher.register("actor.status_expired", _on_status_expired)
