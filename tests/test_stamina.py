from game_sys.character.character_factory import create_character

hero = create_character('hero')
print(f"Max stamina: {hero.max_stamina}")
print(f"Current stamina: {hero.current_stamina}")
