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
    "MINIMAP_GRID_SIZE",
)


class Scene(StrEnum):
    """Enumeration for the scenes in the game."""

    MAIN_MENU = auto()
    GAME_PLAY = auto()
    GAME_END = auto()


# Wall Geometry Constants
CELL_SCALE = 2.0
PILLAR_SIZE = 0.4
PILLAR_HEIGHT = 1.1
SLICE_THICKNESS = 0.2
SLICE_HEIGHT = 1.0

# Minimap Constants
MINIMAP_GRID_SIZE = 15
