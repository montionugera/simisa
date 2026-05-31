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

from .. import TokenID
from ..writer import BlockWriter
from .models import *


def dump(terrain: Terrain, filepath: str, compressed: bool = False) -> None:
    if not isinstance(terrain, Terrain):
        raise TypeError(f"Parameter 'terrain' must be Terrain, but got {type(terrain).__name__}")

    if not isinstance(filepath, str):
        raise TypeError(f"Parameter 'filepath' must be str, but got {type(filepath).__name__}")

    if not isinstance(compressed, bool):
        raise TypeError(f"Parameter 'compressed' must be bool, but got {type(compressed).__name__}")

    with BlockWriter.open(
        filepath,
        filetype="t",
        fileversion="0",
        is_binary=compressed,
        is_unicode=not compressed,
        is_compressed=compressed
    ) as writer:
        write_terrain(writer, terrain)


def dumps(terrain: Terrain) -> str:
    if not isinstance(terrain, Terrain):
        raise TypeError(f"Parameter 'terrain' must be Terrain, but got {type(terrain).__name__}")

    terrain_text = BlockWriter.to_string(
        lambda writer: write_terrain(writer, terrain),
        filetype="t",
        fileversion="0"
    )

    return terrain_text


def write_terrain(writer: BlockWriter, terrain: Terrain) -> None:
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


def write_terrain_shaders(writer: BlockWriter, shaders: list) -> None:
    with writer.sub_block(TokenID.terrain_shaders):
        writer.write_count(len(shaders))
        for shader in shaders:
            with writer.sub_block(TokenID.terrain_shader):
                writer.write_string(shader.shader_name)
                if shader.terrain_texslots:
                    write_terrain_texslots(writer, shader.terrain_texslots)
                if shader.terrain_uvcalcs:
                    write_terrain_uvcalcs(writer, shader.terrain_uvcalcs)


def write_terrain_texslots(writer: BlockWriter, texslots: list) -> None:
    with writer.sub_block(TokenID.terrain_texslots):
        writer.write_count(len(texslots))
        for texslot in texslots:
            with writer.sub_block(TokenID.terrain_texslot):
                writer.write_string(texslot.filename)
                writer.write_int(texslot.a)
                writer.write_int(texslot.b)


def write_terrain_uvcalcs(writer: BlockWriter, uvcalcs: list) -> None:
    with writer.sub_block(TokenID.terrain_uvcalcs):
        writer.write_count(len(uvcalcs))
        for uvcalc in uvcalcs:
            with writer.sub_block(TokenID.terrain_uvcalc):
                writer.write_int(uvcalc.a)
                writer.write_int(uvcalc.b)
                writer.write_int(uvcalc.c)
                writer.write_float(float(uvcalc.d))


def write_terrain_patchsets(writer: BlockWriter, patchsets: list) -> None:
    with writer.sub_block(TokenID.terrain_patchsets):
        writer.write_count(len(patchsets))
        for patchset in patchsets:
            with writer.sub_block(TokenID.terrain_patchset):
                with writer.sub_block(TokenID.terrain_patchset_distance):
                    writer.write_int(patchset.terrain_patchset_distance)
                with writer.sub_block(TokenID.terrain_patchset_npatches):
                    writer.write_int(patchset.terrain_patchset_npatches)
                write_terrain_patchset_patches(writer, patchset.terrain_patchset_patches)


def write_terrain_patchset_patches(writer: BlockWriter, patches: list) -> None:
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