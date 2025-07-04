#!/usr/bin/env python3
"""
Layout System
===========

This module provides a layout system for organizing UI elements.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Union, Any
import tkinter as tk
from tkinter import ttk

from ..base_widget import BaseWidget


class LayoutDirection(Enum):
    """Enum defining layout directions."""
    HORIZONTAL = auto()
    VERTICAL = auto()


class Alignment(Enum):
    """Enum defining alignment options."""
    START = auto()
    CENTER = auto()
    END = auto()
    STRETCH = auto()


class LayoutConstraints:
    """Constraints for positioning and sizing widgets in a layout."""
    
    def __init__(
        self,
        min_width: Optional[int] = None,
        max_width: Optional[int] = None,
        min_height: Optional[int] = None,
        max_height: Optional[int] = None,
        preferred_width: Optional[int] = None,
        preferred_height: Optional[int] = None,
        margin: Union[int, Tuple[int, int, int, int]] = 0,
        horizontal_alignment: Alignment = Alignment.START,
        vertical_alignment: Alignment = Alignment.START,
        weight: int = 0
    ):
        """Initialize layout constraints.
        
        Args:
            min_width: Minimum width in pixels
            max_width: Maximum width in pixels
            min_height: Minimum height in pixels
            max_height: Maximum height in pixels
            preferred_width: Preferred width in pixels
            preferred_height: Preferred height in pixels
            margin: Margin in pixels (all sides or (top, right, bottom, left))
            horizontal_alignment: Horizontal alignment
            vertical_alignment: Vertical alignment
            weight: Weight for flex distribution (0 means fixed size)
        """
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height
        self.preferred_width = preferred_width
        self.preferred_height = preferred_height
        
        # Parse margin
        if isinstance(margin, int):
            self.margin_top = margin
            self.margin_right = margin
            self.margin_bottom = margin
            self.margin_left = margin
        else:
            self.margin_top, self.margin_right, self.margin_bottom, self.margin_left = margin
            
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment
        self.weight = weight
        
    @property
    def has_flex(self) -> bool:
        """Check if this constraint uses flex (weight-based) sizing."""
        return self.weight > 0


class LayoutItem:
    """An item in a layout."""
    
    def __init__(
        self,
        widget: BaseWidget,
        constraints: Optional[LayoutConstraints] = None
    ):
        """Initialize a layout item.
        
        Args:
            widget: The widget to lay out
            constraints: Layout constraints for this widget
        """
        self.widget = widget
        self.constraints = constraints or LayoutConstraints()
        
        # Current layout state
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0


class Layout(BaseWidget):
    """Base class for layouts."""
    
    def __init__(self, parent=None, **kwargs):
        """Initialize the layout.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments
        """
        super().__init__(parent, **kwargs)
        self.items: List[LayoutItem] = []
        
    def add(
        self,
        widget: BaseWidget,
        constraints: Optional[LayoutConstraints] = None
    ) -> 'Layout':
        """Add a widget to the layout.
        
        Args:
            widget: The widget to add
            constraints: Layout constraints for this widget
            
        Returns:
            self for method chaining
        """
        item = LayoutItem(widget, constraints)
        self.items.append(item)
        self.add_child(widget)
        return self
        
    def remove(self, widget: BaseWidget) -> bool:
        """Remove a widget from the layout.
        
        Args:
            widget: The widget to remove
            
        Returns:
            True if the widget was removed, False otherwise
        """
        for i, item in enumerate(self.items):
            if item.widget == widget:
                self.items.pop(i)
                self.remove_child(widget)
                return True
        return False
        
    def create_widget(self, tk_parent) -> ttk.Frame:
        """Create the layout's container widget.
        
        Args:
            tk_parent: The Tkinter parent widget
            
        Returns:
            The created Tkinter widget
        """
        self._tk_widget = ttk.Frame(tk_parent)
        
        # Create child widgets
        for item in self.items:
            item.widget.create_widget(self._tk_widget)
            
        # Layout the children
        self.layout_children()
        
        return self._tk_widget
        
    def layout_children(self):
        """Layout the child widgets.
        
        This method should be implemented by subclasses to perform
        the actual layout logic.
        """
        pass


class BoxLayout(Layout):
    """A layout that arranges widgets in a horizontal or vertical box."""
    
    def __init__(
        self,
        parent=None,
        direction: LayoutDirection = LayoutDirection.VERTICAL,
        spacing: int = 5,
        **kwargs
    ):
        """Initialize the box layout.
        
        Args:
            parent: The parent widget
            direction: The layout direction
            spacing: Spacing between widgets in pixels
            **kwargs: Additional arguments
        """
        super().__init__(parent, **kwargs)
        self.direction = direction
        self.spacing = spacing
        
    def layout_children(self):
        """Layout the child widgets in a box."""
        if not self._tk_widget or not self.items:
            return
            
        # Get container dimensions
        container_width = self._tk_widget.winfo_width()
        container_height = self._tk_widget.winfo_height()
        
        # Ensure we have valid dimensions
        if container_width <= 1 or container_height <= 1:
            # Widget not fully realized yet, use requested size
            container_width = self._tk_widget.winfo_reqwidth()
            container_height = self._tk_widget.winfo_reqheight()
            
            # Fall back to default if still invalid
            if container_width <= 1:
                container_width = 100
            if container_height <= 1:
                container_height = 100
                
        # Calculate sizes
        if self.direction == LayoutDirection.HORIZONTAL:
            self._layout_horizontal(container_width, container_height)
        else:
            self._layout_vertical(container_width, container_height)
            
    def _layout_horizontal(self, container_width: int, container_height: int):
        """Layout widgets horizontally.
        
        Args:
            container_width: Container width in pixels
            container_height: Container height in pixels
        """
        # Calculate available space after margins and spacing
        total_margin_width = sum(
            item.constraints.margin_left + item.constraints.margin_right
            for item in self.items
        )
        total_spacing = self.spacing * (len(self.items) - 1) if len(self.items) > 1 else 0
        available_width = container_width - total_margin_width - total_spacing
        
        # Divide space between flex items
        flex_items = [item for item in self.items if item.constraints.has_flex]
        fixed_items = [item for item in self.items if not item.constraints.has_flex]
        
        # Calculate space used by fixed-size items
        fixed_width = 0
        for item in fixed_items:
            item_width = item.constraints.preferred_width or 0
            if item.constraints.min_width is not None:
                item_width = max(item_width, item.constraints.min_width)
            if item.constraints.max_width is not None:
                item_width = min(item_width, item.constraints.max_width)
            fixed_width += item_width
            
        # Calculate remaining space for flex items
        flex_space = max(0, available_width - fixed_width)
        total_weight = sum(item.constraints.weight for item in flex_items)
        
        # Position and size each widget
        x = 0
        for item in self.items:
            # Calculate item width
            if item.constraints.has_flex:
                # Flex item
                if total_weight > 0:
                    item_width = int(flex_space * item.constraints.weight / total_weight)
                else:
                    item_width = 0
            else:
                # Fixed item
                item_width = item.constraints.preferred_width or 0
                
            # Apply min/max constraints
            if item.constraints.min_width is not None:
                item_width = max(item_width, item.constraints.min_width)
            if item.constraints.max_width is not None:
                item_width = min(item_width, item.constraints.max_width)
                
            # Calculate item height based on vertical alignment
            if item.constraints.vertical_alignment == Alignment.STRETCH:
                item_height = container_height - item.constraints.margin_top - item.constraints.margin_bottom
            else:
                item_height = item.constraints.preferred_height or container_height - item.constraints.margin_top - item.constraints.margin_bottom
                if item.constraints.min_height is not None:
                    item_height = max(item_height, item.constraints.min_height)
                if item.constraints.max_height is not None:
                    item_height = min(item_height, item.constraints.max_height)
                    
            # Calculate vertical position
            if item.constraints.vertical_alignment == Alignment.CENTER:
                y = item.constraints.margin_top + (container_height - item.constraints.margin_top - item.constraints.margin_bottom - item_height) // 2
            elif item.constraints.vertical_alignment == Alignment.END:
                y = container_height - item.constraints.margin_bottom - item_height
            else:  # START or STRETCH
                y = item.constraints.margin_top
                
            # Update item position and size
            item.x = x + item.constraints.margin_left
            item.y = y
            item.width = item_width
            item.height = item_height
            
            # Position the widget using Tkinter's place manager
            item.widget._tk_widget.place(
                x=item.x, y=item.y, width=item.width, height=item.height
            )
            
            # Move to next position
            x += item_width + item.constraints.margin_left + item.constraints.margin_right + self.spacing
            
    def _layout_vertical(self, container_width: int, container_height: int):
        """Layout widgets vertically.
        
        Args:
            container_width: Container width in pixels
            container_height: Container height in pixels
        """
        # Calculate available space after margins and spacing
        total_margin_height = sum(
            item.constraints.margin_top + item.constraints.margin_bottom
            for item in self.items
        )
        total_spacing = self.spacing * (len(self.items) - 1) if len(self.items) > 1 else 0
        available_height = container_height - total_margin_height - total_spacing
        
        # Divide space between flex items
        flex_items = [item for item in self.items if item.constraints.has_flex]
        fixed_items = [item for item in self.items if not item.constraints.has_flex]
        
        # Calculate space used by fixed-size items
        fixed_height = 0
        for item in fixed_items:
            item_height = item.constraints.preferred_height or 0
            if item.constraints.min_height is not None:
                item_height = max(item_height, item.constraints.min_height)
            if item.constraints.max_height is not None:
                item_height = min(item_height, item.constraints.max_height)
            fixed_height += item_height
            
        # Calculate remaining space for flex items
        flex_space = max(0, available_height - fixed_height)
        total_weight = sum(item.constraints.weight for item in flex_items)
        
        # Position and size each widget
        y = 0
        for item in self.items:
            # Calculate item height
            if item.constraints.has_flex:
                # Flex item
                if total_weight > 0:
                    item_height = int(flex_space * item.constraints.weight / total_weight)
                else:
                    item_height = 0
            else:
                # Fixed item
                item_height = item.constraints.preferred_height or 0
                
            # Apply min/max constraints
            if item.constraints.min_height is not None:
                item_height = max(item_height, item.constraints.min_height)
            if item.constraints.max_height is not None:
                item_height = min(item_height, item.constraints.max_height)
                
            # Calculate item width based on horizontal alignment
            if item.constraints.horizontal_alignment == Alignment.STRETCH:
                item_width = container_width - item.constraints.margin_left - item.constraints.margin_right
            else:
                item_width = item.constraints.preferred_width or container_width - item.constraints.margin_left - item.constraints.margin_right
                if item.constraints.min_width is not None:
                    item_width = max(item_width, item.constraints.min_width)
                if item.constraints.max_width is not None:
                    item_width = min(item_width, item.constraints.max_width)
                    
            # Calculate horizontal position
            if item.constraints.horizontal_alignment == Alignment.CENTER:
                x = item.constraints.margin_left + (container_width - item.constraints.margin_left - item.constraints.margin_right - item_width) // 2
            elif item.constraints.horizontal_alignment == Alignment.END:
                x = container_width - item.constraints.margin_right - item_width
            else:  # START or STRETCH
                x = item.constraints.margin_left
                
            # Update item position and size
            item.x = x
            item.y = y + item.constraints.margin_top
            item.width = item_width
            item.height = item_height
            
            # Position the widget using Tkinter's place manager
            item.widget._tk_widget.place(
                x=item.x, y=item.y, width=item.width, height=item.height
            )
            
            # Move to next position
            y += item_height + item.constraints.margin_top + item.constraints.margin_bottom + self.spacing


class GridLayout(Layout):
    """A layout that arranges widgets in a grid."""
    
    def __init__(
        self,
        parent=None,
        rows: int = 1,
        columns: int = 1,
        row_spacing: int = 5,
        column_spacing: int = 5,
        **kwargs
    ):
        """Initialize the grid layout.
        
        Args:
            parent: The parent widget
            rows: Number of rows
            columns: Number of columns
            row_spacing: Spacing between rows in pixels
            column_spacing: Spacing between columns in pixels
            **kwargs: Additional arguments
        """
        super().__init__(parent, **kwargs)
        self.rows = rows
        self.columns = columns
        self.row_spacing = row_spacing
        self.column_spacing = column_spacing
        self.grid_items: Dict[Tuple[int, int], LayoutItem] = {}
        
    def add_at(
        self,
        row: int,
        column: int,
        widget: BaseWidget,
        constraints: Optional[LayoutConstraints] = None,
        row_span: int = 1,
        column_span: int = 1
    ) -> 'GridLayout':
        """Add a widget at a specific grid position.
        
        Args:
            row: Row index (0-based)
            column: Column index (0-based)
            widget: The widget to add
            constraints: Layout constraints for this widget
            row_span: Number of rows this widget spans
            column_span: Number of columns this widget spans
            
        Returns:
            self for method chaining
        """
        if row < 0 or row >= self.rows or column < 0 or column >= self.columns:
            raise ValueError(f"Invalid grid position: {row}, {column}")
            
        item = LayoutItem(widget, constraints)
        item.row = row
        item.column = column
        item.row_span = max(1, min(row_span, self.rows - row))
        item.column_span = max(1, min(column_span, self.columns - column))
        
        # Check for overlapping cells
        for r in range(row, row + item.row_span):
            for c in range(column, column + item.column_span):
                if (r, c) in self.grid_items:
                    raise ValueError(f"Cell {r}, {c} already occupied")
                self.grid_items[(r, c)] = item
                
        self.items.append(item)
        self.add_child(widget)
        return self
        
    def remove(self, widget: BaseWidget) -> bool:
        """Remove a widget from the layout.
        
        Args:
            widget: The widget to remove
            
        Returns:
            True if the widget was removed, False otherwise
        """
        for i, item in enumerate(self.items):
            if item.widget == widget:
                # Remove from grid
                for r in range(item.row, item.row + item.row_span):
                    for c in range(item.column, item.column + item.column_span):
                        if (r, c) in self.grid_items:
                            del self.grid_items[(r, c)]
                            
                # Remove from items
                self.items.pop(i)
                self.remove_child(widget)
                return True
                
        return False
        
    def layout_children(self):
        """Layout the child widgets in a grid."""
        if not self._tk_widget or not self.items:
            return
            
        # Get container dimensions
        container_width = self._tk_widget.winfo_width()
        container_height = self._tk_widget.winfo_height()
        
        # Ensure we have valid dimensions
        if container_width <= 1 or container_height <= 1:
            # Widget not fully realized yet, use requested size
            container_width = self._tk_widget.winfo_reqwidth()
            container_height = self._tk_widget.winfo_reqheight()
            
            # Fall back to default if still invalid
            if container_width <= 1:
                container_width = 100
            if container_height <= 1:
                container_height = 100
                
        # Calculate cell dimensions
        total_spacing_width = self.column_spacing * (self.columns - 1)
        total_spacing_height = self.row_spacing * (self.rows - 1)
        
        cell_width = (container_width - total_spacing_width) // self.columns
        cell_height = (container_height - total_spacing_height) // self.rows
        
        # Position and size each widget
        for item in self.items:
            # Calculate position
            x = item.column * (cell_width + self.column_spacing)
            y = item.row * (cell_height + self.row_spacing)
            
            # Calculate size
            width = item.column_span * cell_width + (item.column_span - 1) * self.column_spacing
            height = item.row_span * cell_height + (item.row_span - 1) * self.row_spacing
            
            # Apply margins
            x += item.constraints.margin_left
            y += item.constraints.margin_top
            width -= item.constraints.margin_left + item.constraints.margin_right
            height -= item.constraints.margin_top + item.constraints.margin_bottom
            
            # Apply min/max constraints
            if item.constraints.min_width is not None:
                width = max(width, item.constraints.min_width)
            if item.constraints.max_width is not None:
                width = min(width, item.constraints.max_width)
            if item.constraints.min_height is not None:
                height = max(height, item.constraints.min_height)
            if item.constraints.max_height is not None:
                height = min(height, item.constraints.max_height)
                
            # Update item position and size
            item.x = x
            item.y = y
            item.width = width
            item.height = height
            
            # Position the widget using Tkinter's place manager
            item.widget._tk_widget.place(
                x=item.x, y=item.y, width=item.width, height=item.height
            )
