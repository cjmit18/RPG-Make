"""
Global configuration constants for game_sys.
"""

from pathlib import Path
from typing import Dict

# ——————————————————————————————————————————————
# Logging
# ——————————————————————————————————————————————
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

# ——————————————————————————————————————————————
# Randomness
# ——————————————————————————————————————————————
# Default RNG seed (None for system time)
DEFAULT_RNG_SEED: int = None

# ——————————————————————————————————————————————
# Enchantment & Scaling Defaults
# ——————————————————————————————————————————————
DEFAULT_GRADE_MULT: float = 0.10
DEFAULT_LEVEL_EXPONENT: float = 0.75
DEFAULT_MAX_LEVEL: int = 100

# Rarity multipliers for stats
RARITY_STATS_MULTIPLIER: Dict[str, float] = {
    "COMMON":    1.00,
    "UNCOMMON":  1.50,
    "RARE":      2.00,
    "EPIC":      2.50,
    "LEGENDARY": 3.00,
    "MYTHIC":    3.50,
    "DIVINE":    5.00,
}

# Grade multipliers
GRADE_STATS_MULTIPLIER: Dict[int, float] = {
    1: 1.00,
    2: 1.25,
    3: 1.50,
    4: 1.75,
    5: 2.00,
    6: 2.50,
    7: 5.00,
}

# ——————————————————————————————————————————————
# Combat Configuration
# ——————————————————————————————————————————————
# Pivot for percent-based defense reduction; higher allows more raw damage through.
DEFENSE_PIVOT: float = 100.0
# Exponent on defense for diminishing returns.
DEFENSE_ALPHA: float = 1.2
# Flat subtraction factor (e.g. 0.1 means subtract 10% of defense).
FLAT_DEFENSE_FACTOR: float = 0.1
# Minimum fraction of raw damage after flat subtraction (before percent reduction).
MIN_DAMAGE_PERCENT: float = 0.1
# Default critical hit chance and variance
CRIT_CHANCE_DEFAULT: float = 0.10
VARIANCE_DEFAULT: float = 0.10

# ——————————————————————————————————————————————
# Loot & Drop Defaults
# ——————————————————————————————————————————————
# Default rarity weight if none specified
DEFAULT_RARITY_WEIGHTS: Dict[str, float] = {
    "common": 1.0,
    "uncommon": 0.5,
    "rare": 0.1,
    "epic": 0.05,
    "legendary": 0.01,
    "mythic": 0.005,
    "divine": 0.001,
}

# ——————————————————————————————————————————————
# Paths
# ——————————————————————————————————————————————
DATA_DIR: Path = Path(__file__).parent / "data"
