"""
This submodule contains the interface objects and types for the submodule.
"""

from __future__ import annotations
from collections.abc import Sequence
from typing import TYPE_CHECKING, override

from ..components.abstract import UiComponent

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = ("GameScene",)


class GameScene(UiComponent):
    """Describes the scene lifecycle component in the game."""

    components: Sequence[UiComponent]
    """Collection of ui components that are drawn in order they appear."""

    def __init__(self, components: Sequence[UiComponent] | None = None) -> None:
        self.components = [] if components is None else components

    @override
    def init(self, state: GameState) -> None:
        """Initializes the scene with game state."""
        for component in self.components:
            component.init(state)

    @override
    def draw(self, state: GameState) -> None:
        """Draws the scene."""
        for component in self.components:
            component.draw(state)

    @override
    def update(self, state: GameState, dt: float) -> None:
        """Updates the scene and returns the next scene that will be next."""
        for component in self.components:
            component.update(state, dt)

    @override
    def clean(self, state: GameState) -> None:
        """Performs scene cleanup."""
        for component in self.components:
            component.clean(state)
