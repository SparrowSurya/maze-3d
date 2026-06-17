"""
This module contains 3D maze component.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import override, TYPE_CHECKING, Any

import pyray as rl
from raylib import ffi

from ..asset import AssetType
from ..player import ViewMode
from ..scene.constants import (
    CELL_SCALE,
    SLICE_THICKNESS,
    SLICE_HEIGHT,
)
from .models import Component3DConfig
from .abstract import UiComponent3D
from ..scene.constants import Scene
from ..maze import Maze
from ..player import Player

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "MazeView",
    "MazeConfig",
)


@dataclass(slots=True)
class MazeConfig(Component3DConfig):
    """Maze configuration."""


class MazeChunk:
    """A spatial chunk of the maze to optimize rendering."""

    def __init__(self, x_start: int, z_start: int, width: int, height: int) -> None:
        self.x_start = x_start
        self.z_start = z_start
        self.width = width
        self.height = height

        # Center for culling
        self.center = rl.Vector3(
            (float(x_start) + float(width) / 2.0) * CELL_SCALE,
            0.0,
            (float(z_start) + float(height) / 2.0) * CELL_SCALE,
        )
        # Approx bounding sphere radius for the chunk
        self.radius = (max(width, height) * CELL_SCALE) * 0.8

        self.ground_transforms: Any = None
        self.h_slice_transforms: Any = None
        self.v_slice_transforms: Any = None

        self.ground_count: int = 0
        self.h_slice_count: int = 0
        self.v_slice_count: int = 0

    def rebuild(self, maze: Maze) -> None:
        """Populates the transform matrices for this specific chunk."""
        ground_m = []
        h_slice_m = []
        v_slice_m = []

        # Ground Transforms within this chunk
        for gz in range(
            int(self.z_start * CELL_SCALE), int((self.z_start + self.height) * CELL_SCALE)
        ):
            for gx in range(
                int(self.x_start * CELL_SCALE), int((self.x_start + self.width) * CELL_SCALE)
            ):
                pos = rl.Vector3(float(gx) + 0.5, 0.0, float(gz) + 0.5)
                ground_m.append(rl.matrix_translate(pos.x, pos.y, pos.z))

        # Wall Geometry within this chunk
        h_slice_scale_m = rl.matrix_scale(CELL_SCALE, SLICE_HEIGHT, SLICE_THICKNESS)
        v_slice_scale_m = rl.matrix_scale(SLICE_THICKNESS, SLICE_HEIGHT, CELL_SCALE)

        for z in range(self.z_start, self.z_start + self.height):
            for x in range(self.x_start, self.x_start + self.width):
                if 0 <= x < maze.width and 0 <= z < maze.height:
                    if maze.grid[z][x] == 1 and maze.has_neighbor(x, z):
                        pillar_z = float(z) * CELL_SCALE + CELL_SCALE / 2.0
                        pillar_x = float(x) * CELL_SCALE + CELL_SCALE / 2.0

                        # Right Connection
                        if x + 1 < maze.width and maze.grid[z][x + 1] == 1:
                            h_slice_pos = rl.Vector3(
                                float(x) * CELL_SCALE + CELL_SCALE,
                                SLICE_HEIGHT / 2.0,
                                pillar_z,
                            )
                            h_slice_m.append(
                                rl.matrix_multiply(
                                    h_slice_scale_m,
                                    rl.matrix_translate(
                                        h_slice_pos.x, h_slice_pos.y, h_slice_pos.z
                                    ),
                                )
                            )

                        # Bottom Connection
                        if z + 1 < maze.height and maze.grid[z + 1][x] == 1:
                            v_slice_pos = rl.Vector3(
                                pillar_x,
                                SLICE_HEIGHT / 2.0,
                                float(z) * CELL_SCALE + CELL_SCALE,
                            )
                            v_slice_m.append(
                                rl.matrix_multiply(
                                    v_slice_scale_m,
                                    rl.matrix_translate(
                                        v_slice_pos.x, v_slice_pos.y, v_slice_pos.z
                                    ),
                                )
                            )

        # Convert to C-Arrays
        self.ground_count = len(ground_m)
        self.h_slice_count = len(h_slice_m)
        self.v_slice_count = len(v_slice_m)

        if self.ground_count > 0:
            self.ground_transforms = ffi.new(f"Matrix[{self.ground_count}]")
            for i, m in enumerate(ground_m):
                self.ground_transforms[i] = m
        if self.h_slice_count > 0:
            self.h_slice_transforms = ffi.new(f"Matrix[{self.h_slice_count}]")
            for i, m in enumerate(h_slice_m):
                self.h_slice_transforms[i] = m
        if self.v_slice_count > 0:
            self.v_slice_transforms = ffi.new(f"Matrix[{self.v_slice_count}]")
            for i, m in enumerate(v_slice_m):
                self.v_slice_transforms[i] = m

    def is_visible(
        self, camera_pos: rl.Vector3, camera_forward: rl.Vector3, view_mode: ViewMode
    ) -> bool:
        """Performs simple view cone and distance culling."""
        dist = rl.vector3_distance(camera_pos, self.center)

        # Max reasonable draw distance
        if dist > 60.0:
            return False

        # Always draw if very close (inside or near the chunk)
        if dist < self.radius + 5.0:
            return True

        if view_mode == ViewMode.FIRST_PERSON:
            to_chunk = rl.vector3_normalize(rl.vector3_subtract(self.center, camera_pos))
            if rl.vector3_dot_product(camera_forward, to_chunk) < 0.2:
                return False

        return True

    def draw(self, shader: rl.Shader, grass: rl.Model, wall: rl.Model) -> None:
        """Renders all instances in this chunk."""
        if grass and self.ground_count > 0:
            grass.materials[0].shader = shader
            rl.draw_mesh_instanced(
                grass.meshes[0],
                grass.materials[0],
                ffi.addressof(self.ground_transforms[0]),
                self.ground_count,
            )

        if wall:
            wall.materials[0].shader = shader
            if self.h_slice_count > 0:
                rl.draw_mesh_instanced(
                    wall.meshes[0],
                    wall.materials[0],
                    ffi.addressof(self.h_slice_transforms[0]),
                    self.h_slice_count,
                )
            if self.v_slice_count > 0:
                rl.draw_mesh_instanced(
                    wall.meshes[0],
                    wall.materials[0],
                    ffi.addressof(self.v_slice_transforms[0]),
                    self.v_slice_count,
                )


class MazeView(UiComponent3D[MazeConfig]):
    """Maze 3D component in the game."""

    CHUNK_SIZE = 8  # Logical cells per chunk

    def __init__(self, config: MazeConfig | None = None) -> None:
        super().__init__(config)
        self._chunks: list[MazeChunk] = []
        self._last_maze_id: int = -1
        self._last_grid_sum: int = -1
        self._instancing_shader: rl.Shader | None = None

    @property
    @override
    def default_config(self) -> MazeConfig:
        return MazeConfig()

    @override
    def draw(self, state: GameState) -> None:
        if state.gameplay is None:
            return

        if self._instancing_shader is None:
            self._instancing_shader = rl.load_shader("assets/shaders/vert/instancing.vs", "")

        if self._should_rebuild(state.gameplay.maze):
            self._rebuild_chunks(state.gameplay.maze)

        rl.begin_mode_3d(state.gameplay.player.get_camera())
        self.draw_maze_chunked(state)
        self.draw_destination(state, state.gameplay.dest)
        self.draw_player(state, state.gameplay.player)
        self.draw_extra(state)
        rl.end_mode_3d()
        self.draw_hud(state)

    def _should_rebuild(self, maze: Maze) -> bool:
        """Checks if the maze structure has changed."""
        grid_sum = sum(sum(row) for row in maze.grid)
        if id(maze) != self._last_maze_id or grid_sum != self._last_grid_sum:
            self._last_maze_id = id(maze)
            self._last_grid_sum = grid_sum
            return True
        return False

    def _rebuild_chunks(self, maze: Maze) -> None:
        """Partitions the maze into chunks and builds their caches."""
        self._chunks = []

        for z in range(0, maze.height, self.CHUNK_SIZE):
            for x in range(0, maze.width, self.CHUNK_SIZE):
                c_width = min(self.CHUNK_SIZE, maze.width - x)
                c_height = min(self.CHUNK_SIZE, maze.height - z)
                chunk = MazeChunk(x, z, c_width, c_height)
                chunk.rebuild(maze)
                self._chunks.append(chunk)

    def draw_maze_chunked(self, state: GameState) -> None:
        """Culls and draws chunks."""
        assert state.gameplay is not None
        player = state.gameplay.player

        # Calculate camera forward vector for culling
        camera_forward = rl.Vector3(
            math.sin(player.yaw) * math.cos(player.pitch),
            math.sin(player.pitch),
            -math.cos(player.yaw) * math.cos(player.pitch),
        )

        ground_asset = state.manager.asset.get_asset(AssetType.GRASS)
        wall_asset = state.manager.asset.get_asset(AssetType.WALL)

        if not (ground_asset and wall_asset and self._instancing_shader):
            return

        for chunk in self._chunks:
            if chunk.is_visible(player.position, camera_forward, player.view_mode):
                chunk.draw(self._instancing_shader, ground_asset.model, wall_asset.model)

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
        assert state.gameplay is not None

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
        assert state.gameplay is not None

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

        is_shift = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SHIFT) or rl.is_key_down(
            rl.KeyboardKey.KEY_RIGHT_SHIFT
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
                state.gameplay.axe = None

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

        if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_V):
            if state.gameplay.player.view_mode == ViewMode.FIRST_PERSON:
                state.gameplay.player.view_mode = ViewMode.TOP_DOWN
            else:
                state.gameplay.player.view_mode = ViewMode.FIRST_PERSON

    def front_wall(self, player: Player, maze: Maze) -> tuple[int, int] | None:
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
            (map_x + 1.0 - start_x) * delta_dist_x
            if step_x == 1
            else (start_x - map_x) * delta_dist_x
        )
        side_dist_z = (
            (map_z + 1.0 - start_z) * delta_dist_z
            if step_z == 1
            else (start_z - map_z) * delta_dist_z
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
