"""
This submodule contains the scene debug class for game play.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import math

import pyray as rl

from ...scene.constants import Scene, CELL_SCALE
from ...scene.game_play import GamePlayScene

if TYPE_CHECKING:
    from ...game.state import GameState


__all__ = (
    "GamePlaySceneDebug",
)


class GamePlaySceneDebug:
    """Game play scene debug view."""

    def __init__(self) -> None:
        self.camera_offset_x = 10.0
        self.camera_offset_y = 10.0
        self.zoom = 20.0
        self.current_tool = 0

    def init(self, state: GameState) -> None:
        pass

    def draw(self, state: GameState) -> None:
        if not state.debug:
            return

        main_scene = state.manager.scene.get_scene(Scene.GAME_PLAY)
        if not isinstance(main_scene, GamePlayScene):
            return

        panel = state.debug.panel_rect
        maze = main_scene.maze
        player = main_scene.player

        # Note: mouse_pos is now back in screen-space
        mouse_pos = rl.get_mouse_position()

        # Scissor area for the map (excluding title bar and tool panel)
        tools_width = 80
        map_area = rl.Rectangle(
            panel.x + 2,
            panel.y + 22,
            panel.width - tools_width - 4,
            panel.height - 24
        )

        # Prevent interaction if we are dragging or resizing the parent window
        if state.debug.is_dragging or state.debug.is_resizing:
            in_map = False
        else:
            in_map = rl.check_collision_point_rec(mouse_pos, map_area)

        # Zoom
        wheel = rl.get_mouse_wheel_move()
        if in_map and wheel != 0:
            # Local mouse coords (relative to grid origin)
            local_mouse_x = mouse_pos.x - (panel.x + self.camera_offset_x)
            local_mouse_y = mouse_pos.y - (panel.y + 20 + self.camera_offset_y)

            mouse_grid_x = local_mouse_x / self.zoom
            mouse_grid_y = local_mouse_y / self.zoom

            self.zoom = max(2.0, self.zoom + wheel * 2.0)

            # Re-calculate local offsets to keep grid under mouse
            self.camera_offset_x = (mouse_pos.x - panel.x) - (mouse_grid_x * self.zoom)
            self.camera_offset_y = (mouse_pos.y - panel.y - 20) - (mouse_grid_y * self.zoom)

        # Pan (Shift + Left Click)
        is_shift = (
            rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SHIFT)
            or rl.is_key_down(rl.KeyboardKey.KEY_RIGHT_SHIFT)
        )
        if in_map and is_shift and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT):
            # Mouse delta is already in screen pixels
            delta = rl.get_mouse_delta()
            self.camera_offset_x += delta.x
            self.camera_offset_y += delta.y

        # Edit (Left Click WITHOUT Shift)
        elif in_map and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT):
            grid_x = int((mouse_pos.x - (panel.x + self.camera_offset_x)) / self.zoom)
            grid_z = int((mouse_pos.y - (panel.y + 20 + self.camera_offset_y)) / self.zoom)

            if 0 <= grid_x < maze.width and 0 <= grid_z < maze.height:
                if self.current_tool == 0:  # WALL
                    maze.grid[grid_z][grid_x] = 1
                elif self.current_tool == 1:  # WAY
                    maze.grid[grid_z][grid_x] = 0
                elif self.current_tool == 2:  # DEST
                    main_scene.destination = rl.Vector3(
                        grid_x * CELL_SCALE + CELL_SCALE / 2.0, 0.5,
                        grid_z * CELL_SCALE + CELL_SCALE / 2.0
                    )
                elif self.current_tool == 3:  # AXE
                    main_scene.axe = rl.Vector3(
                        grid_x * CELL_SCALE + CELL_SCALE / 2.0, 0.5,
                        grid_z * CELL_SCALE + CELL_SCALE / 2.0
                    )
                elif self.current_tool == 4:  # PLAYER
                    if not maze.is_wall(grid_x, grid_z):
                        player.position.x = grid_x * CELL_SCALE + CELL_SCALE / 2.0
                        player.position.z = grid_z * CELL_SCALE + CELL_SCALE / 2.0


        # Draw UI background for tools
        ui_rect = rl.Rectangle(
            panel.x + panel.width - tools_width,
            panel.y + 20,
            tools_width,
            panel.height - 20
        )
        rl.draw_rectangle_rec(ui_rect, rl.fade(rl.DARKGRAY, 0.9))

        # Tool selection
        tools = ["WALL", "WAY", "DEST", "AXE", "PLAYER"]
        for i, tool_name in enumerate(tools):
            btn_rect = rl.Rectangle(ui_rect.x + 5, ui_rect.y + 5 + i * 25, tools_width - 10, 20)

            # Highlighting the active tool
            if self.current_tool == i:
                rl.draw_rectangle_rec(btn_rect, rl.GOLD)

            # Use standard gui_button which returns True if clicked
            if rl.gui_button(btn_rect, tool_name):
                if self.current_tool != i:
                    self.current_tool = i


        # Axe Count Controls
        rl.draw_text("AXES", int(ui_rect.x + 5), int(ui_rect.y + 140), 10, rl.RAYWHITE)
        if rl.gui_button(rl.Rectangle(ui_rect.x + 5, ui_rect.y + 155, 20, 20), "-"):
            player.axe_count = max(0, player.axe_count - 1)
        rl.draw_text(
            str(player.axe_count),
            int(ui_rect.x + 35),
            int(ui_rect.y + 160),
            10,
            rl.GOLD
        )
        if rl.gui_button(rl.Rectangle(ui_rect.x + 55, ui_rect.y + 155, 20, 20), "+"):
            player.axe_count += 1

        # Rotate Player 90 degrees
        rot_btn_rect = rl.Rectangle(ui_rect.x + 5, ui_rect.y + 185, tools_width - 10, 20)
        if rl.gui_button(rot_btn_rect, "ROT 90"):
            player.yaw += math.pi / 2.0

        # Regenerate Maze
        regen_btn_rect = rl.Rectangle(ui_rect.x + 5, ui_rect.y + 215, tools_width - 10, 20)
        if rl.gui_button(regen_btn_rect, "REGEN"):
            main_scene.init(state)

        # Scissor Mode for map (Screen-space coordinates)
        rl.begin_scissor_mode(
            int(map_area.x),
            int(map_area.y),
            int(map_area.width),
            int(map_area.height),
        )

        # Draw Grid
        for z in range(maze.height):
            for x in range(maze.width):
                sx = panel.x + x * self.zoom + self.camera_offset_x
                sy = panel.y + 20 + z * self.zoom + self.camera_offset_y

                # Culling: only draw if visible in map_area
                if (sx + self.zoom < map_area.x or sx > map_area.x + map_area.width or
                    sy + self.zoom < map_area.y or sy > map_area.y + map_area.height):
                    continue

                color = rl.BLACK if maze.grid[z][x] == 1 else rl.WHITE
                rl.draw_rectangle(int(sx), int(sy), int(self.zoom), int(self.zoom), color)
                rl.draw_rectangle_lines(
                    int(sx), int(sy), int(self.zoom), int(self.zoom), rl.LIGHTGRAY
                )

        # Draw Destination
        dx = int(main_scene.destination.x / CELL_SCALE)
        dz = int(main_scene.destination.z / CELL_SCALE)
        dsx = panel.x + dx * self.zoom + self.camera_offset_x
        dsy = panel.y + 20 + dz * self.zoom + self.camera_offset_y
        rl.draw_rectangle(
            int(dsx + 2), int(dsy + 2), int(self.zoom - 4), int(self.zoom - 4), rl.GOLD
        )

        # Draw Axe
        if main_scene.axe:
            ax = int(main_scene.axe.x / CELL_SCALE)
            az = int(main_scene.axe.z / CELL_SCALE)
            asx = panel.x + ax * self.zoom + self.camera_offset_x
            asy = panel.y + 20 + az * self.zoom + self.camera_offset_y
            rl.draw_rectangle(
                int(asx + 4), int(asy + 4), int(self.zoom - 8), int(self.zoom - 8), rl.BLUE
            )

        # Draw Player
        px = panel.x + (player.position.x / CELL_SCALE) * self.zoom + self.camera_offset_x
        py = panel.y + 20 + (player.position.z / CELL_SCALE) * self.zoom + self.camera_offset_y
        rl.draw_circle(int(px), int(py), int(self.zoom / 3.0), rl.RED)

        # Player direction
        dir_x = px + math.sin(player.yaw) * (self.zoom / 2.0)
        dir_y = py - math.cos(player.yaw) * (self.zoom / 2.0)
        rl.draw_line_ex(rl.Vector2(px, py), rl.Vector2(dir_x, dir_y), 2.0, rl.YELLOW)

        rl.end_scissor_mode()

    def update(self, dt: float, state: GameState) -> Scene | None:
        pass

    def clean(self, state: GameState) -> None:
        pass
