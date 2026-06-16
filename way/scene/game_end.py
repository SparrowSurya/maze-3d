"""
This submodule contains the main menu scene.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import pyray as rl

from .constants import Scene

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "GameEndScene",
)


class GameEndScene:
    """Describes the game end scene in the game."""

    def init(self, state: GameState) -> None:
        pass

    def draw(self, state: GameState) -> None:
        rl.draw_rectangle(0, 0, state.width, state.height, rl.fade(rl.BLACK, 0.5))
        rl.draw_text(
            "YOU FOUND THE WAY OUT!", state.width // 2 - 180, state.height // 2 - 40, 30, rl.GOLD
        )
        rl.draw_text(
            "Press [ENTER] to Continue",
            state.width // 2 - 140,
            state.height // 2 + 10,
            15,
            rl.WHITE,
        )

    def update(self, dt: float, state: GameState) -> Scene:
        if rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
            return Scene.MAIN_MENU
        return Scene.GAME_END

    def clean(self, state: GameState) -> None:
        pass
