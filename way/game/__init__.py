"""
This submodues contains game related objects.
"""

import pyray as rl

from .state import GameState, GameManager
from ..maze import MazeAlgorithm
from ..scene import MainMenuScene, MazePlayScene, EndScene, Scene
from ..scene.protocols import GameScene
from ..asset import AssetManager, AssetType
from ..scene.manager import SceneManager


class Game:
    def __init__(self) -> None:
        self.width = 800
        self.height = 600
        self.title = "The Way Out - 3D Maze Game"

        # Initialize managers
        self.asset_manager = AssetManager()
        self.scene_manager: SceneManager = None  # type: ignore
        self.game_manager: GameManager = None  # type: ignore

        # Placeholder for GameState
        self.state: GameState = None  # type: ignore

    def _initialize_scenes(self) -> None:
        """Initialize all game scenes and the scene manager."""
        scenes: dict[Scene, GameScene] = {
            Scene.MAIN_MENU: MainMenuScene(),
            Scene.MAZE_PLAY: MazePlayScene(),
            Scene.END_SCREEN: EndScene(),
        }
        self.scene_manager = SceneManager(data=scenes, initial=Scene.MAIN_MENU)
        self.game_manager = GameManager(asset=self.asset_manager, scene=self.scene_manager)

    def run(self) -> None:
        rl.init_window(self.width, self.height, self.title)
        rl.set_target_fps(60)

        # Load Wall Assets via AssetManager
        self.asset_manager.load_asset(
            "wall.png",
            AssetType.WALL,
            rl.gen_mesh_cube(1.0, 1.0, 1.0),
            material=rl.MATERIAL_MAP_DIFFUSE,  # type: ignore
        )

        # Load Grass Assets via AssetManager
        self.asset_manager.load_asset(
            "grass.png",
            AssetType.GRASS,
            rl.gen_mesh_plane(40.0, 40.0, 1, 1),
            wrap=rl.TEXTURE_WRAP_REPEAT,  # type: ignore
            material=rl.MATERIAL_MAP_DIFFUSE,  # type: ignore
        )

        # Initialize SceneManager and GameManager FIRST
        self._initialize_scenes()

        # Initialize GameState with managers
        self.state = GameState(
            width=self.width,
            height=self.height,
            algo=MazeAlgorithm.DFS,
            manager=self.game_manager,
        )

        # Initialize the initial scene
        self.scene_manager.get_scene(self.scene_manager.current).init(self.state)

        while not rl.window_should_close():
            dt = rl.get_frame_time()
            current_scene = self.scene_manager.get_scene(self.scene_manager.current)

            # Update
            next_scene_type = current_scene.update(dt, self.state)

            # Handle Scene Transitions
            if next_scene_type != self.scene_manager.current:
                new_scene = self.scene_manager.get_scene(next_scene_type)
                new_scene.init(self.state)
                self.scene_manager.set_scene(next_scene_type)

            # Draw
            rl.begin_drawing()
            rl.clear_background(rl.SKYBLUE)

            current_scene = self.scene_manager.get_scene(self.scene_manager.current)
            current_scene.draw(self.state)

            rl.draw_fps(10, self.height - 30)
            rl.end_drawing()

        # Unload assets
        self.asset_manager.unload_all()

        rl.close_window()
