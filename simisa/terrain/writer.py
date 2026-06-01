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

from .. import TokenID
from ..writer import BlockWriter
from .models import *


def dump(terrain: Terrain, filepath: str, compressed: bool = False) -> None:
    """
    Write a terrain object to disk.

    This function supports both compressed/uncompressed as well as binary/text data.
    It writes the terrain data to the file at the given path.

    Args:
        terrain (Terrain): The terrain object to write.
        filepath (str): Path to the output file.
        compressed (bool): Whether to write compressed data. Defaults to False.

    Raises:
        TypeError: If `terrain` is not a Terrain object.
        TypeError: If `filepath` is not a string.
        TypeError: If `compressed` is not a bool.
        OSError: If the file cannot be written.
    """
    if not isinstance(terrain, Terrain):
        raise TypeError(f"Parameter 'terrain' must be Terrain, but got {type(terrain).__name__}")

    if not isinstance(filepath, str):
        raise TypeError(f"Parameter 'filepath' must be str, but got {type(filepath).__name__}")

    if not isinstance(compressed, bool):
        raise TypeError(f"Parameter 'compressed' must be bool, but got {type(compressed).__name__}")

    with BlockWriter.open(
        filepath,
        filetype="t",
        fileversion=6,
        is_binary=compressed,
        is_unicode=not compressed,
        is_compressed=compressed
    ) as writer:
        write_terrain(writer, terrain)


def dumps(terrain: Terrain) -> str:
    """
    Write a terrain object to a string.

    This function does not support binary or compressed data. It writes terrain
    data to a string and returns it.

    Args:
        terrain (Terrain): The terrain object to write.

    Returns:
        str: The string containing the terrain data.

    Raises:
        TypeError: If `terrain` is not a Terrain object.
    """
    if not isinstance(terrain, Terrain):
        raise TypeError(f"Parameter 'terrain' must be Terrain, but got {type(terrain).__name__}")

    terrain_text = BlockWriter.to_string(
        lambda writer: write_terrain(writer, terrain),
        filetype="t",
        fileversion=6
    )

    return terrain_text


def write_terrain(writer: BlockWriter, terrain: Terrain) -> None:
    """
    Write a terrain block to a BlockWriter.

    Writes the `terrain` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the terrain block to.
        terrain (Terrain): The terrain object to write.
    """
    with writer.sub_block(TokenID.terrain):
        with writer.sub_block(TokenID.terrain_errthreshold_scale):
            writer.write_float(terrain.terrain_errthreshold_scale)

        if terrain.terrain_water_height_offset is not None:
            write_terrain_water_height_offset(writer, terrain.terrain_water_height_offset)

        if terrain.terrain_alwaysselect_maxdist is not None:
            with writer.sub_block(TokenID.terrain_alwaysselect_maxdist):
                writer.write_float(terrain.terrain_alwaysselect_maxdist)

        if terrain.terrain_samples is not None:
            write_terrain_samples(writer, terrain.terrain_samples)

        if terrain.terrain_shaders is not None:
            write_terrain_shaders(writer, terrain.terrain_shaders)

        if terrain.terrain_patchsets is not None:
            write_terrain_patchsets(writer, terrain.terrain_patchsets)


def write_terrain_water_height_offset(writer: BlockWriter, offset: TerrainWaterHeightOffset) -> None:
    """
    Write a terrain water height offset block to a BlockWriter.

    Writes the `terrain_water_height_offset` sub-block.

    Args:
        writer (BlockWriter): Writer to write the terrain water height offset block to.
        offset (TerrainWaterHeightOffset): The terrain water height offset object to write.
    """
    if not isinstance(offset, TerrainWaterHeightOffset):
        raise TypeError(f"Terrain property 'terrain_water_height_offset' must be TerrainWaterHeightOffset, but got {type(offset).__name__}")

    with writer.sub_block(TokenID.terrain_water_height_offset):
        if offset.sw is not None:
            writer.write_float(offset.sw)

        if offset.se is not None:
            writer.write_float(offset.se)

        if offset.ne is not None:
            writer.write_float(offset.ne)
        
        if offset.nw is not None:
            writer.write_float(offset.nw)


def write_terrain_samples(writer: BlockWriter, samples: TerrainSamples) -> None:
    """
    Write terrain samples to a BlockWriter.

    Writes the `terrain_samples` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the terrain samples block to.
        samples (TerrainSamples): The terrain samples object to write.
    """
    if not isinstance(samples, TerrainSamples):
        raise TypeError(f"Terrain property 'terrain_samples' must be TerrainSamples, but got {type(samples).__name__}")

    with writer.sub_block(TokenID.terrain_samples):
        if samples.terrain_nsamples is not None:
            with writer.sub_block(TokenID.terrain_nsamples):
                writer.write_int(samples.terrain_nsamples)
        
        if samples.terrain_sample_rotation is not None:
            with writer.sub_block(TokenID.terrain_sample_rotation):
                writer.write_float(samples.terrain_sample_rotation)
        
        if samples.terrain_sample_floor is not None:
            with writer.sub_block(TokenID.terrain_sample_floor):
                writer.write_float(samples.terrain_sample_floor)
        
        if samples.terrain_sample_scale is not None:
            with writer.sub_block(TokenID.terrain_sample_scale):
                writer.write_float(samples.terrain_sample_scale)
        
        if samples.terrain_sample_size is not None:
            with writer.sub_block(TokenID.terrain_sample_size):
                writer.write_float(samples.terrain_sample_size)
        
        if samples.terrain_sample_ybuffer is not None:
            with writer.sub_block(TokenID.terrain_sample_ybuffer):
                writer.write_string(samples.terrain_sample_ybuffer)
        
        if samples.terrain_sample_ebuffer is not None:
            with writer.sub_block(TokenID.terrain_sample_ebuffer):
                writer.write_string(samples.terrain_sample_ebuffer)
        
        if samples.terrain_sample_nbuffer is not None:
            with writer.sub_block(TokenID.terrain_sample_nbuffer):
                writer.write_string(samples.terrain_sample_nbuffer)


