# Way
A 3D first-person maze game built with Python and Raylib.

## Description
In "Way", you are lost in a procedural maze. Your goal is to find the gold pillar (the destination) without a map. You only have a compass and a toggleable minimap to guide you.

## Features
- **Procedural Maze Generation:** A fresh 21x21 maze is generated using the Recursive Backtracker (Randomized DFS) algorithm every session.
- **Optimized Level Design:** Uses Breadth-First Search (BFS) to place the spawn and destination at the two farthest points in the maze.
- **3D World:**
    - Textured brick walls.
    - Tiled grass ground.
    - 3D Camera with first-person movement.
- **Navigation Aids:**
    - **Compass:** Real-time 2D compass on the HUD indicating your current heading (N, S, E, W).
    - **Minimap:** Toggleable (Press [M]) bottom-right map showing maze layout, player orientation, and the goal.
- **Gameplay Loop:** Random spawn -> Exploration -> Goal Reached -> Win Screen -> Restart Mechanism (Press [ENTER] or [R]).

## Controls
- **Up/Down Arrows:** Move forward/backward.
- **Left/Right Arrows:** Rotate camera.
- **[M]:** Toggle Minimap.
- **[ENTER] or [R]:** Play Again (when on the win screen).

## How to Run
Ensure you have `uv` installed, then run:
```bash
uv run main.py
```
