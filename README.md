# Game Sys

A Python-based RPG engine providing character creation, combat, items, and job systems.  
This repository contains both the `game_sys/` package (core engine) and a `playground.py` demo for testing.

---

## Table of Contents

1. [Features](#features)  
2. [Getting Started](#getting-started)  
   1. [Prerequisites](#prerequisites)  
   2. [Installation](#installation)  
   3. [Directory Layout](#directory-layout)  
   4. [Usage](#usage)  
3. [Testing](#testing)  
4. [Contributing](#contributing)  
5. [License](#license)

---

## Features

- **Character Creation** via JSON templates (Warrior, Mage, etc.)  
- **Scaling Stats & Leveling** based on “job” classes  
- **Inventory & Items** (Equipable, Consumable, etc.)  
- **Combat System** (damage, crits, RNG abstractions, encounter loops)  
- **Job System** (loadable from JSON, factories, base stats)  
- **Save/Load** supports serializing characters (including inventory) to/from JSON.  

---

## Getting Started

### Prerequisites

- Python 3.8+  
- `pip` (or `pipenv` / `venv`)  
- (Optional) `virtualenv` to keep dependencies isolated  

### Installation

1. Clone the repo:
   git clone https://github.com/your‐username/game_sys.git
   cd game_sys
2. (Recommended) Create and activate a virtual environment:
    python3 -m venv venv
    source venv/bin/activate   # LinuxmacOS
    venv\Scripts\activate      #Windows
3. Install required Python packages:
    pip install -r requirements.txt
4. (Optional) If you plan to install game_sys system‐wide for import:
    pip install .
    This will install the game_sys package so you can do e.g.: 
    "from game_sys.core.character_creation import create_character"
### Directory Layout
.
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── pyproject.toml       
├── CONTRIBUTING.md     
├── playground.py        # Demo script / entry point
├── logs/
│   └── logs.py          # Logging configuration
├── game_sys/            # Main package
│   ├── __init__.py
│   ├── gen.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── actor.py
│   │   ├── combat_functions.py
│   │   ├── encounter.py
│   │   ├── experience_functions.py
│   │   ├── save_load.py
│   │   ├── stats.py
│   │
│   │ 
│   │
│   │ 
│   │ 
│   ├── inventory/
│   │   ├── __init__.py
│   │   ├── inventory_functions.py
│   │   └── data/
│   │       └── inventories.json
|   ├── character/
|   |    ├── __init__.py
|   |    ├── inventory_functions.py
|   |    └── data/
|   |       └── inventories.json
│   ├── items/
│   │   ├── __init__.py
│   │   ├── item_base.py
│   │   ├── factory.py
│   │   ├── loader.py
│   │   ├── consumable_list.py
│   │   └── data/
│   │       └── items.json
│   └── jobs/
│       ├── __init__.py
│       ├── base.py
│       ├── factory.py
│       ├── loader.py
│       └── data/
│           └── jobs.json
└── tests/
    ├── __init__.py
    ├── test_actor.py
    ├── test_inventory.py
    ├── test_items.py
    └── test_jobs.py

### USAGE

1. Run the demo (playground):
    python playground.py
    This script exercises:
        Creating characters from JSON templates
        Equipping items, adding/removing inventory
        Running a simple encounter between a Player and an Enemy
        Saving/loading a character to/from JSON
2. Import the package into your own code:
    "from game_sys.core.character_creation import create_character"
    "_functions import Combat"
    "from game_sys.core.actor import Actor"

3. Writing Your Own Script:
    # my_script.py
    from game_sys.core.character_creation import create_character, save_character_to_json, load_character_from_json

    # Create a level‐3 Warrior:
    hero = create_character("Warrior", level=3)
    print(hero)

    # Save to JSON:
    save_character_to_json(hero, "hero_save.json")

    # Later… load from disk:
    loaded_hero = load_character_from_json("hero_save.json")
    print("Loaded:", loaded_hero)

### Testing
    We use pytest for automated tests. To run:
        pytest --maxfail=1 --disable-warnings -q
    For a coverage report (requires pytest-cov in requirements.txt):
        pytest --cov=game_sys

### Contributing
    Fork the repository.

    Create a new branch (git checkout -b feature/myfeature).

    Make changes, add tests, and ensure all tests pass.

    Submit a pull request.

    Please follow these guidelines:

    Use PEP8 style (flake8 / pylint recommended).

    Add type hints and docstrings for any new public methods.

    Write unit tests under tests/ and aim for > 80% coverage.

    Run mypy . to catch typing issues.
### License
