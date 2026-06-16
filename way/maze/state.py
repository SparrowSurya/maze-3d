"""
This submodule contains the maze state related classes and functions.
"""


from __future__ import annotations
import random
from collections import deque

from .generators import MazeGenerator, MazeAlgorithm, get_generator


__all__ = (
    "Maze",
    "generate_maze",
    "random_maze",
)


class Maze:
    """Describes the maze data."""

    grid: list[list[int]]
    """Maze 2d grid."""

    def __init__(self, grid: list[list[int]]) -> None:
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

    @classmethod
    def from_strategy(cls, strategy: MazeGenerator, rows: int, cols: int) -> Maze:
        """Create a maze from give strategy."""
        grid = strategy.generate(rows, cols)
        return cls(grid)

    def is_wall(self, x: int, z: int) -> bool:
        """Checks if the given coordinates (x, z) correspond to a wall cell in the maze."""
        if 0 <= z < self.height and 0 <= x < self.width:
            return self.grid[z][x] == 1
        return True

    def get_random_empty_cell(self) -> tuple[int, int]:
        """Returns the (x, z) coordinates of a randomly selected empty (path) cell."""
        empty_cells = [
            (x, z) for z in range(self.height) for x in range(self.width) if self.grid[z][x] == 0
        ]
        if not empty_cells:
            return (1, 1)
        return random.choice(empty_cells)

    def find_farthest_points(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Finds two empty cells that are farthest apart using BFS."""

        def bfs(start_x: int, start_z: int) -> tuple[tuple[int, int], int]:
            distances: dict[tuple[int, int], int] = {(start_x, start_z): 0}
            queue: deque[tuple[int, int]] = deque([(start_x, start_z)])
            farthest_node = (start_x, start_z)
            max_dist = 0

            while queue:
                curr_x, curr_z = queue.popleft()
                dist = distances[(curr_x, curr_z)]

                if dist > max_dist:
                    max_dist = dist
                    farthest_node = (curr_x, curr_z)

                for dx, dz in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, nz = curr_x + dx, curr_z + dz
                    if not self.is_wall(nx, nz) and (nx, nz) not in distances:
                        distances[(nx, nz)] = dist + 1
                        queue.append((nx, nz))

            return farthest_node, max_dist

        # 1. Start from any empty cell
        start_node = self.get_random_empty_cell()

        # 2. Find farthest node from start
        p1, _ = bfs(start_node[0], start_node[1])

        # 3. Find farthest node from p1
        p2, _ = bfs(p1[0], p1[1])

        return p1, p2


def generate_maze(width: int, height: int, algorithm: MazeAlgorithm = MazeAlgorithm.DFS) -> Maze:
    """Generates a maze using the specified algorithm."""
    strategy = get_generator(algorithm)
    return Maze.from_strategy(strategy, height, width)


def random_maze(width: int, height: int) -> Maze:
    """Randomly pick an algorithm."""
    algo = random.choice(list(MazeAlgorithm))
    return generate_maze(width, height, algorithm=algo)
