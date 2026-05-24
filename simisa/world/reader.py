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
from pathlib import Path
from typing import List

from .. import TokenID
from ..reader import BlockReader, SimisaSubheaderError
from .models import *

logger = logging.getLogger(__name__)



def load(filepath: str) -> World:
    """
    Load and parse a world file from disk.

    This function supports both compressed/uncompressed as well as binary/text data.
    It opens the file at the given path, validates that it is a supported world
    file based on its subheader, and returns a parsed World object.

    Args:
        filepath (str): Path to the world file.

    Returns:
        World: The parsed world object.

    Raises:
        TypeError: If `filepath` is not a string.
        SimisaHeaderError: If the data has an invalid or unrecognized SIMISA header.
        SimisaSubheaderError: If the data has an invalid or unrecognized SIMISA subheader.
        BlockReaderError: If the block reader encounters an error or malformed data.
        StfReaderError: If the STF reader encounters an error or malformed data.
        UnresolvableIncludeError: If includes within the file cannot be resolved.
        OSError: If the file cannot be opened.
    """
    if not isinstance(filepath, str):
        raise TypeError(f"Parameter 'filepath' must be str, but got {type(filepath).__name__}")

    with BlockReader.open(filepath) as reader:

        if not reader.filetype == 'w':
            raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a world file?")

        world = read_world(reader)

        file_path = Path(filepath)

        if file_path.is_file():
            world.file_name = file_path.name

        return world


def loads(world_text: str) -> World:
    """
    Parse a world file from a string containing world data.

    This function does not support binary or compressed data. It reads world
    data from the provided string, validates that it represents a supported
    world file based on its subheader, and returns a parsed World object.

    Args:
        world_text (str): String containing world file data.

    Returns:
        World: The parsed world object.

    Raises:
        TypeError: If `world_text` is not a string.
        SimisaHeaderError: If the data has an invalid or unrecognized SIMISA header.
        SimisaSubheaderError: If the data has an invalid or unrecognized SIMISA subheader.
        BlockReaderError: If the block reader encounters an error or malformed data.
        StfReaderError: If the STF reader encounters an error or malformed data.
        UnresolvableIncludeError: If includes within the file cannot be resolved.
    """
    if not isinstance(world_text, str):
        raise TypeError(f"Parameter 'world_text' must be str, but got {type(world_text).__name__}")

    reader = BlockReader.from_string(world_text)

    if not reader.filetype == 'w':
        raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a world file?")

    return read_world(reader)


def read_world(reader: BlockReader) -> World:
    """
    Read and parse a worldfile block from a BlockReader.

    Consumes the `Tr_Worldfile` sub-block and its child blocks, returning a fully
    constructed World object.

    Args:
        reader (BlockReader): Reader positioned at a worldfile block.

    Returns:
        World: The parsed world file.
    """
    with reader.sub_block(TokenID.Tr_Worldfile) as worldfile_block:
        objects = read_world_objects(worldfile_block)

        return World(objects=objects)


def read_world_objects(reader: BlockReader) -> List[WorldObject]:

    reader.verify_id(TokenID.Tr_Worldfile)

    world_objects: List[WorldObject] = []
    current_watermark: int = 0

    for sub_block in reader:
        if sub_block.id == TokenID.CollideObject:
            sub_block.skip()

        elif sub_block.id == TokenID.Static:
            sub_block.skip()

        elif sub_block.id == TokenID.TrackObj:
            sub_block.skip()

        elif sub_block.id == TokenID.CarSpawner:
            sub_block.skip()

        elif sub_block.id == TokenID.Siding:
            sub_block.skip()

        elif sub_block.id == TokenID.Platform:
            sub_block.skip()

        elif sub_block.id == TokenID.Forest:
            sub_block.skip()

        elif sub_block.id == TokenID.LevelCr:
            sub_block.skip()

        elif sub_block.id == TokenID.Dyntrack:
            sub_block.skip()

        elif sub_block.id == TokenID.Transfer:
            sub_block.skip()

        elif sub_block.id == TokenID.Gantry:
            sub_block.skip()

        elif sub_block.id == TokenID.Pickup:
            sub_block.skip()

        elif sub_block.id == TokenID.Hazard:
            sub_block.skip()

        elif sub_block.id == TokenID.Signal:
            sub_block.skip()

        elif sub_block.id == TokenID.Speedpost:
            sub_block.skip()

        elif sub_block.id == TokenID.Tr_Watermark:
            current_watermark = sub_block.read_int()

        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    reader.skip()

    return world_objects