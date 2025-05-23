import items_list as items
import gen
import uuid
import logging
import items_list
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
class Weapon(items_list.Item):
	"""Base class for weapons."""
	"""Weapons that can be used to attack enemies."""
	def __init__(self, name: str = "",
			   description: str = "",
				price: int = 0, attack_power: int = gen.generate_random_number(1,4),
				lvl: int = 1) -> None:
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name:str = "Weapon" if name == "" else name
		self.id = uuid.uuid4()
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
	def compare_to(self, other) -> str:
		diff = self.attack_power - other.attack_power
		if diff == 0:
			return f"{self.name} and {other.name} have the same attack power."
		elif diff < 0:
			diff = -diff
			return f"{self.name} is less powerful than {other.name} by {diff} attack power."
		else:
			return f"{self.name} is more powerful than {other.name} by {diff} attack power."
class Sword(Weapon):
	"""Swords that can be used to attack enemies."""
	def __init__(self, name: str = "",
			   description: str = "",
				price: int = 0,
				attack_power: int = gen.generate_random_number(2,10),
				lvl: int = 0) -> None:
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name: str = "Sword" if name == "" else name
		self.attack_power: int = 0
		if self.lvl == 1:
			self.description:str = "A basic sword" if description == "" else description
			self.attack_power:int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvl > 10:
			self.description: str = f"A Grade {self.lvl} sword" if description == "" else description
			self.price: int = 10 if price == 0 else price
			roll: int = gen.generate_random_number(1, 3)
			if self.lvl > 1 and self.lvl <= 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 2) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif self.lvl > 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
				elif roll == 3:
					self.attack_power:int = gen.generate_random_number(1, 20) * self.lvl
class Axe(Weapon):
	"""Axe that can be used to attack enemies."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, attack_power: int = gen.generate_random_number(1,4), lvl: int = 0) -> None:
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name: str = "Axe" if name == "" else name
		self.attack_power: int = 0
		roll: int = gen.generate_random_number(1, 3)
		"""Randomly assign attack and defense power based on roll"""
		if self.lvl == 1:
			self.description: str = "A basic axe" if description == "" else description
			self.attack_power: int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvl > 1 and self.lvl <= 10:
			self.description: str = f"A Grade {self.lvl} axe" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if self.lvl > 1 and self.lvl <= 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 2) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif self.lvl > 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 20) * self.lvl
class Bow(Weapon):
	"""Bow that can be used to attack enemies."""
	def __init__(self, name: str = "",
			   	description: str = "",
				price: int = 0, attack_power: int = gen.generate_random_number(1,4),
				lvl: int = 0) -> None:
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name: str = "Bow" if name == "" else name
		self.attack_power: int = 0
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		if self.lvl == 1:
			self.description: str = "A basic bow" if description == "" else description
			self.attack_power: int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 2)
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 5)
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 10)
		elif self.lvl > 1 and self.lvl <= 10:
			self.description: str = f"A Grade {self.lvl} bow" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if self.lvl > 1 and self.lvl <= 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 2) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif self.lvl > 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 20) * self.lvl
class Dagger(Weapon):
	"""Dagger that can be used to attack enemies."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, attack_power: int = gen.generate_random_number(1,4), lvl: int = 0) -> None:
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name: str = "Dagger" if name == "" else name
		self.attack_power: int = 0
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		if self.lvl == 1:
			self.description: str = "A basic dagger" if description == "" else description
			self.attack_power: int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 2)
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 5)
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 10)
		elif self.lvl > 1 and self.lvl <= 10:
			self.description: str = f"A Grade {self.lvl} dagger" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if self.lvl > 1 and self.lvl <= 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 2) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif self.lvl > 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 20) * self.lvl
class Staff(Weapon):
	"""Staff that can be used to attack enemies."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, attack_power: int = gen.generate_random_number(1,4), lvl: int = 0) -> None:
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name: str = "Staff" if name == "" else name
		self.attack_power: int = 0
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		if self.lvl == 1:
			self.description: str = "A basic staff" if description == "" else description
			self.attack_power: int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 2)
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 5)
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 10)
		elif self.lvl > 1 and self.lvl <= 10:
			self.description: str = f"A Grade {self.lvl} staff" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if self.lvl > 1 and self.lvl <= 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 2) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif self.lvl > 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 20) * self.lvl
class Off_Hand(Weapon):
	"""Off hand weapon that can be used to attack enemies."""
	def __init__(self, name = "", description = "", price = 0, attack_power = gen.generate_random_number(1, 4), lvl = 1):
		super().__init__(name, description, price, attack_power, lvl)
		self.lvl: int = 1 if lvl == 0 else lvl
		self.name: str = "Off Hand" if name == "" else name
		self.attack_power: int = 0
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		if self.lvl == 1:
			self.description: str = "A basic off hand" if description == "" else description
			self.attack_power: int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 2)
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 5)
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 10)
		elif self.lvl > 1 and self.lvl <= 10:
			self.description: str = f"A Grade {self.lvl} off hand" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if self.lvl > 1 and self.lvl <= 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 2) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
			elif self.lvl > 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 20) * self.lvl
