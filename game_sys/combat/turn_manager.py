# game_sys/combat/turn_manager.py
"""
TurnManager
-----------
Bridges TimeManager -> ActionQueue -> CombatEngine.
Every tick:
    * Pull ready actions from each actor's queue.
    * Dispatch to CombatEngine for execution.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict
import time

if TYPE_CHECKING:
    from game_sys.character.actor import Actor

from game_sys.managers.factories import get_action_queue
from game_sys.managers.time_manager import time_manager
from game_sys.logging import combat_logger, log_exception
from .engine import CombatEngine

_action_queue = get_action_queue()


class TurnManager:
    def __init__(self) -> None:
        self._actors: List[Actor] = []
        self._engine = CombatEngine()  # Each TurnManager gets its own engine
        self._casting_states: Dict[str, Dict] = {}  # actor_id -> spell_state
        combat_logger.info("TurnManager initialized")

    # ------------------------------------------------------------------ #
    #  registration                                                      #
    # ------------------------------------------------------------------ #
    def register(self, actor: "Actor") -> None:
        if actor not in self._actors:
            self._actors.append(actor)
            combat_logger.info(f"Registered actor {actor.name} with TurnManager")

    def unregister(self, actor: "Actor") -> None:
        """Remove actor from turn management (called when actor dies)."""
        if actor in self._actors:
            self._actors.remove(actor)
            combat_logger.info(f"Unregistered actor {actor.name} from TurnManager")
        # Clean up any casting states
        actor_id = getattr(actor, 'id', str(id(actor)))
        if actor_id in self._casting_states:
            del self._casting_states[actor_id]
            combat_logger.debug(f"Cleaned up casting state for {actor.name}")

    # ------------------------------------------------------------------ #
    #  tick driver                                                       #
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    #  tick driver                                                       #
    # ------------------------------------------------------------------ #
    def tick(self, dt: float) -> None:
        # Let ActionQueue advance cooldowns first
        _action_queue.tick(dt)

        # Execute all ready actions
        for actor in list(self._actors):
            for name, payload in _action_queue.consume(actor):
                if name == "attack":
                    tgt_list = payload.get("targets", [])
                    self._engine.execute_attack_sync(actor, tgt_list)
                elif name == "cast":
                    # Handle spell casting with wind-up delay
                    self._handle_spell_cast(actor, payload)
                elif name == "cast_complete":
                    # Handle spell execution after wind-up
                    self._handle_spell_execution(actor, payload)

    @log_exception
    def _handle_spell_cast(self, actor: "Actor", payload: dict) -> None:
        """
        Handle initial spell casting with wind-up delay.
        
        Args:
            actor: The casting actor
            payload: Spell data including targets, spell_id, wind_up_time
        """
        spell_id = payload.get("spell_id", "")
        targets = payload.get("targets", [])
        wind_up_time = payload.get("wind_up_time", 1.0)
        
        combat_logger.info(
            f"{actor.name} begins casting {spell_id} on "
            f"{len(targets)} target(s)"
        )
        
        # Store spell state using actor ID
        actor_id = getattr(actor, 'id', str(id(actor)))
        
        self._casting_states[actor_id] = {
            'targets': targets,
            'wind_up_time': wind_up_time,
            'spell_id': spell_id
        }
        
        # Schedule the actual spell execution after wind-up
        _action_queue.schedule(
            actor,
            "cast_complete",
            {"spell_id": spell_id, "targets": targets},
            wind_up_time
        )
        
        # Emit spell casting started event
        from game_sys.hooks.hooks_setup import emit, ON_ABILITY_CAST
        emit(ON_ABILITY_CAST, actor=actor, ability_id=spell_id,
             targets=targets, phase="start")
        combat_logger.debug(f"Emitted ON_ABILITY_CAST event with phase=start")

    @log_exception
    def _handle_spell_execution(self, actor: "Actor", payload: dict) -> None:
        """
        Execute spell after wind-up delay completes.
        
        Args:
            actor: The casting actor
            payload: Spell execution data
        """
        spell_id = payload.get("spell_id", "")
        targets = payload.get("targets", [])
        actor_id = getattr(actor, 'id', str(id(actor)))
        
        combat_logger.info(
            f"{actor.name} completing spell cast: {spell_id} on "
            f"{len(targets)} target(s)"
        )
        
        # Verify spell casting wasn't interrupted
        if actor_id in self._casting_states:
            # Clean up casting state
            del self._casting_states[actor_id]
            combat_logger.debug(f"Cleared casting state for {actor.name}")
            
            # Execute the spell through combat engine
            # Store spell info temporarily for engine detection
            spell_info = {
                'id': spell_id,
                'targets': targets
            }
            
            combat_logger.debug(f"Executing spell: {spell_info}")
            
            try:
                # Execute using spell pathway
                outcome = self._execute_spell_attack(actor, targets, spell_info)
                
                # Emit spell completion event
                from game_sys.hooks.hooks_setup import emit, ON_ABILITY_CAST
                emit(ON_ABILITY_CAST, actor=actor, ability_id=spell_id,
                     targets=targets, phase="complete", outcome=outcome)
            except Exception as e:
                # Handle spell failure
                from game_sys.hooks.hooks_setup import emit, ON_ABILITY_CAST
                emit(ON_ABILITY_CAST, actor=actor, ability_id=spell_id,
                     targets=targets, phase="failed", error=str(e))

    def _execute_spell_attack(self, actor: "Actor", targets: list, 
                              spell_info: dict):
        """
        Execute spell attack through combat engine.
        
        Args:
            actor: The casting actor
            targets: List of target actors
            spell_info: Spell information dictionary
            
        Returns:
            Combat outcome from spell execution
        """
        # Store spell info in casting states for engine access
        actor_id = getattr(actor, 'id', str(id(actor)))
        
        # Ensure casting state exists for this actor
        if actor_id not in self._casting_states:
            self._casting_states[actor_id] = {}
        
        self._casting_states[actor_id]['executing'] = True
        
        # Set temporary spell state on actor for combat engine detection
        actor._spell_state = True
        
        # Set the spell ID directly on the actor for the engine to access
        spell_id = spell_info.get('id')
        if spell_id:
            actor.pending_spell = spell_id
            print(f"DEBUG: Set pending_spell={spell_id} on actor {actor.name}")
        
        try:
            # Execute through combat engine (no weapon, spell-based)
            print(f"DEBUG: Executing spell attack with pending_spell={getattr(actor, 'pending_spell', None)}")
            print(f"DEBUG: Actor _spell_state={getattr(actor, '_spell_state', False)}")
            
            return self._engine.execute_attack_sync(
                actor, targets, weapon=None
            )
        finally:
            # Clean up execution state
            if hasattr(actor, '_spell_state'):
                delattr(actor, '_spell_state')
            if hasattr(actor, 'pending_spell'):
                delattr(actor, 'pending_spell')
            if (actor_id in self._casting_states and
                    'executing' in self._casting_states[actor_id]):
                del self._casting_states[actor_id]['executing']

    def interrupt_casting(self, actor: "Actor") -> bool:
        """
        Interrupt any ongoing spell casting for an actor.
        
        Args:
            actor: The actor whose casting should be interrupted
            
        Returns:
            True if casting was interrupted, False if not casting
        """
        actor_id = getattr(actor, 'id', str(id(actor)))
        if actor_id in self._casting_states:
            del self._casting_states[actor_id]
            return True
        return False


# ------------------------------------------------------------------ #
#  singleton & registration with TimeManager                         #
# ------------------------------------------------------------------ #
turn_manager = TurnManager()
time_manager.register(turn_manager)
