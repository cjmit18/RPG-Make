#!/usr/bin/env python3
"""
Cleanup Script
=============

This script removes old debug and test files that are no longer needed.
"""

import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cleanup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cleanup")

# Files to remove
FILES_TO_REMOVE = [
    # Debug files
    "debug_ui.py",
    "debug_modular_ui.py",
    "debug_log_ui.py",
    "debug_advanced_ui_demo2.py",
    "comprehensive_ui_debug.py",
    "debug_tabbed_demo.py",
    "minimal_tkinter_demo.py",
    "simple_tabbed_demo.py",
    
    # Older demo versions
    "simplest_ui_demo.py",
    "simple_ui_demo.py", 
    "ui_demo.py",
    "fixed_ui_demo.py",
    "fixed_modular_ui_demo.py",
    "enhanced_ui_demo.py",
    "advanced_ui_demo.py",
    "advanced_ui_demo2.py",
    "console_demo.py",
    "button_demo.py",
    "simple_game_demo.py",
    "game_ui_demo.py",
    "unified_game_demo.py",
    
    # Now that we have demo.py, we can remove these
    "modular_ui_demo.py",
    "simplified_ui_demo.py",
    "final_game_demo.py",
    
    # Old test files - now replaced by comprehensive tests
    "debug_stats.py",
    "demonstrate_stats.py",
    "test_resource_stats.py",
    "verify_system.py",
    "rpg_demo.py",
    "test_stat_scaling.py",
    "verify_all_stats.py",
    "final_stat_test.py",
    
    # Older test files
    "test_leveling_system.py",
    "test_stat_relationships.py",
    "test_demo_stat_allocation.py",
    "test_final_integration.py",
    "test_complete_system.py",
    
    # Log files that can be regenerated
    "ui_debug_*.log",
]

# Directories to organize
MARKDOWN_FILES_TO_MOVE = {
    # Source: Destination
    "mds/CLEANUP_README.md": "docs/CLEANUP_README.md",
    "mds/DEMO_README.md": "docs/DEMO_README.md",
    "mds/UI_CLEANUP_README.md": "docs/UI_CLEANUP_README.md",
    "mds/UI_LOGGING_README.md": "docs/UI_LOGGING_README.md",
    "mds/UI_SYSTEM_README.md": "docs/UI_SYSTEM_README.md",
    "mds/TRADITIONAL_RPG_STATS_SUMMARY.md": "docs/TRADITIONAL_RPG_STATS_SUMMARY.md",
    "mds/RPG_STATS_IMPLEMENTATION_SUMMARY.md": "docs/RPG_STATS_IMPLEMENTATION_SUMMARY.md",
    "RPG_STATS_IMPLEMENTATION_SUMMARY.md": "docs/RPG_STATS_IMPLEMENTATION_SUMMARY.md",
}


def organize_markdown_files():
    """Move markdown files to docs/ directory."""
    project_root = Path(os.path.dirname(os.path.realpath(__file__)))
    
    # Create docs directory if it doesn't exist
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    moved = []
    not_found = []
    errors = []
    
    for source, destination in MARKDOWN_FILES_TO_MOVE.items():
        source_path = project_root / source
        dest_path = project_root / destination
        
        if source_path.exists():
            try:
                # Create destination directory if needed
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                source_path.rename(dest_path)
                moved.append(f"{source} → {destination}")
                logger.info(f"Moved: {source} → {destination}")
            except Exception as e:
                errors.append((source, str(e)))
                logger.error(f"Error moving {source}: {e}")
        else:
            not_found.append(source)
            logger.info(f"Not found: {source}")
    
    return moved, not_found, errors


def main():
    """Main entry point for the cleanup script."""
    # Get the project root
    project_root = Path(os.path.dirname(os.path.realpath(__file__)))
    
    logger.info(f"Cleaning up files in {project_root}")
    
    # Track removed files
    removed = []
    not_found = []
    errors = []
    
    # Remove each file if it exists
    for filename in FILES_TO_REMOVE:
        file_path = project_root / filename
        logger.info(f"Checking file: {filename}")
        
        if file_path.exists():
            try:
                os.remove(file_path)
                removed.append(filename)
                logger.info(f"Removed: {filename}")
            except Exception as e:
                errors.append((filename, str(e)))
                logger.error(f"Error removing {filename}: {e}")
        else:
            not_found.append(filename)
            logger.info(f"Not found: {filename}")
    
    # Organize markdown files
    logger.info("\nOrganizing markdown files...")
    moved, md_not_found, md_errors = organize_markdown_files()
    
    # Clean up empty mds directory if all files were moved
    mds_dir = project_root / "mds"
    if mds_dir.exists() and not any(mds_dir.iterdir()):
        try:
            mds_dir.rmdir()
            logger.info("Removed empty mds/ directory")
        except Exception as e:
            logger.error(f"Could not remove mds/ directory: {e}")
    
    # Print summary
    logger.info("\nCleanup Summary:")
    logger.info(f"- {len(removed)} files removed")
    logger.info(f"- {len(not_found)} files not found")
    logger.info(f"- {len(moved)} markdown files moved")
    logger.info(f"- {len(errors + md_errors)} errors encountered")
    
    if removed:
        logger.info("\nRemoved files:")
        for file in removed:
            logger.info(f"- {file}")
    
    if moved:
        logger.info("\nMoved markdown files:")
        for move in moved:
            logger.info(f"- {move}")
    
    if errors or md_errors:
        logger.error("\nErrors:")
        for file, error in errors + md_errors:
            logger.error(f"- {file}: {error}")


if __name__ == "__main__":
    main()
