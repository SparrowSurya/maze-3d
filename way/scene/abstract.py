"""
This submodule contains the interface objects and types for the submodule.
"""

from __future__ import annotations
import abc
from typing import TYPE_CHECKING

from .constants import Scene

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "GameScene",
)


class GameScene(abc.ABC):
    """Describes the scene lifecycle in the game."""

    @abc.abstractmethod
    def init(self, state: GameState) -> None:
        """Initializes the scene with game state."""

    @abc.abstractmethod
    def draw(self, state: GameState) -> None:
        """Draws the scene."""

    @abc.abstractmethod
    def update(self, dt: float, state: GameState) -> Scene:
        """Updates the scene and returns the next scene that will be next."""

    @abc.abstractmethod
    def clean(self, state: GameState) -> None:
        """Performs scene cleanup."""
