# The Way Out
A 3D strategic puzzle-solving game built with Python and Raylib.

## Description
In "The Way Out", you are challenged to navigate complex procedural mazes using a combination of logic, spatial awareness, and strategic resource management. Instead of just finding an exit, you must calculate the best path, manage your limited tools (like the wall-breaking Axe), and maintain your navigation in a world where every move matters.

## Features
- **Procedural Maze Generation:** Supports 5 distinct algorithms (Recursive Backtracker, Prim's, Kruskal's, Binary Tree, and Sidewinder), selectable in the main menu to provide variety and puzzle complexity.
- **Optimized Level Design:** Uses Breadth-First Search (BFS) to place the spawn and destination at the two farthest points in the maze, ensuring a maximum challenge for every run.
- **3D World:**
    - Textured walls and ground.
    - Immersive 3D Camera with First-Person and Top-Down movement.
- **Strategic Tools:**
    - **Axe & Wall Destruction:** Find the collectible Axe to gain the ability to strategically break non-boundary walls, creating shortcuts or escaping traps.
- **Navigation Aids:**
    - **Minimap:** Toggleable (Press [M]) opaque map showing layout, player orientation, goal, and tool locations.
    - **Compass & Crosshair:** Real-time heading and precise targeting aids.
- **Gameplay Loop:** Select Algorithm -> Strategic Spawn -> Resource Collection -> Calculated Exploration -> Goal Reached -> Success.

## Architecture
The project follows a delegated manager pattern:
- **AssetManager:** Centralized loading and automated unloading of textures and models.
- **SceneManager:** Handles scene transitions and storage.
- **GameManager:** Orchestrates high-level delegates.
- **Late Initialization:** Scenes use an `init()` method to set up state after the global game state is ready, avoiding circular dependencies.

## Controls
- **Up/Down Arrows:** Move forward/backward.
- **Left/Right Arrows:** Rotate camera.
- **[SPACE]:** Jump.
- **[M]:** Toggle Minimap.
- **[SHIFT + V]:** Toggle View Mode (First Person / Top Down).
- **[X]:** Hold to highlight the targeted wall (turns red if destructible and holding Axe).
- **[CTRL + X]:** Destroy the highlighted wall (requires Axe).
- **[SHIFT + R]:** Return to Main Menu for algorithm re-selection.
- **[ENTER] or [R]:** Return to Menu (when on the win screen).
- **[1-5]:** Select Algorithm (in the Main Menu).

## How to Run
Ensure you have `uv` installed, then run:
```bash
uv run main.py
```
