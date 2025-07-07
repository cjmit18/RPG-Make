# game_sys/magic/enchanting_manager.py

from typing import List, Dict, Any


class EnchantingManager:
    """
    Manager for handling enchantment operations between UI and the enchantment
    system. Provides a centralized interface for enchanting functions.
    """

    def __init__(self):
        """Initialize the enchanting manager."""
        pass

    def initialize_actor_enchanting(self, actor) -> None:
        """
        Initialize enchanting system for an actor if needed.
        
        Args:
            actor: The actor to initialize enchanting for
        """
        if (not hasattr(actor, 'enchanting_system') or 
                actor.enchanting_system is None):
            from game_sys.magic.enchanting_system import EnchantingSystem
            actor.enchanting_system = EnchantingSystem(actor)
        
        # Ensure known_enchantments list exists
        if not hasattr(actor, 'known_enchantments'):
            actor.known_enchantments = []
            
    def get_known_enchantments(self, actor) -> List[str]:
        """
        Get the enchantments known by an actor.
        
        Args:
            actor: The actor to get enchantments for
            
        Returns:
            List[str]: List of enchantment IDs
        """
        self.initialize_actor_enchanting(actor)
        return actor.enchanting_system.get_known_enchantments()
    
    def get_unlearned_enchantments(self, actor) -> List[str]:
        """
        Get enchantments not yet learned by an actor.
        
        Args:
            actor: The actor to get unlearned enchantments for
            
        Returns:
            List[str]: List of unlearned enchantment IDs
        """
        self.initialize_actor_enchanting(actor)
        return actor.enchanting_system.get_unlearned_enchantments()
    
    def get_enchantable_items(self, actor) -> List[Any]:
        """
        Get items in the actor's inventory that can be enchanted.
        
        Args:
            actor: The actor to get enchantable items for
            
        Returns:
            List[Any]: List of enchantable items
        """
        self.initialize_actor_enchanting(actor)
        return actor.enchanting_system.get_enchantable_items()
    
    def learn_enchantment(self, actor, enchant_id: str) -> bool:
        """
        Have the actor learn a new enchantment.
        
        Args:
            actor: The actor learning the enchantment
            enchant_id: The ID of the enchantment to learn
            
        Returns:
            bool: True if learned successfully, False otherwise
        """
        self.initialize_actor_enchanting(actor)
        return actor.enchanting_system.learn_enchantment(enchant_id)
    
    def apply_enchantment(self, actor, enchant_id: str, item) -> bool:
        """
        Apply an enchantment to an item.
        
        Args:
            actor: The actor applying the enchantment
            enchant_id: The ID of the enchantment to apply
            item: The item to enchant
            
        Returns:
            bool: True if applied successfully, False otherwise
        """
        self.initialize_actor_enchanting(actor)
        return actor.enchanting_system.apply_enchantment(enchant_id, item)
    
    def get_enchantment_info(self, actor, enchant_id: str) -> Dict:
        """
        Get information about an enchantment.
        
        Args:
            actor: The actor requesting enchantment info
            enchant_id: The ID of the enchantment
            
        Returns:
            Dict: Enchantment information
        """
        self.initialize_actor_enchanting(actor)
        return actor.enchanting_system.get_enchantment_info(enchant_id)


# Create a global instance for convenient access
enchanting_manager = EnchantingManager()
