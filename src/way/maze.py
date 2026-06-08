import random
import sys
from collections import deque
from enum import Enum, auto

# Increase recursion depth for maze generation
sys.setrecursionlimit(2000)


class Algorithm(Enum):
    DFS = auto()
    PRIMS = auto()
    KRUSKALS = auto()
    BINARY_TREE = auto()
    SIDEWINDER = auto()


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


def generate_maze(
    width: int, height: int, sparsity: float = 0.00, algorithm: Algorithm = Algorithm.DFS
) -> Maze:
    # Ensure dimensions are odd for the wall-cell representation
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    grid = [[1 for _ in range(width)] for _ in range(height)]

    if algorithm == Algorithm.DFS:
        _generate_dfs(grid, width, height)
    elif algorithm == Algorithm.PRIMS:
        _generate_prims(grid, width, height)
    elif algorithm == Algorithm.KRUSKALS:
        _generate_kruskals(grid, width, height)
    elif algorithm == Algorithm.BINARY_TREE:
        _generate_binary_tree(grid, width, height)
    elif algorithm == Algorithm.SIDEWINDER:
        _generate_sidewinder(grid, width, height)

    # Post-process: randomly remove some inner walls to create loops and wider areas
    for z in range(1, height - 1):
        for x in range(1, width - 1):
            if grid[z][x] == 1:
                # Check horizontal neighbors
                horiz_empty = grid[z][x - 1] == 0 and grid[z][x + 1] == 0
                # Check vertical neighbors
                vert_empty = grid[z - 1][x] == 0 and grid[z + 1][x] == 0

                # If it connects two corridors, maybe remove it
                if (horiz_empty or vert_empty) and random.random() < sparsity:
                    grid[z][x] = 0

    return Maze(grid)


def _generate_dfs(grid: list[list[int]], width: int, height: int) -> None:
    def walk(x: int, z: int) -> None:
        grid[z][x] = 0
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        for dx, dz in directions:
            nx, nz = x + dx, z + dz
            if 0 < nx < width - 1 and 0 < nz < height - 1 and grid[nz][nx] == 1:
                grid[z + dz // 2][x + dx // 2] = 0
                walk(nx, nz)

    walk(1, 1)


def _generate_prims(grid: list[list[int]], width: int, height: int) -> None:
    # 1. Start from a random cell
    start_x, start_z = 1, 1
    grid[start_z][start_x] = 0

    # 2. Add frontier walls
    frontier = []
    for dx, dz in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
        nx, nz = start_x + dx, start_z + dz
        if 0 < nx < width - 1 and 0 < nz < height - 1:
            frontier.append((nx, nz, start_x, start_z))

    while frontier:
        # 3. Pick random frontier wall
        idx = random.randrange(len(frontier))
        nx, nz, px, pz = frontier.pop(idx)

        if grid[nz][nx] == 1:
            # 4. Carve through
            grid[nz][nx] = 0
            grid[nz + (pz - nz) // 2][nx + (px - nx) // 2] = 0

            # 5. Add new frontier
            for dx, dz in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                nnx, nnz = nx + dx, nz + dz
                if 0 < nnx < width - 1 and 0 < nnz < height - 1 and grid[nnz][nnx] == 1:
                    frontier.append((nnx, nnz, nx, nz))


def _generate_kruskals(grid: list[list[int]], width: int, height: int) -> None:
    # Union-Find for cells
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

    cells = []
    for z in range(1, height, 2):
        for x in range(1, width, 2):
            grid[z][x] = 0
            parent[(x, z)] = (x, z)
            cells.append((x, z))

    walls = []
    for z in range(1, height, 2):
        for x in range(1, width, 2):
            if x + 2 < width:
                walls.append((x, z, x + 2, z))
            if z + 2 < height:
                walls.append((x, z, x, z + 2))

    random.shuffle(walls)

    for x1, z1, x2, z2 in walls:
        if union((x1, z1), (x2, z2)):
            grid[z1 + (z2 - z1) // 2][x1 + (x2 - x1) // 2] = 0


def _generate_binary_tree(grid: list[list[int]], width: int, height: int) -> None:
    for z in range(1, height, 2):
        for x in range(1, width, 2):
            grid[z][x] = 0
            neighbors = []
            if x + 2 < width:
                neighbors.append((x + 1, z))
            if z + 2 < height:
                neighbors.append((x, z + 1))

            if neighbors:
                nx, nz = random.choice(neighbors)
                grid[nz][nx] = 0


def _generate_sidewinder(grid: list[list[int]], width: int, height: int) -> None:
    for z in range(1, height, 2):
        run = []
        for x in range(1, width, 2):
            grid[z][x] = 0
            run.append((x, z))

            at_east_boundary = x + 2 >= width
            at_north_boundary = z + 2 >= height

            # Decide to close run if at boundary or randomly
            should_close = at_east_boundary or (
                not at_north_boundary and random.choice([True, False])
            )

            if should_close:
                # Pick a random cell from the run and carve North
                if not at_north_boundary:
                    cx, cz = random.choice(run)
                    grid[cz + 1][cx] = 0
                run = []
            else:
                # Carve East
                grid[z][x + 1] = 0


def get_default_maze() -> Maze:
    # Randomly pick an algorithm
    algo = random.choice(list(Algorithm))
    return generate_maze(25, 25, algorithm=algo)
