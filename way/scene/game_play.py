"""
This submodule contains the maze play scene.
"""

from __future__ import annotations
import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, override

import pyray as rl

from .abstract import GameScene
from .constants import Scene, CELL_SCALE
from .utils import find_front_wall
from ..components.abstract import UiComponent
from ..maze import Maze, random_maze
from ..player import Player, ViewMode
from ..scene.state import GamePlayState

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "GamePlayScene",
)


class GamePlayScene(GameScene):
    """Describes the maze scene in the game."""

    grid_size: int
    """Describes NxN maze grid."""

    def __init__(self, grid_size: int, components: Sequence[UiComponent] | None = None) -> None:
        GameScene.__init__(self, components)
        self.grid_size = grid_size

    @override
    def init(self, state: GameState) -> None:
        maze = random_maze(self.grid_size, self.grid_size)
        player, dest = self.player_init(maze)
        axe = self.axe_init(maze, player, dest)

        state.gameplay = GamePlayState(
            maze=maze,
            player=player,
            dest=dest,
            axe=axe,
            show_minimap=True,
        )
        
        # Initialize components
        super().init(state)

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
                return potential_axe_pos
        return None

    @override
    def update(self, state: GameState, dt: float) -> None:
        if state.gameplay is None:
            return

        is_shift = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SHIFT) or rl.is_key_down(
            rl.KeyboardKey.KEY_RIGHT_SHIFT
        )

        # 1. Scene Transitions
        if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
            return state.manager.scene.set_scene(Scene.MAIN_MENU)

        # 2. Player Update
        state.gameplay.player.update(dt, state.gameplay.maze)

        # 3. Win Condition
        if rl.vector3_distance(state.gameplay.player.position, state.gameplay.dest) < 0.5:
            return state.manager.scene.set_scene(Scene.GAME_END)

        # 4. Axe Collection
        if state.gameplay.axe:
            if rl.vector3_distance(state.gameplay.player.position, state.gameplay.axe) < 0.5:
                state.gameplay.player.axe_count += 1
                state.gameplay.axe = None

        # 5. Wall Destruction
        is_ctrl = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_CONTROL) or rl.is_key_down(
            rl.KeyboardKey.KEY_RIGHT_CONTROL
        )

        if (
            state.gameplay.player.axe_count > 0
            and is_ctrl
            and rl.is_key_pressed(rl.KeyboardKey.KEY_X)
        ):
            target = find_front_wall(state.gameplay.player, state.gameplay.maze)
            if target:
                tx, tz = target
                state.gameplay.maze.destroy_wall(tx, tz)
                state.gameplay.player.axe_count -= 1

        # 6. View Mode Toggle
        if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_V):
            if state.gameplay.player.view_mode == ViewMode.FIRST_PERSON:
                state.gameplay.player.view_mode = ViewMode.TOP_DOWN
            else:
                state.gameplay.player.view_mode = ViewMode.FIRST_PERSON

        # Update components (UI only)
        super().update(state, dt)

    @override
    def clean(self, state: GameState) -> None:
        super().clean(state)
        state.gameplay = None
