"""
This submodule contains the game state related objects.
"""


from __future__ import annotations
from dataclasses import dataclass

from ..asset import AssetManager
from ..scene.manager import SceneManager


__all__ = (
    "GameState",
    "GameManager",
)


@dataclass
class GameState:
    """Manages the shared state and assets of the game."""

    width: int
    height: int
    title: str
    fps: int
    manager: GameManager


@dataclass
class GameManager:
    """Contains delegate manager for various objects."""

    asset: AssetManager
    scene: SceneManager
