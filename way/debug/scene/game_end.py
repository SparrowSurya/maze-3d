"""
This submodule contains the scene debug class for game end.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from ...scene.constants import Scene

if TYPE_CHECKING:
    from ...game.state import GameState


__all__ = (
    "GameEndSceneDebug",
)


class GameEndSceneDebug:
    """Game end scene debug view."""

    def init(self, state: GameState) -> None:
        pass

    def draw(self, state: GameState) -> None:
        pass

    def update(self, dt: float, state: GameState) -> Scene | None:
        pass

    def clean(self, state: GameState) -> None:
        pass
