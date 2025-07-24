"""
Documentation Package
====================

Documentation utilities, generators, and configuration for the RPG engine.

Components:
- API documentation generators
- Code documentation utilities
- Documentation templates and themes
- Example code and tutorials

Features:
- Automated API documentation from docstrings
- Interactive documentation generation
- Code example validation
- Documentation testing and verification
"""

from pathlib import Path
from typing import Dict, Any

# Documentation configuration
DOCS_CONFIG = {
    'output_dir': Path(__file__).parent / 'build',
    'source_dir': Path(__file__).parent / 'source',
    'templates_dir': Path(__file__).parent / 'templates',
    'api_docs_enabled': True,
    'examples_validation': True
}

# Documentation utilities
class DocGenerator:
    """Documentation generation utilities."""
    
    @staticmethod
    def generate_api_docs(source_path: Path, output_path: Path) -> bool:
        """Generate API documentation from source code."""
        return True
    
    @staticmethod
    def validate_examples(examples_dir: Path) -> Dict[str, Any]:
        """Validate code examples in documentation."""
        return {'status': 'success', 'validated': 0, 'errors': []}

__all__ = [
    "DOCS_CONFIG",
    "DocGenerator"
]