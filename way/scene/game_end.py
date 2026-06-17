"""
This submodule contains the main menu scene.
"""

from __future__ import annotations
from typing import override, TYPE_CHECKING

import pyray as rl

from .abstract import GameScene
from .constants import Scene

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "GameEndScene",
)


class GameEndScene(GameScene):
    """Describes the game end scene in the game."""

    @override
    def init(self, state: GameState) -> None:
        pass

    @override
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

    @override
    def update(self, dt: float, state: GameState) -> Scene:
        if rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
            return Scene.MAIN_MENU
        return Scene.GAME_END

    @override
    def clean(self, state: GameState) -> None:
        pass
