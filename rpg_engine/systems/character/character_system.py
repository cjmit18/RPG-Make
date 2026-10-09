"""
Character System - Main character lifecycle management

Provides async character creation, management, and state transitions
using the state machine framework with comprehensive character features.
"""
import asyncio
import time
import uuid
from typing import Dict, List, Optional, Protocol, Any, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

from ...core.service_container import ServiceContainer, AsyncInitializable
from ...core.event_bus import EventBus, GameEvent
from ...core.config import Rarity, Grade

logger = logging.getLogger(__name__)


# Character creation state machine states
class CharacterCreationState(Enum):
    INITIALIZED = auto()
    TEMPLATE_SELECTED = auto()
    STATS_ALLOCATED = auto()
    SKILLS_SELECTED = auto()
    EQUIPMENT_CONFIGURED = auto()
    BACKGROUND_SELECTED = auto()
    APPEARANCE_CUSTOMIZED = auto()
    PREVIEW_GENERATED = auto()
    VALIDATED = auto()
    FINALIZED = auto()
    ERROR = auto()


# Character states
class CharacterState(Enum):
    ALIVE = "alive"
    UNCONSCIOUS = "unconscious"
    DEAD = "dead"
    RESTING = "resting"
    TRAVELING = "traveling"
    IN_COMBAT = "in_combat"
    CRAFTING = "crafting"
    TRADING = "trading"


# Character-related events
@dataclass(frozen=True)
class CharacterCreatedEvent(GameEvent):
    character_id: str = ""
    character_name: str = ""
    character_type: str = ""
    initial_stats: Dict[str, int] = field(default_factory=dict)
    template_id: Optional[str] = None


@dataclass(frozen=True)
class CharacterUpdatedEvent(GameEvent):
    character_id: str = ""
    field_changed: str = ""
    old_value: Any = None
    new_value: Any = None


@dataclass(frozen=True)
class CharacterLevelUpEvent(GameEvent):
    character_id: str = ""
    old_level: int = 0
    new_level: int = 0
    stat_increases: Dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class CharacterStateChangedEvent(GameEvent):
    character_id: str = ""
    old_state: str = ""
    new_state: str = ""
    reason: str = ""


@dataclass(frozen=True)
class CharacterRelationshipChangedEvent(GameEvent):
    character_id: str = ""
    other_character_id: str = ""
    relationship_type: str = ""
    old_value: int = 0
    new_value: int = 0


@dataclass(frozen=True)
class CharacterDeathEvent(GameEvent):
    character_id: str = ""
    cause_of_death: str = ""
    location: Optional[str] = None


@dataclass(frozen=True)
class CharacterResurrectedEvent(GameEvent):
    character_id: str = ""
    resurrection_method: str = ""
    stat_penalties: Dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class CharacterCreationStartedEvent(GameEvent):
    user_id: str = ""
    session_id: str = ""


@dataclass(frozen=True)
class CharacterTemplateSelectedEvent(GameEvent):
    user_id: str = ""
    session_id: str = ""
    template_id: str = ""


@dataclass(frozen=True)
class CharacterDeletedEvent(GameEvent):
    character_id: str = ""


# Character template for creation
@dataclass
class CharacterTemplate:
    """Template for character creation"""
    id: str
    name: str
    description: str
    character_class: str
    base_stats: Dict[str, int]
    starting_skills: List[str]
    starting_equipment: List[str]
    background: str
    personality_traits: List[str]
    appearance_options: Dict[str, List[str]]
    rarity: Rarity = Rarity.COMMON
    grade: Grade = Grade.ONE
    stat_point_budget: int = 20
    
    def __post_init__(self):
        if not self.personality_traits:
            self.personality_traits = []
        if not self.appearance_options:
            self.appearance_options = {}


# Character background information
@dataclass
class CharacterBackground:
    """Character background and history"""
    background_type: str
    origin_location: str
    family_status: str
    occupation: str
    notable_events: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    fears: List[str] = field(default_factory=list)
    allies: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)


# Character appearance
@dataclass
class CharacterAppearance:
    """Physical appearance of character"""
    height: str = "average"
    build: str = "average"
    hair_color: str = "brown"
    hair_style: str = "short"
    eye_color: str = "brown"
    skin_tone: str = "medium"
    distinguishing_features: List[str] = field(default_factory=list)
    clothing_style: str = "practical"


