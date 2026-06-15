# The Way Out
A 3D strategic puzzle-solving game built with Python and Raylib.

## Description
In "The Way Out", the maze is more than just a path; it is a strategic puzzle. Players must navigate a procedural environment using a combination of traditional exploration and tactical resource management. By using tools like the Axe to manipulate the environment and the Minimap to plan routes, players transform a simple maze into a calculated navigation challenge.

## Features
- **Procedural Maze Generation:** Supports 5 distinct algorithms (Recursive Backtracker, Prim's, Kruskal's, Binary Tree, and Sidewinder), randomly selected for each game.
- **Optimized Level Design:** Uses BFS to place the spawn and destination at the farthest possible points.
- **3D World:**
    - Textured walls and ground.
    - 3D Camera with first-person movement.
- **Navigation Aids:**
    - **Compass:** Real-time heading indicator.
    - **Minimap:** Opaque, toggleable map showing maze layout, player orientation, goal, and item locations.
    - **Crosshair:** Central red dot for precise navigation and raycast targeting.
- **Strategic Mechanics:** 
    - **Axe & Wall Destruction:** Collectible tool used for 3D raycast-based wall removal (non-boundary only).
- **Gameplay Loop:** Menu State -> Random spawn -> Resource Collection -> Strategic Exploration -> Goal Reached -> Win Screen.

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
- **[SPACE]:** Jump.
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