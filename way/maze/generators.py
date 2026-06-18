"""
This submodule contains the maze generator classes.
"""

import sys
import abc
import contextlib
import random
from enum import StrEnum, auto
from collections.abc import Generator
from typing import override, Any


class MazeAlgorithm(StrEnum):
    """Describes the maze generation algorithm."""

    DFS = auto()
    PRIMS = auto()
    KRUSKALS = auto()
    BINARY_TREE = auto()
    SIDEWINDER = auto()


class MazeGenerator(abc.ABC):
    """Describes the maze generation strategy."""

    @abc.abstractmethod
    def generate(self, rows: int, cols: int) -> list[list[int]]:
        """
        Generates the maze grid using the specific algorithm.

        Returns a 2D grid where 1 represents a wall and 0 represents a path.
        """

    @contextlib.contextmanager
    def _recursion_limit(self, limit: int) -> Generator[Any, Any, Any]:
        """Temporarily increases the recursion limit for deep maze generation."""
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, limit))
        try:
            yield
        finally:
            sys.setrecursionlimit(old_limit)


class DFSGenerator(MazeGenerator):
    """Recursive Backtracker (DFS) maze generation."""

    @override
    def generate(self, rows: int, cols: int) -> list[list[int]]:
        with self._recursion_limit(rows * cols * 2):
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


class PrimsGenerator(MazeGenerator):
    """Prim's algorithm maze generation."""

    @override
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


class KruskalsGenerator(MazeGenerator):
    """Kruskal's algorithm maze generation."""

    @override
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


class BinaryTreeGenerator(MazeGenerator):
    """Binary Tree algorithm maze generation."""

    @override
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


class SidewinderGenerator(MazeGenerator):
    """Sidewinder algorithm maze generation."""

    @override
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


def get_generator(algo: MazeAlgorithm) -> MazeGenerator:
    """Returns a generator instance for the given algorithm."""
    generators = {
        MazeAlgorithm.DFS: DFSGenerator,
        MazeAlgorithm.PRIMS: PrimsGenerator,
        MazeAlgorithm.KRUSKALS: KruskalsGenerator,
        MazeAlgorithm.BINARY_TREE: BinaryTreeGenerator,
        MazeAlgorithm.SIDEWINDER: SidewinderGenerator,
    }
    return generators[algo]()
