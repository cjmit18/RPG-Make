"""MODULE CONTAINING LIST OF ITEM OBJECTS USED IN THE GAME"""
import logging
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
class Boots(Item):
	"""Base class for boots"""
	def __init__(self, name: str = "", description: str = "", price: int = 0, effect: str = "boots", lvl: int = 0, speed_power: int = 0, stamina_power: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Boots" if name == "" else name
		self.stamina_power: int = 0
		self.speed_power: int = 0
		# Randomly assign attack and defense power based on roll
		roll: int = gen.generate_random_number(1, 3)
		if lvl == 1:
			self.description: str = "A basic boots" if description == "" else description
			self.price: int = 10 if price == 0 else price
			# Randomly assign health and mana power based on roll
			if roll == 1:
				self.speed_power: int = gen.generate_random_number(2, 10) * self.lvl
				self.stamina_power: int = 0
			elif roll == 2:
				self.speed_power: int = 0
				self.stamina_power: int = gen.generate_random_number(2, 10) * self.lvl
			elif roll == 3:
				self.speed_power: int = gen.generate_random_number(1, 10) * self.lvl
				self.stamina_power: int = gen.generate_random_number(1, 10) * self.lvl
			else:
				# Default values if roll is not in range
				self.health_power: int = 5
				self.mana_power: int = 5
		elif lvl > 1 and lvl <= 10:
			self.description: str = f"A Grade {self.lvl} boots" if description == "" else description
			self.price: int = 20 if price == 0 else price
			self.effect: str = random.choice(["speed", "stamina"])
			# Randomly assign speed and	stamina power based on roll
			if roll == 1:
				if self.effect == "speed":
					self.speed_power: int = gen.generate_random_number(1, 5) * self.lvl
					self.stamina_power: int = 0
				elif self.effect == "stamina":
					self.speed_power = 0
					self.stamina_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif self.effect == "both":
					self.speed_power: int = gen.generate_random_number(0, 5) * self.lvl
					self.stamina_power: int = gen.generate_random_number(0, 5) * self.lvl
			elif roll == 2:
				if self.effect == "speed":
					self.speed_power: int = gen.generate_random_number(1, 10) * self.lvl
					self.stamina_power: int = 0
				elif self.effect == "stamina":
					self.speed_power = 0
					self.stamina_power: int = gen.generate_random_number(1, 10) * self.lvl
				elif self.effect == "both":
					self.speed_power: int = gen.generate_random_number(1, 10) * self.lvl
					self.stamina_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif roll == 3:
				if self.effect == "speed":
					self.speed_power: int = gen.generate_random_number(1, 15) * self.lvl
					self.stamina_power: int = 0
				elif self.effect == "stamina":
					self.speed_power = 0
					self.stamina_power: int = gen.generate_random_number(1, 15) * self.lvl
				elif self.effect == "both":
					self.speed_power: int = gen.generate_random_number(0, 15) * self.lvl
					self.stamina_power: int = gen.generate_random_number(0, 15) * self.lvl
class Amulet(Item):
	"""Base class for amulets"""
	def __init__(self, name: str = "Amulet", description: str = "A basic amulet", price: int = 0, effect: str = "amulet", lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Amulet" if name == "" else name
		self.stamina_power: int = 0
		roll: int = gen.generate_random_number(1, 3)
		if lvl == 1:
			self.description: str = "A basic amulet" if description == "" else description
			self.price: int = 10 if price == 0 else price
			# Randomly assign health and mana power based on roll
			if roll == 1:
				self.health_power: int = gen.generate_random_number(2, 10) * self.lvl
				self.mana_power: int = 0
			elif roll == 2:
				self.health_power: int = 0
				self.mana_power: int = gen.generate_random_number(2, 10) * self.lvl
			elif roll == 3:
				self.health_power: int = gen.generate_random_number(1, 10) * self.lvl
				self.mana_power: int = gen.generate_random_number(1, 10) * self.lvl
			else:
				# Default values if roll is not in range
				self.health_power: int = 5
				self.mana_power: int = 5
		elif lvl > 1 and lvl <= 10:
			self.description: str = f"A Grade {self.lvl} amulet" if description == "" else description
			self.price: int = 20 if price == 0 else price
			self.effect: str = random.choice(["health", "mana"])
			# Randomly assign attack and defense power based on roll
			if roll == 1:
				if self.effect == "health":
					self.health_power: int = gen.generate_random_number(1, 5) * self.lvl
					self.mana_power: int = 0
				elif self.effect == "mana":
					self.health_power = 0
					self.mana_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif self.effect == "both":
					self.health_power: int = gen.generate_random_number(0, 5) * self.lvl
					self.mana_power: int = gen.generate_random_number(0, 5) * self.lvl
			elif roll == 2:
				if self.effect == "healh":
					self.health_power: int = gen.generate_random_number(1, 10) * self.lvl
					self.mana_power: int = 0
				elif self.effect == "mana":
					self.health_power = 0
					self.mana_power: int = gen.generate_random_number(1, 10) * self.lvl
				elif self.effect == "both":
					self.health_power: int = gen.generate_random_number(1, 10) * self.lvl
					self.mana_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif roll == 3:
				if self.effect == "health":
					self.health_power: int = gen.generate_random_number(1, 15) * self.lvl
					self.mana_power: int = 0
				elif self.effect == "mana":
					self.health_power = 0
					self.mana_power: int = gen.generate_random_number(1, 15) * self.lvl
				elif self.effect == "both":
					self.health_power: int = gen.generate_random_number(0, 15) * self.lvl
					self.mana_power: int = gen.generate_random_number(0, 15) * self.lvl
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
		self.stamina_power: int = 0
		self.effect: str = None
		roll: int = gen.generate_random_number(1, 3)
		# Randomly assign health and mana power based on roll
		if lvl == 1:
			if roll == 1:
				self.description: str = "A basic ring" if description == "" else description
				self.price: int = 10 if price == 0 else price
				self.effect: str = random.choice(["health", "mana",])
				if self.effect == "health":
					self.health_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif self.effect == "mana":
					self.mana_power: int = gen.generate_random_number(1, 5) * self.lvl
			elif roll == 2:
				self.description: str = "A basic ring" if description == "" else description
				self.price: int = 10 if price == 0 else price
				self.effect: str = random.choice(["health", "mana","both"])
				if self.effect == "health":
					self.health_power: int = gen.generate_random_number(2, 8) * self.lvl
				elif self.effect == "mana":
					self.mana_power: int = gen.generate_random_number(5, 15) * self.lvl
				elif self.effect == "both":
					self.health_power: int = gen.generate_random_number(1, 10) * self.lvl
					self.mana_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif roll == 3:
				self.description: str = "A basic ring" if description == "" else description
				self.price: int = 10 if price == 0 else price
				self.effect: str = random.choice(["health", "mana","both"])
				if self.effect == "health":
					self.health_power: int = gen.generate_random_number(1, 6)
				elif self.effect == "mana":
					self.mana_power: int = gen.generate_random_number(1, 4)
				elif self.effect == "both":
					self.health_power: int = gen.generate_random_number(0, 15)
					self.mana_power: int = gen.generate_random_number(0, 15)
		elif lvl > 1 and lvl <= 10:
			self.description: str = f"A Grade {self.lvl} ring" if description == "" else description
			self.price: int = 20 if price == 0 else price
			self.effect: str = random.choice(["health", "mana",])
			if self.effect == "health":
				self.health_power: int = gen.generate_random_number(1, 10)
			elif self.effect == "mana":
				self.mana_power: int = gen.generate_random_number(1, 20)
		elif lvl > 10:
			self.description: str = f"A Grade {self.lvl} ring" if description == "" else description
			self.price: int = 30 if price == 0 else price
			self.effect: str = random.choice(["health", "mana",])
			if self.effect == "health":
				self.health_power: int = gen.generate_random_number(5, 20)
			elif self.effect == "mana":
				self.mana_power: int = gen.generate_random_number(5, 30)
	def __str__(self) -> str:
		return f"Ring: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}, Effect: {self.effect}, Health Power: {self.health_power}"
	def __repr__(self) -> str:
		return f"Ring: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}, Effect: {self.effect}, Health Power: {self.health_power}"
