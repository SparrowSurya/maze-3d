"""
This submodule contains game related objects.
"""

import pyray as rl

from .state import GameState, GameManager, GameDebug
from ..asset import AssetManager, AssetType
from ..components import CompassUi, MinimapUi
from ..debug.scene import MainMenuSceneDebug, GamePlaySceneDebug, GameEndSceneDebug, SceneDebug
from ..scene import MainMenuScene, GamePlayScene, GameEndScene, Scene
from ..scene.manager import SceneManager


class Game:
    """
    Main game application class.

    This class orchestrates the game lifecycle, including initialization of Raylib,
    asset management, scene management, and the main game loop.
    """

    __slots__ = ("state",)

    def __init__(self, width: int, height: int, title: str, *, debug: bool = False) -> None:
        self.state = GameState(
            width=width,
            height=height,
            title=title,
            fps=60,
            debug=GameDebug(
                scene={
                    Scene.MAIN_MENU: MainMenuSceneDebug(),
                    Scene.GAME_PLAY: GamePlaySceneDebug(),
                    Scene.GAME_END: GameEndSceneDebug(),
                },
            ) if debug else None,
            manager=GameManager(
                asset=AssetManager(),
                scene=SceneManager({
                    Scene.MAIN_MENU: MainMenuScene(),
                    Scene.GAME_PLAY: GamePlayScene(
                        components=[
                            CompassUi(),
                            MinimapUi(),
                        ],
                    ),
                    Scene.GAME_END: GameEndScene(),
                }, Scene.MAIN_MENU),
            )
        )

    def _init_window(self) -> None:
        """Initialises window settings."""
        rl.init_window(self.state.width, self.state.height, self.state.title)
        rl.set_window_state(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        rl.set_target_fps(self.state.fps)

    def _load_assets(self) -> None:
        """Loads game assets."""
        asset_manager = self.state.manager.asset

        asset_manager.load_asset(
            "wall.png",
            AssetType.WALL,
            rl.gen_mesh_cube(1.0, 1.0, 1.0),
            material=int(rl.MaterialMapIndex.MATERIAL_MAP_ALBEDO),
        )

        asset_manager.load_asset(
            "grass.png",
            AssetType.GRASS,
            rl.gen_mesh_plane(1.0, 1.0, 1, 1),
            wrap=rl.TextureWrap.TEXTURE_WRAP_REPEAT,
            material=int(rl.MaterialMapIndex.MATERIAL_MAP_ALBEDO),
        )

    def run(self) -> None:
        """
        Start the game.

        This method contains the main game loop, handles window resizing via a
        render texture, manages scene transitions, and orchestrates the update/draw cycle.
        """
        self._init_window()
        self._load_assets()

        # To dynamically display the scene with resiable window we render everything to
        # target texture which can later be placed accordingly.
        target = rl.load_render_texture(self.state.width, self.state.height)
        rl.set_texture_filter(target.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)

        scene_manager = self.state.manager.scene
        scene_manager.get_scene(scene_manager.current).init(self.state)

        debug = self.state.debug

        while not rl.window_should_close():
            dt = rl.get_frame_time()
            current_scene = scene_manager.get_scene(scene_manager.current)
            debug_scene = None if debug is None else debug.scene.get(scene_manager.current)

            # Scene update (optionally with debug)
            next_scene_type = current_scene.update(dt, self.state)
            if debug_scene:
                debug_next_scene_type = debug_scene.update(dt, self.state)
                if debug_next_scene_type:
                    next_scene_type = debug_next_scene_type

            # Scene Transition
            if next_scene_type != scene_manager.current:
                new_scene = scene_manager.get_scene(next_scene_type)
                new_scene.init(self.state)
                scene_manager.set_scene(next_scene_type)
                new_debug_scene = None if not debug else debug.scene.get(next_scene_type)
                if new_debug_scene:
                    new_debug_scene.init(self.state)

            # Toggle scene debug
            if debug and rl.is_key_pressed(rl.KeyboardKey.KEY_F3):
                debug.view_scene = not debug.view_scene

            rl.begin_texture_mode(target)
            rl.clear_background(rl.SKYBLUE)

            current_scene = scene_manager.get_scene(scene_manager.current)
            current_scene.draw(self.state)

            rl.draw_fps(10, self.state.height - 30)
            rl.end_texture_mode()

            rl.begin_drawing()
            rl.clear_background(rl.BLACK)

            rl.draw_texture_pro(
                target.texture,
                rl.Rectangle(0.0, 0.0, float(self.state.width), float(-self.state.height)),
                self._evaluate_target(),
                rl.Vector2(0.0, 0.0),
                0.0,
                rl.WHITE,
            )

            # Debug window
            if debug and debug_scene and debug.view_scene:
                self._draw_debug_window(debug_scene)

            rl.end_drawing()

        self.state.manager.asset.unload_all()
        rl.unload_render_texture(target)

        rl.close_window()

    def _evaluate_target(self) -> rl.Rectangle:
        """Evaluates the destination rectangle to render ``target`` texture."""
        screen_w = rl.get_screen_width()
        screen_h = rl.get_screen_height()
        scale = min(screen_w / self.state.width, screen_h / self.state.height)

        dest_w = self.state.width * scale
        dest_h = self.state.height * scale
        dest_x = (screen_w - dest_w) / 2.0
        dest_y = (screen_h - dest_h) / 2.0

        return rl.Rectangle(float(dest_x), float(dest_y), float(dest_w), float(dest_h))

    def _draw_debug_window(self, debug_scene: SceneDebug) -> None:
        """Draw the debug window."""

        debug = self.state.debug
        if not debug:
            return

        # Handle dragging and resizing in screen pixels
        mouse_pos = rl.get_mouse_position()
        mouse_delta = rl.get_mouse_delta()

        if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
            # Check for dragging (title bar - top 20px)
            title_rect = rl.Rectangle(
                debug.panel_rect.x,
                debug.panel_rect.y,
                debug.panel_rect.width,
                20,
            )
            # Check for resizing (bottom-right corner handle, 15x15)
            resizer_rect = rl.Rectangle(
                debug.panel_rect.x + debug.panel_rect.width - 15,
                debug.panel_rect.y + debug.panel_rect.height - 15,
                15,
                15,
            )

            if rl.check_collision_point_rec(mouse_pos, resizer_rect):
                debug.is_resizing = True
            elif rl.check_collision_point_rec(mouse_pos, title_rect):
                debug.is_dragging = True

        if debug.is_resizing:
            debug.panel_rect.width = max(100, debug.panel_rect.width + mouse_delta.x)
            debug.panel_rect.height = max(100, debug.panel_rect.height + mouse_delta.y)
            if rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT):
                debug.is_resizing = False

        if debug.is_dragging:
            debug.panel_rect.x += mouse_delta.x
            debug.panel_rect.y += mouse_delta.y
            if rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT):
                debug.is_dragging = False

        # Manual Panel Rendering (more reliable than gui_window_box in some envs)
        rl.draw_rectangle_rec(debug.panel_rect, rl.fade(rl.GRAY, 0.9))
        rl.draw_rectangle_lines_ex(debug.panel_rect, 1, rl.DARKGRAY)

        # Title Bar
        title_bar = rl.Rectangle(
            debug.panel_rect.x, debug.panel_rect.y, debug.panel_rect.width, 20
        )
        rl.draw_rectangle_rec(title_bar, rl.DARKGRAY)
        rl.draw_text(
            "DEBUG PANEL",
            int(debug.panel_rect.x + 5),
            int(debug.panel_rect.y + 5),
            10,
            rl.RAYWHITE
        )

        # Close Button
        close_btn_rect = rl.Rectangle(
            debug.panel_rect.x + debug.panel_rect.width - 20,
            debug.panel_rect.y,
            20,
            20
        )
        if rl.gui_button(close_btn_rect, "X"):
            debug.view_scene = False

        debug_scene.draw(self.state)

        # Resize handle
        rl.draw_triangle(
            rl.Vector2(debug.panel_rect.x + debug.panel_rect.width - 2,
                        debug.panel_rect.y + debug.panel_rect.height - 12),
            rl.Vector2(debug.panel_rect.x + debug.panel_rect.width - 12,
                        debug.panel_rect.y + debug.panel_rect.height - 2),
            rl.Vector2(debug.panel_rect.x + debug.panel_rect.width - 2,
                        debug.panel_rect.y + debug.panel_rect.height - 2),
            rl.GOLD
        )
