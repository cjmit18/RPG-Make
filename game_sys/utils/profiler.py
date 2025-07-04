# game_sys/utils/profiler.py
"""
Simple profiler for performance monitoring.
Future-ready for integration with external profiling tools.
"""

import time
from contextlib import contextmanager
from typing import List, Optional
from dataclasses import dataclass, field
from game_sys.logging import get_logger

# Create a dedicated logger for the profiler
profiler_logger = get_logger("game_sys.utils.profiler")


@dataclass
class ProfileSpan:
    """Represents a profiled time span."""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    children: List["ProfileSpan"] = field(default_factory=list)
    
    def finish(self) -> None:
        """Mark the span as finished and calculate duration."""
        if self.end_time is None:
            self.end_time = time.perf_counter()
            self.duration = self.end_time - self.start_time


class SimpleProfiler:
    """
    Simple profiler for tracking function/method execution times.
    
    This is a lightweight implementation that can be easily replaced
    with more sophisticated profiling tools in the future.
    """
    
    def __init__(self):
        self._enabled = False
        self._spans: List[ProfileSpan] = []
        self._current_span: Optional[ProfileSpan] = None
    
    def enable(self) -> None:
        """Enable profiling."""
        self._enabled = True
        profiler_logger.info("Profiling enabled")
    
    def disable(self) -> None:
        """Disable profiling."""
        self._enabled = False
        profiler_logger.info("Profiling disabled")
    
    def is_enabled(self) -> bool:
        """Check if profiling is enabled."""
        return self._enabled
    
    @contextmanager
    def span(self, name: str):
        """
        Context manager for profiling a code section.
        
        Usage:
            with profiler.span("combat_calculation"):
                # code to profile
                pass
        """
        if not self._enabled:
            yield
            return
        
        profiler_logger.debug(f"Starting profiling span: {name}")
        span = ProfileSpan(name=name, start_time=time.perf_counter())
        
        # Track parent-child relationships
        if self._current_span:
            self._current_span.children.append(span)
        else:
            self._spans.append(span)
        
        # Set as current span
        parent_span = self._current_span
        self._current_span = span
        
        try:
            yield span
        finally:
            # Finish the span
            span.finish()
            duration_ms = (span.duration or 0) * 1000
            profiler_logger.debug(
                f"Completed profiling span: {name} in {duration_ms:.2f}ms"
            )
            # Restore parent span
            self._current_span = parent_span
    
    def get_results(self) -> List[ProfileSpan]:
        """Get all profiling results."""
        return self._spans.copy()
    
    def clear(self) -> None:
        """Clear all profiling data."""
        count = len(self._spans)
        self._spans.clear()
        self._current_span = None
        profiler_logger.info(f"Cleared {count} profiling spans")
    
    def print_summary(self) -> None:
        """Print a summary of profiling results."""
        if not self._spans:
            profiler_logger.info("No profiling data available.")
            return
        
        profiler_logger.info("Profiling Summary:")
        profiler_logger.info("-" * 50)
        for span in self._spans:
            self._print_span(span, indent=0)
    
    def _print_span(self, span: ProfileSpan, indent: int = 0) -> None:
        """Print a single span with indentation for hierarchy."""
        prefix = "  " * indent
        duration_ms = (span.duration or 0) * 1000
        profiler_logger.info(f"{prefix}{span.name}: {duration_ms:.2f}ms")
        
        for child in span.children:
            self._print_span(child, indent + 1)


# Global profiler instance
profiler = SimpleProfiler()
