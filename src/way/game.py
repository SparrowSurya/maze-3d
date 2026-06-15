import math
from enum import Enum, auto

import pyray as rl

from .maze import Algorithm, Maze, generate_maze, get_default_maze
from .player import Player, ViewMode


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    WON = auto()


class Game:
    def __init__(self) -> None:
        self.width = 800
        self.height = 600
        self.title = "The Way Out - 3D Maze Game"

        self.wall_texture: rl.Texture2D | None = None  # type: ignore
        self.wall_model: rl.Model | None = None  # type: ignore

        self.grass_texture: rl.Texture2D | None = None  # type: ignore
        self.ground_model: rl.Model | None = None  # type: ignore

        self.state = GameState.MENU
        self.selected_algo = Algorithm.DFS
        self.show_minimap = False

        # Properly type and initialize placeholders
        self.maze: Maze = Maze([])
        self.player: Player = Player(rl.Vector3(0, 0, 0), 0.0)
        self.destination: rl.Vector3 = rl.Vector3(0, 0, 0)
        self.is_won: bool = False
        self.axes_count: int = 0
        self.axe_pos: rl.Vector3 | None = None

    def init_game(self, algo: Algorithm | None = None) -> None:
        if algo:
            self.selected_algo = algo
            self.maze = generate_maze(25, 25, algorithm=algo)
        else:
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

        # Spawn Axe (collectible)
        self.axes_count = 0
        self.axe_pos = None

        # Find a suitable spot for the axe (not too close to spawn or destination)
        min_dist = max(self.maze.width, self.maze.height) / 3.0
        max_attempts = 100
        for _ in range(max_attempts):
            ax, az = self.maze.get_random_empty_cell()
            potential_axe_pos = rl.Vector3(float(ax) + 0.5, 0.5, float(az) + 0.5)
            d_spawn = rl.vector3_distance(potential_axe_pos, self.player.position)
            d_dest = rl.vector3_distance(potential_axe_pos, self.destination)
            if d_spawn > min_dist and d_dest > min_dist:
                self.axe_pos = potential_axe_pos
                break

        self.is_won = False
        self.state = GameState.PLAYING

    def run(self) -> None:
        rl.init_window(self.width, self.height, self.title)
        rl.set_target_fps(60)

        # Load Wall Assets
        self.wall_texture = rl.load_texture("assets/wall_texture.png")
        mesh_cube = rl.gen_mesh_cube(1.0, 1.0, 1.0)
        self.wall_model = rl.load_model_from_mesh(mesh_cube)
        if self.wall_model and self.wall_texture:
            rl.set_material_texture(
                self.wall_model.materials[0],
                rl.MATERIAL_MAP_DIFFUSE,  # type: ignore
                self.wall_texture,
            )

        # Load Grass Assets
        self.grass_texture = rl.load_texture("assets/grass_texture.png")
        if self.grass_texture:
            rl.set_texture_wrap(self.grass_texture, rl.TEXTURE_WRAP_REPEAT)  # type: ignore

        # We generate a generic ground model
        mesh_plane = rl.gen_mesh_plane(30.0, 30.0, 1, 1)
        self.ground_model = rl.load_model_from_mesh(mesh_plane)
        if self.ground_model and self.grass_texture:
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
        # Global Reset Shortcut: Shift + R
        is_shift = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SHIFT) or rl.is_key_down(  # type: ignore
            rl.KeyboardKey.KEY_RIGHT_SHIFT  # type: ignore
        )
        if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_R):  # type: ignore
            self.state = GameState.MENU

        if self.state == GameState.MENU:
            self.update_menu()
        elif self.state == GameState.PLAYING:
            self.player.update(delta_time, self.maze)

            # Check win condition
            dist = rl.vector3_distance(self.player.position, self.destination)
            if dist < 0.5:
                self.is_won = True
                self.state = GameState.WON

            # Check axe collection
            if self.axe_pos:
                dist_axe = rl.vector3_distance(self.player.position, self.axe_pos)
                if dist_axe < 0.8:
                    self.axes_count += 1
                    self.axe_pos = None

            # Wall Destruction Logic
            is_ctrl = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_CONTROL) or rl.is_key_down(
                rl.KeyboardKey.KEY_RIGHT_CONTROL
            )
            if self.axes_count > 0 and is_ctrl and rl.is_key_pressed(rl.KeyboardKey.KEY_X):
                target = self.get_targeted_wall()
                if target:
                    tx, tz = target
                    self.maze.grid[tz][tx] = 0
                    self.axes_count -= 1

            # Toggle minimap with M
            if rl.is_key_pressed(rl.KeyboardKey.KEY_M):  # type: ignore
                self.show_minimap = not self.show_minimap

            # Toggle view mode with Shift + V
            if is_shift and rl.is_key_pressed(rl.KeyboardKey.KEY_V):  # type: ignore
                if self.player.view_mode == ViewMode.FIRST_PERSON:
                    self.player.view_mode = ViewMode.TOP_DOWN
                else:
                    self.player.view_mode = ViewMode.FIRST_PERSON
        elif self.state == GameState.WON:
            if rl.is_key_pressed(rl.KeyboardKey.KEY_R) or rl.is_key_pressed(  # type: ignore
                rl.KeyboardKey.KEY_ENTER  # type: ignore
            ):
                self.state = GameState.MENU

    def get_targeted_wall(self) -> tuple[int, int] | None:
        # Construct ray from player position in their forward direction (yaw)
        # This works in both First Person and Top-Down modes.
        ray_origin = self.player.position
        ray_dir = rl.Vector3(
            math.sin(self.player.yaw),
            0.0,  # Aim horizontally to hit the center of wall height
            -math.cos(self.player.yaw),
        )
        ray = rl.Ray(ray_origin, ray_dir)

        closest_hit_dist = 5.0  # Max interaction range
        hit_cell = None

        px, pz = int(self.player.position.x), int(self.player.position.z)
        radius = 5
        for z in range(max(0, pz - radius), min(self.maze.height, pz + radius + 1)):
            for x in range(max(0, px - radius), min(self.maze.width, px + radius + 1)):
                if self.maze.is_wall(x, z):
                    # Boundary walls cannot be removed
                    if x == 0 or x == self.maze.width - 1 or z == 0 or z == self.maze.height - 1:
                        continue

                    box = rl.BoundingBox(
                        rl.Vector3(float(x), 0.0, float(z)),
                        rl.Vector3(float(x) + 1.0, 1.0, float(z) + 1.0),
                    )
                    collision = rl.get_ray_collision_box(ray, box)
                    if collision.hit and collision.distance < closest_hit_dist:
                        closest_hit_dist = collision.distance
                        hit_cell = (x, z)

        return hit_cell

    def update_menu(self) -> None:
        if rl.is_key_pressed(rl.KeyboardKey.KEY_ONE):  # type: ignore
            self.init_game(Algorithm.DFS)
        if rl.is_key_pressed(rl.KeyboardKey.KEY_TWO):  # type: ignore
            self.init_game(Algorithm.PRIMS)
        if rl.is_key_pressed(rl.KeyboardKey.KEY_THREE):  # type: ignore
            self.init_game(Algorithm.KRUSKALS)
        if rl.is_key_pressed(rl.KeyboardKey.KEY_FOUR):  # type: ignore
            self.init_game(Algorithm.BINARY_TREE)
        if rl.is_key_pressed(rl.KeyboardKey.KEY_FIVE):  # type: ignore
            self.init_game(Algorithm.SIDEWINDER)

    def draw(self) -> None:
        rl.begin_drawing()
        rl.clear_background(rl.SKYBLUE)

        if self.state == GameState.MENU:
            self.draw_menu()
        else:
            rl.begin_mode_3d(self.player.get_camera())

            # Draw ground model
            if self.ground_model:
                pos = rl.Vector3(self.maze.width / 2.0, 0, self.maze.height / 2.0)
                rl.draw_model(self.ground_model, pos, 1.0, rl.WHITE)

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

            # Draw player as cylinder in top-down mode
            if self.player.view_mode == ViewMode.TOP_DOWN:
                # Player position is at their feet, but base_y = 0.5.
                # rl.draw_cylinder expects start and end points.
                start_pos = rl.Vector3(self.player.position.x, 0.0, self.player.position.z)
                end_pos = rl.Vector3(
                    self.player.position.x, self.player.height, self.player.position.z
                )
                rl.draw_cylinder(
                    start_pos,
                    self.player.radius,
                    self.player.radius,
                    self.player.height,
                    16,
                    rl.RED,
                )
                # Draw a small line to indicate direction
                dir_len = 0.5
                dir_end = rl.Vector3(
                    self.player.position.x + math.sin(self.player.yaw) * dir_len,
                    self.player.height,
                    self.player.position.z - math.cos(self.player.yaw) * dir_len,
                )
                rl.draw_line_3d(end_pos, dir_end, rl.WHITE)

            # Draw axe collectible
            if self.axe_pos:
                bobbing = math.sin(rl.get_time() * 4.0) * 0.1
                axe_draw_pos = rl.Vector3(self.axe_pos.x, self.axe_pos.y + bobbing, self.axe_pos.z)
                rl.draw_cube(axe_draw_pos, 0.2, 0.2, 0.2, rl.BLUE)
                rl.draw_cube_wires(axe_draw_pos, 0.2, 0.2, 0.2, rl.DARKBLUE)

            # Targeting Highlight
            if self.axes_count > 0 and rl.is_key_down(rl.KeyboardKey.KEY_X):
                target = self.get_targeted_wall()
                if target:
                    tx, tz = target
                    highlight_pos = rl.Vector3(float(tx) + 0.5, 0.5, float(tz) + 0.5)
                    # Make the wall surface appear as red using a semi-transparent cube
                    # Increased size to 1.1 and opacity to 0.7 for better visibility from top-down
                    rl.draw_cube(highlight_pos, 1.1, 1.1, 1.1, rl.fade(rl.RED, 0.7))
                    rl.draw_cube_wires(highlight_pos, 1.1, 1.1, 1.1, rl.RED)

            rl.end_mode_3d()
            self.draw_hud()

        rl.end_drawing()

    def draw_menu(self) -> None:
        rl.draw_rectangle(0, 0, self.width, self.height, rl.fade(rl.BLACK, 0.8))
        rl.draw_text("THE WAY OUT - CHOOSE ALGORITHM", self.width // 2 - 250, 100, 30, rl.GOLD)

        algos = [
            "1. Recursive Backtracker (DFS)",
            "2. Randomized Prim's",
            "3. Randomized Kruskal's",
            "4. Binary Tree",
            "5. Sidewinder",
        ]

        for i, text in enumerate(algos):
            rl.draw_text(text, self.width // 2 - 150, 200 + i * 40, 20, rl.WHITE)

        rl.draw_text("Press [NUMBER] to Start", self.width // 2 - 120, 450, 20, rl.LIGHTGRAY)
        rl.draw_text(
            "SHIFT + R: Return to Menu from game",
            self.width // 2 - 160,
            500,
            15,
            rl.GRAY,
        )

    def draw_hud(self) -> None:
        if self.state == GameState.WON:
            rl.draw_rectangle(0, 0, self.width, self.height, rl.fade(rl.BLACK, 0.5))
            rl.draw_text(
                "YOU FOUND THE WAY OUT!", self.width // 2 - 180, self.height // 2 - 40, 30, rl.GOLD
            )
            rl.draw_text(
                "Press [ENTER] or [R] to Main Menu",
                self.width // 2 - 140,
                self.height // 2 + 10,
                15,
                rl.WHITE,
            )
        else:
            rl.draw_text(f"Algorithm: {self.selected_algo.name}", 10, 10, 20, rl.BLACK)
            rl.draw_text("Find the gold pillar!", 10, 40, 15, rl.DARKGRAY)
            rl.draw_text("Press [M] Minimap | SHIFT+V View | SHIFT+R Menu", 10, 60, 12, rl.GRAY)

            if self.axes_count > 0:
                rl.draw_text(f"Axe: {self.axes_count}", 10, 80, 15, rl.BLUE)

            # Draw a smol red dot in the center of the screen
            dot_radius = 3
            rl.draw_circle(self.width // 2, self.height // 2, dot_radius, rl.RED)

            self.draw_compass()
            if self.show_minimap:
                self.draw_minimap()

        rl.draw_fps(10, self.height - 30)

    def draw_compass(self) -> None:
        compass_x = self.width - 60
        compass_y = 60
        rl.draw_circle(compass_x, compass_y, 40, rl.LIGHTGRAY)
        rl.draw_circle_lines(compass_x, compass_y, 40, rl.DARKGRAY)

        # Needle
        needle_len = 25
        needle_end_x = compass_x + int(math.sin(self.player.yaw) * needle_len)
        needle_end_y = compass_y - int(math.cos(self.player.yaw) * needle_len)
        rl.draw_line_ex(
            rl.Vector2(float(compass_x), float(compass_y)),
            rl.Vector2(float(needle_end_x), float(needle_end_y)),
            3,
            rl.RED,
        )

        # Directions
        rl.draw_text("N", compass_x - 3, compass_y - 32, 10, rl.BLACK)
        rl.draw_text("S", compass_x - 3, compass_y + 22, 10, rl.BLACK)
        rl.draw_text("E", compass_x + 22, compass_y - 5, 10, rl.BLACK)
        rl.draw_text("W", compass_x - 32, compass_y - 5, 10, rl.BLACK)

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

        # Axe (if not collected)
        if self.axe_pos:
            ax = int(self.axe_pos.x)
            az = int(self.axe_pos.z)
            rl.draw_rectangle(
                offset_x + ax * cell_size,
                offset_y + az * cell_size,
                cell_size,
                cell_size,
                rl.BLUE,
            )

        # Player
        px = int(self.player.position.x * cell_size)
        pz = int(self.player.position.z * cell_size)

        # Player Direction (long line)
        dir_len = 12
        dx = int(math.sin(self.player.yaw) * dir_len)
        dz = -int(math.cos(self.player.yaw) * dir_len)

        rl.draw_line_ex(
            rl.Vector2(float(offset_x + px), float(offset_y + pz)),
            rl.Vector2(float(offset_x + px + dx), float(offset_y + pz + dz)),
            2,
            rl.RED,
        )

        # Draw player dot
        rl.draw_circle(offset_x + px, offset_y + pz, 4, rl.RED)
        rl.draw_circle_lines(offset_x + px, offset_y + pz, 4, rl.WHITE)

