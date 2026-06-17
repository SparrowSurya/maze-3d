# The Way Out
A 3D strategic puzzle-solving game built with Python and Raylib.

## Description
In "The Way Out", the maze is more than just a path; it is a strategic puzzle. Players must navigate a procedural environment using a combination of traditional exploration and tactical resource management. By using tools like the Axe to manipulate the environment and the Minimap to plan routes, players transform a simple maze into a calculated navigation challenge.

## Features
- **Procedural Maze Generation:** Supports 5 distinct algorithms (Recursive Backtracker, Prim's, Kruskal's, Binary Tree, and Sidewinder).
- **Optimized Level Design:** Uses BFS to place the spawn and destination at the farthest possible points.
- **3D World:**
    - **Thin Wall Geometry:** Walls are rendered as central pillars with thin connecting slices, creating a less cramped and more detailed environment.
    - **Scaled Grid System:** Logical maze cells are mapped to a larger world area based on a configurable scale, creating wider corridors and improved spatial depth.
    - Textured walls and ground.
    - 3D Camera with First-Person and Top-Down view modes.
- **Navigation Aids:**
    - **Compass:** Real-time heading indicator.
    - **Minimap:** Opaque, toggleable map showing maze layout, player orientation, goal, and item locations.
    - **Crosshair:** Central red dot for precise navigation and raycast targeting.
- **Strategic Mechanics:**
    - **Axe & Wall Destruction:** Collectible tool used for 3D raycast-based wall removal (non-boundary only). Highlights the targeted logical cell in red when holding [X] (requires Axe).
- **Gameplay Loop:** Menu State -> Random spawn -> Resource Collection -> Strategic Exploration -> Goal Reached -> Win Screen.

## Technical Stack
- **Language:** Python 3.12
- **Graphics Library:** Raylib (via `pyray` bindings)
- **Package Manager:** `uv`
- **Linting & Formatting:** `ruff`
- **Type Checking:** `pyright` (Strict Mode) - MUST be run for verification after every change.
- **Quick:** use `Makefile` to lint, format and typecheck.

## Project Structure
- `way/`: Core package.
    - `maze/`: Procedural generation and graph analysis.
    - `game/`: Game orchestration, state management, and main loop.
    - `scene/`: Scene management and individual game screens (Menu, Play, End).
    - `player.py`: Camera management and collision physics.
    - `asset.py`: Centralized asset and scene management delegates.
    - `main.py`: Package entry point.
- `assets/`: Game textures (brick and grass).
- `main.py`: Root entry point for `uv run`.

## Code Quality
- Always use `pyray` provided class for defining `raylib` C like constant values.
- Always provide documentation to class, methods and functions.
- Always declare imports at top in groups: builtin, 3rd party and project pkg import.
- Do not use `# type: ignore` if type checking or linitng do not shows any error.
- Do not use import statements inside functions or methods.
- Do not provide documentation on class method or function which are overloading or are adhering to `Protocol` execpt parent protocol class.

## Always
- When providing code updates, only modify the specific functions or blocks requested. Do not make unprompted rewrites or overwrite any manual changes I have already made to the code.


## Controls
- `Up/Down Arrows`: Move forward/backward.
- `Left/Right Arrows`: Rotate camera.
- `[SPACE]`: Jump.
- `[M]`: Toggle Minimap.
- `[SHIFT + V]`: Toggle View Mode (First Person / Top Down).
- `[X]`: Hold to highlight the targeted wall (turns red if destructible and holding Axe).
- `[CTRL + X]`: Destroy the highlighted wall (requires Axe).
- `[SHIFT + ENTER]`: Return to Main Menu for algorithm re-selection.
- `[ENTER] or [R]`: Return to Menu (when on the win screen).
- `[1-5]`: Select Algorithm (in the Main Menu).

## How to Run
```bash
uv run main.py
```
