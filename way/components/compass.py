"""
This module contains compass 2D component.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import override, TYPE_CHECKING

import pyray as rl

from .models import Component2DConfig, Alignment
from .abstract import UiComponent2D

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "CompassUi",
    "CompassConfig",
)


@dataclass(slots=True)
class CompassConfig(Component2DConfig):
    """Compass configuration."""


class CompassUi(UiComponent2D[CompassConfig]):
    """Compass component in the game."""

    @property
    @override
    def default_config(self) -> CompassConfig:
        return CompassConfig(
            align=Alignment.top_right(),
            radius=40.0,
            offset=rl.Vector2(10.0, 10.0),
        )

    def _get_center(self, state: GameState) -> rl.Vector2:
        """Calculates the center of the compass based on config and screen size."""
        radius = self.config.radius or 40.0

        if self.config.pos is None:
            # Case 1: Position relative to screen using alignment
            align = self.config.align or Alignment.center()

            # Map align.x (-1.0 to 1.0) to screen X
            # -1.0 -> offset.x + radius
            #  1.0 -> width - offset.x - radius
            #  0.0 -> center
            x = (float(state.width) / 2.0) + align.x * (
                float(state.width) / 2.0 - radius - self.config.offset.x
            )

            # Map align.y (-1.0 to 1.0) to screen Y
            y = (float(state.height) / 2.0) + align.y * (
                float(state.height) / 2.0 - radius - self.config.offset.y
            )
        else:
            # Case 2: Position relative to an absolute pos, using alignment as anchor
            # align.x = 1.0 means right edge is at pos.x -> center.x = pos.x - radius
            # align.x = -1.0 means left edge is at pos.x -> center.x = pos.x + radius
            align = self.config.align or Alignment.center()
            x = self.config.pos.x - (align.x * radius) + self.config.offset.x
            y = self.config.pos.y - (align.y * radius) + self.config.offset.y

        return rl.Vector2(x, y)

    @override
    def draw(self, state: GameState) -> None:
        self.draw_base(state)
        self.draw_marker(state)
        self.draw_needle(state)

    def draw_base(self, state: GameState) -> None:
        """Draws the base layout of the compass."""
        center = self._get_center(state)
        radius = self.config.radius or 40.0

        rl.draw_circle_v(center, radius, rl.WHITE)
        rl.draw_circle_lines_v(center, radius, rl.DARKGRAY)
        rl.draw_circle_lines_v(center, radius * 0.95, rl.fade(rl.LIGHTGRAY, 0.5))

    def draw_marker(self, state: GameState) -> None:
        """Draws the base marking of the compass for direction indication."""
        center = self._get_center(state)
        radius = self.config.radius or 40.0
        font_size = max(10, int(radius * 0.3))

        # Major ticks
        for i in range(12):
            angle = i * (math.pi / 6)
            inner = radius * 0.85
            outer = radius * 0.95
            if i % 3 == 0:
                inner = radius * 0.75

            p1 = rl.Vector2(center.x + math.sin(angle) * inner, center.y - math.cos(angle) * inner)
            p2 = rl.Vector2(center.x + math.sin(angle) * outer, center.y - math.cos(angle) * outer)
            rl.draw_line_v(p1, p2, rl.GRAY)

        directions = [
            ("N", 0, rl.RED),
            ("E", math.pi / 2, rl.DARKGRAY),
            ("S", math.pi, rl.DARKGRAY),
            ("W", 3 * math.pi / 2, rl.DARKGRAY),
        ]

        for label, angle, color in directions:
            # Position text slightly inside the radius, centered on the angle
            text_radius = radius * 0.65
            tx = center.x + math.sin(angle) * text_radius - rl.measure_text(label, font_size) / 2
            ty = center.y - math.cos(angle) * text_radius - font_size / 2
            rl.draw_text(label, int(tx), int(ty), font_size, color)

    def draw_needle(self, state: GameState) -> None:
        """
        Draws the diamond shaped needle with one color end pointing to north.

        The compass follows magnetic behavior relative to the player's view:
        - World North (True North) is defined as the negative Z-axis (-Z).
        - World Up is defined as the positive Y-axis (+Y).
        - The needle indicates the direction of True North relative to the player's yaw.
        """
        center = self._get_center(state)
        radius = self.config.radius or 40.0

        # Attempt to retrieve the player's yaw from the current scene in GameState
        # This handles the case where the component is used within a GamePlayScene
        scene = state.manager.scene.data.get(state.manager.scene.current)
        player = getattr(scene, "player", None)
        yaw = 0.0
        if player is not None and hasattr(player, "yaw"):
            # Use negative yaw so the needle always points to World North (-Z).
            # This implements magnetic compass behavior where the dial is fixed (N at top)
            # and the needle rotates to point towards True North relative to the view.
            yaw = -float(player.yaw)

        needle_len = radius * 0.8
        needle_width = radius * 0.15

        # Tip North
        tn = rl.Vector2(
            center.x + math.sin(yaw) * needle_len, center.y - math.cos(yaw) * needle_len
        )

        # Tip South
        ts = rl.Vector2(
            center.x - math.sin(yaw) * needle_len, center.y + math.cos(yaw) * needle_len
        )

        # Middle Left and Right (relative to needle direction)
        ml = rl.Vector2(
            center.x + math.sin(yaw - math.pi / 2) * needle_width,
            center.y - math.cos(yaw - math.pi / 2) * needle_width,
        )
        mr = rl.Vector2(
            center.x + math.sin(yaw + math.pi / 2) * needle_width,
            center.y - math.cos(yaw + math.pi / 2) * needle_width,
        )

        # Needle ends
        rl.draw_triangle(tn, ml, mr, rl.RED)
        rl.draw_triangle(ts, mr, ml, rl.BLACK)

        # Pivot
        rl.draw_circle_v(center, 3, rl.DARKGRAY)
        rl.draw_circle_v(center, 1, rl.LIGHTGRAY)
