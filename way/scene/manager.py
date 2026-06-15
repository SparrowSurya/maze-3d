"""
This submodule contains the scene manager class.
"""


from dataclasses import dataclass, field

from ..scene.protocols import GameScene, Scene
\

__all__ = (
    "SceneManager",
)


@dataclass(slots=True)
class SceneManager:
    """Manages the scene inside game."""

    data: dict[Scene, GameScene]
    """Scenes in the game associated with scene key."""

    initial: Scene
    """Initial scene in the game."""

    current: Scene = field(init=False)
    """Current scene in the game."""

    def __post_init__(self) -> None:
        self.current = self.initial

    def get_scene(self, scene: Scene) -> GameScene:
        """Provide the requested scene."""
        return self.data[scene]

    def set_scene(self, scene: Scene) -> None:
        """Sets the current scene."""
        self.current = scene

    def reset(self) -> None:
        """Resets to initial screen."""
        self.set_scene(self.initial)
