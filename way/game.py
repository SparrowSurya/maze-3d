import pyray as rl

from .maze import MazeAlgorithm
from .scene import GameScene, GameState, MainMenu, MazePlayScene, EndScene, Scene


class Game:
    def __init__(self) -> None:
        self.width = 800
        self.height = 600
        self.title = "The Way Out - 3D Maze Game"

        # Initialize placeholders for assets that will be loaded in run()
        self.state: GameState = None  # type: ignore

        # Scene management
        self.current_scene_type: Scene = Scene.MAIN_MENU
        self.current_scene: GameScene = MainMenu()

    def run(self) -> None:
        rl.init_window(self.width, self.height, self.title)
        rl.set_target_fps(60)

        # Load Wall Assets
        wall_texture = rl.load_texture("assets/wall_texture.png")
        mesh_cube = rl.gen_mesh_cube(1.0, 1.0, 1.0)
        wall_model = rl.load_model_from_mesh(mesh_cube)
        if wall_model and wall_texture:
            rl.set_material_texture(
                wall_model.materials[0],
                rl.MATERIAL_MAP_DIFFUSE,  # type: ignore
                wall_texture,
            )

        # Load Grass Assets
        grass_texture = rl.load_texture("assets/grass_texture.png")
        if grass_texture:
            rl.set_texture_wrap(grass_texture, rl.TEXTURE_WRAP_REPEAT)  # type: ignore

        # We generate a generic ground model
        mesh_plane = rl.gen_mesh_plane(40.0, 40.0, 1, 1)
        ground_model = rl.load_model_from_mesh(mesh_plane)
        if ground_model and grass_texture:
            rl.set_material_texture(
                ground_model.materials[0],
                rl.MATERIAL_MAP_DIFFUSE,  # type: ignore
                grass_texture,
            )

        # Initialize GameState with loaded assets
        self.state = GameState(
            width=self.width,
            height=self.height,
            selected_algo=MazeAlgorithm.DFS,
            wall_texture=wall_texture,
            wall_model=wall_model,
            grass_texture=grass_texture,
            ground_model=ground_model,
        )

        while not rl.window_should_close():
            dt = rl.get_frame_time()

            # Update
            next_scene_type = self.current_scene.update(dt, self.state)

            # Handle Scene Transitions
            if next_scene_type != self.current_scene_type:
                self.transition_to(next_scene_type)

            # Draw
            rl.begin_drawing()
            rl.clear_background(rl.SKYBLUE)

            self.current_scene.draw(self.state)

            rl.draw_fps(10, self.height - 30)
            rl.end_drawing()

        # Unload assets
        rl.unload_texture(wall_texture)
        rl.unload_model(wall_model)
        rl.unload_texture(grass_texture)
        rl.unload_model(ground_model)

        rl.close_window()

    def transition_to(self, scene_type: Scene) -> None:
        """Handles the logic of switching between scenes."""
        if scene_type == Scene.MAIN_MENU:
            self.current_scene = MainMenu()
        elif scene_type == Scene.MAZE_PLAY:
            self.current_scene = MazePlayScene(self.state)
        elif scene_type == Scene.END_SCREEN:
            self.current_scene = EndScene()

        self.current_scene_type = scene_type
