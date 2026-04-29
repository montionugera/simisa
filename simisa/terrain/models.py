"""
This file is part of Simisa.

Copyright (C) 2026 Peter Grønbæk Andersen <peter@grnbk.io>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TerrainWaterHeightOffset:
    sw: Optional[float] = None
    se: Optional[float] = None
    ne: Optional[float] = None
    nw: Optional[float] = None

    def __repr__(self):
        return (
            f"TerrainWaterHeightOffset("
            f"sw={self.sw}, se={self.se}, "
            f"ne={self.ne}, nw={self.nw})"
        )


@dataclass
class TerrainSamples:
    terrain_nsamples: Optional[int] = None
    terrain_sample_rotation: Optional[float] = None
    terrain_sample_floor: Optional[float] = None
    terrain_sample_scale: Optional[float] = None
    terrain_sample_size: Optional[float] = None
    terrain_sample_ybuffer: Optional[str] = None
    terrain_sample_ebuffer: Optional[str] = None
    terrain_sample_nbuffer: Optional[str] = None

    def __repr__(self):
        return (
            "TerrainSamples("
            f"nsamples={self.terrain_nsamples}, "
            f"rotation={self.terrain_sample_rotation}, "
            f"floor={self.terrain_sample_floor}, "
            f"scale={self.terrain_sample_scale}, "
            f"size={self.terrain_sample_size})"
        )


@dataclass
class TerrainTexslot:
    filename: str
    a: int
    b: int

    def __repr__(self):
        return (
            f"TerrainTexslot("
            f"filename='{self.filename}', a={self.a}, b={self.b})"
        )


@dataclass
class TerrainUVCalc:
    a: int
    b: int
    c: int
    d: int

    def __repr__(self):
        return (
            f"TerrainUVCalc(a={self.a}, b={self.b}, "
            f"c={self.c}, d={self.d})"
        )


@dataclass
class TerrainShader:
    shader_name: str
    terrain_texslots: List[TerrainTexslot]
    terrain_uvcalcs: List[TerrainUVCalc]

    def __repr__(self):
        return (
            "TerrainShader("
            f"name='{self.shader_name}', "
            f"texslots={len(self.terrain_texslots)}, "
            f"uvcalcs={len(self.terrain_uvcalcs)})"
        )


@dataclass
class TerrainPatchsetPatch:
    flags: int
    center_x: float
    center_z: float
    average_y: float
    range_y: float
    factor_y: float
    shader_index: int
    error_bias: float
    x: float
    y: float
    w: float
    h: float
    b: float
    c: float
    radius_m: float

    @property
    def water_enabled(self) -> bool:
        return (self.flags & 0xC0) != 0

    @property
    def drawing_enabled(self) -> bool:
        return (self.flags & 1) == 0

    def __repr__(self):
        return (
            "TerrainPatchsetPatch("
            f"flags={self.flags}, "
            f"center=({self.center_x}, {self.center_z}), "
            f"radius={self.radius_m}, "
            f"shader_index={self.shader_index})"
        )


@dataclass
class TerrainPatchset:
    terrain_patchset_distance: int
    terrain_patchset_npatches: int
    terrain_patchset_patches: List[TerrainPatchsetPatch]

    def get_patch(self, x: int, z: int) -> TerrainPatchsetPatch:
        return self.terrain_patchset_patches[
            z * self.terrain_patchset_npatches + x
        ]

    def __repr__(self):
        return (
            "TerrainPatchset("
            f"distance={self.terrain_patchset_distance}, "
            f"npatches={self.terrain_patchset_npatches})"
        )


@dataclass
class Terrain:
    terrain_errthreshold_scale: float = 1.0
    terrain_water_height_offset: Optional[TerrainWaterHeightOffset] = None
    terrain_alwaysselect_maxdist: Optional[float] = None
    terrain_samples: Optional[TerrainSamples] = None
    terrain_shaders: Optional[List[TerrainShader]] = None
    terrain_patchsets: Optional[List[TerrainPatchset]] = None

    def __repr__(self):
        return (
            "Terrain("
            f"err_scale={self.terrain_errthreshold_scale}, "
            f"shaders={len(self.terrain_shaders or [])}, "
            f"patchsets={len(self.terrain_patchsets or [])})"
        )