# Character relationships
@dataclass
class CharacterRelationship:
    """Relationship between characters"""
    other_character_id: str
    relationship_type: str  # "friend", "enemy", "neutral", "family", "romantic", etc.
    relationship_value: int  # -100 to 100, where negative is hostile, positive is friendly
    relationship_history: List[str] = field(default_factory=list)
    last_interaction: float = 0.0


# Enhanced Character data model
@dataclass
class Character:
    """Enhanced character data structure with comprehensive information"""
    id: str
    name: str
    character_class: str
    level: int
    experience: int
    base_stats: Dict[str, int]
    derived_stats: Dict[str, int]
    skills: List[str]
    equipment: Dict[str, Optional[str]]
    inventory: List[str]
    created_at: float
    last_updated: float
    
    # Enhanced character information
    template_id: Optional[str] = None
    current_state: CharacterState = CharacterState.ALIVE
    current_health: int = 100
    current_mana: int = 50
    current_location: Optional[str] = None
    background: Optional[CharacterBackground] = None
    appearance: Optional[CharacterAppearance] = None
    personality_traits: List[str] = field(default_factory=list)
    relationships: Dict[str, CharacterRelationship] = field(default_factory=dict)
    rarity: Rarity = Rarity.COMMON
    grade: Grade = Grade.ONE
    
    # Character flags and conditions
    is_player_character: bool = False
    is_companion: bool = False
    is_merchant: bool = False
    is_quest_giver: bool = False
    active_conditions: List[str] = field(default_factory=list)  # "poisoned", "blessed", etc.
    
    # Progression tracking
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    enemies_defeated: int = 0
    quests_completed: int = 0
    items_crafted: int = 0
    distance_traveled: float = 0.0
    
    # Death/resurrection tracking
    death_count: int = 0
    resurrection_count: int = 0
    last_death_time: Optional[float] = None
    
    def __post_init__(self):
        if self.background is None:
            self.background = CharacterBackground(
                background_type="unknown",
                origin_location="unknown",
                family_status="unknown",
                occupation="adventurer"
            )
        if self.appearance is None:
            self.appearance = CharacterAppearance()


# Character Repository Interface
class CharacterRepository:
    """Repository interface for character data persistence"""
    
    async def save_character(self, character: Character) -> bool:
        """Save character to persistent storage"""
        raise NotImplementedError
    
    async def load_character(self, character_id: str) -> Optional[Character]:
        """Load character from persistent storage"""
        raise NotImplementedError
    
    async def delete_character(self, character_id: str) -> bool:
        """Delete character from persistent storage"""
        raise NotImplementedError
    
    async def list_characters(self, user_id: Optional[str] = None) -> List[Character]:
        """List all characters for a user or all characters"""
        raise NotImplementedError
    
    async def search_characters(self, criteria: Dict[str, Any]) -> List[Character]:
        """Search characters by criteria"""
        raise NotImplementedError


# Memory-based implementation for development
class InMemoryCharacterRepository(CharacterRepository):
    """In-memory character repository for development and testing"""
    
    def __init__(self):
        self._characters: Dict[str, Character] = {}
        self.logger = logging.getLogger(__name__)
    
    async def save_character(self, character: Character) -> bool:
        """Save character to memory"""
        try:
            character.last_updated = time.time()
            self._characters[character.id] = character
            self.logger.debug(f"Saved character {character.name} ({character.id})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save character {character.id}: {e}")
            return False
    
    async def load_character(self, character_id: str) -> Optional[Character]:
        """Load character from memory"""
        try:
            character = self._characters.get(character_id)
            if character:
                self.logger.debug(f"Loaded character {character.name} ({character_id})")
            return character
        except Exception as e:
            self.logger.error(f"Failed to load character {character_id}: {e}")
            return None
    
    async def delete_character(self, character_id: str) -> bool:
        """Delete character from memory"""
        try:
            if character_id in self._characters:
                character = self._characters.pop(character_id)
                self.logger.debug(f"Deleted character {character.name} ({character_id})")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete character {character_id}: {e}")
            return False
    
    async def list_characters(self, user_id: Optional[str] = None) -> List[Character]:
        """List all characters"""
        try:
            characters = list(self._characters.values())
            self.logger.debug(f"Listed {len(characters)} characters")
            return characters
        except Exception as e:
            self.logger.error(f"Failed to list characters: {e}")
            return []
    
    async def search_characters(self, criteria: Dict[str, Any]) -> List[Character]:
        """Search characters by criteria"""
        try:
            results = []
            for character in self._characters.values():
                match = True
                for key, value in criteria.items():
                    if hasattr(character, key):
                        if getattr(character, key) != value:
                            match = False
                            break
                if match:
                    results.append(character)
            self.logger.debug(f"Found {len(results)} characters matching criteria")
            return results
        except Exception as e:
            self.logger.error(f"Failed to search characters: {e}")
            return []


