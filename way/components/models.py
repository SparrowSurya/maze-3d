"""
This submocdule contains various dataclass models used by components.
"""


from __future__ import annotations
from dataclasses import dataclass

import pyray as rl


__all__ = (
    "Component2DConfig",
    "Component3DConfig",
    "Alignment",
)


@dataclass
class Component2DConfig:
    """Defines the 2D ui configuration of the comopnent."""

    align: Alignment | None = None
    """
    If pos is ``None`` then describes the position w.r.t screen.
    If pos is not ``None`` then describes the internal anchor of point w.r.t size.
    """

    pos: rl.Vector2 | None = None
    """Anchor position of the component."""

    size: rl.Vector2 | None = None
    """Size of the component. ``None`` means fullsize or undefined based on component."""

    radius: float | None = None
    """Radius of the component. ``None`` means undefined."""

    offset: rl.Vector2 = rl.Vector2(0.0, 0.0)
    """Offset from edges based on alignment."""

    padding: rl.Vector2 = rl.Vector2(0.0, 0.0)
    """
    Describes the internal padding of content in component. Padding is exclusive of
    size/radius. Padding is also the part of drawable content.
    """

    def __post_init__(self) -> None:
        assert(self.align is not None or self.pos is not None)


@dataclass
class Component3DConfig:
    """Defines the 3D ui configuration of the comopnent."""


@dataclass(slots=True)
class Alignment:
    """
    Defines the alignment of component. The ``x`` and ``y``` values are the axis whose
    values goes from ``-1`` to ``+1``.
    """

    x: float = 0.0
    y: float = 0.0

    @classmethod
    def top_left(cls) -> Alignment:
        """Alignment at the top-left corner."""
        return cls(x=-1.0, y=-1.0)

    @classmethod
    def top(cls) -> Alignment:
        """Alignment at the top-center."""
        return cls(x=0.0, y=-1.0)

    @classmethod
    def top_right(cls) -> Alignment:
        """Alignment at the top-right corner."""
        return cls(x=1.0, y=-1.0)

    @classmethod
    def left(cls) -> Alignment:
        """Alignment at the center-left."""
        return cls(x=-1.0, y=0.0)

    @classmethod
    def center(cls) -> Alignment:
        """Alignment at the center."""
        return cls(x=0.0, y=0.0)

    @classmethod
    def right(cls) -> Alignment:
        """Alignment at the center-right."""
        return cls(x=1.0, y=0.0)

    @classmethod
    def bottom_left(cls) -> Alignment:
        """Alignment at the bottom-left corner."""
        return cls(x=-1.0, y=1.0)

    @classmethod
    def bottom(cls) -> Alignment:
        """Alignment at the bottom-center."""
        return cls(x=0.0, y=1.0)

    @classmethod
    def bottom_right(cls) -> Alignment:
        """Alignment at the bottom-right corner."""
        return cls(x=1.0, y=1.0)
