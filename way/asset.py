"""
This modules provide the asset related classes.
"""

from __future__ import annotations
import pathlib
from enum import StrEnum, auto
from dataclasses import dataclass, field

import pyray as rl


__all__ = (
    "Asset",
    "AssetType",
    "AssetManager",
)


@dataclass
class Asset:
    """Describes an asset in the game."""

    texture: rl.Texture
    model: rl.Model

    BASE_PATH: pathlib.Path = field(init=False, default=pathlib.Path("assets", "texture"))

    @classmethod
    def create(
        cls,
        name: str,
        mesh: rl.Mesh,
        wrap: int | rl.TextureWrap | None = None,
        material: int | None = None,
    ) -> Asset:
        """Loads the texture from name with 3d model.."""
        texture = rl.load_texture(str(cls.BASE_PATH / name))
        model = rl.load_model_from_mesh(mesh)

        if wrap is not None:
            rl.set_texture_wrap(texture, wrap)

        if material is not None:
            rl.set_material_texture(model.materials[0], material, texture)

        return cls(texture, model)

    def unload(self) -> None:
        """Unloads the asset resources."""
        rl.unload_texture(self.texture)
        rl.unload_model(self.model)


class AssetType(StrEnum):
    """Asset type category."""

    WALL = auto()
    GRASS = auto()


@dataclass(slots=True)
class AssetManager:
    """Manages the assets in the game."""

    data: dict[AssetType, Asset] = field(init=False, default_factory=dict)
    """Contains runtime assets."""

    def load_asset(
        self,
        name: str,
        type: AssetType,
        mesh: rl.Mesh,
        wrap: int | rl.TextureWrap | None = None,
        material: int | None = None,
    ) -> Asset:
        """Loads an asset."""
        asset = self.data.get(type)
        if asset is None:
            self.data[type] = asset = Asset.create(name, mesh, wrap, material)
        return asset

    def get_asset(self, type: AssetType) -> Asset | None:
        """Reads and asset"""
        return self.data.get(type, None)

    def unload_all(self) -> None:
        """Unloads all assets."""
        for asset in self.data.values():
            asset.unload()
        self.data.clear()
