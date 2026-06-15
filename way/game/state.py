"""
This submodule contains the game state related objects.
"""


from dataclasses import dataclass

import pyray as rl

from ..maze import MazeAlgorithm


__all__ = (
    "GameState",
)


@dataclass
class GameState:
    """Manages the shared state and assets of the game."""

    width: int
    height: int
    selected_algo: MazeAlgorithm

    # Graphical Assets
    wall_texture: rl.Texture
    wall_model: rl.Model
    grass_texture: rl.Texture
    ground_model: rl.Model
