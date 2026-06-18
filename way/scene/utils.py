"""
This submodule contains the maze utility functions.
"""

from __future__ import annotations
import math

import pyray as rl

from ..player import Player
from ..maze import Maze
from .constants import (
    CELL_SCALE,
    SLICE_THICKNESS,
    SLICE_HEIGHT,
)


def find_front_wall(player: Player, maze: Maze) -> tuple[int, int] | None:
    """Finds the wall the player is looking at with pixel-perfect accuracy."""
    ray_start = player.position
    forward = rl.Vector3(
        math.sin(player.yaw) * math.cos(player.pitch),
        math.sin(player.pitch),
        -math.cos(player.yaw) * math.cos(player.pitch),
    )
    ray = rl.Ray(ray_start, forward)

    max_dist = 5.0  # Max cells to check

    # Grid space start (0.1 offset to skip immediate player collision)
    start_x = (player.position.x + forward.x * 0.1) / CELL_SCALE
    start_z = (player.position.z + forward.z * 0.1) / CELL_SCALE

    map_x, map_z = int(start_x), int(start_z)

    delta_dist_x = abs(1.0 / forward.x) * CELL_SCALE if forward.x != 0 else 1e30
    delta_dist_z = abs(1.0 / forward.z) * CELL_SCALE if forward.z != 0 else 1e30

    step_x = 1 if forward.x >= 0 else -1
    step_z = 1 if forward.z >= 0 else -1

    side_dist_x = (
        (map_x + 1.0 - start_x) * delta_dist_x if step_x == 1 else (start_x - map_x) * delta_dist_x
    )
    side_dist_z = (
        (map_z + 1.0 - start_z) * delta_dist_z if step_z == 1 else (start_z - map_z) * delta_dist_z
    )

    # Perform DDA with 3D validation
    player_cell = (int(player.position.x / CELL_SCALE), int(player.position.z / CELL_SCALE))

    # Helper to check collision with a specific box
    def check_box(px: float, pz: float, sx: float, sz: float, h: float) -> bool:
        box = rl.BoundingBox(
            rl.Vector3(px - sx / 2, 0.0, pz - sz / 2), rl.Vector3(px + sx / 2, h, pz + sz / 2)
        )
        return rl.get_ray_collision_box(ray, box).hit

    dist_traveled = 0.0
    while dist_traveled < (max_dist * CELL_SCALE):
        # If current cell is a wall, check visual geometry
        if 0 <= map_x < maze.width and 0 <= map_z < maze.height:
            if (
                (map_x, map_z) != player_cell
                and maze.grid[map_z][map_x] == 1
                and maze.has_neighbor(map_x, map_z)
            ):
                pillar_x = map_x * CELL_SCALE + CELL_SCALE / 2
                pillar_z = map_z * CELL_SCALE + CELL_SCALE / 2

                # Check Right Connection
                if map_x + 1 < maze.width and maze.grid[map_z][map_x + 1] == 1:
                    if check_box(
                        map_x * CELL_SCALE + CELL_SCALE,
                        pillar_z,
                        CELL_SCALE,
                        SLICE_THICKNESS,
                        SLICE_HEIGHT,
                    ):
                        return (
                            (map_x, map_z)
                            if (0 < map_x < maze.width - 1 and 0 < map_z < maze.height - 1)
                            else None
                        )

                # Check Bottom Connection
                if map_z + 1 < maze.height and maze.grid[map_z + 1][map_x] == 1:
                    if check_box(
                        pillar_x,
                        map_z * CELL_SCALE + CELL_SCALE,
                        SLICE_THICKNESS,
                        CELL_SCALE,
                        SLICE_HEIGHT,
                    ):
                        return (
                            (map_x, map_z)
                            if (0 < map_x < maze.width - 1 and 0 < map_z < maze.height - 1)
                            else None
                        )

                # Check Left Connection (Right connection of map_x - 1)
                if map_x - 1 >= 0 and maze.grid[map_z][map_x - 1] == 1:
                    if check_box(
                        map_x * CELL_SCALE, pillar_z, CELL_SCALE, SLICE_THICKNESS, SLICE_HEIGHT
                    ):
                        return (
                            (map_x, map_z)
                            if (0 < map_x < maze.width - 1 and 0 < map_z < maze.height - 1)
                            else None
                        )

                # Check Top Connection (Bottom connection of map_z - 1)
                if map_z - 1 >= 0 and maze.grid[map_z - 1][map_x] == 1:
                    if check_box(
                        pillar_x, map_z * CELL_SCALE, SLICE_THICKNESS, CELL_SCALE, SLICE_HEIGHT
                    ):
                        return (
                            (map_x, map_z)
                            if (0 < map_x < maze.width - 1 and 0 < map_z < maze.height - 1)
                            else None
                        )

        # DDA Step
        if side_dist_x < side_dist_z:
            dist_traveled = side_dist_x
            side_dist_x += delta_dist_x
            map_x += step_x
        else:
            dist_traveled = side_dist_z
            side_dist_z += delta_dist_z
            map_z += step_z

    return None
