"""
Thus submodule provide logcial mixin classes for components.
"""

from __future__ import annotations
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "LayoutCacheMixin",
)


class LayoutCacheMixin[TCache](abc.ABC):
    """Mixin to handle caching of UI layout metrics."""

    _layout_cache: TCache | None = None
    _last_width: int = -1
    _last_height: int = -1

    def get_layout(self, state: GameState) -> TCache:
        """Decides if we need to compute or reuse existing cache."""
        if self._is_cache_stale(state):
            self._layout_cache = self.compute_layout(state)
            self._last_width = state.width
            self._last_height = state.height

        assert self._layout_cache is not None
        return self._layout_cache

    def _is_cache_stale(self, state: GameState) -> bool:
        """Determines if the screen size or config has changed."""
        return (self._layout_cache is None or
                state.width != self._last_width or
                state.height != self._last_height)

    @abc.abstractmethod
    def compute_layout(self, state: GameState) -> TCache:
        """Performs the actual heavy lifting/math."""