# Character creation workflow state machine
class CharacterCreationWorkflow:
    """Manages the character creation process"""
    
    def __init__(self, service_container):
        self.service_container = service_container
        self.event_bus = None  # Will be set during initialization
        self.logger = logging.getLogger(__name__)
        
        # Available character templates
        self.character_templates: Dict[str, CharacterTemplate] = {}
        self.load_default_templates()
    
    def load_default_templates(self):
        """Load default character templates"""
        # Example warrior template
        warrior_template = CharacterTemplate(
            id="warrior_basic",
            name="Basic Warrior",
            description="A strong melee combatant with high defense",
            character_class="Warrior",
            base_stats={
                "strength": 16,
                "constitution": 14,
                "dexterity": 12,
                "intelligence": 8,
                "wisdom": 10,
                "charisma": 10
            },
            starting_skills=["sword_fighting", "heavy_armor", "intimidation"],
            starting_equipment=["iron_sword", "leather_armor", "wooden_shield"],
            background="soldier",
            personality_traits=["brave", "loyal", "disciplined"],
            appearance_options={
                "build": ["muscular", "stocky", "tall"],
                "hair_color": ["brown", "black", "blonde"],
                "eye_color": ["brown", "blue", "green"]
            }
        )
        
        # Example mage template
        mage_template = CharacterTemplate(
            id="mage_basic",
            name="Basic Mage",
            description="A scholarly spellcaster with arcane knowledge",
            character_class="Mage",
            base_stats={
                "strength": 8,
                "constitution": 10,
                "dexterity": 12,
                "intelligence": 16,
                "wisdom": 14,
                "charisma": 10
            },
            starting_skills=["arcane_magic", "scholarly_lore", "meditation"],
            starting_equipment=["oak_staff", "apprentice_robes", "spell_component_pouch"],
            background="scholar",
            personality_traits=["curious", "methodical", "studious"],
            appearance_options={
                "build": ["slender", "average", "frail"],
                "hair_color": ["gray", "white", "brown"],
                "eye_color": ["blue", "gray", "violet"]
            },
            rarity=CharacterRarity.UNCOMMON
        )
        
        # Example rogue template
        rogue_template = CharacterTemplate(
            id="rogue_basic",
            name="Basic Rogue",
            description="A nimble and stealthy character skilled in subterfuge",
            character_class="Rogue",
            base_stats={
                "strength": 10,
                "constitution": 12,
                "dexterity": 16,
                "intelligence": 12,
                "wisdom": 14,
                "charisma": 8
            },
            starting_skills=["stealth", "lockpicking", "sleight_of_hand"],
            starting_equipment=["thieves_tools", "leather_armor", "short_sword"],
            background="criminal",
            personality_traits=["sneaky", "opportunistic", "independent"],
            appearance_options={
                "build": ["lithe", "average", "compact"],
                "hair_color": ["black", "brown", "dark_blonde"],
                "eye_color": ["green", "brown", "hazel"]
            }
        )
        
        self.character_templates = {
            "warrior_basic": warrior_template,
            "mage_basic": mage_template,
            "rogue_basic": rogue_template
        }
    
    async def start_character_creation(self, user_id: str) -> Dict[str, Any]:
        """Start the character creation process"""
        try:
            creation_data = {
                "user_id": user_id,
                "session_id": str(uuid.uuid4()),
                "state": CharacterCreationState.INITIALIZED,
                "available_templates": list(self.character_templates.keys()),
                "selected_template": None,
                "character_data": {},
                "created_at": time.time()
            }
            
            await self.event_bus.publish(CharacterCreationStartedEvent(
                user_id=user_id,
                session_id=creation_data["session_id"],
                timestamp=creation_data["created_at"]
            ))
            
            self.logger.info(f"Started character creation for user {user_id}")
            return creation_data
            
        except Exception as e:
            self.logger.error(f"Failed to start character creation for user {user_id}: {e}")
            raise
    
    async def select_template(self, session_data: Dict[str, Any], template_id: str) -> Dict[str, Any]:
        """Select a character template"""
        try:
            if template_id not in self.character_templates:
                raise ValueError(f"Invalid template ID: {template_id}")
            
            template = self.character_templates[template_id]
            session_data["selected_template"] = template_id
            session_data["state"] = CharacterCreationState.BACKGROUND_SELECTED
            session_data["character_data"]["template"] = template
            
            await self.event_bus.publish(CharacterTemplateSelectedEvent(
                user_id=session_data["user_id"],
                session_id=session_data["session_id"],
                template_id=template_id,
                timestamp=time.time()
            ))
            
            self.logger.debug(f"Selected template {template_id} for session {session_data['session_id']}")
            return session_data
            
        except Exception as e:
            self.logger.error(f"Failed to select template {template_id}: {e}")
            raise
    
    async def customize_appearance(self, session_data: Dict[str, Any], appearance_data: Dict[str, str]) -> Dict[str, Any]:
        """Customize character appearance"""
        try:
            template = session_data["character_data"]["template"]
            
            # Validate appearance options against template
            for key, value in appearance_data.items():
                if key in template.appearance_options:
                    if value not in template.appearance_options[key]:
                        raise ValueError(f"Invalid {key} option: {value}")
            
            # Create appearance object
            appearance = CharacterAppearance(**appearance_data)
            session_data["character_data"]["appearance"] = appearance
            session_data["state"] = CharacterCreationState.APPEARANCE_CUSTOMIZED
            
            self.logger.debug(f"Customized appearance for session {session_data['session_id']}")
            return session_data
            
        except Exception as e:
            self.logger.error(f"Failed to customize appearance: {e}")
            raise
    
    async def finalize_character(self, session_data: Dict[str, Any], character_name: str) -> Character:
        """Finalize character creation"""
        try:
            template = session_data["character_data"]["template"]
            appearance = session_data["character_data"].get("appearance", CharacterAppearance())
            
            # Create background
            background = CharacterBackground(
                background_type=template.background,
                origin_location="starting_village",
                family_status="unknown",
                occupation=template.character_class.lower()
            )
            
            # Create character
            character = Character(
                id=str(uuid.uuid4()),
                name=character_name,
                character_class=template.character_class,
                level=1,
                experience=0,
                base_stats=template.base_stats.copy(),
                derived_stats=self._calculate_derived_stats(template.base_stats),
                skills=template.starting_skills.copy(),
                equipment={},
                inventory=template.starting_equipment.copy(),
                created_at=time.time(),
                last_updated=time.time(),
                template_id=template.id,
                background=background,
                appearance=appearance,
                personality_traits=template.personality_traits.copy(),
                rarity=template.rarity
            )
            
            await self.event_bus.publish(CharacterCreatedEvent(
                character_id=character.id,
                character_name=character_name,
                character_type=character.character_class,
                initial_stats=character.base_stats,
                template_id=character.template_id,
                timestamp=character.created_at
            ))
            
            self.logger.info(f"Created character {character_name} ({character.id})")
            return character
            
        except Exception as e:
            self.logger.error(f"Failed to finalize character: {e}")
            raise
    
    def _calculate_derived_stats(self, base_stats: Dict[str, int]) -> Dict[str, int]:
        """Calculate derived stats from base stats"""
        return {
            "health": base_stats.get("constitution", 10) * 10 + 50,
            "mana": base_stats.get("intelligence", 10) * 5 + 25,
            "armor_class": 10 + base_stats.get("dexterity", 10) // 2,
            "initiative": base_stats.get("dexterity", 10) // 2,
            "carry_capacity": base_stats.get("strength", 10) * 15
        }


