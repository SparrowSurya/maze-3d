"""
This modules provides the maze related classes.
"""


from .generators import MazeGenerator, MazeAlgorithm
from .state import Maze, generate_maze


__all__ = (
    "MazeAlgorithm",
    "MazeGenerator",
    "Maze",
    "generate_maze",
)
