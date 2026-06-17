"""
This submodule contains the interface objects and types for the submodule.
"""

from __future__ import annotations
import abc
from collections.abc import Sequence
from typing import TYPE_CHECKING

from .constants import Scene
from ..components.abstract import UiComponent

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "GameScene",
)


class GameScene(abc.ABC):
    """Describes the scene lifecycle in the game."""

    components: Sequence[UiComponent]
    """Collection of ui components that are drawn in order they appear."""

    def __init__(self, components: Sequence[UiComponent] | None = None) -> None:
        self.components = [] if components is None else components

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
