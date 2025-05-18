"""MODULE CONTAINING LIST OF ITEM OBJECTS USED IN THE GAME"""
import character_creation
import class_creation
import combat_functions
import inventory_functions
import logging
import os
import random
import time
import uuid
import experience_functions
class Item:
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
		self.lvls: experience_functions = experience_functions.Levels(self, lvl)
		self.lvl: experience_functions.lvl = self.lvls.lvl
		self.experience: experience_functions.experience = self.lvls.experience
		self.class_: class_creation.c_class = class_creation.c_class(self)
	def __str__(self) -> str:
		return f"Item: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}, ID: {self.id}"
	def __repr__(self) -> str:
		return f"Item: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}, ID: {self.id}"
class Consumable(Item):
	"""Consumable items that can be used during combat or exploration."""
	def __init__(self, name: str = "Consumable",
			   	description: str = "A basic consumable",
				price: int = 0,
				effect: str = "consumable",
				amount: int = 1,
				duration: int = 1,
				lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.name: str = name
		self.effect: str = effect
		self.amount: int= amount
		self.duration: int = duration
	def __str__(self) -> str:
		return f"Consumable: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return f"Consumable: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
class Potion(Consumable):
	"""Potions that can be used to restore health or mana."""
	def __init__(self, 
			  	name: str = "Potion",
			   	description: str = "A basic potion",
				price: int = 0, effect: str = "potion",
				amount: int = 1,
				duration: int = 1,
				lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.name: str = name
		self.effect: int = effect
		self.amount: int = amount
		self.duration: int = duration
	def __str__(self) -> str:
		return f"Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return f"Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
class Health_Potion(Potion):
	"""Health potions that can be used to restore health."""
	def __init__(
				self,
			   	name: str = "Health Potion"
			  ,	description: str = "A basic health potion",
				price: int = 0, 
				effect: str = "health" ,
				amount: int = 0,
				duration: int = 0,
				lvl: int = 0) -> None:
		super().__init__(name, description, price, effect, amount, duration, lvl)
		lvl = 1 if lvl == 0 else lvl
		self.name: str = "Health Potion" if name == "" else name
		self.effect: str = "health"
		if lvl == 1:
			self.description: str = "A basic health potion" if description == "" else description
			self.price = 10 if price == 0 else price
			self.amount: int = 25 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
		elif lvl == 2:
			self.name: str = "Health Potion" if name == "" else name
			self.description: str = "A Grade 2 health potion" if description == "" else description
			self.price: int = 20 if price == 0 else price
			self.amount: int = 100 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
		elif lvl == 3:
			self.name: str = "Health Potion" if name == "" else name
			self.description: str = "A Grade 3 health potion" if description == "" else description
			self.price: int = 30 if price == 0 else price
			self.amount: int = 250 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
	def __str__(self) -> str:
		return f"Health Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return f"Health Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
class Mana_Potion(Potion):
	"""Mana potions that can be used to restore mana."""
	def __init__(self, name: str = "Mana Potion", description: str = "A basic mana potion", price: int = 0, effect: str = "mana" , amount: int = 1, duration: int = 1) -> None:
		super().__init__(name, description, price, effect, amount, duration)
		self.lvl = 1 if self.lvl == 0 else self.lvl
		self.name: str = "Mana Potion" if name == "" else name
		self.effect: str = "mana"
		if self.lvl == 1:
			self.description: str = "A basic mana potion" if description == "" else description
			self.price = 10 if price == 0 else price
			self.amount: int = 25 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
		elif self.lvl == 2:
			self.description: str = "A Grade 2 mana potion" if description == "" else description
			self.price: int = 20 if price == 0 else price
			self.amount: int = 100 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
		elif self.lvl == 3:
			self.description: str = "A Grade 3 mana potion" if description == "" else description
			self.price: int = 30 if price == 0 else price
			self.effect: str = 'mana'
			self.amount: int = 250 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
	def __str__(self) -> str:
		return f"Mana Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return f"Mana Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
class Weapon(Item):
	"""Base class for weapons."""
	"""Weapons that can be used to attack enemies."""
	def __init__(self, name: str = "Weapon", description: str = "A basic weapon", price: int = 0, attack_power: int = 10, lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name = "Weapon" if name == "" else name
		if lvl == 1:
			self.description = "A basic weapon" if description == "" else description
			self.attack_power = 10 if attack_power == 0 else attack_power
			self.price = 10 if price == 0 else price
		elif lvl == 2:
			self.description = "A Grade 2 weapon" if description == "" else description
			self.attack_power = 20 if attack_power == 0 else attack_power
			self.price = 20 if price == 0 else price

		elif lvl == 3:
			self.description = "A Grade 3 weapon" if description == "" else description
			self.attack_power = 30 if attack_power == 0 else attack_power
			self.price = 30 if price == 0 else price
		self.name = name
		self.description = description
	def __str__(self) -> str:
		return f"Weapon: {self.name} \nDescription: {self.description} \nPrice: {self.price}, Attack Power: {self.attack_power}, Level: {self.lvl}"
	def __repr__(self) -> str:
		return f"Weapon: {self.name}, Description: {self.description}, Price: {self.price}, Attack Power: {self.attack_power}, Level: {self.lvl}"
class Sword(Weapon):
	"""Swords that can be used to attack enemies."""
	def __init__(self, name: str = "Sword", description: str = "A basic sword", price: int = 0, attack_power: int = 10, lvl: int = 0) -> None:
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name = "Sword" if name == "" else name
		if lvl == 1:
			self.description = "A basic sword" if description == "" else description
			self.attack_power = 10 if attack_power == 0 else attack_power
			self.price = 10 if price == 0 else price
		elif lvl == 2:
			self.description = "A Grade 2 sword" if description == "" else description
			self.attack_power = 20 if attack_power == 0 else attack_power
			self.price = 20 if price == 0 else price

		elif lvl == 3:
			self.description = "A Grade 3 sword" if description == "" else description
			self.attack_power = 30 if attack_power == 0 else attack_power
			self.price = 30 if price == 0 else price
	def __str__(self) -> str:
			return f"\n{self.name} \nDescription: {self.description} \nPrice: {self.price}, Attack Power: {self.attack_power}, Level: {self.lvl}"
	def __repr__(self) -> str:
			return f"\n{self.name} \nDescription: {self.description} \nPrice: {self.price}, Attack Power: {self.attack_power}, Level: {self.lvl}"
class Armor(Item):
	"""Base class for armor."""
	"""Armor that can be used to protect against enemy attacks."""
	def __init__(self, name: str = "Armor", description: str = "A basic armor", price: int = 0, defense_power: int = 0, lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name = "Armor" if name == "" else name
		if lvl == 1:
			self.description = "A basic armor" if description == "" else description
			self.defense_power = 10 if defense_power == 0 else defense_power
			self.price = 10 if price == 0 else price
		elif lvl == 2:
			self.description = "A Grade 2 armor" if description == "" else description
			self.defense_power = 20 if defense_power == 0 else defense_power
			self.price = 20 if price == 0 else price

		elif lvl == 3:
			self.description = "A Grade 3 armor" if description == "" else description
			self.defense_power = 30 if defense_power == 0 else defense_power
			self.price = 30 if price == 0 else price
	def __str__(self) -> str:
		return f"Armor: {self.name}, Description: {self.description}, Price: {self.price}, Defense Power: {self.defense_power}, Level: {self.lvl}"
	def __repr__(self) -> str:
		return f"Armor: {self.name}, Description: {self.description}, Price: {self.price}, Defense Power: {self.defense_power}, Level: {self.lvl}"
