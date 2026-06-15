"""
This submodule contains the interface objects and types for the submodule.
"""

from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

from .constants import Scene

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "GameScene",
)


class GameScene(Protocol):
    """Describes the scene in the game."""

    def init(self, state: GameState) -> None:
        """Initializes the scene with game state."""
        ...

    def draw(self, state: GameState) -> None:
        """Draws the scene."""
        ...

    def update(self, dt: float, state: GameState) -> Scene:
        """Updates the scene and returns the next scene that will be next."""
        ...
