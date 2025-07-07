#!/usr/bin/env python3
"""
Cleanup Script
=============

This script removes old debug and test files that are no longer needed.

Usage:
    python cleanup.py          # Perform cleanup
    python cleanup.py --dry    # Show what would be cleaned (dry run)
"""

import os
import sys
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
    
    # Older test files - removed during test cleanup
    "test_leveling_system.py",
    
    # Log files that can be regenerated
    "ui_debug_*.log",
    
    # Test files cleaned up in test folder reorganization
    "tests/test_comprehensive_backup.py",
    "tests/test_comprehensive_fixed.py",
    "tests/test_comprehensive_final.py",
    "tests/test_comprehensive_new.py",
    "tests/test_combat_new.py",
    "tests/test_integration_new.py",
    "tests/test_complete_system.py",
    "tests/test_demo_manual.py",
    "tests/test_demo_stat_allocation.py",
    "tests/test_final.py",
    "tests/test_simple.py",
    "tests/test_dual_wield.py",
    "tests/test_stamina.py",
    "tests/test_basic_properties.py",
    "tests/console_methods.py",
    "tests/enhanced_leveling_demo.py",
    
    # Recent fix verification files - can be regenerated if needed
    "check_items.py",
    "demo_fixes_summary.py",
    "demo_verification.py",
    "test_combat_fixes.py",
    "test_demo_fixes.py",
    "test_dual_wield_fix.py",
    "test_fixes.py",
    "test_fixes_verification.py",
    "comprehensive_effect_test.py",
    "debug_starting_equipment.py",
    
    # Individual test files that have been moved to tests folder
    "test_armor_equip.py",
    "test_ui_defense.py",
]

# Directories to organize
MARKDOWN_FILES_TO_MOVE = {
    # Source: Destination
    "mds/CLEANUP_README.md": "docs/CLEANUP_README.md",
    "mds/DEMO_README.md": "docs/DEMO_README.md",
    "mds/UI_CLEANUP_README.md": "docs/UI_CLEANUP_README.md",
    "mds/UI_LOGGING_README.md": "docs/UI_LOGGING_README.md",
    "mds/UI_SYSTEM_README.md": "docs/UI_SYSTEM_README.md",
    "mds/TRADITIONAL_RPG_STATS_SUMMARY.md": (
        "docs/TRADITIONAL_RPG_STATS_SUMMARY.md"
    ),
    "mds/RPG_STATS_IMPLEMENTATION_SUMMARY.md": (
        "docs/RPG_STATS_IMPLEMENTATION_SUMMARY.md"
    ),
    "RPG_STATS_IMPLEMENTATION_SUMMARY.md": (
        "docs/RPG_STATS_IMPLEMENTATION_SUMMARY.md"
    ),
    
    # Recent fix summaries to preserve in docs
    "COMPREHENSIVE_FIXES_SUMMARY.md": "docs/COMPREHENSIVE_FIXES_SUMMARY.md",
    "DEMO_FIXES_COMPLETE.md": "docs/DEMO_FIXES_COMPLETE.md",
}


def clean_cache_directories():
    """Clean up Python cache directories and temporary files."""
    project_root = Path(os.path.dirname(os.path.realpath(__file__)))
    
    # Cache directories to clean
    cache_dirs = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".coverage",
        "test_results",
    ]
    
    cleaned = []
    errors = []
    
    # Remove cache directories recursively
    for cache_dir_name in cache_dirs:
        for cache_dir in project_root.rglob(cache_dir_name):
            if cache_dir.is_dir():
                try:
                    import shutil
                    shutil.rmtree(cache_dir)
                    cleaned.append(str(cache_dir.relative_to(project_root)))
                    logger.info(f"Removed cache directory: {cache_dir}")
                except Exception as e:
                    errors.append((str(cache_dir), str(e)))
                    logger.error(f"Error removing {cache_dir}: {e}")
            elif cache_dir.is_file():
                try:
                    cache_dir.unlink()
                    cleaned.append(str(cache_dir.relative_to(project_root)))
                    logger.info(f"Removed cache file: {cache_dir}")
                except Exception as e:
                    errors.append((str(cache_dir), str(e)))
                    logger.error(f"Error removing {cache_dir}: {e}")
    
    # Clean up log files except the current cleanup.log
    log_files = project_root.glob("*.log")
    for log_file in log_files:
        if log_file.name != "cleanup.log":
            try:
                log_file.unlink()
                cleaned.append(str(log_file.relative_to(project_root)))
                logger.info(f"Removed log file: {log_file}")
            except Exception as e:
                errors.append((str(log_file), str(e)))
                logger.error(f"Error removing {log_file}: {e}")
    
    return cleaned, errors


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


def move_test_files():
    """Move test files from root directory to tests/ folder."""
    project_root = Path(os.path.dirname(os.path.realpath(__file__)))
    tests_dir = project_root / "tests"
    
    # Create tests directory if it doesn't exist
    tests_dir.mkdir(exist_ok=True)
    
    moved = []
    errors = []
    
    # Find all test_*.py files in root directory
    root_test_files = project_root.glob("test_*.py")
    
    for test_file in root_test_files:
        dest_path = tests_dir / test_file.name
        try:
            # Check if destination already exists
            if dest_path.exists():
                logger.warning(f"Destination exists: {dest_path.name}, skipping")
                continue
                
            # Move the file
            test_file.rename(dest_path)
            moved.append(test_file.name)
            logger.info(f"Moved test file: {test_file.name} → tests/")
        except Exception as e:
            errors.append((test_file.name, str(e)))
            logger.error(f"Error moving {test_file.name}: {e}")
    
    return moved, errors


