
import gen
import uuid
import logging
from items.items_list import Item
import core.experience_functions as experience_functions
log = logging.getLogger()
class Weapon(Item):
	"""Base class for weapons."""
	"""Weapons that can be used to attack enemies."""
	slot: str = "weapon"
	def __init__(self, 
			  	name: str = "",
			   	description: str = "",
				price: int = 0,
				attack_power: int = 0,
				lvl: int = 0
				) -> None:
		super().__init__(name, description, price, lvl or 1)
		self.attack_power: int = attack_power
		"""Initialize the weapon with the given attributes."""
		self.lvls.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Weapon" if name == "" else name
		if self.lvls.lvl == 1:
			self.description: str = "A basic weapon" if description == "" else description
			self.attack_power: int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvls.lvl > 1:
			self.attack_power: int = attack_power * self.lvls.lvl if attack_power != 0 else 10
			self.description: str = f"A Grade {self.lvls.lvl} weapon" if description == "" else description
			self.price: int = 10 if price == 0 else price
	def __str__(self) -> str:
		return f"{self.name} \nDescription: {self.description} \nPrice: {self.price}, Attack Power: {self.attack_power}, Level: {self.lvls.lvl}"
	def __repr__(self) -> str:
		return f"{self.name} \nDescription: {self.description} \nPrice: {self.price}, Attack Power: {self.attack_power}, Level: {self.lvls.lvl}"
	def compare_to(self, other) -> str:
		diff = self.attack_power - other.attack_power
		if diff == 0:
			return f"{self.name} and {other.name} have the same attack power."
		elif diff < 0:
			diff = -diff
			return f"{self.name} is less powerful than {other.name} by {diff} attack power."
		else:
			return f"{self.name} is more powerful than {other.name} by {diff} attack power."
	def stat_mod(self) -> dict[str, int]:
		"""Return a dictionary of stat modifiers for the weapon."""
		return {"attack": getattr(self, "attack_power", 0),}
class Sword(Weapon):
	"""Swords that can be used to attack enemies."""
	def __init__(self,
			   	name: str = "",
			   	description: str = "",
				price: int = 0,
				attack_power: int = 0,
				lvl: int = 0
				) -> None:
		super().__init__(name, description, price, lvl or 1)
		self.lvls.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Sword" if name == "" else name
		self.attack_power: int = attack_power
		roll: int = gen.generate_random_number(1, 3)
		"""Randomly assign attack and defense power based on roll"""
		if self.lvls.lvl == 1:
			self.description:str = "A basic sword" if description == "" else description
			self.attack_power:int = gen.generate_random_number(1,10) if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvls.lvl > 1 and self.lvls.lvl <= 10:
			if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 2) * self.lvls.lvl
			elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
		elif self.lvls.lvl > 10:
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
			elif roll == 3:
				self.attack_power:int = gen.generate_random_number(1, 20) * self.lvls.lvl
class Axe(Weapon):
	"""Axe that can be used to attack enemies."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, attack_power: int = 0, lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl or 1)
		self.lvls.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Axe" if name == "" else name
		self.attack_power: int = attack_power
		roll: int = gen.generate_random_number(1, 3)
		"""Randomly assign attack and defense power based on roll"""
		if self.lvls.lvl == 1:
			self.description: str = "A basic axe" if description == "" else description
			self.attack_power: int = gen.generate_random_number(1,10) if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvls.lvl > 1 and self.lvls.old_level <= 10:
			self.description: str = f"A Grade {self.lvls.lvl} axe" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 2) * self.lvls.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
		elif self.lvls.lvl > 10:
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 20) * self.lvls.lvl
class Bow(Weapon):
	"""Bow that can be used to attack enemies."""
	def __init__(self, 
			  	name: str = "",
			   	description: str = "",
				price: int = 0, attack_power: int = 0,
				lvl: int = 0
				) -> None:
		super().__init__(name, description, price, lvl or 1)
		self.lvls.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Bow" if name == "" else name
		self.attack_power: int = attack_power
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		if self.lvls.lvl == 1:
			self.description: str = "A basic bow" if description == "" else description
			self.attack_power: int = gen.generate_random_number(1,10) if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvls.lvl > 1 and self.lvls.lvl <= 10:
			self.description: str = f"A Grade {self.lvls.lvl} bow" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if self.lvls.lvl > 1 and self.lvls.lvl <= 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 2) * self.lvls.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
			elif self.lvls.lvl > 10:
				if roll == 1:
					self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
				elif roll == 2:
					self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
				elif roll == 3:
					self.attack_power: int = gen.generate_random_number(1, 20) * self.lvls.lvl
class Dagger(Weapon):
	"""Dagger that can be used to attack enemies."""
	def __init__(self, name: str = "", description: str = "", price: int = 0, attack_power: int = 0, lvl: int = 0) -> None:
		super().__init__(name, description, price, lvl or 1)
		self.lvls.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Dagger" if name == "" else name
		self.attack_power: int = attack_power
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		if self.lvls.lvl == 1:
			self.description: str = "A basic dagger" if description == "" else description
			self.attack_power: int = gen.generate_random_number(1,10) if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvls.lvl > 1 and self.lvls.lvl <= 10:
			self.description: str = f"A Grade {self.lvls.lvl} dagger" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 2) * self.lvls.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
		elif self.lvls.lvl > 10:
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 20) * self.lvls.lvl
class Staff(Weapon):
	"""Staff that can be used to attack enemies."""
	def __init__(self,
			   	name: str = "",
				description: str = "",
				price: int = 0, 
				attack_power: int = 0, 
				lvl: int = 0
				) -> None:
		super().__init__(name, description, price, lvl or 1) 
		self.lvls.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Staff" if name == "" else name
		self.attack_power: int = attack_power
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		if self.lvls.lvl == 1:
			self.description: str = "A basic staff" if description == "" else description
			self.price: int = 10 if price == 0 else price
			self.attack_power: int = gen.generate_random_number(1,10) if attack_power == 0 else attack_power
		elif self.lvls.lvl > 1 and self.lvls.lvl <= 10:
			self.description: str = f"A Grade {self.lvls.lvl} staff" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 2) * self.lvls.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
		elif self.lvls.lvl > 10:
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 20) * self.lvls.lvl
class Off_Hand(Weapon):
	"""Off hand weapon that can be used to attack enemies."""
	def __init__(self, 
			  name: str = "", 
			  description: str = "", 
			  price: int = 0, 
			  attack_power: int = 0, 
			  lvl: int = 0
			  ) -> None:
		super().__init__(name, description, price, lvl)
		self.lvls.lvl = 1 if lvl == 0 else lvl
		self.name: str = "Off Hand" if name == "" else name
		self.attack_power: int = 0
		"""Randomly assign attack and defense power based on roll"""
		roll: int = gen.generate_random_number(1, 3)
		if self.lvls.lvl == 1:
			self.description: str = "A basic off hand" if description == "" else description
			self.attack_power: int = 10 if attack_power == 0 else attack_power
			self.price: int = 10 if price == 0 else price
		elif self.lvls.lvl > 1 and self.lvls.lvl <= 10:
			self.description: str = f"A Grade {self.lvls.lvl} off hand" if description == "" else description
			self.price: int = 10 if price == 0 else price
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 2) * self.lvls.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
		elif self.lvls.lvl > 10:
			if roll == 1:
				self.attack_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
			elif roll == 2:
				self.attack_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
			elif roll == 3:
				self.attack_power: int = gen.generate_random_number(1, 20) * self.lvls.lvl