# Service interfaces
class CharacterServiceInterface:
    """Interface for character-related services"""
    
    async def create_character(self, user_id: str, character_data: Dict[str, Any]) -> Character:
        """Create a new character"""
        raise NotImplementedError
    
    async def get_character(self, character_id: str) -> Optional[Character]:
        """Get character by ID"""
        raise NotImplementedError
    
    async def update_character(self, character: Character) -> bool:
        """Update character data"""
        raise NotImplementedError
    
    async def delete_character(self, character_id: str) -> bool:
        """Delete character"""
        raise NotImplementedError
    
    async def list_user_characters(self, user_id: str) -> List[Character]:
        """List all characters for a user"""
        raise NotImplementedError
    
    async def update_character_state(self, character_id: str, new_state: CharacterState) -> bool:
        """Update character state"""
        raise NotImplementedError
    
    async def handle_character_death(self, character_id: str, cause: str) -> bool:
        """Handle character death"""
        raise NotImplementedError
    
    async def resurrect_character(self, character_id: str, method: str) -> bool:
        """Resurrect a dead character"""
        raise NotImplementedError
    
    async def update_relationship(self, character_id: str, other_character_id: str, 
                                 relationship_type: str, relationship_value: int) -> bool:
        """Update relationship between characters"""
        raise NotImplementedError


