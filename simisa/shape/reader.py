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
        texture_filter_names = read_texture_filter_names(shape_block)
        points = read_points(shape_block)
        uv_points = read_uv_points(shape_block)
        normals = read_normals(shape_block)
        sort_vectors = read_sort_vectors(shape_block)
        colours = read_colours(shape_block)
        matrices = read_matrices(shape_block)
        images: List[str] = []
        textures: List[Texture] = []
        light_materials: List[LightMaterial] = []
        light_model_cfgs: List[LightModelCfg] = []
        vtx_states: List[VtxState] = []
        prim_states: List[PrimState] = []
        lod_controls: List[LodControl] = []
        animations: List[Animation] = []

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


def read_texture_filter_names(reader: BlockReader) -> List[str]:

    with reader.sub_block(TokenID.texture_filter_names) as texture_filter_names_block:
        named_filter_modes: List[str] = []
        count = texture_filter_names_block.read_int()
        
        for named_filter_mode_block in texture_filter_names_block:
            named_filter_mode = named_filter_mode_block.read_string()
            named_filter_modes.append(named_filter_mode)

        texture_filter_names_block.verify_count(count, len(named_filter_modes))

        return named_filter_modes


def read_points(reader: BlockReader) -> List[Point]:

    with reader.sub_block(TokenID.points) as points_block:
        points: List[Point] = []
        count = points_block.read_int()
        
        for point_block in points_block:
            point = read_point(point_block)
            points.append(point)

        points_block.verify_count(count, len(points))

        return points


def read_point(reader: BlockReader) -> Point:

    reader.verify_id(TokenID.point)

    x = reader.read_float()
    y = reader.read_float()
    z = reader.read_float()

    return Point(x, y, z)


def read_uv_points(reader: BlockReader) -> List[UVPoint]:

    with reader.sub_block(TokenID.uv_points) as uv_points_block:
        uv_points: List[UVPoint] = []
        count = uv_points_block.read_int()
        
        for uv_point_block in uv_points_block:
            uv_point = read_uv_point(uv_point_block)
            uv_points.append(uv_point)

        uv_points_block.verify_count(count, len(uv_points))

        return uv_points


def read_uv_point(reader: BlockReader) -> UVPoint:

    reader.verify_id(TokenID.uv_point)

    u = reader.read_float()
    v = reader.read_float()

    return UVPoint(u, v)


def read_normals(reader: BlockReader) -> List[Vector]:

    with reader.sub_block(TokenID.normals) as normals_block:
        normals: List[Vector] = []
        count = normals_block.read_int()
        
        for vector_block in normals_block:
            vector = read_vector_item(vector_block)
            normals.append(vector)

        normals_block.verify_count(count, len(normals))

        return normals


def read_vector_item(reader: BlockReader) -> Vector:

    reader.verify_id(TokenID.vector)

    x = reader.read_float()
    y = reader.read_float()
    z = reader.read_float()

    return Vector(x, y, z)


def read_sort_vectors(reader: BlockReader) -> List[Vector]:

    with reader.sub_block(TokenID.sort_vectors) as sort_vectors_block:
        sort_vectors: List[Vector] = []
        count = sort_vectors_block.read_int()
        
        for vector_block in sort_vectors_block:
            vector = read_vector_item(vector_block)
            sort_vectors.append(vector)

        sort_vectors_block.verify_count(count, len(sort_vectors))

        return sort_vectors


def read_colours(reader: BlockReader) -> List[Colour]:

    with reader.sub_block(TokenID.colours) as colours_block:
        colours: List[Colour] = []
        count = colours_block.read_int()
        
        for colour_block in colours_block:
            colour = read_colour(colour_block)
            colours.append(colour)

        colours_block.verify_count(count, len(colours))

        return colours


def read_colour(reader: BlockReader) -> Colour:

    reader.verify_id(TokenID.colour)

    a = reader.read_float()
    r = reader.read_float()
    g = reader.read_float()
    b = reader.read_float()

    return Colour(a, r, g, b)


def read_matrices(reader: BlockReader) -> List[Matrix]:

    with reader.sub_block(TokenID.matrices) as matrices_block:
        matrices: List[Matrix] = []
        count = matrices_block.read_int()
        
        for matrix_block in matrices_block:
            matrix = read_matrix(matrix_block)
            matrices.append(matrix)

        matrices_block.verify_count(count, len(matrices))

        return matrices


def read_matrix(reader: BlockReader) -> Matrix:

    reader.verify_id(TokenID.matrix)

    name = reader.label
    ax = reader.read_float()
    ay = reader.read_float()
    az = reader.read_float()
    bx = reader.read_float()
    by = reader.read_float()
    bz = reader.read_float()
    cx = reader.read_float()
    cy = reader.read_float()
    cz = reader.read_float()
    dx = reader.read_float()
    dy = reader.read_float()
    dz = reader.read_float()

    return Matrix(
        name,
        ax, ay, az,
        bx, by, bz,
        cx, cy, cz,
        dx, dy, dz
    )