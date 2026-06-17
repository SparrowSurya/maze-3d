"""
This submodule defines abstract & base classes for UI components.
"""


from __future__ import annotations
import abc
from typing import TYPE_CHECKING, override

from .models import Component2DConfig, Component3DConfig

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "UiComponent",
    "CofigurableComponent",
    "UiComponent2D",
    "UiComponent3D",
)


class UiComponent(abc.ABC):
    """
    Defines an UI component lifecycle that draws the UI from ``GameState``.

    A component is a drawable+updatable entity in the game. It provides lifecycle methods
    for initilization, draw+update, cleanup.
    """

    @abc.abstractmethod
    def init(self, state: GameState) -> None:
        """Initializes the component."""

    @abc.abstractmethod
    def draw(self, state: GameState) -> None:
        """Draws the component on the screen."""

    @abc.abstractmethod
    def update(self, state: GameState, dt: float) -> None:
        """Updates the component."""

    @abc.abstractmethod
    def clean(self, state: GameState) -> None:
        """Performs component cleanup."""


class CofigurableComponent[Cfg](UiComponent):
    """Defines an config base UI component that draws the UI from ``GameState``."""

    config: Cfg

    def __init__(self, config: Cfg | None = None) -> None:
        self.config = config or self.default_config

    @property
    @abc.abstractmethod
    def default_config(self) -> Cfg:
        """Provides the default config for the component."""

    @override
    def init(self, state: GameState) -> None:
        pass

    @override
    def draw(self, state: GameState) -> None:
        pass

    @override
    def update(self, state: GameState, dt: float) -> None:
        pass

    @override
    def clean(self, state: GameState) -> None:
        pass


class UiComponent2D[Cfg2D: Component2DConfig](CofigurableComponent[Cfg2D]):
    """Defines a configurable UI 2D component that draws the UI from ``GameState``."""


class UiComponent3D[Cfg3D: Component3DConfig](CofigurableComponent[Cfg3D]):
    """Defines a configurable UI 3D component that draws the UI from ``GameState``."""
