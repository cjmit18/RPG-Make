#!/usr/bin/env python3
"""
Administrative Tools Package
===========================

Administrative utilities, debugging tools, and system management.

Components:
- Admin service for system management
- Debug utilities and diagnostics
- System monitoring and performance tools
- Configuration management interface

Features:
- System health monitoring
- Performance profiling
- Configuration hot-reloading
- Debug command interface
- User management tools
"""

try:
    from .admin_service import AdminService
except ImportError:
    AdminService = None

__all__ = [
    "AdminService",
    "DebugManager"
]
