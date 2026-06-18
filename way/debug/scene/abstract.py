"""
This submodule contains the abstract base classes for the submodule.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, override

from ...components.abstract import UiComponent

if TYPE_CHECKING:
    from ...game.state import GameState


__all__ = ("SceneDebug",)


class SceneDebug(UiComponent):
    """Scene debug helper for game state."""

    @override
    def init(self, state: GameState) -> None:
        """Initializes the scene debug with game state."""

    @override
    def draw(self, state: GameState) -> None:
        """Draws the scene debug."""

    @override
    def update(self, state: GameState, dt: float) -> None:
        """Updates the scene debug and returns the next scene that will be next."""

    @override
    def clean(self, state: GameState) -> None:
        """Performs scene debug cleanup."""
