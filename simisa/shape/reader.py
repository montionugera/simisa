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

from typing import List

from .. import TokenID, Units
from ..reader import BlockReader
from .models import *


def load(filepath: str) -> Shape:
    with BlockReader.open(filepath) as reader:
        return read_shape(reader)


def loads(shape_string: str) -> Shape:
    reader = BlockReader.from_string(shape_string)
    return read_shape(reader)


def read_shape(reader: BlockReader) -> Shape:

    with reader.sub_block(TokenID.shape):

        shape_header = read_shape_header(reader)

        volumes: List[VolumeSphere] = []
        shader_names: List[str] = []
        texture_filter_names: List[str] = []
        points: List[Point] = []
        uv_points: List[UVPoint] = []
        normals: List[Vector] = []
        sort_vectors: List[Vector] = []
        colours: List[Colour] = []
        matrices: List[Matrix] = []
        images: List[str] = []
        textures: List[Texture] = []
        light_materials: List[LightMaterial] = []
        light_model_cfgs: List[LightModelCfg] = []
        vtx_states: List[VtxState] = []
        prim_states: List[PrimState] = []
        lod_controls: List[LodControl] = []
        animations: List[Animation] = []

        handlers = {
            #TokenID.volume_sphere: lambda b: volumes.append(read_volume_sphere(b)),
            #TokenID.shader_name: lambda b: shader_names.append(b.read_string()),
            #TokenID.texture_filter_name: lambda b: texture_filter_names.append(b.read_string()),
            #TokenID.matrix: lambda b: matrices.append(read_matrix(b)),
            #TokenID.texture: lambda b: textures.append(read_texture(b)),
        }

        for block in reader:
            handler = handlers.get(block.id)

            if handler:
                handler(block)
            else:
                block.skip()

        return Shape(
            shape_header,
            volumes,
            shader_names,
            texture_filter_names,
            points,
            uv_points,
            normals,
            sort_vectors,
            colours,
            matrices,
            images,
            textures,
            light_materials,
            light_model_cfgs,
            vtx_states,
            prim_states,
            lod_controls,
            animations,
        )


def read_shape_header(reader: BlockReader) -> ShapeHeader:

    with reader.block(TokenID.shape_header):

        flags1 = reader.read_flags()
        flags2 = reader.read_flags()

        return ShapeHeader(flags1, flags2)


def read_volume_sphere(reader: BlockReader) -> VolumeSphere:

    with reader.block(TokenID.volume_sphere):

        radius = reader.read_float()
        vector = read_vector()

        return VolumeSphere(radius, vector)


def read_vector(reader: BlockReader) -> Vector:

    with reader.block(TokenID.vector):

        x = reader.read_float()
        y = reader.read_float()
        z = reader.read_float()

        return Vector(x, y, z)

