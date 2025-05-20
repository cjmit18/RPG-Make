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