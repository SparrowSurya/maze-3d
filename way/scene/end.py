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
    "EndScene",
)


class EndScene:
    """Describes the game end scene in the game."""

    def init(self, state: GameState) -> None:
        """Initializes the scene."""
        pass

    def draw(self, state: GameState) -> None:
        rl.draw_rectangle(0, 0, state.width, state.height, rl.fade(rl.BLACK, 0.5))
        rl.draw_text(
            "YOU FOUND THE WAY OUT!", state.width // 2 - 180, state.height // 2 - 40, 30, rl.GOLD
        )
        rl.draw_text(
            "Press [ENTER] or [R] to Main Menu",
            state.width // 2 - 140,
            state.height // 2 + 10,
            15,
            rl.WHITE,
        )

    def update(self, dt: float, state: GameState) -> Scene:
        if rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER) or rl.is_key_pressed(rl.KeyboardKey.KEY_R):  # type: ignore
            return Scene.MAIN_MENU
        return Scene.END_SCREEN
