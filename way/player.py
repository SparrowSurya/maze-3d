"""
This modules contains the player related classes.
"""

from enum import StrEnum, auto
import math
from dataclasses import dataclass, field

import pyray as rl

from .maze import Maze


class ViewMode(StrEnum):
    """Describes the player's view in the game."""

    FIRST_PERSON = auto()
    TOP_DOWN = auto()


@dataclass
class Player:
    """Describes the player in the game."""

    position: rl.Vector3
    yaw: float  # Rotation in radians
    pitch: float = 0.0
    move_speed: float = 3.0
    rotation_speed: float = 3.0

    # Physics constants
    vertical_velocity: float = 0.0
    jump_force: float = 5.0
    gravity: float = -15.0
    is_grounded: bool = field(init=False, default=True)
    base_y: float = 0.5
    radius: float = 0.3  # Cylindrical radius
    height: float = 0.8

    axe_count: int = 0

    view_mode: ViewMode = ViewMode.FIRST_PERSON
    TOP_DOWN_HEIGHT: float = 12.0

    def get_camera(self) -> rl.Camera3D:
        """Provides the camers as per player's presepective view."""
        if self.view_mode == ViewMode.FIRST_PERSON:
            target = rl.Vector3(
                self.position.x + math.sin(self.yaw),
                self.position.y + math.sin(self.pitch),
                self.position.z - math.cos(self.yaw),
            )
            return rl.Camera3D(
                self.position,
                target,
                rl.Vector3(0.0, 1.0, 0.0),
                45.0,
                rl.CAMERA_PERSPECTIVE,  # type: ignore
            )
        else:
            # Top-down view
            # Camera is high above the player, looking straight down
            camera_pos = rl.Vector3(
                self.position.x,
                self.position.y + self.TOP_DOWN_HEIGHT,
                self.position.z,
            )
            # Look at the player
            target = self.position
            # Up vector is the player's forward direction to make them always face "up"
            up = rl.Vector3(math.sin(self.yaw), 0.0, -math.cos(self.yaw))
            return rl.Camera3D(
                camera_pos,
                target,
                up,
                45.0,
                rl.CAMERA_PERSPECTIVE,  # type: ignore
            )

    def _check_collision(self, px: float, pz: float, maze: Maze) -> bool:
        """Checks if a cylinder at (px, pz) intersects any thin maze walls."""
        from .scene.constants import PILLAR_SIZE, SLICE_THICKNESS, CELL_SCALE

        # Check a 3x3 grid of cells around the player
        grid_x = int(math.floor(px / CELL_SCALE))
        grid_z = int(math.floor(pz / CELL_SCALE))

        half_pillar = PILLAR_SIZE / 2.0
        half_slice = SLICE_THICKNESS / 2.0

        for i in range(grid_x - 1, grid_x + 2):
            for j in range(grid_z - 1, grid_z + 2):
                if maze.is_wall(i, j):
                    # 1. Pillar Collision
                    # AABB: (i*CELL_SCALE + half_cell - half_pillar)
                    cx = float(i) * CELL_SCALE + CELL_SCALE / 2.0
                    cz = float(j) * CELL_SCALE + CELL_SCALE / 2.0
                    if self._check_circle_aabb_collision(
                        px,
                        pz,
                        cx - half_pillar,
                        cz - half_pillar,
                        cx + half_pillar,
                        cz + half_pillar,
                    ):
                        return True

                    # 2. Right Slice Collision
                    if maze.is_wall(i + 1, j):
                        # AABB: Connects (i, j) pillar to (i+1, j) pillar
                        # Center x is at (i+1)*CELL_SCALE
                        # Span is CELL_SCALE long
                        if self._check_circle_aabb_collision(
                            px,
                            pz,
                            float(i) * CELL_SCALE + CELL_SCALE / 2.0,
                            cz - half_slice,
                            float(i + 1) * CELL_SCALE + CELL_SCALE / 2.0,
                            cz + half_slice,
                        ):
                            return True

                    # 3. Bottom Slice Collision
                    if maze.is_wall(i, j + 1):
                        if self._check_circle_aabb_collision(
                            px,
                            pz,
                            cx - half_slice,
                            float(j) * CELL_SCALE + CELL_SCALE / 2.0,
                            cx + half_slice,
                            float(j + 1) * CELL_SCALE + CELL_SCALE / 2.0,
                        ):
                            return True

                    # 4. Left Slice Collision
                    if maze.is_wall(i - 1, j):
                        if self._check_circle_aabb_collision(
                            px,
                            pz,
                            float(i - 1) * CELL_SCALE + CELL_SCALE / 2.0,
                            cz - half_slice,
                            float(i) * CELL_SCALE + CELL_SCALE / 2.0,
                            cz + half_slice,
                        ):
                            return True

                    # 5. Top Slice Collision
                    if maze.is_wall(i, j - 1):
                        if self._check_circle_aabb_collision(
                            px,
                            pz,
                            cx - half_slice,
                            float(j - 1) * CELL_SCALE + CELL_SCALE / 2.0,
                            cx + half_slice,
                            float(j) * CELL_SCALE + CELL_SCALE / 2.0,
                        ):
                            return True
        return False


    def _check_circle_aabb_collision(
        self, px: float, pz: float, min_x: float, min_z: float, max_x: float, max_z: float
    ) -> bool:
        """Helper to check circle vs AABB collision."""
        closest_x = max(min_x, min(px, max_x))
        closest_z = max(min_z, min(pz, max_z))
        dx = px - closest_x
        dz = pz - closest_z
        return (dx * dx + dz * dz) < (self.radius * self.radius)

    def update(self, delta_time: float, maze: Maze) -> None:
        """Updates the player in the game."""
        # Rotation
        if rl.is_key_down(rl.KeyboardKey.KEY_LEFT):  # type: ignore
            self.yaw -= self.rotation_speed * delta_time
        if rl.is_key_down(rl.KeyboardKey.KEY_RIGHT):  # type: ignore
            self.yaw += self.rotation_speed * delta_time

        # Movement
        # forward vector: x = sin(yaw), z = -cos(yaw)
        forward = rl.Vector3(math.sin(self.yaw), 0.0, -math.cos(self.yaw))

        move_vec = rl.Vector3(0, 0, 0)
        if rl.is_key_down(rl.KeyboardKey.KEY_UP):  # type: ignore
            move_vec.x += forward.x * self.move_speed * delta_time
            move_vec.z += forward.z * self.move_speed * delta_time
        if rl.is_key_down(rl.KeyboardKey.KEY_DOWN):  # type: ignore
            move_vec.x -= forward.x * self.move_speed * delta_time
            move_vec.z -= forward.z * self.move_speed * delta_time

        # Jumping
        if self.is_grounded and rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE):  # type: ignore
            self.vertical_velocity = self.jump_force
            self.is_grounded = False

        # Apply gravity
        self.vertical_velocity += self.gravity * delta_time
        self.position.y += self.vertical_velocity * delta_time

        # Ground collision
        if self.position.y <= self.base_y:
            self.position.y = self.base_y
            self.vertical_velocity = 0
            self.is_grounded = True

        # Robust sliding collision
        new_x = self.position.x + move_vec.x
        new_z = self.position.z + move_vec.z

        # 1. Try full movement
        if not self._check_collision(new_x, new_z, maze):
            self.position.x = new_x
            self.position.z = new_z
        else:
            # 2. Try sliding along X
            if not self._check_collision(new_x, self.position.z, maze):
                self.position.x = new_x

            # 3. Try sliding along Z
            # (Note: we check against current self.position.x which might have been updated)
            if not self._check_collision(self.position.x, new_z, maze):
                self.position.z = new_z
