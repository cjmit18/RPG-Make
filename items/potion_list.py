"""Potion list module for the game."""
# This module contains the Potion class and its subclasses for different types of potions.
import uuid
import items.items_list as items
class Potion(items.Consumable):
	def __init__(self,
        name: str = "Potion",
        description: str = "A basic potion",
    	price: int = 0,
        effect: str = "potion",
        amount: int = 1,
        duration: int = 1,
        lvl: int = 0) -> None:
        # pass lvl through so self.lvls is correct
		super().__init__(name, description, price, effect, amount, duration, lvl or 1)
		slot: str = "Consumable"
	def __str__(self) -> str:
		return f"Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return f"Potion: {self.name}, Description: {self.description}, Price: {self.price}, Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def compare_to(self, other) -> str:
		if self.category == other.category:
			if self.amount:
				diff = self.amount - other.amount
				return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} {self.effect}."
			if self.duration:
				diff = self.duration - other.duration
				return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} {self.effect}."
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
		self.name: str = "Health Potion" if name == "" else name
		self.effect: str = "health"
		if self.lvls.lvl == 1:
			self.description: str = "A basic health potion" if description == "" else description
			self.price: int = 10 if price == 0 else price
			self.amount: int = 25 if amount == 0 else amount
			self.duration: int = 1 if duration == 0 else duration
		elif self.lvls.lvl == 2:
			self.name: str = "Health Potion" if name == "" else name
			self.description: str = "A Grade 2 health potion" if description == "" else description
			self.price: int = 20 if price == 0 else price
			self.amount: int = 100 if amount == 0 else amount
			self.duration: int  = 1 if duration == 0 else duration
		elif self.lvls.lvl == 3:
			self.name: str = "Health Potion" if name == "" else name
			self.description: str = "A Grade 3 health potion" if description == "" else description
			self.price: int = 30 if price == 0 else price
			self.amount: int = 250 if amount == 0 else amount
			self.duration: int = 1 if duration == 0 else duration
	def __str__(self) -> str:
		return super().__str__() + f", Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return super().__repr__() + f", Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
class Mana_Potion(Potion):
	"""Mana potions that can be used to restore mana."""
	def __init__(self, name: str = "Mana Potion", description: str = "A basic mana potion", price: int = 0, effect: str = "mana" , amount: int = 0, duration: int = 0, lvl: int = 0) -> None:
		super().__init__(name, description, price, effect, amount, duration, lvl)
		self.name: str = "Mana Potion" if name == "" else name
		self.effect: str = "mana"
		if self.lvls.lvl == 1:
			self.description: str = "A basic mana potion" if description == "" else description
			self.price: int = 10 if price == 0 else price
			self.amount: int = 25 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
		elif self.lvls.lvl == 2:
			self.description: str = "A Grade 2 mana potion" if description == "" else description
			self.price: int = 20 if price == 0 else price
			self.amount: int = 100 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
		elif self.lvls.lvl == 3:
			self.description: str = "A Grade 3 mana potion" if description == "" else description
			self.price: int = 30 if price == 0 else price
			self.effect: str = 'mana'
			self.amount: int = 250 if amount == 0 else amount
			self.duration: int = 1 if duration == 0 else duration
	def __str__(self) -> str:
		return super().__str__() + f", Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return super().__repr__() + f", Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
class Stamina_Potion(Potion):
	"""Stamina potions that can be used to restore stamina."""
	def __init__(self, name: str = "Stamina Potion", description: str = "A basic stamina potion", price: int = 0, effect: str = "" , amount: int = 0, duration: int = 0, lvl: int = 0) -> None:
		super().__init__(name, description, price, effect, amount, duration, lvl)
		self.name: str = "Stamina Potion" if name == "" else name
		self.effect: str = "stamina"
		if self.lvls.lvl == 1:
			self.description: str = "A basic stamina potion" if description == "" else description
			self.price: int = 10 if price == 0 else price
			self.amount: int = 25 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
		elif self.lvls.lvl == 2:
			self.description: str = "A Grade 2 stamina potion" if description == "" else description
			self.price: int = 20 if price == 0 else price
			self.amount: int = 100 if amount == 0 else amount
			self.duration = 1 if duration == 0 else duration
		elif self.lvls.lvl == 3:
			self.description: str = "A Grade 3 stamina potion" if description == "" else description
			self.price: int = 30 if price == 0 else price
			self.amount: int = 250 if amount == 0 else amount
			self.duration: int = 1 if duration == 0 else duration
	def __str__(self) -> str:
		return super().__str__() + f", Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"
	def __repr__(self) -> str:
		return super().__repr__() + f", Effect: {self.effect}, Amount: {self.amount}, Duration: {self.duration}"