"""
This submodule contains the game state related objects.
"""


from __future__ import annotations
from dataclasses import dataclass

import pyray as rl

from ..asset import AssetManager
from ..debug.scene.protocols import SceneDebug
from ..scene.manager import SceneManager
from ..scene.abstract import Scene


__all__ = (
    "GameState",
    "GameManager",
    "GameDebug",
)


@dataclass(slots=True)
class GameState:
    """Manages the shared state and assets of the game."""

    width: int
    height: int
    title: str
    fps: int
    manager: GameManager
    debug: GameDebug | None = None


@dataclass(slots=True)
class GameManager:
    """Contains delegate manager for various objects."""

    asset: AssetManager
    scene: SceneManager

@dataclass(slots=True)
class GameDebug:
    """Contains the debug objects."""

    scene: dict[Scene, SceneDebug]
    view_scene: bool = False
    panel_rect: rl.Rectangle = rl.Rectangle(10.0, 10.0, 200.0, 150.0)
    is_dragging: bool = False
    is_resizing: bool = False
