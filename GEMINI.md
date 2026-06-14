# Way
A 3D first-person maze game built with Python and Raylib.

## Description
In "Way", you are lost in a procedural maze. Your goal is to find the gold pillar (the destination) without a map. You only have a compass and a toggleable minimap to guide you.

## Features
- **Procedural Maze Generation:** Supports 5 distinct algorithms (Recursive Backtracker, Prim's, Kruskal's, Binary Tree, and Sidewinder), randomly selected for each game to provide maximum variety.
- **Optimized Level Design:** Uses Breadth-First Search (BFS) to place the spawn and destination at the two farthest points in the maze.
- **3D World:**
    - Textured brick walls.
    - Tiled grass ground.
    - 3D Camera with first-person movement.
- **Health System:** A visual health bar on the HUD.
- **Navigation Aids:**
    - **Compass:** Real-time 2D compass on the HUD indicating your current heading.
    - **Minimap:** Toggleable (Press [M]) bottom-right map showing maze layout, player orientation, goal, and axe location.
    - **Crosshair:** A red dot in the center of the screen for precise navigation and targeting.
- **Axe & Wall Destruction:** 
    - **Collectible Axe:** A floating blue cube that can be used once to destroy a wall.
    - **Targeting:** Precise 3D raycasting to identify walls.
    - **Safety:** Boundary walls are protected and cannot be destroyed.
- **Gun & Shooting:**
    - **Collectible Gun:** A floating black cube.
    - **Shooting:** Shoot yellow spheres that collide with walls.
- **Gameplay Loop:** Menu State (Select Algorithm) -> Random spawn -> Exploration & Collection -> Goal Reached -> Win Screen -> Restart Mechanism.

## Technical Stack
- **Language:** Python 3.12
- **Graphics Library:** Raylib (via `pyray` bindings)
- **Package Manager:** `uv`
- **Linting & Formatting:** `ruff`
- **Type Checking:** `pyright` (Strict Mode)

## Project Structure
- `src/way/`: Core package.
    - `maze.py`: Procedural generation and graph analysis.
    - `player.py`: Camera management and collision physics.
    - `game.py`: Main game orchestration and rendering.
    - `main.py`: Package entry point.
- `assets/`: Game textures (brick and grass).
- `main.py`: Root entry point for `uv run`.

## Controls
- **Up/Down Arrows:** Move forward/backward.
- **Left/Right Arrows:** Rotate camera.
- **[W]:** Jump.
- **[SPACE]:** Shoot Bullet (requires Gun).
- **[M]:** Toggle Minimap.
- **[X]:** Hold to highlight the targeted wall (turns red).
- **[CTRL + X]:** Destroy the highlighted wall (requires Axe).
- **[SHIFT + R]:** Return to Main Menu for algorithm re-selection.
- **[ENTER] or [R]:** Return to Menu (when on the win screen).
- **[1-5]:** Select Algorithm (in the Main Menu).

## How to Run
```bash
uv run main.py
```
