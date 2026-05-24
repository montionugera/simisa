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


def read_world_objects(reader: BlockReader) -> List[WorldObj]:

    reader.verify_id(TokenID.Tr_Worldfile)

    objects: List[WorldObj] = []
    current_watermark: int = 0

    for sub_block in reader:
        world_object = None

        if sub_block.id == TokenID.CollideObject:
            world_object = read_collide_object(sub_block, current_watermark)
            sub_block.skip()

        elif sub_block.id == TokenID.Static:
            world_object = read_static_object(sub_block, current_watermark)
            sub_block.skip()

        elif sub_block.id == TokenID.TrackObj:
            world_object = read_track_object(sub_block, current_watermark)
            sub_block.skip()

        elif sub_block.id == TokenID.CarSpawner:
            world_object = read_carspawner_object(sub_block, current_watermark)
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
            sub_block.skip()

        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

        if world_object is not None:
            objects.append(world_object)

    reader.skip()

    return objects


def read_collide_object(reader: BlockReader, detail_level: int) -> StaticObj:

    reader.verify_id(TokenID.CollideObject)

    static_obj = StaticObj()
    static_obj.static_detail_level = detail_level

    for sub_block in reader:
        if sub_block.id == TokenID.UiD:
            static_obj.uid = sub_block.read_uint()

        elif sub_block.id == TokenID.FileName:
            static_obj.file_name = sub_block.read_string()

        elif sub_block.id == TokenID.Position:
            static_obj.position = read_position(sub_block)

        elif sub_block.id == TokenID.QDirection:
            static_obj.direction = read_qdirection(sub_block)

        elif sub_block.id == TokenID.Matrix3x3:
            static_obj.matrix3x3 = read_matrix3x3(sub_block)

        elif sub_block.id == TokenID.VDbId:
            static_obj.vdb_id = sub_block.read_uint()

        elif sub_block.id == TokenID.StaticFlags:
            static_obj.static_flags = sub_block.read_flags()
        
        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    return static_obj


def read_static_object(reader: BlockReader, detail_level: int) -> StaticObj:

    reader.verify_id(TokenID.Static)

    static_obj = StaticObj()
    static_obj.static_detail_level = detail_level

    for sub_block in reader:
        if sub_block.id == TokenID.UiD:
            static_obj.uid = sub_block.read_uint()

        elif sub_block.id == TokenID.FileName:
            static_obj.file_name = sub_block.read_string()

        elif sub_block.id == TokenID.Position:
            static_obj.position = read_position(sub_block)

        elif sub_block.id == TokenID.QDirection:
            static_obj.direction = read_qdirection(sub_block)

        elif sub_block.id == TokenID.Matrix3x3:
            static_obj.matrix3x3 = read_matrix3x3(sub_block)

        elif sub_block.id == TokenID.VDbId:
            static_obj.vdb_id = sub_block.read_uint()

        elif sub_block.id == TokenID.StaticFlags:
            static_obj.static_flags = sub_block.read_flags()
        
        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    return static_obj


def read_track_object(reader: BlockReader, detail_level: int) -> TrackObj:

    reader.verify_id(TokenID.TrackObj)

    track_obj = TrackObj()
    track_obj.static_detail_level = detail_level

    for sub_block in reader:
        if sub_block.id == TokenID.UiD:
            track_obj.uid = sub_block.read_uint()

        elif sub_block.id == TokenID.FileName:
            track_obj.file_name = sub_block.read_string()

        elif sub_block.id == TokenID.SectionIdx:
            track_obj.section_index = sub_block.read_uint()

        elif sub_block.id == TokenID.Elevation:
            track_obj.elevation = sub_block.read_float()

        elif sub_block.id == TokenID.CollideFlags:
            track_obj.collide_flags = sub_block.read_flags()

        elif sub_block.id == TokenID.Position:
            track_obj.position = read_position(sub_block)

        elif sub_block.id == TokenID.QDirection:
            track_obj.direction = read_qdirection(sub_block)

        elif sub_block.id == TokenID.Matrix3x3:
            track_obj.matrix3x3 = read_matrix3x3(sub_block)

        elif sub_block.id == TokenID.JNodePosn:
            track_obj.jnode_position = read_jnode_position(sub_block)

        elif sub_block.id == TokenID.VDbId:
            track_obj.vdb_id = sub_block.read_uint()

        elif sub_block.id == TokenID.StaticFlags:
            track_obj.static_flags = sub_block.read_flags()
        
        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    return track_obj


