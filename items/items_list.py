"""MODULE CONTAINING LIST OF ITEM OBJECTS USED IN THE GAME"""
import logging
import uuid
import core.experience_functions as experience_functions
import gen
import random
class Item:
	slot: str = None
	"""Base class for all items in the game.
	This class is used to create items in the game. It contains the following attributes:"""
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
	slot: str = "Consumable"
	"""Consumable items that can be used during combat or exploration."""
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
	def use(self, character) -> None:
			"""
			Applies this consumable’s effect to the character.
			E.g. health/mana/stamina restore.
			"""
			match self.effect:
				case "health":
					character.health   = min(character.health   + self.amount, character.max_health)
				case "mana":
					character.mana     = min(character.mana     + self.amount, character.max_mana)
				case "stamina":
					character.stamina  = min(character.stamina  + self.amount, character.max_stamina)
				# future: add poison, buff, etc.