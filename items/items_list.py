"""MODULE CONTAINING LIST OF ITEM OBJECTS USED IN THE GAME"""
import logging
import uuid
import core.experience_functions as experience_functions
import gen
import random
class Item:
	"""Base class for all items in the game."""
	slot: str = None
	def __init__(self, 
			  	name: str = "Item",
			   	description: str = "A basic item",
				price: int = 0,
				lvl: int = 0) -> None:
		self.id: uuid = uuid.uuid4()
		self.name: str = name
		self.description: str = description
		self.price: int  = price
		self.quantity: int = 1
		self.lvls = experience_functions.Levels(self, lvl)
	def stat_mod(self) -> dict[str, int]:
		"""Return a dictionary of stat modifiers for the item."""
		"""Default is empty, but subclasses can override this to provide specific stat modifiers."""
		return {}
	def __str__(self) -> str:
		return f"Item: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvls.lvl}, ID: {self.id}"
	def __repr__(self) -> str:
		return f"Item: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvls.lvl}, ID: {self.id}"
	def to_dict(self) -> dict:
		"""Convert the item to a dictionary representation."""
		return {
			"id": str(self.id),
			"name": self.name,
			"description": self.description,
			"price": self.price,
			"level": self.lvls.lvl,
			"type": self.__class__.__name__,
		}

	@classmethod
	def from_dict(cls, data: dict):
		"""Create an item from a dictionary representation."""
		return cls(
			name=data.get("name", "Item"),
			description=data.get("description", ""),
			price=data.get("price", 0),
			lvl=data.get("level", 0)
		)
	def compare_to(self, other) -> str:
		"""Compare this item to another item."""
		if self.price:
			diff = self.price - other.price
			return f"{self.name} is {'more' if diff > 0 else 'less'} expensive than {other.name} by {abs(diff)}."
		else:
			return f"{self.name} has no price to compare."
	@property
	def category(self) -> str:
		return self.__class__.__name__
class Consumable(Item):
	"""Consumable items that can be used to restore health, mana, or stamina."""
	slot: str = "Consumable"
	def __init__(self, name: str = "Consumable",
			   	description: str = "A basic consumable",
				price: int = 0,
				effect: str = "consumable",
				amount: int = 1,
				duration: int = 1,
				lvl: int = 0
				) -> None:
		super().__init__(name, description, price, lvl)
		self.name: str = name
		self.effect: str = effect
		self.amount: int= amount
		self.duration: int = duration
	def __str__(self) -> str:
		return f"Consumable: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return f"Consumable: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def use(self, target):
			"""Apply this consumable's effect to `target` (a Character)."""
			if self.effect in ["health", "heal", "hp"]:
				new_health = min(target.max_health, target.current_health + self.amount)
				heal_amount = new_health - target.current_health
				target.health = new_health
				return f"{target.name} uses {self.name} and restores {heal_amount} HP."

			if self.effect == ["mana", "mp"]:
				new_mana = min(target.max_mana, target.current_mana + self.amount)
				mana_amount = new_mana - target.current_mana
				target.mana = new_mana
				return f"{target.name} uses {self.name} and restores {mana_amount} MP."

			if self.effect == ["stamina", "sp"]:
				new_stamina = min(target.max_stamina, target.current_stamina + self.amount)
				stamina_amount = new_stamina - target.current_stamina
				target.stamina = new_stamina
				return f"{target.name} uses {self.name} and restores {stamina_amount} stamina."

			# Fallback for any other effects
			return f"{target.name} uses {self.name}."