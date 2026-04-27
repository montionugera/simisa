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

import logging
from typing import List

from .. import TokenID, Units
from ..reader import BlockReader, SimisaSubheaderError
from .models import *

logger = logging.getLogger(__name__)



def load(filepath: str) -> Shape:
    if not isinstance(filepath, str):
        raise TypeError(f"Parameter 'filepath' must be str, but got {type(filepath).__name__}")

    with BlockReader.open(filepath) as reader:

        if not reader.filetype == 's':
            raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it actually a shape?")

        return read_shape(reader)


def loads(shape_text: str) -> Shape:
    if not isinstance(shape_text, str):
        raise TypeError(f"Parameter 'shape_text' must be str, but got {type(shape_text).__name__}")

    reader = BlockReader.from_string(shape_text)

    if not reader.filetype == 's':
        raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it actually a shape?")

    return read_shape(reader)


def read_shape(reader: BlockReader) -> Shape:

    with reader.sub_block(TokenID.shape) as shape_block:
        shape_header = read_shape_header(shape_block)
        volumes = read_volumes(shape_block)
        shader_names = read_shader_names(shape_block)
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

        #for block in reader:
        #    handler = handlers.get(shape_block.id)
        #
        #    if handler:
        #        handler(shape_block)
        #    else:
        #        shape_block.skip()

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

    with reader.sub_block(TokenID.shape_header) as header_block:
        flags1 = header_block.read_flags()
        flags2 = None

        if not header_block.end_of_block():
            flags2 = header_block.read_flags()

        return ShapeHeader(flags1, flags2)


def read_volumes(reader: BlockReader) -> List[VolumeSphere]:

    with reader.sub_block(TokenID.volumes) as volumes_block:
        volume_spheres: List[VolumeSphere] = []
        count = volumes_block.read_int()
        
        for vol_sphere_block in volumes_block:
            volume_sphere = read_volume_sphere(vol_sphere_block)
            volume_spheres.append(volume_sphere)

        volumes_block.verify_count(count, len(volume_spheres))

        return volume_spheres


def read_volume_sphere(reader: BlockReader) -> VolumeSphere:

    reader.verify_id(TokenID.vol_sphere)

    vector = read_vector(reader)
    radius = reader.read_float()

    return VolumeSphere(radius, vector)


def read_vector(reader: BlockReader) -> Vector:

    with reader.sub_block(TokenID.vector) as vector_block:
        x = vector_block.read_float()
        y = vector_block.read_float()
        z = vector_block.read_float()

        return Vector(x, y, z)


def read_shader_names(reader: BlockReader) -> List[str]:

    with reader.sub_block(TokenID.shader_names) as shader_names_block:
        shader_names: List[str] = []
        count = shader_names_block.read_int()
        
        for named_shader_block in shader_names_block:
            named_shader = named_shader_block.read_string()
            shader_names.append(named_shader)

        shader_names_block.verify_count(count, len(shader_names))

        return shader_names