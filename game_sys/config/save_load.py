"""
Async save/load utilities for party/world actors.
Includes async modding hooks for extensibility.
"""
import asyncio
import json
from typing import List
from game_sys.character.actor import Actor

try:
    import aiofiles
except ImportError:
    aiofiles = None

from game_sys.hooks.hooks_setup import emit_async, ON_PRE_SAVE, ON_POST_SAVE, ON_PRE_LOAD, ON_POST_LOAD

async def save_actors_async(actors: List[Actor], path: str) -> None:
    """Asynchronously save a list of actors to a file, with async modding hooks."""
    import os
    try:
        # Ensure the save directory exists
        save_dir = os.path.join(os.path.dirname(path), 'save') if not os.path.basename(os.path.dirname(path)) == 'save' else os.path.dirname(path)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, os.path.basename(path))
        await emit_async(ON_PRE_SAVE, actors=actors, path=save_path)
        data = [actor.serialize() for actor in actors]
        json_data = json.dumps(data)
        if aiofiles:
            async with aiofiles.open(save_path, 'w') as f:
                await f.write(json_data)
        else:
            await asyncio.to_thread(_save_sync, save_path, json_data)
        await emit_async(ON_POST_SAVE, actors=actors, path=save_path)
    except Exception as e:
        import logging
        logging.getLogger("save_load").error(f"Save failed: {e}")
        raise

def _save_sync(path: str, data: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)

async def load_actors_async(path: str) -> List[Actor]:
    """Asynchronously load a list of actors from a file, with async modding hooks."""
    import os
    try:
        # Always load from the save directory
        save_dir = os.path.join(os.path.dirname(path), 'save') if not os.path.basename(os.path.dirname(path)) == 'save' else os.path.dirname(path)
        save_path = os.path.join(save_dir, os.path.basename(path))
        await emit_async(ON_PRE_LOAD, path=save_path)
        if aiofiles:
            async with aiofiles.open(save_path, 'r') as f:
                data_str = await f.read()
        else:
            data_str = await asyncio.to_thread(_load_sync, save_path)
        data = json.loads(data_str)
        actors = []
        for actor_json in data:
            # actor_json is a JSON string, so parse it
            if isinstance(actor_json, str):
                actor_data = json.loads(actor_json)
            else:
                actor_data = actor_json
            # Use the saved name and base_stats
            name = actor_data.get('name', 'LoadedActor')
            base_stats = actor_data.get('base_stats', {})
            actor = Actor(name=name, base_stats=base_stats)
            actor.deserialize(json.dumps(actor_data))
            # Clamp all pools to their max after deserialization
            actor.update_stats()
            actor.current_health = min(actor.current_health, actor.max_health)
            actor.current_mana = min(actor.current_mana, actor.max_mana)
            actor.current_stamina = min(actor.current_stamina, actor.max_stamina)
            actors.append(actor)
        await emit_async(ON_POST_LOAD, actors=actors, path=save_path)
        return actors
    except Exception as e:
        import logging
        logging.getLogger("save_load").error(f"Load failed: {e}")
        return []

def _load_sync(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
