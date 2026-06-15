"""
This submodule contains the main menu scene.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import pyray as rl

from .constants import Scene
from ..maze import MazeAlgorithm

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "MainMenuScene",
)


class MainMenuScene:
    """Main Menu scene in the game."""

    def init(self, state: GameState) -> None:
        """Initializes the scene."""
        pass

    def draw(self, state: GameState) -> None:
        rl.draw_rectangle(0, 0, state.width, state.height, rl.fade(rl.BLACK, 0.8))
        rl.draw_text(
            "THE WAY OUT - CHOOSE ALGORITHM", state.width // 2 - 250, 100, 30, rl.GOLD
        )

        algos = [
            "1. Recursive Backtracker (DFS)",
            "2. Randomized Prim's",
            "3. Randomized Kruskal's",
            "4. Binary Tree",
            "5. Sidewinder",
        ]

        for i, text in enumerate(algos):
            rl.draw_text(text, state.width // 2 - 150, 200 + i * 40, 20, rl.WHITE)

        rl.draw_text(
            "Press [NUMBER] to Start", state.width // 2 - 120, 450, 20, rl.LIGHTGRAY
        )
        rl.draw_text(
            "SHIFT + R: Return to Menu from game",
            state.width // 2 - 160,
            500,
            15,
            rl.GRAY,
        )

    def update(self, dt: float, state: GameState) -> Scene:
        if rl.is_key_pressed(rl.KeyboardKey.KEY_ONE):  # type: ignore
            state.algo = MazeAlgorithm.DFS
            return Scene.MAZE_PLAY
        if rl.is_key_pressed(rl.KeyboardKey.KEY_TWO):  # type: ignore
            state.algo = MazeAlgorithm.PRIMS
            return Scene.MAZE_PLAY
        if rl.is_key_pressed(rl.KeyboardKey.KEY_THREE):  # type: ignore
            state.algo = MazeAlgorithm.KRUSKALS
            return Scene.MAZE_PLAY
        if rl.is_key_pressed(rl.KeyboardKey.KEY_FOUR):  # type: ignore
            state.algo = MazeAlgorithm.BINARY_TREE
            return Scene.MAZE_PLAY
        if rl.is_key_pressed(rl.KeyboardKey.KEY_FIVE):  # type: ignore
            state.algo = MazeAlgorithm.SIDEWINDER
            return Scene.MAZE_PLAY

        return Scene.MAIN_MENU
