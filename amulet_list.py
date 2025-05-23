import random
import uuid
import gen
import items_list
class Amulet(items_list.Item):
	"""Base class for amulets"""
	def __init__(self, name: str = "", description: str = "", price: int = 0, effect: str = "", lvl: int = 0, health_power: int = 0, mana_power: int = 0, stamina_power: int = 0) -> None:
		"""Initialize the amulet with name, description, price, effect, level, health power, mana power and stamina power"""
		self.id: uuid = uuid.uuid4()
		self.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Amulet" if name == "" else name
		roll = gen.generate_random_number(1, 3)
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
		# Randomly assign attack and defense power based on roll
		if self.lvl == 1:
			self.description: str = "A basic amulet" if description == "" else description
			self.price: int = 10 if price == 0 else price
			self.health_power: int = gen.generate_random_number(0, 5) * self.lvl if health_power == 0 else health_power
			self.mana_power: int = gen.generate_random_number(0, 5) * self.lvl if mana_power == 0 else mana_power
			# Randomly assign health and mana power based on roll
		elif self.lvl > 1 and lvl <= 10:
			self.description: str = f"A Grade {self.lvl} amulet" if description == "" else description
			self.price: int = 20 if price == 0 else price			# Randomly assign attack and defense power based on roll
			if roll == 1:
				self.health_power: int = gen.generate_random_number(1, 5) * self.lvl
				self.mana_power: int = gen.generate_random_number(1, 5) * self.lvl
			elif roll == 2:
				self.health_power: int = gen.generate_random_number(1, 10) * self.lvl
				self.mana_power: int = gen.generate_random_number(1, 5) * self.lvl
			elif roll == 3:
				self.health_power: int = gen.generate_random_number(1, 15) * self.lvl
				self.mana_power: int = gen.generate_random_number(1, 15) * self.lvl
	def __str__(self) -> str:
		return f"Amulet: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}"
	def __repr__(self) -> str:
		return f"Amulet: {self.name}, Description: {self.description}, Price: {self.price}, Level: {self.lvl}"