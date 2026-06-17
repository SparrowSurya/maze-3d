"""
This submodule contains the scene debug class for main menu.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .abstract import SceneDebug

if TYPE_CHECKING:
    from ...game.state import GameState


__all__ = (
    "MainMenuSceneDebug",
)


class MainMenuSceneDebug(SceneDebug):
    """Main menun scene debug view."""

    def init(self, state: GameState) -> None:
        pass

    def draw(self, state: GameState) -> None:
        pass

    def update(self, state: GameState, dt: float) -> None:
        pass

    def clean(self, state: GameState) -> None:
        pass
