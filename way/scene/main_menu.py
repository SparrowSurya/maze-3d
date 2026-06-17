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
    "MainMenuScene",
)


class MainMenuScene(GameScene):
    """Main Menu scene in the game."""

    @override
    def init(self, state: GameState) -> None:
        pass

    @override
    def draw(self, state: GameState) -> None:
        rl.draw_rectangle(0, 0, state.width, state.height, rl.fade(rl.BLACK, 0.8))

        text = state.title.upper()
        width = rl.measure_text(text, 30)
        rl.draw_text(text, (state.width - width) // 2, state.height // 2 + 15, 30, rl.GOLD)

        text = "Press [ENTER] to Start"
        width = rl.measure_text(text, 20)
        rl.draw_text(
            text, (state.width - width) // 2, state.height // 2 + 45, 20, rl.LIGHTGRAY
        )

    @override
    def update(self, dt: float, state: GameState) -> Scene:
        if rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
            return Scene.GAME_PLAY
        return Scene.MAIN_MENU

    @override
    def clean(self, state: GameState) -> None:
        pass
