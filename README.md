# The Way Out
A 3D strategic puzzle-solving game built with Python and Raylib.

## Description
In "The Way Out", you are challenged to navigate complex procedural mazes using a combination of logic, spatial awareness, and strategic resource management. Instead of just finding an exit, you must calculate the best path, manage your limited tools (like the wall-breaking Axe), and maintain your survival in a world where every move matters.

## Features
- **Procedural Maze Generation:** Supports 5 distinct algorithms (Recursive Backtracker, Prim's, Kruskal's, Binary Tree, and Sidewinder), randomly selected for each game to provide maximum variety and puzzle complexity.
- **Optimized Level Design:** Uses Breadth-First Search (BFS) to place the spawn and destination at the two farthest points in the maze, ensuring a maximum challenge for every run.
- **3D World:**
    - Textured brick walls and tiled grass ground.
    - Immersive 3D Camera with first-person movement.
- **Strategic Tools:**
    - **Axe & Wall Destruction:** Find the collectible Axe to gain the ability to strategically break one non-boundary wall, creating shortcuts or escaping traps.
- **Navigation Aids:**
    - **Minimap:** Toggleable (Press [M]) opaque map showing layout, player orientation, goal, and tool locations.
    - **Compass & Crosshair:** Real-time heading and precise targeting aids.
- **Gameplay Loop:** Select Algorithm -> Strategic Spawn -> Resource Collection -> Calculated Exploration -> Goal Reached -> Success.

## Controls
- **Up/Down Arrows:** Move forward/backward.
- **Left/Right Arrows:** Rotate camera.
- **[SPACE]:** Jump.
- **[M]:** Toggle Minimap.
- **[X]:** Hold to highlight the targeted wall (turns red).
- **[CTRL + X]:** Destroy the highlighted wall (consumes 1 Axe).
- **[SHIFT + R]:** Instant re-generate maze with current algorithm.
- **[ENTER] or [R]:** Return to Menu (when on the win screen).
- **[1-5]:** Select Algorithm (in the Main Menu).

## How to Run
Ensure you have `uv` installed, then run:
```bash
uv run main.py
```