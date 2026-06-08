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
- **Navigation Aids:**
    - **Compass:** Real-time 2D compass on the HUD indicating your current heading (N, S, E, W).
    - **Minimap:** Toggleable (Press [M]) bottom-right map showing maze layout, player orientation, and the goal.
- **Gameplay Loop:** Menu State (Select Algorithm) -> Random spawn -> Exploration -> Goal Reached -> Win Screen -> Restart Mechanism.

## Controls
- **Up/Down Arrows:** Move forward/backward.
- **Left/Right Arrows:** Rotate camera.
- **[SPACE]:** Jump.
- **[M]:** Toggle Minimap.
- **[SHIFT + R]:** Instant re-generate maze with current algorithm.
- **[ENTER] or [R]:** Return to Menu (when on the win screen).
- **[1-5]:** Select Algorithm (in the Main Menu).

## How to Run
Ensure you have `uv` installed, then run:
```bash
uv run main.py
```
