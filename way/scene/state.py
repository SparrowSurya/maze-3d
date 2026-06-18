"""
This submodule contains the state data classes for scenes.
"""

from __future__ import annotations
from dataclasses import dataclass

import pyray as rl

from ..maze import Maze
from ..player import Player


__all__ = ("GamePlayState",)


@dataclass(slots=True)
class GamePlayState:
    """Contains the intformation about player and maze and other objects in maze."""

    maze: Maze
    player: Player
    dest: rl.Vector3
    axe: rl.Vector3 | None
    show_minimap: bool
