# The Way Out
A 3D strategic puzzle-solving game built with Python and Raylib.

## Description
In "The Way Out", you are challenged to navigate complex procedural mazes using a combination of logic, spatial awareness, and strategic resource management. Instead of just finding an exit, you must calculate the best path, manage your limited tools (like the wall-breaking Axe), and maintain your navigation in a world where every move matters.

## Features
- **Procedural Maze Generation:** Supports 5 distinct algorithms (Recursive Backtracker, Prim's, Kruskal's, Binary Tree, and Sidewinder).
- **Optimized Level Design:** Uses Breadth-First Search (BFS) to place the spawn and destination at the two farthest points in the maze, ensuring a maximum challenge for every run.
- **High-Performance 3D World:**
    - **Chunked & Instanced Rendering:** The maze is partitioned into spatial chunks for efficient view-cone culling. It utilizes a custom vertex shader for instanced rendering, allowing for smooth performance even in large environments.
    - **Thin Wall Geometry:** Walls are rendered as central pillars with thin slices connecting neighbors, providing a modern and spacious aesthetic.
    - **Scaled Grid System:** Logical maze cells are scaled to a larger world area, creating wide corridors and realistic wall proportions.
    - Textured walls and ground with animated collectables.
- **Strategic Mechanics:**
    - **Axe & Wall Destruction:** Collect the Axe to gain the ability to strategically break non-boundary walls.
    - **Targeting System:** Hold [X] to highlight the targeted logical cell; it turns red if the wall is destructible and you have an Axe charge.
- **Navigation Aids:**
    - **Minimap:** Toggleable (Press [M]) dynamic map that stays centered on the player, showing the layout, goal, and item locations.
    - **Compass & Crosshair:** Real-time magnetic compass and a dynamic crosshair that provides feedback during targeting.
- **Gameplay Loop:** Select Algorithm -> Strategic Spawn -> Resource Collection -> Calculated Exploration -> Goal Reached -> Success.

## Architecture
The project follows a delegated manager pattern:
- **AssetManager:** Centralized loading and automated unloading of textures and models.
- **SceneManager:** Handles scene transitions and storage.
- **GameManager:** Orchestrates high-level delegates.
- **Component-Based UI:** Modular 2D/3D components (Minimap, Compass, MazeView) for clean separation of concerns.

## Controls
- **Up/Down Arrows:** Move forward/backward.
- **Left/Right Arrows:** Rotate camera.
- **[SPACE]:** Jump.
- **[M]:** Toggle Minimap.
- **[SHIFT + V]:** Toggle View Mode (First Person / Top Down).
- **[X]:** Hold to highlight the targeted wall (turns red if destructible and holding Axe).
- **[CTRL + X]:** Destroy the highlighted wall (consumes 1 Axe charge).
- **[SHIFT + ENTER]:** Return to Main Menu for algorithm re-selection.
- **[ENTER] or [R]:** Return to Menu (when on the win screen).
- **[1-5]:** Select Algorithm (in the Main Menu).

## How to Run
Ensure you have `uv` installed, then run:
```bash
uv run main.py
```
