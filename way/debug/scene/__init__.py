"""
This module provides scene debug classes.
"""


from .protocols import SceneDebug
from .main_menu import MainMenuSceneDebug
from .game_play import GamePlaySceneDebug
from .game_end import GameEndSceneDebug


__all__ = (
    "SceneDebug",
    "MainMenuSceneDebug",
    "GamePlaySceneDebug",
    "GameEndSceneDebug",
)
