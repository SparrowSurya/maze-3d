import math
from dataclasses import dataclass

import pyray as rl

from .maze import Maze


@dataclass
class Player:
    position: rl.Vector3
    yaw: float  # Rotation in radians
    pitch: float = 0.0
    move_speed: float = 5.0
    rotation_speed: float = 2.0

    def get_camera(self) -> rl.Camera3D:
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
            rl.CAMERA_PERSPECTIVE,
        )

    def update(self, delta_time: float, maze: Maze) -> None:
        # Rotation
        if rl.is_key_down(rl.KeyboardKey.KEY_LEFT):
            self.yaw -= self.rotation_speed * delta_time
        if rl.is_key_down(rl.KeyboardKey.KEY_RIGHT):
            self.yaw += self.rotation_speed * delta_time

        # Movement
        # forward vector: x = sin(yaw), z = -cos(yaw)
        forward = rl.Vector3(math.sin(self.yaw), 0.0, -math.cos(self.yaw))
        new_pos = rl.Vector3(self.position.x, self.position.y, self.position.z)

        if rl.is_key_down(rl.KeyboardKey.KEY_UP):
            new_pos.x += forward.x * self.move_speed * delta_time
            new_pos.z += forward.z * self.move_speed * delta_time
        if rl.is_key_down(rl.KeyboardKey.KEY_DOWN):
            new_pos.x -= forward.x * self.move_speed * delta_time
            new_pos.z -= forward.z * self.move_speed * delta_time

        # Simple collision: check if new position is in a wall
        padding = 0.4

        # Check X movement
        can_move_x = True
        for offset_x in [-padding, padding]:
            for offset_z in [-padding, padding]:
                if maze.is_wall(int(new_pos.x + offset_x), int(self.position.z + offset_z)):
                    can_move_x = False
                    break
            if not can_move_x:
                break
        if can_move_x:
            self.position.x = new_pos.x

        # Check Z movement
        can_move_z = True
        for offset_z in [-padding, padding]:
            for offset_x in [-padding, padding]:
                if maze.is_wall(int(self.position.x + offset_x), int(new_pos.z + offset_z)):
                    can_move_z = False
                    break
            if not can_move_z:
                break
        if can_move_z:
            self.position.z = new_pos.z
