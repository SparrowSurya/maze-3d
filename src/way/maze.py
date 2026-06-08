import random
import sys
from collections import deque

# Increase recursion depth for maze generation
sys.setrecursionlimit(2000)


class Maze:
    def __init__(self, grid: list[list[int]]) -> None:
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

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


def generate_maze(width: int, height: int) -> Maze:
    # Ensure dimensions are odd for the wall-cell representation
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    grid = [[1 for _ in range(width)] for _ in range(height)]

    def walk(x: int, z: int) -> None:
        grid[z][x] = 0

        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)

        for dx, dz in directions:
            nx, nz = x + dx, z + dz
            if 0 < nx < width - 1 and 0 < nz < height - 1 and grid[nz][nx] == 1:
                grid[z + dz // 2][x + dx // 2] = 0
                walk(nx, nz)

    # Start generation from (1, 1)
    walk(1, 1)

    return Maze(grid)


def get_default_maze() -> Maze:
    # Generate a fresh 21x21 maze by default
    return generate_maze(21, 21)
