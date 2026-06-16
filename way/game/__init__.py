"""
This submodule contains game related objects.
"""

import pyray as rl

from .state import GameState, GameManager
from ..scene import MainMenuScene, GamePlayScene, GameEndScene, Scene
from ..asset import AssetManager, AssetType
from ..scene.manager import SceneManager


class Game:
    """
    Main game application class.

    This class orchestrates the game lifecycle, including initialization of Raylib,
    asset management, scene management, and the main game loop.
    """

    def __init__(self, width: int, height: int, title: str) -> None:
        self.state = GameState(
            width=width,
            height=height,
            title=title,
            fps=60,
            manager=GameManager(
                asset=AssetManager(),
                scene=SceneManager({
                    Scene.MAIN_MENU: MainMenuScene(),
                    Scene.GAME_PLAY: GamePlayScene(),
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

        while not rl.window_should_close():
            dt = rl.get_frame_time()
            current_scene = scene_manager.get_scene(scene_manager.current)

            next_scene_type = current_scene.update(dt, self.state)

            # Scene Transition
            if next_scene_type != scene_manager.current:
                new_scene = scene_manager.get_scene(next_scene_type)
                new_scene.init(self.state)
                scene_manager.set_scene(next_scene_type)

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