def write_terrain_shaders(writer: BlockWriter, shaders: List[TerrainShader]) -> None:
    """
    Write terrain shaders to a BlockWriter.

    Writes the `terrain_shaders` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the terrain shaders block to.
        shaders (List[TerrainShader]): List of terrain shader objects to write.
    """
    for shader in shaders:
        if not isinstance(shader, TerrainShader):
            raise TypeError(f"Terrain property 'terrain_shaders' must contain TerrainShader objects, but got {type(shader).__name__}")

    with writer.sub_block(TokenID.terrain_shaders):
        writer.write_count(len(shaders))

        for shader in shaders:
            with writer.sub_block(TokenID.terrain_shader):
                writer.write_string(shader.shader_name)

                if shader.terrain_texslots:
                    write_terrain_texslots(writer, shader.terrain_texslots)
                
                if shader.terrain_uvcalcs:
                    write_terrain_uvcalcs(writer, shader.terrain_uvcalcs)


def write_terrain_texslots(writer: BlockWriter, texslots: List[TerrainTexslot]) -> None:
    """
    Write terrain texture slots to a BlockWriter.

    Writes the `terrain_texslots` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the terrain texture slots block to.
        texslots (List[TerrainTexslot]): List of terrain texture slot objects to write.
    """
    for texslot in texslots:
        if not isinstance(texslot, TerrainTexslot):
            raise TypeError(f"TerrainShader property 'terrain_texslots' must contain TerrainTexslot objects, but got {type(texslot).__name__}")

    with writer.sub_block(TokenID.terrain_texslots):
        writer.write_count(len(texslots))

        for texslot in texslots:
            with writer.sub_block(TokenID.terrain_texslot):
                writer.write_string(texslot.filename)
                writer.write_int(texslot.a)
                writer.write_int(texslot.b)


def write_terrain_uvcalcs(writer: BlockWriter, uvcalcs: List[TerrainUVCalc]) -> None:
    """
    Write terrain UV calculations to a BlockWriter.

    Writes the `terrain_uvcalcs` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the terrain UV calculations block to.
        uvcalcs (List[TerrainUVCalc]): List of terrain UV calculation objects to write.
    """
    for uvcalc in uvcalcs:
        if not isinstance(uvcalc, TerrainUVCalc):
            raise TypeError(f"TerrainShader property 'terrain_uvcalcs' must contain TerrainUVCalc objects, but got {type(uvcalc).__name__}")

    with writer.sub_block(TokenID.terrain_uvcalcs):
        writer.write_count(len(uvcalcs))

        for uvcalc in uvcalcs:
            with writer.sub_block(TokenID.terrain_uvcalc):
                writer.write_int(uvcalc.a)
                writer.write_int(uvcalc.b)
                writer.write_int(uvcalc.c)
                writer.write_float(float(uvcalc.d))


def write_terrain_patchsets(writer: BlockWriter, patchsets: List[TerrainPatchset]) -> None:
    """
    Write terrain patchsets to a BlockWriter.

    Writes the `terrain_patchsets` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the terrain patchsets block to.
        patchsets (List[TerrainPatchset]): List of terrain patchset objects to write.
    """
    for patchset in patchsets:
        if not isinstance(patchset, TerrainPatchset):
            raise TypeError(f"Terrain property 'terrain_patchsets' must contain TerrainPatchset objects, but got {type(patchset).__name__}")

    with writer.sub_block(TokenID.terrain_patchsets):
        writer.write_count(len(patchsets))

        for patchset in patchsets:
            with writer.sub_block(TokenID.terrain_patchset):
                with writer.sub_block(TokenID.terrain_patchset_distance):
                    writer.write_int(patchset.terrain_patchset_distance)
                
                with writer.sub_block(TokenID.terrain_patchset_npatches):
                    writer.write_int(patchset.terrain_patchset_npatches)
                
                write_terrain_patchset_patches(writer, patchset.terrain_patchset_patches)


def write_terrain_patchset_patches(writer: BlockWriter, patches: List[TerrainPatchsetPatch]) -> None:
    """
    Write terrain patchset patches to a BlockWriter.

    Writes the `terrain_patchset_patches` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the terrain patchset patches block to.
        patches (List[TerrainPatchsetPatch]): List of terrain patchset patch objects to write.
    """
    for patch in patches:
        if not isinstance(patch, TerrainPatchsetPatch):
            raise TypeError(f"TerrainPatchset property 'patches' must contain TerrainPatchsetPatch objects, but got {type(patch).__name__}")

    with writer.sub_block(TokenID.terrain_patchset_patches):
        for patch in patches:
            with writer.sub_block(TokenID.terrain_patchset_patch):
                writer.write_flags(patch.flags)
                writer.write_float(patch.center_x)
                writer.write_float(patch.average_y)
                writer.write_float(patch.center_z)
                writer.write_float(patch.factor_y)
                writer.write_float(patch.range_y)
                writer.write_float(patch.radius_m)
                writer.write_int(patch.shader_index)
                writer.write_float(patch.x)
                writer.write_float(patch.y)
                writer.write_float(patch.w)
                writer.write_float(patch.b)
                writer.write_float(patch.c)
                writer.write_float(patch.h)
                writer.write_float(patch.error_bias)