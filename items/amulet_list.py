import random
import uuid
import gen
from items.items_list import Item
class Amulet(Item):
	slot: str = "amulet"
	"""Base class for amulets"""
	def __init__(self, 
			  	name: str = "",
				description: str = "",
				price: int = 0,
				effect: str = "",
				lvl: int = 0,
				health_power: int = 0,
				mana_power: int = 0,
				stamina_power: int = 0
				) -> None:
		
		super().__init__(name, description, price, lvl or 1)
		"""Initialize the amulet with name, description, price, effect, level, health power, mana power and stamina power"""
		self.lvls.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Amulet" if name == "" else name
		self.effect: str = "Amulet" if effect == "" else effect
		roll = gen.generate_random_number(1, 3)
		# Randomly assign attack and defense power based on roll
		if self.lvls.lvl == 1:
			self.description: str = "A basic amulet" if description == "" else description
			self.price: int = 10 if price == 0 else price
			self.health_power: int = gen.generate_random_number(0, 5) * self.lvls.lvl if health_power == 0 else health_power
			self.mana_power: int = gen.generate_random_number(0, 5) * self.lvls.lvl if mana_power == 0 else mana_power
			if gen.generate_random_number(0, 100) < 10:
				self.stamina_power: int = gen.generate_random_number(0, 5) * self.lvls.lvl
			# Randomly assign health and mana power based on roll
		elif self.lvls.lvl > 1 and self.lvls.lvl <= 10:
			self.description: str = f"A Grade {self.lvls.lvl} amulet" if description == "" else description
			self.price: int = 20 if price == 0 else price			# Randomly assign attack and defense power based on roll
			if gen .generate_random_number(0, 100) < 10:
				self.stamina_power: int = gen.generate_random_number(0, 5) * self.lvls.lvl
			if roll == 1:
				self.health_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
				self.mana_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 2:
				self.health_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
				self.mana_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 3:
				self.health_power: int = gen.generate_random_number(1, 15) * self.lvls.lvl
				self.mana_power: int = gen.generate_random_number(1, 15) * self.lvls.lvl
	def __str__(self) -> str:
		return f"Amulet: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvls.lvl}"
	def __repr__(self) -> str:
		return f"Amulet: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvls.lvl}"
	def compare_to(self, other) -> str:
		if self.health_power:
			diff = self.health_power - other.health_power
			return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} health power."
		if self.mana_power:
			diff = self.mana_power - other.mana_power
			return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} mana power."
		if self.stamina_power:
			diff = self.stamina_power - other.stamina_power
			return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} stamina power."
