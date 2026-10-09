"""
Notification System Module

This module provides event-driven notification management for the RPG engine.
It demonstrates observer pattern implementation by reacting to game events
and providing user-friendly feedback notifications.
"""

from .notification_system import NotificationSystem, Notification, NotificationEvent, NotificationType

__all__ = ['NotificationSystem', 'Notification', 'NotificationEvent', 'NotificationType']
