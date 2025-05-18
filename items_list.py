"""MODULE CONTAINING LIST OF ITEM OBJECTS USED IN THE GAME"""
import character_creation
import class_creation
import combat_functions
import inventory_functions
import logging
import os
import time
import uuid
import experience_functions
import gen
import random
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
			self.duration: int = 1 if duration == 0 else duration
		elif lvl == 2:
			self.name: str = "Health Potion" if name == "" else name
			self.description: str = "A Grade 2 health potion" if description == "" else description
			self.price: int = 20 if price == 0 else price
			self.amount: int = 100 if amount == 0 else amount
			self.duration: int  = 1 if duration == 0 else duration
		elif lvl == 3:
			self.name: str = "Health Potion" if name == "" else name
			self.description: str = "A Grade 3 health potion" if description == "" else description
			self.price: int = 30 if price == 0 else price
			self.amount: int = 250 if amount == 0 else amount
			self.duration: int = 1 if duration == 0 else duration
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
			self.duration: int = 1 if duration == 0 else duration
	def __str__(self) -> str:
		return f"Mana Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return f"Mana Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
class Weapon(Item):
	"""Base class for weapons."""
	"""Weapons that can be used to attack enemies."""
	def __init__(self, name: str = "Weapon", description: str = "", price: int = 0, attack_power: int = gen.generate_random_number(1,4), lvl: int = 1) -> None:
		super().__init__(name, description, price, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name:str = "Weapon" if name == "" else name
		if self.lvl == 1:
			self.description: str = "A basic weapon" if description == "" else description
			self.attack_power: int = 10
			self.price: int = 10 if price == 0 else price
		elif self.lvl > 1:
			self.attack_power: int = attack_power * self.lvl if attack_power != 0 else 10
			self.description: str = f"A Grade {self.lvl} weapon" if description == "" else description
			self.price: int = 10 if price == 0 else price
	def __str__(self) -> str:
		return f"{self.name} \nDescription: {self.description} \nPrice: {self.price}, Attack Power: {self.attack_power}, Level: {self.lvl}"
	def __repr__(self) -> str:
		return f"{self.name} \nDescription: {self.description} \nPrice: {self.price}, Attack Power: {self.attack_power}, Level: {self.lvl}"
class Sword(Weapon):
	"""Swords that can be used to attack enemies."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, attack_power: int = gen.generate_random_number(1,4), lvl: int = 0) -> None:
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name: str = "Sword" if name == "" else name
		if self.lvl == 1:
			self.description:str = "A basic sword" if description == "" else description
			self.attack_power:int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvl > 1:
			self.description: str = f"A Grade {self.lvl} sword" if description == "" else description
			self.attack_power: int = attack_power * self.lvl if attack_power != 0 else 10
			self.price: int = 10 if price == 0 else price
	def __str__(self) -> str:
		return super().__str__()
	def __repr__(self) -> str:
		return super().__repr__()
class Axe(Weapon):
	"""Axe that can be used to attack enemies."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, attack_power: int = gen.generate_random_number(1,4), lvl: int = 0) -> None:
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name: str = "Axe" if name == "" else name
		if self.lvl == 1:
			self.description: str = "A basic axe" if description == "" else description
			self.attack_power: int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvl > 1 and self.lvl <= 10:
			self.description: str = f"A Grade {self.lvl} axe" if description == "" else description
			self.attack_power: int = attack_power * self.lvl if attack_power != 0 else 10
			self.price: int = 10 if price == 0 else price
	def __str__(self) -> str:
		return super().__str__()
	def __repr__(self) -> str:
		return super().__repr__()
class Bow(Weapon):
	"""Bow that can be used to attack enemies."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, attack_power: int = gen.generate_random_number(1,4), lvl: int = 0) -> None:
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name: str = "Bow" if name == "" else name
		if self.lvl == 1:
			self.description: str = "A basic bow" if description == "" else description
			self.attack_power: int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvl > 1:
			self.description: str = f"A Grade {self.lvl} bow" if description == "" else description
			self.attack_power: int = attack_power * self.lvl if attack_power != 0 else 10
			self.price: int = 10 if price == 0 else price
	def __str__(self) -> str:
		return super().__str__()
	def __repr__(self) -> str:
		return super().__repr__()
class Shield(Weapon):
	"""Base class for shields."""
	"""Shields that can be used to protect against enemy attacks."""
	def __init__(self, name: str = "Shield", description: str = "A basic shield", price: int = 0, defense_power: int = 0, lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name = "Shield" if name == "" else name
		roll = gen.generate_random_number(1, 3)
		if self.lvl == 1:
			self.description = "A basic shield" if description == "" else description
			self.defense_power = 10 if defense_power == 0 else defense_power
			self.price = 10 if price == 0 else price
			if roll == 1:
				self.attack_power = gen.generate_random_number(0, 2)
			elif roll == 2:
				self.attack_power = gen.generate_random_number(0, 5)
			elif roll == 3:
				self.attack_power = 0
		elif self.lvl > 1:
			self.description = f"A Grade {self.lvl} shield" if description == "" else description
			self.defense_power = defense_power * self.lvl if defense_power != 0 else 10
			self.price = 10 if price == 0 else price
			if self.lvl > 1 and self.lvl < 10:
				if roll == 1:
					self.attack_power = gen.generate_random_number(0, 2)
				elif roll == 2:
					self.attack_power = gen.generate_random_number(0, 5)
				elif roll == 3:
					self.attack_power = 0
			elif self.lvl >= 10:
				if roll == 1:
					self.attack_power = gen.generate_random_number(0, 10)
				elif roll == 2:
					self.attack_power = gen.generate_random_number(5, 10)
				elif roll == 3:
					self.attack_power = gen.generate_random_number(0, 20)	
	def __str__(self) -> str:
		return f"Shield: {self.name}, Description: {self.description}, Price: {self.price}, Defense Power: {self.defense_power}, Level: {self.lvl}"
	def __repr__(self) -> str:
		return f"Shield: {self.name}, Description: {self.description}, Price: {self.price}, Defense Power: {self.defense_power}, Level: {self.lvl}"
class Armor(Item):
	"""Base class for armor."""
	"""Armor that can be used to protect against enemy attacks."""
	def __init__(self, name: str = "Armor", description: str = "A basic armor", price: int = 0, defense_power:int = gen.generate_random_number(1,4), lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name = "Armor" if name == "" else name
		if lvl == 1:
			self.description = "Basic armor" if description == "" else description
			self.defense_power = 10 if defense_power == 0 else defense_power
			self.price = 10 if price == 0 else price
		elif self.lvl > 1:
			self.description = f"A Grade {self.lvl} armor" if description == "" else description
			self.defense_power = defense_power * self.lvl if defense_power != 0 else 10
			self.price = 10 if price == 0 else price
	def __str__(self) -> str:
		return f"Armor: {self.name}, Description: {self.description}, Price: {self.price}, Defense Power: {self.defense_power}, Level: {self.lvl}"
	def __repr__(self) -> str:
		return f"Armor: {self.name}, Description: {self.description}, Price: {self.price}, Defense Power: {self.defense_power}, Level: {self.lvl}"
class Amulet(Item):
	"""Base class for amulets"""
	def __init__(self, name: str = "Amulet", description: str = "A basic amulet", price: int = 0, effect: str = "amulet", lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Amulet" if name == "" else name
		roll = gen.generate_random_number(1, 3)
		if lvl == 1:
			self.description = "A basic amulet" if description == "" else description
			self.price = 10 if price == 0 else price
			# Randomly assign attack and defense power based on roll
			if roll == 1:
				self.attack_power = 5
				self.defense_power = 0
			elif roll == 2:
				self.attack_power = 0
				self.defense_power = 5
			elif roll == 3:
				self.attack_power = 5
				self.defense_power = 5
			else:
				# Default values if roll is not in range
				self.attack_power = 5
				self.defense_power = 5
		elif lvl > 1:
			self.description = "A Grade 2 amulet" if description == "" else description
			self.price = 20 if price == 0 else price
			# Randomly assign attack and defense power based on roll
			if roll == 1:
				self.attack_power = gen.generate_random_number(0, 5)
				self.defense_power = 0
			elif roll == 2:
				self.attack_power = gen.generate_random_number(0, 10)
				self.defense_power = 10
			elif roll == 3:
				self.attack_power = 10
				self.defense_power = 10
			else:
				# Default values if roll is not in range
				self.attack_power = 10
				self.defense_power = 10
	def __str__(self) -> str:
		return f"Amulet: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}"
	def __repr__(self) -> str:
		return f"Amulet: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}"
class Ring(Item):
	"""Base class for rings"""
	def __init__(self, name: str = "Ring", description: str = "", price: int = 0, effect: str = "", lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name = "Ring" if name == "" else name
		self.health_power: int = 0
		self.mana_power: int = 0
		self.effect: str = None
		roll = gen.generate_random_number(1, 3)
		if lvl == 1:
			if roll == 1:
				self.description = "A basic ring" if description == "" else description
				self.price = 10 if price == 0 else price
				self.effect = random.choice(["health", "mana",])
				if self.effect == "health":
					self.health_power = gen.generate_random_number(1, 5)
				elif self.effect == "mana":
					self.mana_power = gen.generate_random_number(1, 5)
			elif roll == 2:
				self.description = "A basic ring" if description == "" else description
				self.price = 10 if price == 0 else price
				self.effect = random.choice(["health", "mana","both"])
				if self.effect == "health":
					self.health_power = gen.generate_random_number(2, 8)
				elif self.effect == "mana":
					self.mana_power = gen.generate_random_number(5, 15)
				elif self.effect == "both":
					self.health_power = gen.generate_random_number(1, 10)
					self.mana_power = gen.generate_random_number(1, 10)
			elif roll == 3:
				self.description = "A basic ring" if description == "" else description
				self.price = 10 if price == 0 else price
				self.effect = random.choice(["health", "mana","both"])
				if self.effect == "health":
					self.health_power = gen.generate_random_number(0, 6)
				elif self.effect == "mana":
					self.mana_power = gen.generate_random_number(0, 4)
				elif self.effect == "both":
					self.health_power = gen.generate_random_number(5, 15)
					self.mana_power = gen.generate_random_number(5, 15)
		elif lvl > 1 and lvl <= 10:
			self.description = f"A Grade {self.lvl} ring" if description == "" else description
			self.price = 20 if price == 0 else price
			self.effect = random.choice(["health", "mana",])
			if self.effect == "health":
				self.health_power = gen.generate_random_number(5, 10)
			elif self.effect == "mana":
				self.mana_power = gen.generate_random_number(10, 20)
		elif lvl > 10:
			self.description = f"A Grade {self.lvl} ring" if description == "" else description
			self.price = 30 if price == 0 else price
			self.effect = random.choice(["health", "mana",])
			if self.effect == "health":
				self.health_power = gen.generate_random_number(10, 20)
			elif self.effect == "mana":
				self.mana_power = gen.generate_random_number(20, 30)
	def __str__(self) -> str:
		return f"Ring: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}, Effect: {self.effect}, Health Power: {self.health_power}"
	def __repr__(self) -> str:
		return f"Ring: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}, Effect: {self.effect}, Health Power: {self.health_power}"
