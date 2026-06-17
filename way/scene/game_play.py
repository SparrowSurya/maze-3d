"""
This submodule contains the maze play scene.
"""

from __future__ import annotations
import math
from collections.abc import Sequence
from typing import override, TYPE_CHECKING

import pyray as rl

from .abstract import GameScene
from .constants import (
    Scene,
    PILLAR_SIZE,
    PILLAR_HEIGHT,
    SLICE_THICKNESS,
    SLICE_HEIGHT,
    CELL_SCALE,
    MINIMAP_GRID_SIZE,
)
from ..maze import Maze, random_maze
from ..player import Player, ViewMode
from ..asset import AssetType
from ..components.abstract import UiComponent

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "GamePlayScene",
)


class GamePlayScene(GameScene):
    """Describes the maze scene in the game."""

    maze: Maze
    player: Player
    dest: rl.Vector3
    axe: rl.Vector3 | None
    show_minimap: bool

    def __init__(self, components: Sequence[UiComponent]) -> None:
        GameScene.__init__(self, components)
        self.player = Player(rl.Vector3(0, 0, 0), 0.0)
        self.dest = rl.Vector3(0, 0, 0)
        self.axe = None
        self.show_minimap: bool = False

    @override
    def init(self, state: GameState) -> None:
        self.maze = random_maze(40, 40)
        self._set_ends()
        self._set_axe()

    def _set_ends(self) -> None:
        """Sets the source and destination."""
        p1, p2 = self.maze.find_farthest_points()
        spawn_x, spawn_z = p1
        dest_x, dest_z = p2

        # Determine initial facing
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

    def _set_axe(self) -> None:
        """Sets the axe position."""
        self.axe = None
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
                self.axe = potential_axe_pos
                break

    def _front_wall(self) -> tuple[int, int] | None:
        """Finds the wall the player is looking at using raycasting."""
        # Calculate targeting ray based on player's yaw and pitch (independent of camera view)
        ray_start = self.player.position
        forward = rl.Vector3(
            math.sin(self.player.yaw),
            math.sin(self.player.pitch),
            -math.cos(self.player.yaw),
        )
        ray = rl.Ray(ray_start, forward)

        closest_dist = 5.0 * CELL_SCALE
        hit_cell = None

        for z in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.grid[z][x] == 1 and self.maze.has_neighbor(x, z):
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

    @override
    def draw(self, state: GameState) -> None:
        rl.begin_mode_3d(self.player.get_camera())

        ground_asset = state.manager.asset.get_asset(AssetType.GRASS)
        wall_asset = state.manager.asset.get_asset(AssetType.WALL)

        if ground_asset:
            # Draw a grid of unit-sized planes to achieve tiling effect
            # Each logical cell covers CELL_SCALE x CELL_SCALE area.
            for gz in range(int(self.maze.height * CELL_SCALE)):
                for gx in range(int(self.maze.width * CELL_SCALE)):
                    rl.draw_model(
                        ground_asset.model,
                        rl.Vector3(float(gx) + 0.5, 0.0, float(gz) + 0.5),
                        1.0,
                        rl.WHITE,
                    )

        if wall_asset:
            pillar_scale = rl.Vector3(PILLAR_SIZE, PILLAR_HEIGHT, PILLAR_SIZE)
            h_slice_scale = rl.Vector3(CELL_SCALE, SLICE_HEIGHT, SLICE_THICKNESS)
            v_slice_scale = rl.Vector3(SLICE_THICKNESS, SLICE_HEIGHT, CELL_SCALE)

            for z in range(self.maze.height):
                for x in range(self.maze.width):
                    if self.maze.is_wall(x, z) and self.maze.has_neighbor(x, z):
                        # Central Pillar
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

                        # Right Connection
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

                        # Bottom Connection
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

        # Axe
        if self.axe:
            bobbing = math.sin(rl.get_time() * 4.0) * 0.1
            axe_draw_pos = rl.Vector3(self.axe.x, self.axe.y + bobbing, self.axe.z)
            rl.draw_cube(axe_draw_pos, 0.2, 0.2, 0.2, rl.BLUE)
            rl.draw_cube_wires(axe_draw_pos, 0.2, 0.2, 0.2, rl.DARKBLUE)

        # Player View
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
            target = self._front_wall()
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
        rl.draw_text("Find the gold pillar!", 10, 10, 15, rl.DARKGRAY)
        rl.draw_text("Press [M] Minimap | SHIFT+V View | SHIFT+ENTER Menu", 10, 40, 12, rl.GRAY)

        if self.player.axe_count > 0:
            rl.draw_text(f"Axe: {self.player.axe_count}", 10, 80, 15, rl.BLUE)

        # Crosshair
        if rl.is_key_down(rl.KeyboardKey.KEY_X):
            target_wall = self._front_wall()
            # Rule #3: Only turn red if target is valid AND player has axe
            crosshair_color = rl.RED if (target_wall and self.player.axe_count > 0) else rl.GRAY
            rl.draw_circle(state.width // 2, state.height // 2, 4, crosshair_color)
        else:
            rl.draw_circle(state.width // 2, state.height // 2, 2, rl.RED)

        for component in self.components:
            component.draw(state)

        if self.show_minimap:
            self.draw_minimap(state)

    def draw_minimap(self, state: GameState) -> None:
        max_map_pixel_size = 90
        cell_size = max_map_pixel_size // MINIMAP_GRID_SIZE
        actual_width = cell_size * MINIMAP_GRID_SIZE
        actual_height = cell_size * MINIMAP_GRID_SIZE
        offset_x = state.width - actual_width - 10
        offset_y = state.height - actual_height - 10

        # Calculate logical grid coordinates for the player
        pgx = self.player.position.x / CELL_SCALE
        pgz = self.player.position.z / CELL_SCALE

        # Determine the floating-point top-left corner for the smooth scrolling grid
        view_left = pgx - MINIMAP_GRID_SIZE / 2.0
        view_top = pgz - MINIMAP_GRID_SIZE / 2.0

        # Clamp view boundaries to stay within the maze
        view_left = max(0.0, min(view_left, float(self.maze.width - MINIMAP_GRID_SIZE)))
        view_top = max(0.0, min(view_top, float(self.maze.height - MINIMAP_GRID_SIZE)))

        # Background
        rl.draw_rectangle(offset_x, offset_y, actual_width, actual_height, rl.fade(rl.BLACK, 0.7))

        rl.begin_scissor_mode(
            int(offset_x),
            int(offset_y),
            int(actual_width),
            int(actual_height),
        )

        # Iterate through logical cells that overlap with the view
        # Using floor/ceil to get the range of indices
        for z in range(int(math.floor(view_top)), int(math.ceil(view_top + MINIMAP_GRID_SIZE)) + 1):
            for x in range(
                int(math.floor(view_left)), int(math.ceil(view_left + MINIMAP_GRID_SIZE)) + 1
            ):
                if 0 <= x < self.maze.width and 0 <= z < self.maze.height:
                    if self.maze.is_wall(x, z):
                        # Calculate smooth pixel coordinates relative to the view
                        rx = (float(x) - view_left) * cell_size
                        rz = (float(z) - view_top) * cell_size
                        cx = offset_x + int(rx) + cell_size // 2
                        cz = offset_y + int(rz) + cell_size // 2

                        # Connections only (No Pillars)
                        if x + 1 < self.maze.width and self.maze.is_wall(x + 1, z):
                            rl.draw_line(cx, cz, cx + cell_size, cz, rl.GRAY)
                        if z + 1 < self.maze.height and self.maze.is_wall(x, z + 1):
                            rl.draw_line(cx, cz, cx, cz + cell_size, rl.GRAY)

        # Icons (only if within current view)
        dgx = int(self.destination.x / CELL_SCALE)
        dgz = int(self.destination.z / CELL_SCALE)
        in_view_x = view_left <= dgx < view_left + MINIMAP_GRID_SIZE
        in_view_z = view_top <= dgz < view_top + MINIMAP_GRID_SIZE
        if in_view_x and in_view_z:
            rl.draw_rectangle(
                offset_x + int((float(dgx) - view_left) * cell_size) + cell_size // 4,
                offset_y + int((float(dgz) - view_top) * cell_size) + cell_size // 4,
                max(3, cell_size // 2),
                max(3, cell_size // 2),
                rl.GOLD,
            )

        if self.axe:
            agx = int(self.axe.x / CELL_SCALE)
            agz = int(self.axe.z / CELL_SCALE)
            in_view_x = view_left <= agx < view_left + MINIMAP_GRID_SIZE
            in_view_z = view_top <= agz < view_top + MINIMAP_GRID_SIZE
            if in_view_x and in_view_z:
                rl.draw_rectangle(
                    offset_x + int((float(agx) - view_left) * cell_size) + cell_size // 4,
                    offset_y + int((float(agz) - view_top) * cell_size) + cell_size // 4,
                    max(3, cell_size // 2),
                    max(3, cell_size // 2),
                    rl.BLUE,
                )

        # Player Position (Always relative to start_x, start_z)
        px = int((pgx - view_left) * cell_size)
        pz = int((pgz - view_top) * cell_size)

        dir_len = 12
        dx = int(math.sin(self.player.yaw) * dir_len)
        dz = -int(math.cos(self.player.yaw) * dir_len)
        rl.draw_line_ex(
            rl.Vector2(float(offset_x + px), float(offset_y + pz)),
            rl.Vector2(float(offset_x + px + dx), float(offset_y + pz + dz)),
            1,
            rl.YELLOW,
        )
        rl.draw_circle(offset_x + px, offset_y + pz, 3, rl.RED)

        rl.end_scissor_mode()
        rl.draw_rectangle_lines(offset_x, offset_y, actual_width, actual_height, rl.BLACK)

    @override
    def update(self, dt: float, state: GameState) -> Scene:
        is_shift = (
            rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SHIFT)
            or rl.is_key_down(rl.KeyboardKey.KEY_RIGHT_SHIFT)
        )

        if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
            return Scene.MAIN_MENU

        self.player.update(dt, self.maze)

        # Win condition
        if rl.vector3_distance(self.player.position, self.destination) < 0.5:
            return Scene.GAME_END

        # Axe collection
        if self.axe:
            if rl.vector3_distance(self.player.position, self.axe) < 0.5:
                self.player.axe_count += 1

        # Wall destruction
        is_ctrl = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_CONTROL) or rl.is_key_down(
            rl.KeyboardKey.KEY_RIGHT_CONTROL
        )
        if self.player.axe_count > 0 and is_ctrl and rl.is_key_pressed(rl.KeyboardKey.KEY_X):
            target = self._front_wall()
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

        return Scene.GAME_PLAY

    @override
    def clean(self, state: GameState) -> None:
        pass
