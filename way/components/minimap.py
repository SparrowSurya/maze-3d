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
from .logical import LayoutCacheMixin

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "MinimapUi",
    "MinimapConfig",
)


@dataclass(slots=True)
class MinimapLayout:
    """Computed layout cache for minimap."""

    rect: rl.Rectangle
    cell_size: float
    view_lx: float
    view_lz: float


@dataclass(slots=True)
class MinimapConfig(Component2DConfig):
    """Minimap configuration."""

    neighbours_level: int = 5
    """Descrbies the neighbour levels to show around the player cells."""


class MinimapUi(UiComponent2D[MinimapConfig], LayoutCacheMixin[MinimapLayout]):
    """Minimap component in the game."""

    _last_px: float = -1.0
    _last_pz: float = -1.0

    @property
    @override
    def default_config(self) -> MinimapConfig:
        return MinimapConfig(
            pos=None,
            align=Alignment.bottom_right(),
            size=rl.Vector2(100.0, 100.0),
            offset=rl.Vector2(10.0, 10.0),
            neighbours_level=7,
            padding=rl.Vector2(1.0, 1.0),
        )

    @override
    def _is_cache_stale(self, state: GameState) -> bool:
        if super()._is_cache_stale(state):
            return True
        if not state.gameplay:
            return False
        player = state.gameplay.player
        return player.position.x != self._last_px or player.position.z != self._last_pz

    def _get_rect(self, state: GameState) -> rl.Rectangle:
        """Calculates the rectangle of the minimap based on config and screen size."""
        size = self.config.size
        assert size is not None

        if self.config.pos is None:
            # Case 1: Position relative to screen using alignment
            align = self.config.align or Alignment.center()

            # Map align.x (-1.0 to 1.0) to screen X
            x = (float(state.width) - size.x) / 2.0 + align.x * (
                float(state.width) / 2.0 - size.x / 2.0 - self.config.offset.x
            )

            # Map align.y (-1.0 to 1.0) to screen Y
            y = (float(state.height) - size.y) / 2.0 + align.y * (
                float(state.height) / 2.0 - size.y / 2.0 - self.config.offset.y
            )
        else:
            # Case 2: Position relative to an absolute pos, using alignment as anchor
            align = self.config.align or Alignment.center()
            x = self.config.pos.x - ((align.x + 1.0) / 2.0 * size.x) + self.config.offset.x
            y = self.config.pos.y - ((align.y + 1.0) / 2.0 * size.y) + self.config.offset.y

        return rl.Rectangle(x, y, size.x, size.y)

    @override
    def compute_layout(self, state: GameState) -> MinimapLayout:
        assert state.gameplay is not None

        player = state.gameplay.player
        self._last_px = player.position.x
        self._last_pz = player.position.z

        maze = state.gameplay.maze
        rect = self._get_rect(state)
        level = self.config.neighbours_level
        cell_count = 2 * level + 1
        cell_size = rect.width / cell_count

        # Calculate raw logical grid coordinates for the player
        pgx = player.position.x / CELL_SCALE
        pgz = player.position.z / CELL_SCALE

        # Calculate clamped view center
        half_view = cell_count / 2.0
        pad_x, pad_y = self.config.padding.x, self.config.padding.y

        min_lx, max_rx = 0.5 - pad_x, (maze.width - 0.5) + pad_x
        min_lz, max_rz = 0.5 - pad_y, (maze.height - 0.5) + pad_y

        min_cx, max_cx = min_lx + half_view, max_rx - half_view
        min_cz, max_cz = min_lz + half_view, max_rz - half_view

        view_cx = (min_lx + max_rx) / 2.0 if min_cx > max_cx else max(min_cx, min(max_cx, pgx))
        view_cz = (min_lz + max_rz) / 2.0 if min_cz > max_cz else max(min_cz, min(max_cz, pgz))

        view_lx = view_cx - half_view
        view_lz = view_cz - half_view

        return MinimapLayout(
            rect=rect,
            cell_size=cell_size,
            view_lx=view_lx,
            view_lz=view_lz,
        )

    @override
    def draw(self, state: GameState) -> None:
        if not state.gameplay or not state.gameplay.show_minimap:
            return

        layout = self.get_layout(state)
        rl.begin_scissor_mode(
            int(layout.rect.x),
            int(layout.rect.y),
            int(layout.rect.width),
            int(layout.rect.height),
        )

        self.draw_base(state, layout)
        self.draw_walls(state, layout)
        self.draw_extra(state, layout)

        rl.end_scissor_mode()
        rl.draw_rectangle_lines_ex(layout.rect, 1, rl.BLACK)

    def draw_base(self, state: GameState, layout: MinimapLayout) -> None:
        """Draws the base layout of the minimap."""
        rl.draw_rectangle_rec(layout.rect, rl.fade(rl.BLACK, 0.7))

    def draw_walls(self, state: GameState, layout: MinimapLayout) -> None:
        """Draws the walls as lines."""
        assert state.gameplay is not None
        maze = state.gameplay.maze
        level = self.config.neighbours_level
        cell_count = 2 * level + 1

        # Iterate through logical cells that overlap with the view
        start_x = int(math.floor(layout.view_lx))
        end_x = int(math.ceil(layout.view_lx + cell_count))
        start_z = int(math.floor(layout.view_lz))
        end_z = int(math.ceil(layout.view_lz + cell_count))

        for z in range(start_z, end_z + 1):
            for x in range(start_x, end_x + 1):
                if 0 <= x < maze.width and 0 <= z < maze.height:
                    if maze.is_wall(x, z):
                        # Calculate screen coordinates for the CENTER of the logical cell
                        cx = layout.rect.x + (float(x) + 0.5 - layout.view_lx) * layout.cell_size
                        cz = layout.rect.y + (float(z) + 0.5 - layout.view_lz) * layout.cell_size

                        # Connections only
                        if x + 1 < maze.width and maze.is_wall(x + 1, z):
                            rl.draw_line_ex(
                                rl.Vector2(cx, cz),
                                rl.Vector2(cx + layout.cell_size, cz),
                                1.0,
                                rl.GRAY,
                            )
                        if z + 1 < maze.height and maze.is_wall(x, z + 1):
                            rl.draw_line_ex(
                                rl.Vector2(cx, cz),
                                rl.Vector2(cx, cz + layout.cell_size),
                                1.0,
                                rl.GRAY,
                            )

    def draw_extra(self, state: GameState, layout: MinimapLayout) -> None:
        """Draws the extra things in maze like player, destination, pickups etc."""
        assert state.gameplay is not None

        level = self.config.neighbours_level
        cell_count = 2 * level + 1

        pgx = state.gameplay.player.position.x / CELL_SCALE
        pgz = state.gameplay.player.position.z / CELL_SCALE

        # Destination
        dgx = state.gameplay.dest.x / CELL_SCALE
        dgz = state.gameplay.dest.z / CELL_SCALE
        if (
            layout.view_lx <= dgx < layout.view_lx + cell_count
            and layout.view_lz <= dgz < layout.view_lz + cell_count
        ):
            rl.draw_rectangle_v(
                rl.Vector2(
                    layout.rect.x
                    + (dgx - layout.view_lx) * layout.cell_size
                    - layout.cell_size / 4,
                    layout.rect.y
                    + (dgz - layout.view_lz) * layout.cell_size
                    - layout.cell_size / 4,
                ),
                rl.Vector2(layout.cell_size / 2, layout.cell_size / 2),
                rl.GOLD,
            )

        # Axe
        if state.gameplay.axe:
            agx = state.gameplay.axe.x / CELL_SCALE
            agz = state.gameplay.axe.z / CELL_SCALE
            if (
                layout.view_lx <= agx < layout.view_lx + cell_count
                and layout.view_lz <= agz < layout.view_lz + cell_count
            ):
                rl.draw_rectangle_v(
                    rl.Vector2(
                        layout.rect.x
                        + (agx - layout.view_lx) * layout.cell_size
                        - layout.cell_size / 4,
                        layout.rect.y
                        + (agz - layout.view_lz) * layout.cell_size
                        - layout.cell_size / 4,
                    ),
                    rl.Vector2(layout.cell_size / 2, layout.cell_size / 2),
                    rl.BLUE,
                )

        # Player
        px = layout.rect.x + (pgx - layout.view_lx) * layout.cell_size
        py = layout.rect.y + (pgz - layout.view_lz) * layout.cell_size

        dir_len = layout.cell_size * 0.8
        dx = math.sin(state.gameplay.player.yaw) * dir_len
        dz = -math.cos(state.gameplay.player.yaw) * dir_len

        rl.draw_line_ex(
            rl.Vector2(px, py),
            rl.Vector2(px + dx, py + dz),
            2.0,
            rl.YELLOW,
        )
        rl.draw_circle_v(rl.Vector2(px, py), 3.0, rl.RED)

    @override
    def update(self, state: GameState, dt: float) -> None:
        if not state.gameplay:
            return

        if rl.is_key_pressed(rl.KeyboardKey.KEY_M):
            state.gameplay.show_minimap = not state.gameplay.show_minimap
