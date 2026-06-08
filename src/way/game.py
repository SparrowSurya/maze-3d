import math
import pyray as rl

from .maze import get_default_maze
from .player import Player


class Game:
    def __init__(self) -> None:
        self.width = 800
        self.height = 600
        self.title = "Way - 3D Maze Game"

        self.wall_texture: rl.Texture2D | None = None
        self.wall_model: rl.Model | None = None

        self.grass_texture: rl.Texture2D | None = None
        self.ground_model: rl.Model | None = None

        self.init_game()

    def init_game(self) -> None:
        self.maze = get_default_maze()

        # Find two farthest points
        p1, p2 = self.maze.find_farthest_points()
        spawn_x, spawn_z = p1
        dest_x, dest_z = p2

        # Determine initial yaw (face toward an empty neighbor)
        spawn_yaw = 0.0
        if not self.maze.is_wall(spawn_x, spawn_z - 1):
            spawn_yaw = 0.0  # North
        elif not self.maze.is_wall(spawn_x + 1, spawn_z):
            spawn_yaw = math.pi / 2  # East
        elif not self.maze.is_wall(spawn_x, spawn_z + 1):
            spawn_yaw = math.pi  # South
        elif not self.maze.is_wall(spawn_x - 1, spawn_z):
            spawn_yaw = 3 * math.pi / 2  # West

        self.player = Player(
            rl.Vector3(float(spawn_x) + 0.5, 0.5, float(spawn_z) + 0.5), spawn_yaw
        )

        self.destination = rl.Vector3(float(dest_x) + 0.5, 0.5, float(dest_z) + 0.5)

        self.is_won = False
        self.show_minimap = False

    def run(self) -> None:
        rl.init_window(self.width, self.height, self.title)
        rl.set_target_fps(60)

        # Load Wall Assets
        self.wall_texture = rl.load_texture("assets/wall_texture.png")
        mesh_cube = rl.gen_mesh_cube(1.0, 1.0, 1.0)
        self.wall_model = rl.load_model_from_mesh(mesh_cube)
        if self.wall_texture:
            rl.set_material_texture(
                self.wall_model.materials[0],
                rl.MATERIAL_MAP_DIFFUSE,
                self.wall_texture,
            )

        # Load Grass Assets
        self.grass_texture = rl.load_texture("assets/grass_texture.png")
        if self.grass_texture:
            rl.set_texture_wrap(self.grass_texture, rl.TEXTURE_WRAP_REPEAT)  # type: ignore

        mesh_plane = rl.gen_mesh_plane(float(self.maze.width), float(self.maze.height), 1, 1)
        self.ground_model = rl.load_model_from_mesh(mesh_plane)
        if self.ground_model:
            if self.grass_texture:
                rl.set_material_texture(
                    self.ground_model.materials[0],
                    rl.MATERIAL_MAP_DIFFUSE,  # type: ignore
                    self.grass_texture,
                )


        while not rl.window_should_close():
            delta_time = rl.get_frame_time()
            self.update(delta_time)
            self.draw()

        # Unload assets
        if self.wall_texture:
            rl.unload_texture(self.wall_texture)
        if self.wall_model:
            rl.unload_model(self.wall_model)
        if self.grass_texture:
            rl.unload_texture(self.grass_texture)
        if self.ground_model:
            rl.unload_model(self.ground_model)

        rl.close_window()

    def update(self, delta_time: float) -> None:
        if not self.is_won:
            self.player.update(delta_time, self.maze)

            # Check win condition
            dist = rl.vector3_distance(self.player.position, self.destination)
            if dist < 0.5:
                self.is_won = True

            # Toggle minimap with M
            if rl.is_key_pressed(rl.KeyboardKey.KEY_M):
                self.show_minimap = not self.show_minimap
        else:
            # Play again with R or Enter
            if rl.is_key_pressed(rl.KeyboardKey.KEY_R) or rl.is_key_pressed(
                rl.KeyboardKey.KEY_ENTER
            ):
                self.init_game()

    def draw(self) -> None:
        rl.begin_drawing()
        rl.clear_background(rl.SKYBLUE)

        rl.begin_mode_3d(self.player.get_camera())

        # Draw ground model
        if self.ground_model:
            pos = rl.Vector3(self.maze.width / 2.0, 0, self.maze.height / 2.0)
            rl.draw_model(self.ground_model, pos, 1.0, rl.WHITE)
        else:
            rl.draw_plane(
                rl.Vector3(self.maze.width / 2.0, 0, self.maze.height / 2.0),
                rl.Vector2(float(self.maze.width), float(self.maze.height)),
                rl.GREEN,
            )

        # Draw maze walls
        if self.wall_model:
            for z in range(self.maze.height):
                for x in range(self.maze.width):
                    if self.maze.is_wall(x, z):
                        pos = rl.Vector3(float(x) + 0.5, 0.5, float(z) + 0.5)
                        rl.draw_model(self.wall_model, pos, 1.0, rl.WHITE)

        # Draw destination marker
        rl.draw_cube(self.destination, 0.5, 2.0, 0.5, rl.GOLD)
        rl.draw_cube_wires(self.destination, 0.5, 2.0, 0.5, rl.ORANGE)

        rl.end_mode_3d()

        # Draw HUD
        self.draw_hud()

        rl.end_drawing()

    def draw_hud(self) -> None:
        if self.is_won:
            # Semi-transparent overlay
            rl.draw_rectangle(0, 0, self.width, self.height, rl.fade(rl.BLACK, 0.5))
            rl.draw_text(
                "YOU FOUND THE WAY!", self.width // 2 - 150, self.height // 2 - 40, 30, rl.GOLD
            )
            rl.draw_text(
                "Press [ENTER] or [R] to Play Again",
                self.width // 2 - 140,
                self.height // 2 + 10,
                15,
                rl.WHITE,
            )
        else:
            rl.draw_text("Find the gold pillar!", 10, 10, 20, rl.BLACK)
            rl.draw_text("Press [M] to Toggle Minimap", 10, 40, 15, rl.GRAY)

            # Compass
            self.draw_compass()

            # Minimap
            if self.show_minimap:
                self.draw_minimap()

        rl.draw_fps(10, self.height - 30)

    def draw_compass(self) -> None:
        compass_x = self.width - 60
        compass_y = 60
        rl.draw_circle(compass_x, compass_y, 40, rl.LIGHTGRAY)
        rl.draw_circle_lines(compass_x, compass_y, 40, rl.DARKGRAY)

        # Needle points North (Up) when yaw=0
        needle_len = 25  # Smaller needle
        needle_end_x = compass_x + int(math.sin(self.player.yaw) * needle_len)
        needle_end_y = compass_y - int(math.cos(self.player.yaw) * needle_len)
        rl.draw_line_ex(
            rl.Vector2(float(compass_x), float(compass_y)),
            rl.Vector2(float(needle_end_x), float(needle_end_y)),
            3,
            rl.RED,
        )

        # Directions - Little more outwards
        rl.draw_text("N", compass_x - 3, compass_y - 35, 10, rl.BLACK)
        rl.draw_text("S", compass_x - 3, compass_y + 25, 10, rl.BLACK)
        rl.draw_text("E", compass_x + 25, compass_y - 5, 10, rl.BLACK)
        rl.draw_text("W", compass_x - 35, compass_y - 5, 10, rl.BLACK)

    def draw_minimap(self) -> None:
        max_map_size = 180
        cell_size = max_map_size // max(self.maze.width, self.maze.height)
        
        actual_width = cell_size * self.maze.width
        actual_height = cell_size * self.maze.height
        
        offset_x = self.width - actual_width - 10
        offset_y = self.height - actual_height - 10

        # Background
        rl.draw_rectangle(offset_x, offset_y, actual_width, actual_height, rl.fade(rl.BLACK, 0.7))

        # Walls
        for z in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.is_wall(x, z):
                    rl.draw_rectangle(
                        offset_x + x * cell_size,
                        offset_y + z * cell_size,
                        cell_size,
                        cell_size,
                        rl.GRAY,
                    )

        # Boundary Outline
        rl.draw_rectangle_lines(offset_x, offset_y, actual_width, actual_height, rl.BLACK)

        # Destination
        dest_x = int(self.destination.x)
        dest_z = int(self.destination.z)
        rl.draw_rectangle(
            offset_x + dest_x * cell_size,
            offset_y + dest_z * cell_size,
            cell_size,
            cell_size,
            rl.GOLD,
        )

        # Player
        px = int(self.player.position.x * cell_size)
        pz = int(self.player.position.z * cell_size)

        # Player Direction (long line)
        dir_len = 12
        dx = int(math.sin(self.player.yaw) * dir_len)
        dz = -int(math.cos(self.player.yaw) * dir_len)  # -cos for North=Up

        # Draw direction line
        rl.draw_line_ex(
            rl.Vector2(float(offset_x + px), float(offset_y + pz)),
            rl.Vector2(float(offset_x + px + dx), float(offset_y + pz + dz)),
            2,
            rl.RED,
        )

        # Draw player dot
        rl.draw_circle(offset_x + px, offset_y + pz, 4, rl.RED)
        rl.draw_circle_lines(offset_x + px, offset_y + pz, 4, rl.WHITE)
