"""
This submodule defines abstract & base classes for UI components.
"""


from __future__ import annotations
import abc
from typing import TYPE_CHECKING

from .models import Component2DConfig

if TYPE_CHECKING:
    from ..game.state import GameState


__all__ = (
    "UiComponent",
    "UiComponent2D",
    "UiComponent3D",
)


class UiComponent(abc.ABC):
    """Defines an UI component that draws the UI from ``GameState``."""

    @abc.abstractmethod
    def draw(self, state: GameState) -> None:
        """Draws the component on the screen."""


class UiComponent2D(UiComponent):
    """Defines an UI 2D component that draws the UI from ``GameState``."""

    @property
    @abc.abstractmethod
    def default_config(self) -> Component2DConfig:
        """Provides the default 2D config for the component."""


class UiComponent3D(UiComponent):
    """Defines an UI 3D component that draws the UI from ``GameState``."""
