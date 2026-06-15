"""
This submodule contains the constants used in this submodule.
"""


from enum import StrEnum, auto


__all__ = (
    "Scene",
)


class Scene(StrEnum):
    """Enumeration for the scenes in the game."""

    MAIN_MENU = auto()
    MAZE_PLAY = auto()
    END_SCREEN = auto()
