import random
import uuid
import gen
class Amulet():
	"""Base class for amulets"""
	def __init__(self, name: str = "Amulet", description: str = "A basic amulet", price: int = 0, effect: str = "amulet", lvl: int = 0, health_power: int = 0, mana_power: int = 0, stamina_power: int = 0) -> None:
		"""Initialize the amulet with name, description, price, effect, level, health power, mana power and stamina power"""
		self.id = uuid.uuid4()
		self.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Amulet" if name == "" else name
		roll = 1
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