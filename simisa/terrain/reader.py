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

from .. import TokenID
from ..reader import BlockReader, SimisaSubheaderError
from .models import *

logger = logging.getLogger(__name__)



def load(filepath: str) -> Terrain:
    """
    Load and parse a terrain file from disk.

    This function supports both compressed/uncompressed as well as binary/text data.
    It opens the file at the given path, validates that it is a supported shape
    file based on its subheader, and returns a parsed Terrain object.

    Args:
        filepath (str): Path to the terrain file.

    Returns:
        Terrain: The parsed terrain object.

    Raises:
        TypeError: If `filepath` is not a string.
        SimisaHeaderError: If the data has an invalid or unrecognized SIMISA header.
        SimisaSubheaderError: If the data has an invalid or unrecognized SIMISA subheader.
        BlockReaderError: If the block reader encounters an error or malformed data.
        StfReaderError: If the STF reader encounters an error or malformed data.
        OSError: If the file cannot be opened.
    """
    if not isinstance(filepath, str):
        raise TypeError(f"Parameter 'filepath' must be str, but got {type(filepath).__name__}")

    with BlockReader.open(filepath) as reader:

        if not reader.filetype == 't':
            raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a terrain file?")

        return read_shape(reader)


def loads(terrain_text: str) -> Terrain:
    """
    Parse a shape from a string containing terrain data.

    This function does not support binary or compressed data. It reads terrain
    data from the provided string, validates that it represents a supported
    terrain file based on its subheader, and returns a parsed Terrain object.

    Args:
        terrain_text (str): String containing terrain file data.

    Returns:
        Terrain: The parsed terrain object.

    Raises:
        TypeError: If `terrain_text` is not a string.
        SimisaHeaderError: If the data has an invalid or unrecognized SIMISA header.
        SimisaSubheaderError: If the data has an invalid or unrecognized SIMISA subheader.
        BlockReaderError: If the block reader encounters an error or malformed data.
        StfReaderError: If the STF reader encounters an error or malformed data.
    """
    if not isinstance(terrain_text, str):
        raise TypeError(f"Parameter 'terrain_text' must be str, but got {type(terrain_text).__name__}")

    reader = BlockReader.from_string(terrain_text)

    if not reader.filetype == 't':
        raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a terrain file?")

    return read_terrain(reader)


def read_terrain(reader: BlockReader) -> Terrain:
    """
    Read and parse a terrain block from a BlockReader.

    Consumes the `terrain` sub-block and its child sections, returning a fully
    constructed Terrain object.

    Args:
        reader (BlockReader): Reader positioned at a terrain block.

    Returns:
        Terrain: The parsed terrain.
    """
    with reader.sub_block(TokenID.terrain) as terrain_block:
        print(terrain_block.id)
        # shape_header = read_shape_header(shape_block)
        # volumes = read_volumes(shape_block)
        # shader_names = read_shader_names(shape_block)
        # texture_filter_names = read_texture_filter_names(shape_block)
        # points = read_points(shape_block)
        # uv_points = read_uv_points(shape_block)
        # normals = read_normals(shape_block)
        # sort_vectors = read_sort_vectors(shape_block)
        # colours = read_colours(shape_block)
        # matrices = read_matrices(shape_block)
        # images = read_images(shape_block)
        # textures = read_textures(shape_block)
        # light_materials = read_light_materials(shape_block)
        # light_model_cfgs = read_light_model_cfgs(shape_block)
        # vtx_states = read_vtx_states(shape_block)
        # prim_states = read_prim_states(shape_block)
        # lod_controls = read_lod_controls(shape_block)

        # if not shape_block.end_of_block():
        #     animations = read_animations(shape_block)
        # else:
        #     animations = None

        # return Shape(
        #     shape_header=shape_header,
        #     volumes=volumes,
        #     shader_names=shader_names,
        #     texture_filter_names=texture_filter_names,
        #     points=points,
        #     uv_points=uv_points,
        #     normals=normals,
        #     sort_vectors=sort_vectors,
        #     colours=colours,
        #     matrices=matrices,
        #     images=images,
        #     textures=textures,
        #     light_materials=light_materials,
        #     light_model_cfgs=light_model_cfgs,
        #     vtx_states=vtx_states,
        #     prim_states=prim_states,
        #     lod_controls=lod_controls,
        #     animations=animations
        # )