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



def load(filepath: str) -> TSection:
    """
    Load and parse a tracksections file from disk.

    It opens the file at the given path, validates that it is a supported tracksections
    file based on its subheader, and returns a parsed TSection object.

    Args:
        filepath (str): Path to the tracksections file.

    Returns:
        TSection: The parsed tracksections object.

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

        if reader.filetype not in ('F', 'T'):
            raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a tsection file?")

        return read_tsection(reader)


def loads(tsection_text: str) -> TSection:
    """
    Parse tracksections from a string containing tracksection data.

    This function reads tracksections data from the provided string, validates
    that it represents a supported tracksections file based on its subheader, and
    returns a parsed TSection object.

    Args:
        tsection_text (str): String containing tracksections file data.

    Returns:
        TSection: The parsed tracksections object.

    Raises:
        TypeError: If `tsection_text` is not a string.
        SimisaHeaderError: If the data has an invalid or unrecognized SIMISA header.
        SimisaSubheaderError: If the data has an invalid or unrecognized SIMISA subheader.
        BlockReaderError: If the block reader encounters an error or malformed data.
        StfReaderError: If the STF reader encounters an error or malformed data.
    """
    if not isinstance(tsection_text, str):
        raise TypeError(f"Parameter 'tsection_text' must be str, but got {type(tsection_text).__name__}")

    reader = BlockReader.from_string(tsection_text)

    if reader.filetype not in ('F', 'T'):
        raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a tsection file?")

    return read_tsection(reader)


def read_tsection(reader: BlockReader) -> TSection:
    """
    Read and parse a tsection file from a BlockReader.

    Consumes the `TrackSections`, `TrackShapes`, and `SectionIdx` sub-blocks
    and their child blocks, returning a fully constructed TSection object.

    Args:
        reader (BlockReader): Reader positioned at the start of a tsection file.

    Returns:
        TSection: The parsed tsection file.
    """
    # with reader.sub_block(TokenID.terrain) as terrain_block:
    #     terrain = Terrain()

    #     for sub_block in terrain_block:
    #         if sub_block.id == TokenID.terrain_errthreshold_scale:
    #             terrain.terrain_errthreshold_scale = sub_block.read_float()
            
    #         elif sub_block.id == TokenID.terrain_water_height_offset:
    #             terrain.terrain_water_height_offset = read_terrain_water_height_offset(sub_block)
            
    #         elif sub_block.id == TokenID.terrain_alwaysselect_maxdist:
    #             terrain.terrain_alwaysselect_maxdist = sub_block.read_float()
            
    #         elif sub_block.id == TokenID.terrain_samples:
    #             terrain.terrain_samples = read_terrain_samples(sub_block)
            
    #         elif sub_block.id == TokenID.terrain_shaders:
    #             terrain.terrain_shaders = read_terrain_shaders(sub_block)
            
    #         elif sub_block.id == TokenID.terrain_patches:
    #             terrain.terrain_patchsets = read_terrain_patchsets(sub_block)
            
    #         else:
    #             logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
    #             sub_block.skip()

    #     return terrain