"""
This module contains 3D maze component.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import override, TYPE_CHECKING

import pyray as rl

from ..asset import AssetType
from ..player import ViewMode
from ..scene.constants import (
    CELL_SCALE,
    PILLAR_SIZE,
    PILLAR_HEIGHT,
    SLICE_THICKNESS,
    SLICE_HEIGHT,
)
from .models import Component3DConfig
from .abstract import UiComponent3D
from ..scene.constants import Scene
from ..maze import Maze, random_maze
from ..player import Player
from ..scene.state import GamePlayState

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "MazeView",
    "MazeConfig",
)


@dataclass(slots=True)
class MazeConfig(Component3DConfig):
    """Maze configuration."""

    grid_size: int
    """Describes NxN maze grid."""


class MazeView(UiComponent3D[MazeConfig]):
    """Maze 3D component in the game."""

    @property
    @override
    def default_config(self) -> MazeConfig:
        return MazeConfig(grid_size=40)

    @override
    def init(self, state: GameState) -> None:
        size = self.config.grid_size
        maze = random_maze(size, size)
        player, dest = self.player_init(maze)
        axe = self.axe_init(maze, player, dest)

        state.gameplay = GamePlayState(
            maze=maze,
            player=player,
            dest=dest,
            axe=axe,
            show_minimap=True,
        )

    def player_init(self, maze: Maze) -> tuple[Player, rl.Vector3]:
        """Provides start and destination."""
        p1, p2 = maze.find_farthest_points()
        spawn_x, spawn_z = p1
        dest_x, dest_z = p2

        # Determine initial facing
        spawn_yaw = 0.0
        if not maze.is_wall(spawn_x, spawn_z - 1):
            spawn_yaw = 0.0  # North
        elif not maze.is_wall(spawn_x + 1, spawn_z):
            spawn_yaw = math.pi / 2  # East
        elif not maze.is_wall(spawn_x, spawn_z + 1):
            spawn_yaw = math.pi  # South
        elif not maze.is_wall(spawn_x - 1, spawn_z):
            spawn_yaw = 3 * math.pi / 2  # West

        player = Player(
            rl.Vector3(
                float(spawn_x) * CELL_SCALE + CELL_SCALE / 2.0,
                0.5,
                float(spawn_z) * CELL_SCALE + CELL_SCALE / 2.0,
            ),
            spawn_yaw,
        )

        dest = rl.Vector3(
            float(dest_x) * CELL_SCALE + CELL_SCALE / 2.0,
            0.5,
            float(dest_z) * CELL_SCALE + CELL_SCALE / 2.0,
        )

        return (player, dest)

    def axe_init(self, maze: Maze, player: Player, dest: rl.Vector3) -> rl.Vector3 | None:
        """Provides axe position."""
        min_dist = (max(maze.width, maze.height) * CELL_SCALE) / 3.0
        max_attempts = 100
        for _ in range(max_attempts):
            ax, az = maze.get_random_empty_cell()
            potential_axe_pos = rl.Vector3(
                float(ax) * CELL_SCALE + CELL_SCALE / 2.0,
                0.5,
                float(az) * CELL_SCALE + CELL_SCALE / 2.0,
            )
            d_spawn = rl.vector3_distance(potential_axe_pos, player.position)
            d_dest = rl.vector3_distance(potential_axe_pos, dest)
            if d_spawn > min_dist and d_dest > min_dist:
                self.axe = potential_axe_pos
                break

    @override
    def draw(self, state: GameState) -> None:
        if state.gameplay is None:
            return

        rl.begin_mode_3d(state.gameplay.player.get_camera())
        self.draw_ground(state, state.gameplay.maze)
        self.draw_walls(state, state.gameplay.maze)
        self.draw_destination(state, state.gameplay.dest)
        self.draw_player(state, state.gameplay.player)
        self.draw_extra(state)
        rl.end_mode_3d()
        self.draw_hud(state)

    def draw_ground(self, state: GameState, maze: Maze) -> None:
        """Draws the ground."""
        ground_asset = state.manager.asset.get_asset(AssetType.GRASS)
        if ground_asset:
            # Draw a grid of unit-sized planes to achieve tiling effect
            # Each logical cell covers CELL_SCALE x CELL_SCALE area.
            for gz in range(int(maze.height * CELL_SCALE)):
                for gx in range(int(maze.width * CELL_SCALE)):
                    rl.draw_model(
                        ground_asset.model,
                        rl.Vector3(float(gx) + 0.5, 0.0, float(gz) + 0.5),
                        1.0,
                        rl.WHITE,
                    )

    def draw_walls(self, state: GameState, maze: Maze) -> None:
        """Draws the walls."""
        wall_asset = state.manager.asset.get_asset(AssetType.WALL)
        if wall_asset:
            pillar_scale = rl.Vector3(PILLAR_SIZE, PILLAR_HEIGHT, PILLAR_SIZE)
            h_slice_scale = rl.Vector3(CELL_SCALE, SLICE_HEIGHT, SLICE_THICKNESS)
            v_slice_scale = rl.Vector3(SLICE_THICKNESS, SLICE_HEIGHT, CELL_SCALE)

            for z in range(maze.height):
                for x in range(maze.width):
                    if maze.is_wall(x, z) and maze.has_neighbor(x, z):
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
                        if x + 1 < maze.width and maze.is_wall(x + 1, z):
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
                        if z + 1 < maze.height and maze.is_wall(x, z + 1):
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

    def draw_destination(self, state: GameState, dest: rl.Vector3) -> None:
        """Draws the destination"""
        rl.draw_cube(dest, 0.5, 2.0, 0.5, rl.GOLD)
        rl.draw_cube_wires(dest, 0.5, 2.0, 0.5, rl.ORANGE)

    def draw_player(self, state: GameState, player: Player) -> None:
        """Draws the player"""
        if player.view_mode == ViewMode.TOP_DOWN:
            player_base_pos = rl.Vector3(player.position.x, 0.0, player.position.z)
            rl.draw_cylinder(
                player_base_pos,
                player.radius,
                player.radius,
                player.height,
                16,
                rl.GREEN,
            )
            rl.draw_cylinder_wires(
                player_base_pos,
                player.radius,
                player.radius,
                player.height,
                16,
                rl.DARKGREEN,
            )

    def draw_extra(self, state: GameState) -> None:
        """Draws the rest of things like collectables etc."""
        assert(state.gameplay is not None)

        axe = state.gameplay.axe
        player = state.gameplay.player
        maze = state.gameplay.maze

        if axe:
            bobbing = math.sin(rl.get_time() * 4.0) * 0.1
            axe_draw_pos = rl.Vector3(axe.x, axe.y + bobbing, axe.z)
            rl.draw_cube(axe_draw_pos, 0.2, 0.2, 0.2, rl.BLUE)
            rl.draw_cube_wires(axe_draw_pos, 0.2, 0.2, 0.2, rl.DARKBLUE)

        # Wall Highlight
        if player.axe_count > 0 and rl.is_key_down(rl.KeyboardKey.KEY_X):
            target = self.front_wall(player, maze)
            if target:
                tx, tz = target
                highlight_pos = rl.Vector3(
                    float(tx) * CELL_SCALE + CELL_SCALE / 2.0,
                    0.6,
                    float(tz) * CELL_SCALE + CELL_SCALE / 2.0,
                )
                # Only highlight the wall that can be destructed
                rl.draw_cube(highlight_pos, CELL_SCALE, 1.2, CELL_SCALE, rl.fade(rl.RED, 0.5))
                rl.draw_cube_wires(highlight_pos, CELL_SCALE, 1.2, CELL_SCALE, rl.RED)

    def draw_hud(self, state: GameState) -> None:
        """Draws static 2d elements and cross-hair."""
        assert(state.gameplay is not None)

        player = state.gameplay.player
        maze = state.gameplay.maze

        rl.draw_text("Find the gold pillar!", 10, 10, 15, rl.DARKGRAY)
        rl.draw_text("Press [M] Minimap | SHIFT+V View | SHIFT+ENTER Menu", 10, 40, 12, rl.GRAY)

        if player.axe_count > 0:
            rl.draw_text(f"Axe: {player.axe_count}", 10, 80, 15, rl.BLUE)

        # Crosshair + highlight
        if rl.is_key_down(rl.KeyboardKey.KEY_X):
            target_wall = self.front_wall(player, maze)
            crosshair_color = rl.RED if (target_wall and player.axe_count > 0) else rl.GRAY
            rl.draw_circle(state.width // 2, state.height // 2, 4, crosshair_color)
        else:
            rl.draw_circle(state.width // 2, state.height // 2, 2, rl.RED)


    @override
    def update(self, state: GameState, dt: float) -> None:
        if state.gameplay is None:
            return

        is_shift = (
            rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SHIFT)
            or rl.is_key_down(rl.KeyboardKey.KEY_RIGHT_SHIFT)
        )

        if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
            return state.manager.scene.set_scene(Scene.MAIN_MENU)

        state.gameplay.player.update(dt, state.gameplay.maze)

        # Win condition
        if rl.vector3_distance(state.gameplay.player.position, state.gameplay.dest) < 0.5:
            return state.manager.scene.set_scene(Scene.GAME_END)

        # Axe collection
        if state.gameplay.axe:
            if rl.vector3_distance(state.gameplay.player.position, state.gameplay.axe) < 0.5:
                state.gameplay.player.axe_count += 1

        is_ctrl = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_CONTROL) or rl.is_key_down(
            rl.KeyboardKey.KEY_RIGHT_CONTROL
        )

        # Wall destruction
        if (
            state.gameplay.player.axe_count > 0
            and is_ctrl
            and rl.is_key_pressed(rl.KeyboardKey.KEY_X)
        ):
            target = self.front_wall(state.gameplay.player, state.gameplay.maze)
            if target:
                tx, tz = target
                state.gameplay.maze.grid[tz][tx] = 0
                state.gameplay.player.axe_count -= 1

        if rl.is_key_pressed(rl.KeyboardKey.KEY_M):
            self.show_minimap = not self.show_minimap

        if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_V):
            if state.gameplay.player.view_mode == ViewMode.FIRST_PERSON:
                state.gameplay.player.view_mode = ViewMode.TOP_DOWN
            else:
                state.gameplay.player.view_mode = ViewMode.FIRST_PERSON

    def front_wall(self, player: Player, maze: Maze) -> tuple[int, int] | None:
        """Finds the wall the player is looking at using raycasting."""
        ray_start = player.position
        forward = rl.Vector3(
            math.sin(player.yaw),
            math.sin(player.pitch),
            -math.cos(player.yaw),
        )
        ray = rl.Ray(ray_start, forward)

        closest_dist = 5.0 * CELL_SCALE
        hit_cell = None

        for z in range(maze.height):
            for x in range(maze.width):
                if maze.grid[z][x] == 1 and maze.has_neighbor(x, z):
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

                        # Only highlight non-boundary walls as targets
                        if 0 < x < maze.width - 1 and 0 < z < maze.height - 1:
                            hit_cell = (x, z)
                        else:
                            # Boundary wall blocks the ray but isn't a valid destructible target
                            hit_cell = None

        return hit_cell

    @override
    def clean(self, state: GameState) -> None:
        state.gameplay = None
