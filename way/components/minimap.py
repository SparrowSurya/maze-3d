"""
This module contains minimap 2D component.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import override, TYPE_CHECKING

import pyray as rl

from ..scene.constants import CELL_SCALE
from .models import Component2DConfig, Alignment
from .abstract import UiComponent2D

if TYPE_CHECKING:
    from ..scene.game_play import GamePlayScene
    from ..game.state import GameState


__all__ = (
    "MinimapUi",
    "MinimapConfig",
)


@dataclass(slots=True)
class MinimapConfig(Component2DConfig):
    """Compass configuration."""

    neighbours_level: int = 5
    """Descrbies the neighbour levels to show around the player cells."""


class MinimapUi(UiComponent2D):
    """Minimap component in the game."""

    config: MinimapConfig | None = None
    """Optional configuration override for the minimap."""

    @property
    @override
    def default_config(self) -> MinimapConfig:
        return MinimapConfig(
            pos=None,
            align=Alignment.bottom_right(),
            size=rl.Vector2(100.0, 100.0),
            offset=rl.Vector2(10.0, 10.0),
            neighbours_level=7,
        )

    @property
    def current_config(self) -> MinimapConfig:
        """Provides the current configuration being used."""
        return self.config or self.default_config

    def _get_rect(self, state: GameState) -> rl.Rectangle:
        """Calculates the rectangle of the minimap based on config and screen size."""
        config = self.current_config
        size = config.size or rl.Vector2(100.0, 100.0)

        if config.pos is None:
            # Case 1: Position relative to screen using alignment
            align = config.align or Alignment.center()

            # Map align.x (-1.0 to 1.0) to screen X
            # -1.0 -> offset.x
            #  1.0 -> width - offset.x - size.x
            #  0.0 -> center - size.x / 2
            x = (float(state.width) - size.x) / 2.0 + align.x * (
                float(state.width) / 2.0 - size.x / 2.0 - config.offset.x
            )

            # Map align.y (-1.0 to 1.0) to screen Y
            y = (float(state.height) - size.y) / 2.0 + align.y * (
                float(state.height) / 2.0 - size.y / 2.0 - config.offset.y
            )
        else:
            # Case 2: Position relative to an absolute pos, using alignment as anchor
            align = config.align or Alignment.center()
            x = config.pos.x - ((align.x + 1.0) / 2.0 * size.x) + config.offset.x
            y = config.pos.y - ((align.y + 1.0) / 2.0 * size.y) + config.offset.y

        return rl.Rectangle(x, y, size.x, size.y)

    @override
    def draw(self, state: GameState) -> None:
        # Only draw if we are in GamePlayScene
        scene = state.manager.scene.data.get(state.manager.scene.current)
        if scene is None or not hasattr(scene, "maze"):
            return

        rect = self._get_rect(state)
        rl.begin_scissor_mode(int(rect.x), int(rect.y), int(rect.width), int(rect.height))

        self.draw_base(state)
        self.draw_walls(state)
        self.draw_extra(state)

        rl.end_scissor_mode()
        rl.draw_rectangle_lines_ex(rect, 1, rl.BLACK)

    def draw_base(self, state: GameState) -> None:
        """Draws the base layout of the minimap."""
        rect = self._get_rect(state)
        rl.draw_rectangle_rec(rect, rl.fade(rl.BLACK, 0.7))

    def draw_walls(self, state: GameState) -> None:
        """Draws walls of the maze."""
        scene: GamePlayScene = state.manager.scene.data[state.manager.scene.current]  # type: ignore
        rect = self._get_rect(state)
        config = self.current_config
        level = config.neighbours_level

        # Calculate logical grid coordinates for the player
        pgx = scene.player.position.x / CELL_SCALE
        pgz = scene.player.position.z / CELL_SCALE

        cell_count = 2 * level + 1
        cell_size = rect.width / cell_count

        # Top-left logical coord of the view
        view_lx = pgx - level - 0.5
        view_lz = pgz - level - 0.5

        # Iterate through logical cells that overlap with the view
        start_x = int(math.floor(view_lx))
        end_x = int(math.ceil(view_lx + cell_count))
        start_z = int(math.floor(view_lz))
        end_z = int(math.ceil(view_lz + cell_count))

        for z in range(start_z, end_z + 1):
            for x in range(start_x, end_x + 1):
                if 0 <= x < scene.maze.width and 0 <= z < scene.maze.height:
                    if scene.maze.is_wall(x, z):
                        # Calculate screen coordinates relative to the view
                        rx = rect.x + (float(x) - view_lx) * cell_size
                        rz = rect.y + (float(z) - view_lz) * cell_size

                        # Connections only (following existing minimap style)
                        if x + 1 < scene.maze.width and scene.maze.is_wall(x + 1, z):
                            rl.draw_line_ex(
                                rl.Vector2(rx, rz),
                                rl.Vector2(rx + cell_size, rz),
                                1.0,
                                rl.GRAY,
                            )
                        if z + 1 < scene.maze.height and scene.maze.is_wall(x, z + 1):
                            rl.draw_line_ex(
                                rl.Vector2(rx, rz),
                                rl.Vector2(rx, rz + cell_size),
                                1.0,
                                rl.GRAY,
                            )

    def draw_extra(self, state: GameState) -> None:
        """Draws the extra things in maze like player, destination, pickups etc."""
        scene: GamePlayScene = state.manager.scene.data[state.manager.scene.current]  # type: ignore
        rect = self._get_rect(state)
        config = self.current_config
        level = config.neighbours_level

        pgx = scene.player.position.x / CELL_SCALE
        pgz = scene.player.position.z / CELL_SCALE

        cell_count = 2 * level + 1
        cell_size = rect.width / cell_count

        view_lx = pgx - level - 0.5
        view_lz = pgz - level - 0.5

        # Destination
        dgx = scene.destination.x / CELL_SCALE
        dgz = scene.destination.z / CELL_SCALE
        if view_lx <= dgx < view_lx + cell_count and view_lz <= dgz < view_lz + cell_count:
            rl.draw_rectangle_v(
                rl.Vector2(
                    rect.x + (dgx - view_lx) * cell_size - cell_size / 4,
                    rect.y + (dgz - view_lz) * cell_size - cell_size / 4,
                ),
                rl.Vector2(cell_size / 2, cell_size / 2),
                rl.GOLD,
            )

        # Axe
        if scene.axe:
            agx = scene.axe.x / CELL_SCALE
            agz = scene.axe.z / CELL_SCALE
            if view_lx <= agx < view_lx + cell_count and view_lz <= agz < view_lz + cell_count:
                rl.draw_rectangle_v(
                    rl.Vector2(
                        rect.x + (agx - view_lx) * cell_size - cell_size / 4,
                        rect.y + (agz - view_lz) * cell_size - cell_size / 4,
                    ),
                    rl.Vector2(cell_size / 2, cell_size / 2),
                    rl.BLUE,
                )

        # Player (Center of the minimap)
        px = rect.x + rect.width / 2.0
        py = rect.y + rect.height / 2.0

        dir_len = cell_size * 0.8
        dx = math.sin(scene.player.yaw) * dir_len
        dz = -math.cos(scene.player.yaw) * dir_len

        rl.draw_line_ex(
            rl.Vector2(px, py),
            rl.Vector2(px + dx, py + dz),
            2.0,
            rl.YELLOW,
        )
        rl.draw_circle_v(rl.Vector2(px, py), 3.0, rl.RED)