# Main character system implementation
class CharacterSystem(CharacterServiceInterface):
    """Main character system managing all character-related operations"""
    
    def __init__(self, service_container):
        self.service_container = service_container
        self.event_bus = None  # Will be set during initialization
        self.repository = InMemoryCharacterRepository()  # Default to in-memory
        self.creation_workflow = CharacterCreationWorkflow(service_container)
        self.logger = logging.getLogger(__name__)
        
        # Character state tracking
        self._active_characters: Dict[str, Character] = {}
        self._character_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Register event handlers
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Register event handlers for character-related events"""
        # We'll implement these as the event bus system is developed
        pass
    
    async def initialize(self) -> bool:
        """Initialize the character system"""
        try:
            # Initialize event bus
            self.event_bus = await self.service_container.get_service(EventBus)
            
            # Initialize creation workflow event bus
            self.creation_workflow.event_bus = self.event_bus
            
            # Load any persistent character data
            characters = await self.repository.list_characters()
            for character in characters:
                self._active_characters[character.id] = character
            
            self.logger.info(f"Character system initialized with {len(characters)} characters")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize character system: {e}")
            return False
    
    async def create_character(self, user_id: str, character_data: Dict[str, Any]) -> Character:
        """Create a new character using the creation workflow"""
        try:
            # Start character creation workflow
            session_data = await self.creation_workflow.start_character_creation(user_id)
            
            # Process creation steps based on provided data
            if "template_id" in character_data:
                session_data = await self.creation_workflow.select_template(
                    session_data, character_data["template_id"]
                )
            
            if "appearance" in character_data:
                session_data = await self.creation_workflow.customize_appearance(
                    session_data, character_data["appearance"]
                )
            
            # Finalize character
            character_name = character_data.get("name", "Unnamed Character")
            character = await self.creation_workflow.finalize_character(session_data, character_name)
            
            # Save to repository
            await self.repository.save_character(character)
            self._active_characters[character.id] = character
            
            self.logger.info(f"Created character {character.name} for user {user_id}")
            return character
            
        except Exception as e:
            self.logger.error(f"Failed to create character for user {user_id}: {e}")
            raise
    
    async def get_character(self, character_id: str) -> Optional[Character]:
        """Get character by ID"""
        try:
            # Check active characters first
            if character_id in self._active_characters:
                return self._active_characters[character_id]
            
            # Load from repository
            character = await self.repository.load_character(character_id)
            if character:
                self._active_characters[character_id] = character
            
            return character
            
        except Exception as e:
            self.logger.error(f"Failed to get character {character_id}: {e}")
            return None
    
    async def update_character(self, character: Character) -> bool:
        """Update character data"""
        try:
            success = await self.repository.save_character(character)
            if success:
                self._active_characters[character.id] = character
                
                await self.event_bus.publish(CharacterUpdatedEvent(
                    character_id=character.id,
                    field_changed="character_data",
                    old_value=None,
                    new_value=character.name,
                    timestamp=time.time()
                ))
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update character {character.id}: {e}")
            return False
    
    async def delete_character(self, character_id: str) -> bool:
        """Delete character"""
        try:
            success = await self.repository.delete_character(character_id)
            if success:
                self._active_characters.pop(character_id, None)
                
                await self.event_bus.publish(CharacterDeletedEvent(
                    character_id=character_id,
                    timestamp=time.time()
                ))
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete character {character_id}: {e}")
            return False
    
    async def list_user_characters(self, user_id: str) -> List[Character]:
        """List all characters for a user"""
        try:
            # For now, we'll return all characters since we don't have user tracking
            # This should be enhanced when user system is implemented
            return await self.repository.list_characters()
            
        except Exception as e:
            self.logger.error(f"Failed to list characters for user {user_id}: {e}")
            return []
    
    async def update_character_state(self, character_id: str, new_state: CharacterState) -> bool:
        """Update character state"""
        try:
            character = await self.get_character(character_id)
            if not character:
                return False
            
            old_state = character.current_state
            character.current_state = new_state
            
            success = await self.update_character(character)
            if success:
                await self.event_bus.publish(CharacterStateChangedEvent(
                    character_id=character_id,
                    old_state=old_state.value,
                    new_state=new_state.value,
                    timestamp=time.time()
                ))
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update character state for {character_id}: {e}")
            return False
    
    async def handle_character_death(self, character_id: str, cause: str) -> bool:
        """Handle character death"""
        try:
            character = await self.get_character(character_id)
            if not character:
                return False
            
            # Update character state and death tracking
            character.current_state = CharacterState.DEAD
            character.death_count += 1
            character.last_death_time = time.time()
            character.current_health = 0
            
            success = await self.update_character(character)
            if success:
                await self.event_bus.publish(CharacterDeathEvent(
                    character_id=character_id,
                    character_name=character.name,
                    cause=cause,
                    death_count=character.death_count,
                    timestamp=character.last_death_time
                ))
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to handle death for character {character_id}: {e}")
            return False
    
    async def resurrect_character(self, character_id: str, method: str) -> bool:
        """Resurrect a dead character"""
        try:
            character = await self.get_character(character_id)
            if not character or character.current_state != CharacterState.DEAD:
                return False
            
            # Update character state and resurrection tracking
            character.current_state = CharacterState.ALIVE
            character.resurrection_count += 1
            character.current_health = character.derived_stats.get("health", 100) // 2  # Half health
            
            success = await self.update_character(character)
            if success:
                await self.event_bus.publish(CharacterResurrectedEvent(
                    character_id=character_id,
                    character_name=character.name,
                    method=method,
                    resurrection_count=character.resurrection_count,
                    timestamp=time.time()
                ))
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to resurrect character {character_id}: {e}")
            return False
    
    async def update_relationship(self, character_id: str, other_character_id: str, 
                                 relationship_type: str, relationship_value: int) -> bool:
        """Update relationship between characters"""
        try:
            character = await self.get_character(character_id)
            if not character:
                return False
            
            # Create or update relationship
            relationship = CharacterRelationship(
                other_character_id=other_character_id,
                relationship_type=relationship_type,
                relationship_value=relationship_value,
                last_interaction=time.time()
            )
            
            character.relationships[other_character_id] = relationship
            
            success = await self.update_character(character)
            if success:
                await self.event_bus.publish(CharacterRelationshipChangedEvent(
                    character_id=character_id,
                    other_character_id=other_character_id,
                    relationship_type=relationship_type,
                    relationship_value=relationship_value,
                    timestamp=time.time()
                ))
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update relationship for character {character_id}: {e}")
            return False
    
    # Additional utility methods
    async def get_characters_by_class(self, character_class: str) -> List[Character]:
        """Get all characters of a specific class"""
        try:
            criteria = {"character_class": character_class}
            return await self.repository.search_characters(criteria)
        except Exception as e:
            self.logger.error(f"Failed to get characters by class {character_class}: {e}")
            return []
    
    async def get_characters_by_level_range(self, min_level: int, max_level: int) -> List[Character]:
        """Get characters within a level range"""
        try:
            all_characters = await self.repository.list_characters()
            return [c for c in all_characters if min_level <= c.level <= max_level]
        except Exception as e:
            self.logger.error(f"Failed to get characters by level range: {e}")
            return []
    
    async def get_character_statistics(self) -> Dict[str, Any]:
        """Get overall character statistics"""
        try:
            characters = await self.repository.list_characters()
            
            stats = {
                "total_characters": len(characters),
                "characters_by_class": {},
                "characters_by_state": {},
                "characters_by_level": {},
                "average_level": 0,
                "total_deaths": 0,
                "total_resurrections": 0
            }
            
            if characters:
                # Calculate statistics
                total_level = 0
                for character in characters:
                    # By class
                    class_name = character.character_class
                    stats["characters_by_class"][class_name] = stats["characters_by_class"].get(class_name, 0) + 1
                    
                    # By state
                    state_name = character.current_state.value
                    stats["characters_by_state"][state_name] = stats["characters_by_state"].get(state_name, 0) + 1
                    
                    # By level
                    level = character.level
                    stats["characters_by_level"][level] = stats["characters_by_level"].get(level, 0) + 1
                    total_level += level
                    
                    # Deaths and resurrections
                    stats["total_deaths"] += character.death_count
                    stats["total_resurrections"] += character.resurrection_count
                
                stats["average_level"] = total_level / len(characters)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get character statistics: {e}")
            return {}
    
    async def shutdown(self) -> bool:
        """Shutdown the character system"""
        try:
            # Save any pending character data
            for character in self._active_characters.values():
                await self.repository.save_character(character)
            
            self._active_characters.clear()
            self._character_sessions.clear()
            
            self.logger.info("Character system shut down successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown character system: {e}")
            return False
