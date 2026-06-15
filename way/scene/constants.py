"""
This submodule contains the constants used in this submodule.
"""


from enum import StrEnum, auto


__all__ = (
    "Scene",
    "PILLAR_SIZE",
    "PILLAR_HEIGHT",
    "SLICE_THICKNESS",
    "SLICE_HEIGHT",
)


class Scene(StrEnum):
    """Enumeration for the scenes in the game."""

    MAIN_MENU = auto()
    MAZE_PLAY = auto()
    END_SCREEN = auto()


# Wall Geometry Constants
PILLAR_SIZE = 0.32
PILLAR_HEIGHT = 1.2
SLICE_THICKNESS = 0.2
SLICE_HEIGHT = 1.0
