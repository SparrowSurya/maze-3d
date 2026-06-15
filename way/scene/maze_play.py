"""
This submodule contains the maze play scene.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import math

import pyray as rl

from .constants import (
    Scene,
    PILLAR_SIZE,
    PILLAR_HEIGHT,
    SLICE_THICKNESS,
    SLICE_HEIGHT,
    CELL_SCALE,
)
from ..maze import Maze, generate_maze
from ..player import Player, ViewMode
from ..asset import AssetType

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "MazePlayScene",
)


class MazePlayScene:
    """Describes the maze scene in the game."""

    def __init__(self) -> None:
        self.maze: Maze | None = None
        self.player = Player(rl.Vector3(0, 0, 0), 0.0)
        self.destination: rl.Vector3 = rl.Vector3(0, 0, 0)
        self.axe_pos: rl.Vector3 | None = None
        self.show_minimap: bool = False

    def init(self, state: GameState) -> None:
        """Initializes the maze and player position."""
        from .constants import CELL_SCALE

        self.maze = generate_maze(25, 25, algorithm=state.algo)
        # Find two farthest points
        p1, p2 = self.maze.find_farthest_points()
        spawn_x, spawn_z = p1
        dest_x, dest_z = p2

        # Determine initial yaw (face toward an empty neighbor)
        spawn_yaw = 0.0
        if not self.maze.is_wall(spawn_x, spawn_z - 1):
            spawn_yaw = 0.0  # North
        elif not self.maze.is_wall(spawn_x + 1, spawn_z):
            spawn_yaw = math.pi / 2  # East
        elif not self.maze.is_wall(spawn_x, spawn_z + 1):
            spawn_yaw = math.pi  # South
        elif not self.maze.is_wall(spawn_x - 1, spawn_z):
            spawn_yaw = 3 * math.pi / 2  # West

        self.player = Player(
            rl.Vector3(
                float(spawn_x) * CELL_SCALE + CELL_SCALE / 2.0,
                0.5,
                float(spawn_z) * CELL_SCALE + CELL_SCALE / 2.0,
            ),
            spawn_yaw,
        )

        self.destination = rl.Vector3(
            float(dest_x) * CELL_SCALE + CELL_SCALE / 2.0,
            0.5,
            float(dest_z) * CELL_SCALE + CELL_SCALE / 2.0,
        )

        # Spawn Axe (collectible)
        self.axe_pos = None

        # Find a suitable spot for the axe (not too close to spawn or destination)
        min_dist = (max(self.maze.width, self.maze.height) * CELL_SCALE) / 3.0
        max_attempts = 100
        for _ in range(max_attempts):
            ax, az = self.maze.get_random_empty_cell()
            potential_axe_pos = rl.Vector3(
                float(ax) * CELL_SCALE + CELL_SCALE / 2.0,
                0.5,
                float(az) * CELL_SCALE + CELL_SCALE / 2.0,
            )
            d_spawn = rl.vector3_distance(potential_axe_pos, self.player.position)
            d_dest = rl.vector3_distance(potential_axe_pos, self.destination)
            if d_spawn > min_dist and d_dest > min_dist:
                self.axe_pos = potential_axe_pos
                break

    def get_targeted_wall(self) -> tuple[int, int] | None:
        """Finds the wall the player is looking at using raycasting."""
        if self.maze is None:
            return None

        from .constants import CELL_SCALE

        # Calculate targeting ray based on player's yaw and pitch (independent of camera view)
        ray_start = self.player.position
        forward = rl.Vector3(
            math.sin(self.player.yaw),
            math.sin(self.player.pitch),
            -math.cos(self.player.yaw),
        )
        ray = rl.Ray(ray_start, forward)

        closest_dist = 5.0 * CELL_SCALE  # Scale interaction range
        hit_cell = None

        for z in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.grid[z][x] == 1:
                    wall_box = rl.BoundingBox(
                        rl.Vector3(float(x) * CELL_SCALE, 0.0, float(z) * CELL_SCALE),
                        rl.Vector3(
                            float(x) * CELL_SCALE + CELL_SCALE,
                            1.2,
                            float(z) * CELL_SCALE + CELL_SCALE,
                        ),
                    )
                    hit_info = rl.get_ray_collision_box(ray, wall_box)
                    if hit_info.hit and hit_info.distance < closest_dist:
                        closest_dist = hit_info.distance
                        # Rule #1 & #2: Only highlight non-boundary walls as targets
                        if 0 < x < self.maze.width - 1 and 0 < z < self.maze.height - 1:
                            hit_cell = (x, z)
                        else:
                            # Boundary wall blocks the ray but isn't a valid destructible target
                            hit_cell = None

        return hit_cell

    def draw(self, state: GameState) -> None:
        if self.maze is None:
            return

        rl.begin_mode_3d(self.player.get_camera())

        ground_asset = state.manager.asset.get_asset(AssetType.GRASS)
        wall_asset = state.manager.asset.get_asset(AssetType.WALL)

        # Ground
        if ground_asset:
            # Draw a grid of unit-sized planes to achieve tiling effect
            # Each logical cell covers CELL_SCALE x CELL_SCALE area.
            # We draw planes of 1.0x1.0 units.
            for gz in range(int(self.maze.height * CELL_SCALE)):
                for gx in range(int(self.maze.width * CELL_SCALE)):
                    rl.draw_model(
                        ground_asset.model,
                        rl.Vector3(float(gx) + 0.5, 0.0, float(gz) + 0.5),
                        1.0,
                        rl.WHITE,
                    )

        # Walls
        if wall_asset:
            pillar_scale = rl.Vector3(PILLAR_SIZE, PILLAR_HEIGHT, PILLAR_SIZE)
            h_slice_scale = rl.Vector3(CELL_SCALE, SLICE_HEIGHT, SLICE_THICKNESS)
            v_slice_scale = rl.Vector3(SLICE_THICKNESS, SLICE_HEIGHT, CELL_SCALE)

            for z in range(self.maze.height):
                for x in range(self.maze.width):
                    if self.maze.is_wall(x, z):
                        # Draw Central Pillar
                        pillar_pos = rl.Vector3(
                            float(x) * CELL_SCALE + CELL_SCALE / 2.0,
                            PILLAR_HEIGHT / 2.0,
                            float(z) * CELL_SCALE + CELL_SCALE / 2.0,
                        )
                        rl.draw_model_ex(
                            wall_asset.model,
                            pillar_pos,
                            rl.Vector3(0, 1, 0),
                            0.0,
                            pillar_scale,
                            rl.WHITE,
                        )

                        # Draw Right Connection
                        if x + 1 < self.maze.width and self.maze.is_wall(x + 1, z):
                            h_slice_pos = rl.Vector3(
                                float(x) * CELL_SCALE + CELL_SCALE,
                                SLICE_HEIGHT / 2.0,
                                float(z) * CELL_SCALE + CELL_SCALE / 2.0,
                            )
                            rl.draw_model_ex(
                                wall_asset.model,
                                h_slice_pos,
                                rl.Vector3(0, 1, 0),
                                0.0,
                                h_slice_scale,
                                rl.WHITE,
                            )

                        # Draw Bottom Connection
                        if z + 1 < self.maze.height and self.maze.is_wall(x, z + 1):
                            v_slice_pos = rl.Vector3(
                                float(x) * CELL_SCALE + CELL_SCALE / 2.0,
                                SLICE_HEIGHT / 2.0,
                                float(z) * CELL_SCALE + CELL_SCALE,
                            )
                            rl.draw_model_ex(
                                wall_asset.model,
                                v_slice_pos,
                                rl.Vector3(0, 1, 0),
                                0.0,
                                v_slice_scale,
                                rl.WHITE,
                            )

        # Destination (Gold Pillar)
        rl.draw_cube(self.destination, 0.5, 2.0, 0.5, rl.GOLD)
        rl.draw_cube_wires(self.destination, 0.5, 2.0, 0.5, rl.ORANGE)

        # Draw axe collectible
        if self.axe_pos:
            bobbing = math.sin(rl.get_time() * 4.0) * 0.1
            axe_draw_pos = rl.Vector3(self.axe_pos.x, self.axe_pos.y + bobbing, self.axe_pos.z)
            rl.draw_cube(axe_draw_pos, 0.2, 0.2, 0.2, rl.BLUE)
            rl.draw_cube_wires(axe_draw_pos, 0.2, 0.2, 0.2, rl.DARKBLUE)

        # Player Model (Top Down View)
        if self.player.view_mode == ViewMode.TOP_DOWN:
            player_base_pos = rl.Vector3(self.player.position.x, 0.0, self.player.position.z)
            rl.draw_cylinder(
                player_base_pos,
                self.player.radius,
                self.player.radius,
                self.player.height,
                16,
                rl.GREEN,
            )
            rl.draw_cylinder_wires(
                player_base_pos,
                self.player.radius,
                self.player.radius,
                self.player.height,
                16,
                rl.DARKGREEN,
            )

        # Targeting Highlight (Rule #3: available in both views)
        if self.player.axe_count > 0 and rl.is_key_down(rl.KeyboardKey.KEY_X):
            target = self.get_targeted_wall()
            if target:
                tx, tz = target
                highlight_pos = rl.Vector3(
                    float(tx) * CELL_SCALE + CELL_SCALE / 2.0,
                    0.6,
                    float(tz) * CELL_SCALE + CELL_SCALE / 2.0,
                )
                # Rule #1: Only highlight the wall that can be destructed
                rl.draw_cube(highlight_pos, CELL_SCALE, 1.2, CELL_SCALE, rl.fade(rl.RED, 0.5))
                rl.draw_cube_wires(highlight_pos, CELL_SCALE, 1.2, CELL_SCALE, rl.RED)

        rl.end_mode_3d()

        # HUD
        rl.draw_text(f"Algorithm: {state.algo.name}", 10, 10, 20, rl.BLACK)
        rl.draw_text("Find the gold pillar!", 10, 40, 15, rl.DARKGRAY)
        rl.draw_text("Press [M] Minimap | SHIFT+V View | SHIFT+R Menu", 10, 60, 12, rl.GRAY)

        if self.player.axe_count > 0:
            rl.draw_text(f"Axe: {self.player.axe_count}", 10, 80, 15, rl.BLUE)

        # Crosshair
        if rl.is_key_down(rl.KeyboardKey.KEY_X):
            target_wall = self.get_targeted_wall()
            # Rule #3: Only turn red if target is valid AND player has axe
            crosshair_color = rl.RED if (target_wall and self.player.axe_count > 0) else rl.GRAY
            rl.draw_circle(state.width // 2, state.height // 2, 4, crosshair_color)
        else:
            rl.draw_circle(state.width // 2, state.height // 2, 2, rl.RED)

        self.draw_compass(state)
        if self.show_minimap:
            self.draw_minimap(state)

    def draw_compass(self, state: GameState) -> None:
        compass_x = state.width - 60
        compass_y = 60
        rl.draw_circle(compass_x, compass_y, 40, rl.LIGHTGRAY)
        rl.draw_circle_lines(compass_x, compass_y, 40, rl.DARKGRAY)

        needle_len = 25
        needle_end_x = compass_x + int(math.sin(self.player.yaw) * needle_len)
        needle_end_y = compass_y - int(math.cos(self.player.yaw) * needle_len)
        rl.draw_line_ex(
            rl.Vector2(float(compass_x), float(compass_y)),
            rl.Vector2(float(needle_end_x), float(needle_end_y)),
            3,
            rl.RED,
        )

        rl.draw_text("N", compass_x - 3, compass_y - 32, 10, rl.BLACK)
        rl.draw_text("S", compass_x - 3, compass_y + 22, 10, rl.BLACK)
        rl.draw_text("E", compass_x + 22, compass_y - 5, 10, rl.BLACK)
        rl.draw_text("W", compass_x - 32, compass_y - 5, 10, rl.BLACK)

    def draw_minimap(self, state: GameState) -> None:
        if self.maze is None:
            return

        from .constants import CELL_SCALE

        max_map_size = 180
        cell_size = max_map_size // max(self.maze.width, self.maze.height)
        actual_width = cell_size * self.maze.width
        actual_height = cell_size * self.maze.height
        offset_x = state.width - actual_width - 10
        offset_y = state.height - actual_height - 10

        rl.draw_rectangle(offset_x, offset_y, actual_width, actual_height, rl.fade(rl.BLACK, 0.7))
        for z in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.is_wall(x, z):
                    rl.draw_rectangle(
                        offset_x + x * cell_size,
                        offset_y + z * cell_size,
                        cell_size,
                        cell_size,
                        rl.GRAY,
                    )
        rl.draw_rectangle_lines(offset_x, offset_y, actual_width, actual_height, rl.BLACK)

        dest_grid_x = int(self.destination.x / CELL_SCALE)
        dest_grid_z = int(self.destination.z / CELL_SCALE)
        rl.draw_rectangle(
            offset_x + dest_grid_x * cell_size,
            offset_y + dest_grid_z * cell_size,
            cell_size,
            cell_size,
            rl.GOLD,
        )

        if self.axe_pos:
            axe_grid_x = int(self.axe_pos.x / CELL_SCALE)
            axe_grid_z = int(self.axe_pos.z / CELL_SCALE)
            rl.draw_rectangle(
                offset_x + axe_grid_x * cell_size,
                offset_y + axe_grid_z * cell_size,
                cell_size,
                cell_size,
                rl.BLUE,
            )

        px = int((self.player.position.x / CELL_SCALE) * cell_size)
        pz = int((self.player.position.z / CELL_SCALE) * cell_size)
        dir_len = 12
        dx = int(math.sin(self.player.yaw) * dir_len)
        dz = -int(math.cos(self.player.yaw) * dir_len)
        rl.draw_line_ex(
            rl.Vector2(float(offset_x + px), float(offset_y + pz)),
            rl.Vector2(float(offset_x + px + dx), float(offset_y + pz + dz)),
            2,
            rl.RED,
        )
        rl.draw_circle(offset_x + px, offset_y + pz, 4, rl.RED)

    def update(self, dt: float, state: GameState) -> Scene:
        assert self.maze is not None

        is_shift = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SHIFT) or rl.is_key_down(
            rl.KeyboardKey.KEY_RIGHT_SHIFT
        )
        if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_R):
            return Scene.MAIN_MENU

        self.player.update(dt, self.maze)

        # Win condition
        if rl.vector3_distance(self.player.position, self.destination) < 0.5:
            return Scene.END_SCREEN

        # Axe collection
        if self.axe_pos:
            if rl.vector3_distance(self.player.position, self.axe_pos) < 0.8:
                self.player.axe_count += 1
                self.axe_pos = None

        # Wall destruction
        is_ctrl = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_CONTROL) or rl.is_key_down(
            rl.KeyboardKey.KEY_RIGHT_CONTROL
        )
        if self.player.axe_count > 0 and is_ctrl and rl.is_key_pressed(rl.KeyboardKey.KEY_X):
            target = self.get_targeted_wall()
            if target:
                tx, tz = target
                # Destruction logic (already filtered for boundaries by get_targeted_wall)
                self.maze.grid[tz][tx] = 0
                self.player.axe_count -= 1

        if rl.is_key_pressed(rl.KeyboardKey.KEY_M):
            self.show_minimap = not self.show_minimap

        if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_V):
            if self.player.view_mode == ViewMode.FIRST_PERSON:
                self.player.view_mode = ViewMode.TOP_DOWN
            else:
                self.player.view_mode = ViewMode.FIRST_PERSON

        return Scene.MAZE_PLAY
