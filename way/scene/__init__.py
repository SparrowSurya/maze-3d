"""
This submodule contains scene related classes and functions.
"""


from .constants import Scene
from .protocols import GameScene
from .main_menu import MainMenuScene
from .maze_play import MazePlayScene
from .end import EndScene


__all__ = (
    "Scene",
    "GameScene",
    "MainMenuScene",
    "MazePlayScene",
    "EndScene",
)