def read_carspawner_object(reader: BlockReader, detail_level: int) -> CarSpawnerObj:

    reader.verify_id(TokenID.CarSpawner)

    carspawner_obj = CarSpawnerObj()
    carspawner_obj.static_detail_level = detail_level

    for sub_block in reader:
        if sub_block.id == TokenID.UiD:
            carspawner_obj.uid = sub_block.read_uint()

        elif sub_block.id == TokenID.FileName:
            carspawner_obj.file_name = sub_block.read_string()

        elif sub_block.id == TokenID.Position:
            carspawner_obj.position = read_position(sub_block)

        elif sub_block.id == TokenID.QDirection:
            carspawner_obj.direction = read_qdirection(sub_block)

        elif sub_block.id == TokenID.Matrix3x3:
            carspawner_obj.matrix3x3 = read_matrix3x3(sub_block)

        elif sub_block.id == TokenID.VDbId:
            carspawner_obj.vdb_id = sub_block.read_uint()

        elif sub_block.id == TokenID.StaticFlags:
            carspawner_obj.static_flags = sub_block.read_flags()

        elif sub_block.id == TokenID.CarFrequency:
            carspawner_obj.car_frequency = sub_block.read_float()

        elif sub_block.id == TokenID.CarAvSpeed:
            carspawner_obj.car_avg_speed = sub_block.read_float()

        elif sub_block.id == TokenID.ORTSListName:
            carspawner_obj.list_name = sub_block.read_string()

        elif sub_block.id == TokenID.TrItemId:
            if carspawner_obj.tr_item_ids is None:
                carspawner_obj.tr_item_ids = []
            
            tr_item_id = read_tr_item_id(sub_block)
            carspawner_obj.tr_item_ids.append(tr_item_ids)
        
        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    return static_obj


def read_position(reader: BlockReader) -> Position:

    reader.verify_id(TokenID.Position)

    x = reader.read_float()
    y = reader.read_float()
    z = reader.read_float()

    return Position(
        x=x,
        y=y,
        z=z
    )


def read_qdirection(reader: BlockReader) -> QDirection:

    reader.verify_id(TokenID.QDirection)

    x = reader.read_float()
    y = reader.read_float()
    z = reader.read_float()
    w = reader.read_float()

    return QDirection(
        x=x,
        y=y,
        z=z,
        w=w
    )


def read_matrix3x3(reader: BlockReader) -> Matrix3x3:

    reader.verify_id(TokenID.Matrix3x3)

    ax = reader.read_float()
    ay = reader.read_float()
    az = reader.read_float()
    bx = reader.read_float()
    by = reader.read_float()
    bz = reader.read_float()
    cx = reader.read_float()
    cy = reader.read_float()
    cz = reader.read_float()

    return Matrix3x3(
        ax=ax,
        ay=ay,
        az=az,
        bx=bx,
        by=by,
        bz=bz,
        cx=cx,
        cy=cy,
        cz=cz
    )


def read_jnode_position(reader: BlockReader) -> JNodePosn:

    reader.verify_id(TokenID.JNodePosn)

    tile_x = reader.read_int()
    tile_z = reader.read_int()
    x = reader.read_float()
    y = reader.read_float()
    z = reader.read_float()

    return JNodePosn(
        tile_x=tile_x,
        tile_z=tile_z,
        x=x,
        y=y,
        z=z
    )


def read_tr_item_id(reader: BlockReader) -> TrItemId:

    reader.verify_id(TokenID.TrItemId)

    db = reader.read_int()
    db_id = reader.read_int()

    return TrItemId(
        db=db,
        db_id=db_id
    )