def main():
    """Main entry point for the cleanup script."""
    # Check for dry run option
    dry_run = "--dry" in sys.argv or "--dry-run" in sys.argv
    
    if dry_run:
        logger.info("DRY RUN MODE - No files will be actually removed")
    
    # Get the project root
    project_root = Path(os.path.dirname(os.path.realpath(__file__)))
    
    logger.info(f"Cleaning up files in {project_root}")
    
    # Track removed files
    removed = []
    not_found = []
    errors = []
    
    # Move test files from root to tests folder
    action_word = "Would move" if dry_run else "Moving"
    logger.info(f"\n{action_word} test files from root to tests/...")
    if not dry_run:
        test_moved, test_errors = move_test_files()
        errors.extend(test_errors)
    else:
        # For dry run, just show what would be moved
        test_moved = []
        root_test_files = project_root.glob("test_*.py")
        for test_file in root_test_files:
            test_moved.append(test_file.name)

    # Remove each file if it exists
    for filename in FILES_TO_REMOVE:
        file_path = project_root / filename
        logger.info(f"Checking file: {filename}")
        
        if file_path.exists():
            try:
                if not dry_run:
                    os.remove(file_path)
                removed.append(filename)
                action = "Would remove" if dry_run else "Removed"
                logger.info(f"{action}: {filename}")
            except Exception as e:
                if not dry_run:
                    errors.append((filename, str(e)))
                    logger.error(f"Error removing {filename}: {e}")
        else:
            not_found.append(filename)
            logger.info(f"Not found: {filename}")
    
    # Clean cache directories and temporary files
    action_word = "Would clean" if dry_run else "Cleaning"
    logger.info(f"\n{action_word} cache directories and temporary files...")
    if not dry_run:
        cache_cleaned, cache_errors = clean_cache_directories()
        errors.extend(cache_errors)
    else:
        # For dry run, just list what would be cleaned
        cache_cleaned = []
        project_root = Path(os.path.dirname(os.path.realpath(__file__)))
        for cache_dir_name in ["__pycache__", ".pytest_cache", ".mypy_cache"]:
            for cache_dir in project_root.rglob(cache_dir_name):
                cache_cleaned.append(str(cache_dir.relative_to(project_root)))
    
    # Organize markdown files
    action_word = "Would organize" if dry_run else "Organizing"
    logger.info(f"\n{action_word} markdown files...")
    if not dry_run:
        moved, md_not_found, md_errors = organize_markdown_files()
        errors.extend(md_errors)
    else:
        # For dry run, just show what would be moved
        moved = []
        for source, dest in MARKDOWN_FILES_TO_MOVE.items():
            source_path = project_root / source
            if source_path.exists():
                moved.append(f"{source} → {dest}")
    
    # Move test files to tests/ directory
    action_word = "Would move" if dry_run else "Moving"
    logger.info(f"\n{action_word} test files to tests/ directory...")
    if not dry_run:
        test_moved, test_errors = move_test_files()
        errors.extend(test_errors)
    else:
        # For dry run, just show what would be moved
        test_moved = []
        project_root = Path(os.path.dirname(os.path.realpath(__file__)))
        for test_file in project_root.glob("test_*.py"):
            test_moved.append(test_file.name)
    
    # Clean up empty mds directory if all files were moved
    if not dry_run:
        mds_dir = project_root / "mds"
        if mds_dir.exists() and not any(mds_dir.iterdir()):
            try:
                mds_dir.rmdir()
                logger.info("Removed empty mds/ directory")
            except Exception as e:
                logger.error(f"Could not remove mds/ directory: {e}")
    
    # Print summary
    summary_word = "DRY RUN" if dry_run else "Cleanup"
    logger.info(f"\n{summary_word} Summary:")
    action_word = "would be" if dry_run else "were"
    logger.info(f"- {len(removed)} files {action_word} removed")
    cache_action = f"cache files/directories {action_word} cleaned"
    logger.info(f"- {len(cache_cleaned)} {cache_action}")
    logger.info(f"- {len(not_found)} files not found")
    logger.info(f"- {len(moved)} markdown files {action_word} moved")
    logger.info(f"- {len(test_moved)} test files {action_word} moved")
    if not dry_run:
        logger.info(f"- {len(errors)} errors encountered")
    
    if removed:
        action_word = "Would remove" if dry_run else "Removed"
        logger.info(f"\n{action_word} files:")
        for file in removed:
            logger.info(f"- {file}")
    
    if cache_cleaned:
        action_word = "Would clean" if dry_run else "Cleaned"
        logger.info(f"\n{action_word} cache files/directories:")
        for item in cache_cleaned[:10]:  # Show first 10 to avoid spam
            logger.info(f"- {item}")
        if len(cache_cleaned) > 10:
            logger.info(f"... and {len(cache_cleaned) - 10} more")
    
    if moved:
        action_word = "Would move" if dry_run else "Moved"
        logger.info(f"\n{action_word} markdown files:")
        for move in moved:
            logger.info(f"- {move}")
    
    if test_moved:
        action_word = "Would move" if dry_run else "Moved"
        logger.info(f"\n{action_word} test files to tests/:")
        for test_file in test_moved:
            logger.info(f"- {test_file}")
    
    if errors and not dry_run:
        logger.error("\nErrors:")
        for file, error in errors:
            logger.error(f"- {file}: {error}")
    
    completion_word = "completed" if not dry_run else "simulation completed"
    logger.info(f"\nCleanup {completion_word} successfully!")
    
    if dry_run:
        logger.info("\nTo actually perform cleanup, run without --dry flag")


if __name__ == "__main__":
    main()
