"""
This module handles everything related to maze representation and generation.
"""

from __future__ import annotations
import random
from collections import deque
from enum import StrEnum, auto
from typing import Protocol


class MazeAlgorithm(StrEnum):
    """Describes the maze generation algorithm."""

    DFS = auto()
    PRIMS = auto()
    KRUSKALS = auto()
    BINARY_TREE = auto()
    SIDEWINDER = auto()


class MazeGenerator(Protocol):
    """Describes the maze generation strategy."""

    def generate(self, rows: int, cols: int) -> list[list[int]]:
        """Generates the maze grid data."""
        ...


class DFSGenerator:
    """Recursive Backtracker (DFS) maze generation."""

    def generate(self, rows: int, cols: int) -> list[list[int]]:
        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1

        grid = [[1 for _ in range(cols)] for _ in range(rows)]

        def walk(x: int, z: int) -> None:
            grid[z][x] = 0
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(directions)
            for dx, dz in directions:
                nx, nz = x + dx, z + dz
                if 0 < nx < cols - 1 and 0 < nz < rows - 1 and grid[nz][nx] == 1:
                    grid[z + dz // 2][x + dx // 2] = 0
                    walk(nx, nz)

        walk(1, 1)
        return grid


class PrimsGenerator:
    """Prim's algorithm maze generation."""

    def generate(self, rows: int, cols: int) -> list[list[int]]:
        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1

        grid = [[1 for _ in range(cols)] for _ in range(rows)]
        start_x, start_z = 1, 1
        grid[start_z][start_x] = 0

        frontier = []
        for dx, dz in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
            nx, nz = start_x + dx, start_z + dz
            if 0 < nx < cols - 1 and 0 < nz < rows - 1:
                frontier.append((nx, nz, start_x, start_z))

        while frontier:
            idx = random.randrange(len(frontier))
            nx, nz, px, pz = frontier.pop(idx)

            if grid[nz][nx] == 1:
                grid[nz][nx] = 0
                grid[nz + (pz - nz) // 2][nx + (px - nx) // 2] = 0

                for dx, dz in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                    nnx, nnz = nx + dx, nz + dz
                    if 0 < nnx < cols - 1 and 0 < nnz < rows - 1 and grid[nnz][nnx] == 1:
                        frontier.append((nnx, nnz, nx, nz))
        return grid


class KruskalsGenerator:
    """Kruskal's algorithm maze generation."""

    def generate(self, rows: int, cols: int) -> list[list[int]]:
        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1

        grid = [[1 for _ in range(cols)] for _ in range(rows)]
        parent: dict[tuple[int, int], tuple[int, int]] = {}

        def find(i: tuple[int, int]) -> tuple[int, int]:
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i: tuple[int, int], j: tuple[int, int]) -> bool:
            root_i, root_j = find(i), find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False

        for z in range(1, rows, 2):
            for x in range(1, cols, 2):
                grid[z][x] = 0
                parent[(x, z)] = (x, z)

        walls = []
        for z in range(1, rows, 2):
            for x in range(1, cols, 2):
                if x + 2 < cols:
                    walls.append((x, z, x + 2, z))
                if z + 2 < rows:
                    walls.append((x, z, x, z + 2))

        random.shuffle(walls)

        for x1, z1, x2, z2 in walls:
            if union((x1, z1), (x2, z2)):
                grid[z1 + (z2 - z1) // 2][x1 + (x2 - x1) // 2] = 0
        return grid


class BinaryTreeGenerator:
    """Binary Tree algorithm maze generation."""

    def generate(self, rows: int, cols: int) -> list[list[int]]:
        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1

        grid = [[1 for _ in range(cols)] for _ in range(rows)]
        for z in range(1, rows, 2):
            for x in range(1, cols, 2):
                grid[z][x] = 0
                neighbors = []
                if x + 2 < cols:
                    neighbors.append((x + 1, z))
                if z + 2 < rows:
                    neighbors.append((x, z + 1))

                if neighbors:
                    nx, nz = random.choice(neighbors)
                    grid[nz][nx] = 0
        return grid


class SidewinderGenerator:
    """Sidewinder algorithm maze generation."""

    def generate(self, rows: int, cols: int) -> list[list[int]]:
        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1

        grid = [[1 for _ in range(cols)] for _ in range(rows)]
        for z in range(1, rows, 2):
            run = []
            for x in range(1, cols, 2):
                grid[z][x] = 0
                run.append((x, z))

                at_east_boundary = x + 2 >= cols
                at_north_boundary = z + 2 >= rows

                should_close = at_east_boundary or (
                    not at_north_boundary and random.choice([True, False])
                )

                if should_close:
                    if not at_north_boundary:
                        cx, cz = random.choice(run)
                        grid[cz + 1][cx] = 0
                    run = []
                else:
                    grid[z][x + 1] = 0
        return grid


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
        if 0 <= z < self.height and 0 <= x < self.width:
            return self.grid[z][x] == 1
        return True

    def get_random_empty_cell(self) -> tuple[int, int]:
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


def get_generator(algorithm: MazeAlgorithm) -> MazeGenerator:
    """Returns a generator instance for the given algorithm."""
    generators = {
        MazeAlgorithm.DFS: DFSGenerator,
        MazeAlgorithm.PRIMS: PrimsGenerator,
        MazeAlgorithm.KRUSKALS: KruskalsGenerator,
        MazeAlgorithm.BINARY_TREE: BinaryTreeGenerator,
        MazeAlgorithm.SIDEWINDER: SidewinderGenerator,
    }
    return generators[algorithm]()


def generate_maze(
    width: int, height: int, algorithm: MazeAlgorithm = MazeAlgorithm.DFS
) -> Maze:
    """Generates a maze using the specified algorithm."""
    strategy = get_generator(algorithm)
    return Maze.from_strategy(strategy, height, width)


def get_default_maze() -> Maze:
    """Randomly pick an algorithm."""
    algo = random.choice(list(MazeAlgorithm))
    return generate_maze(25, 25, algorithm=algo)
