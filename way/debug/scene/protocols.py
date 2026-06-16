"""
This submodule contains the interface objects and types for the submodule.
"""

from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ...game.state import GameState
    from ...scene.constants import Scene


__all__ = (
    "SceneDebug",
)


class SceneDebug(Protocol):
    """Scene debug helper for game state."""

    def init(self, state: GameState) -> None:
        """Initializes the scene debug with game state."""
        ...

    def draw(self, state: GameState) -> None:
        """Draws the scene debug."""
        ...

    def update(self, dt: float, state: GameState) -> Scene | None:
        """Updates the scene debug and returns the next scene that will be next."""
        ...

    def clean(self, state: GameState) -> None:
        """Performs scene debug cleanup."""
        ...
