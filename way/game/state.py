"""
This submodule contains the game state related objects.
"""


from __future__ import annotations
from dataclasses import dataclass

from ..asset import AssetManager
from ..debug.scene.protocols import SceneDebug
from ..scene.manager import SceneManager
from ..scene.protocols import Scene


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
