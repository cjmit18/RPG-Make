import items_list as items
import gen
import logging
import random
import uuid
log = logging.getLogger()
class Armor(items.Item):
	"""Base class for armor."""
	"""Armor that can be used to protect against enemy attacks."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, defense_power:int = 0, lvl: int = 0) -> None:
		self.lvl = 1 if lvl == 0 else lvl
		self.name = "Armor" if name == "" else name
		self.id = uuid.uuid4()
		self.attack_power: int
		roll: int = gen.generate_random_number(1, 3)
		# Randomly assign attack and defense power based on roll
		if lvl == 1:
			self.description: str = "Basic armor" if description == "" else description
			self.defense_power: int = gen.generate_random_float(1,10) if defense_power == 0 else defense_power
			self.price: int = 10 if price == 0 else price
		elif lvl > 1 and lvl <= 10:
			self.description: str = f"A Grade {self.lvl} armor" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.defense_power: int = gen.generate_random_number(1, 5) * self.lvl
			elif roll == 2:
				self.defense_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif roll == 3:
				self.defense_power: int = gen.generate_random_number(1, 20) * self.lvl
		elif lvl > 10:
			self.description: str = f"A Grade {self.lvl} armor" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.defense_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif roll == 2:
				self.defense_power: int = gen.generate_random_number(5, 10) * self.lvl
			elif roll == 3:
				self.defense_power: int = gen.generate_random_number(1, 20) * self.lvl
	def __str__(self) -> str:
		return f"{self.name} \nDescription: {self.description} \nPrice: {self.price}, Defense Power: {self.defense_power}, Level: {self.lvl}"
	def __repr__(self) -> str:
		return f"{self.name} \nDescription: {self.description} \nPrice: {self.price}, Defense Power: {self.defense_power}, Level: {self.lvl}"
	def compare_to(self, other) -> str:
		"""Compare this armor to another armor."""
		if self.attack_power and self.defense_power:
			diff = self.attack_power - other.attack_power
			return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} attack power."
		if self.defense_power:
			diff = self.defense_power - other.defense_power
			return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} defense power."
		else:
			return f"{self.name} has no defense power to compare."
	    
class Shield(Armor):
	"""Base class for shields."""
	"""Shields that can be used to protect against enemy attacks."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, defense_power: int = 0, lvl: int = 0) -> None:
		super().__init__(name, description, price, defense_power, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name = "Shield" if name == "" else name
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		# Randomly assign attack and defense power based on roll
		if self.lvl == 1:
			self.description: str = "A basic shield" if description == "" else description
			self.defense_power: int = 10 if defense_power == 0 else defense_power
			self.price: int = 10 if price == 0 else price
		elif self.lvl > 1 and self.lvl <= 10:
			# Randomly assign attack and defense power based on roll
			self.description: str = f"A Grade {self.lvl} shield" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(0, 2) * self.lvl
				self.defense_power: int = gen.generate_random_number(1, 5) * self.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(0, 5) * self.lvl
				self.defense_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(0, 10) * self.lvl
				self.defense_power: int = gen.generate_random_number(1, 20) * self.lvl
			elif self.lvl >= 10:
				self.effect: str = random.choice(["attack", "defense"])
				if roll == 1:
					if self.effect == "attack":
						self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
						self.defense_power: int = gen.generate_random_number(1, 10) * self.lvl
					elif self.effect == "defense":
						self.defense_power: int = gen.generate_random_number(1, 20) * self.lvl
					elif self.effect == "both":
						self.attack_power: int = gen.generate_random_number(2, 10) * self.lvl
						self.defense_power: int = gen.generate_random_number(5, 20) * self.lvl
				elif roll == 2:
					if self.effect == "attack":
						self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
						self.defense_power: int = gen.generate_random_number(1, 20) * self.lvl
					elif self.effect == "defense":
						self.defense_power: int = gen.generate_random_number(5, 10) * self.lvl
					elif self.effect == "both":
						self.attack_power: int = gen.generate_random_number(2, 15) * self.lvl
						self.defense_power: int = gen.generate_random_number(5, 20) * self.lvl
				elif roll == 3:
					if self.effect == "attack":
						self.attack_power: int = gen.generate_random_number(1, 20) * self.lvl
						self.defense_power: int = gen.generate_random_number(1, 30) * self.lvl
					elif self.effect == "defense":
						self.defense_power: int = gen.generate_random_number(5, 20) * self.lvl
					elif self.effect == "both":
						self.attack_power: int = gen.generate_random_number(2, 20) * self.lvl
						self.defense_power: int = gen.generate_random_number(5, 30) * self.lvl
	def compare_to(self, other):
		"""Compare this shield to another shield."""
		if self.attack_power and self.defense_power:
			diff = self.attack_power - other.attack_power
			return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} attack power."
		if self.defense_power:
			diff = self.defense_power - other.defense_power
			return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} defense power."
		else:
			return f"{self.name} has no attack or defense power to compare."
class Robe(Armor):
	"""Base class for robes."""
	"""Robes that can be used to protect against enemy attacks."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, defense_power: int = 0, lvl: int = 0) -> None:
		super().__init__(name, description, price, defense_power, lvl)
		self.lvl = 1 if lvl == 0 else lvl
		self.name = "Robe" if name == "" else name
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		# Randomly assign attack and defense power based on roll
		if self.lvl == 1:
			self.description: str = "A basic robe" if description == "" else description
			self.defense_power: int = gen.generate_random_number(1,10) if defense_power == 0 else defense_power
			self.price: int = 10 if price == 0 else price
		elif self.lvl > 1 and self.lvl <= 10:
			# Randomly assign attack and defense power based on roll
			self.description: str = f"A Grade {self.lvl} robe" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(0, 5) * self.lvl
				self.mana_power: int = gen.generate_random_number(0, 5) * self.lvl
				self.defense_power: int = gen.generate_random_number(1, 5) * self.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(0, 10) * self.lvl
				self.mana_power: int = gen.generate_random_number(0, 10) * self.lvl
				self.defense_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(0, 10) * self.lvl
				self.mana_power: int = gen.generate_random_number(0, 20) * self.lvl
				self.defense_power: int = gen.generate_random_number(1, 20) * self.lvl
		elif self.lvl >= 10:
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				self.defense_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
				self.mana_power: int = gen.generate_random_number(1, 5) * self.lvl
				self.defense_power: int = gen.generate_random_number(1, 20) * self.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 20) * self.lvl
				self.mana_power: int = gen.generate_random_number(1, 10) * self.lvl
				self.defense_power: int = gen.generate_random_number(1, 30) * self.lvl
	def compare_to(self, other) -> str:
		"""Compare this robe to another robe."""
		if self.attack_power and self.defense_power:
			diff = self.attack_power - other.attack_power
			return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} attack power."
		elif self.defense_power:
			diff = self.defense_power - other.defense_power
			return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} defense power."
		else:
			return f"{self.name} has no attack or defense power to compare."
