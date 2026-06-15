"""
This submodule contains the interface objects and types for the submodule.
"""

from typing import Protocol

from .constants import Scene
from ..game import GameState


__all__ = (
    "GameScene",
)


class GameScene(Protocol):
    """Describes the scene in the game."""

    def draw(self, state: GameState) -> None:
        """Draws the scene."""
        ...

    def update(self, dt: float, state: GameState) -> Scene:
        """Updates the scene and returns the next scene that will be next."""
        ...
