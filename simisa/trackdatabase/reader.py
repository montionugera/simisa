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

import math
import logging
from typing import List

from .. import TokenID
from ..reader import BlockReader
from .models import *

logger = logging.getLogger(__name__)



def load(filepath: str) -> TrackDB:
    """
    Load and parse a track database file from disk.

    This function opens the file at the given path, validates that it is a supported tdb
    file based on its subheader, and returns a parsed `TrackDB` object.

    Args:
        filepath (str): Path to the tdb file.

    Returns:
        TrackDB: The parsed track database object.

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

        if not reader.filetype == 'T':
            raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a track database?")

        return read_trackdb(reader)


def loads(tdb_text: str) -> TrackDB:
    """
    Parse a track database from a string containing tdb data.

    This function does not support binary or compressed data. It reads tdb
    data from the provided string, validates that it represents a supported
    track database file based on its subheader, and returns a parsed `TrackDB` object.

    Args:
        tdb_text (str): String containing tdb file data.

    Returns:
        TrackDB: The parsed track database object.

    Raises:
        TypeError: If `tdb_text` is not a string.
        SimisaHeaderError: If the data has an invalid or unrecognized SIMISA header.
        SimisaSubheaderError: If the data has an invalid or unrecognized SIMISA subheader.
        BlockReaderError: If the block reader encounters an error or malformed data.
        StfReaderError: If the STF reader encounters an error or malformed data.
        UnresolvableIncludeError: If includes within the file cannot be resolved.
    """
    if not isinstance(tdb_text, str):
        raise TypeError(f"Parameter 'tdb_text' must be str, but got {type(tdb_text).__name__}")

    reader = BlockReader.from_string(tdb_text)

    if not reader.filetype == 'T':
        raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a track database?")

    return read_trackdb(reader)


def read_trackdb(reader: BlockReader) -> TrackDB:

    with reader.sub_block(TokenID.TrackDB) as trackdb_block:
        serial = 0

        with trackdb_block.sub_block(TokenID.Serial) as serial_block:
            serial = serial_block.read_uint()

        track_nodes = read_track_nodes(trackdb_block)
        tr_item_table = read_tr_item_table(trackdb_block)

        return TrackDB(
            serial=serial,
            track_nodes=track_nodes,
            tr_item_table=tr_item_table
        )


def read_track_nodes(reader: BlockReader) -> List[TrackNode]:
    
    with reader.sub_block(TokenID.TrackNodes) as track_nodes_block:
        if track_nodes_block is None:
            return []
        
        track_nodes: List[TrackNode] = []
        count = track_nodes_block.read_uint()
        
        for track_node_block in track_nodes_block:
            track_node_block.verify_id(TokenID.TrackNode)

            index = track_node_block.read_uint()
            uid = None
            tr_junction_node = None
            tr_vector_node = None
            tr_end_node = False
            tr_pins = []
            inpins = 0
            outpins = 0

            for sub_block in track_node_block:
                if sub_block.id == TokenID.UiD:
                    uid = read_uid(sub_block)

                elif sub_block.id == TokenID.TrJunctionNode:
                    tr_junction_node = read_tr_junction_node(sub_block)

                elif sub_block.id == TokenID.TrVectorNode:
                    tr_vector_node = read_tr_vector_node(sub_block)

                elif sub_block.id == TokenID.TrEndNode:
                    tr_end_node = True
                    sub_block.skip()

                elif sub_block.id == TokenID.TrPins:
                    inpins = sub_block.read_uint()
                    outpins = sub_block.read_uint()

                    tr_pins = read_tr_pins(sub_block)

                    sub_block.verify_count(inpins + outpins, len(tr_pins))
                    sub_block.skip()
                
                else:
                    logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
                    sub_block.skip()

            track_node = TrackNode(
                index=index,
                uid=uid,
                tr_junction_node=tr_junction_node,
                tr_vector_node=tr_vector_node,
                tr_end_node=tr_end_node,
                tr_pins=tr_pins
            )
            track_nodes.append(track_node)

        track_nodes_block.verify_count(count, len(track_nodes))

        return track_nodes


def read_uid(reader: BlockReader) -> UiD:

    reader.verify_id(TokenID.UiD)
    
    world_tile_x = reader.read_int()
    world_tile_z = reader.read_int()
    world_id = reader.read_int()
    _ = reader.read_int()
    tile_x = reader.read_int()
    tile_z = reader.read_int()
    x = reader.read_float()
    y = reader.read_float()
    z = reader.read_float()
    ax = reader.read_float()
    ay = reader.read_float()
    az = reader.read_float()

    reader.skip()

    return UiD(
        tile_x=tile_x,
        tile_z=tile_z,
        x=x,
        y=y,
        z=z,
        ax=ax,
        ay=ay,
        az=az,
        world_tile_x=world_tile_x,
        world_tile_z=world_tile_z,
        world_id=world_id
    )


def read_tr_junction_node(reader: BlockReader) -> TrJunctionNode:

    reader.verify_id(TokenID.TrJunctionNode)

    _ = reader.read_string()
    shape_index = reader.read_uint()

    reader.skip()

    return TrJunctionNode(
        shape_index=shape_index
    )


def read_tr_vector_node(reader: BlockReader) -> TrVectorNode:
    reader.verify_id(TokenID.TrVectorNode)

    tr_vector_sections: List[TrVectorSection] = []
    tr_item_refs: List[int] = []

    for sub_block in reader:
        if sub_block.id == TokenID.TrVectorSections:
            tr_vector_sections = read_tr_vector_sections(sub_block)

        elif sub_block.id == TokenID.TrItemRefs:
            tr_item_refs = read_tr_item_refs(sub_block)

        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    reader.skip()

    return TrVectorNode(
        tr_vector_sections=tr_vector_sections,
        tr_item_refs=tr_item_refs
    )


def read_tr_vector_sections(reader: BlockReader) -> List[TrVectorSection]:
    reader.verify_id(TokenID.TrVectorSections)

    tr_vector_sections: List[TrVectorSection] = []
    count = reader.read_uint()

    for _ in range(count):
        section_index = reader.read_uint()
        shape_index = reader.read_uint()
        wf_name_x = reader.read_int()
        wf_name_z = reader.read_int()
        wf_uid = reader.read_uint()
        flags1 = reader.read_flags()
        flags2 = reader.read_flags()
        _ = reader.read_string()
        tile_x = reader.read_int()
        tile_z = reader.read_int()
        x = reader.read_float()
        y = reader.read_float()
        z = reader.read_float()
        ax = reader.read_float()
        ay = reader.read_float()
        az = reader.read_float()

        tr_vector_section = TrVectorSection(
            flags1=flags1,
            flags2=flags2,
            section_index=section_index,
            shape_index=shape_index,
            tile_x=tile_x,
            tile_z=tile_z,
            x=x,
            y=y,
            z=z,
            ax=ax,
            ay=ay,
            az=az,
            wf_uid=wf_uid,
            wf_name_x=wf_name_x,
            wf_name_z=wf_name_z
        )
        tr_vector_sections.append(tr_vector_section)

    reader.skip()
    reader.verify_count(count, len(tr_vector_sections))

    return tr_vector_sections


def read_tr_item_refs(reader: BlockReader) -> List[int]:
    reader.verify_id(TokenID.TrItemRefs)
    
    tr_item_refs: List[int] = []
    count = reader.read_uint()

    for sub_block in reader:
        sub_block.verify_id(TokenID.TrItemRef)

        tr_item_ref = sub_block.read_int()
        tr_item_refs.append(tr_item_ref)

    reader.skip()
    reader.verify_count(count, len(tr_item_refs))

    return tr_item_refs


def read_tr_pins(reader: BlockReader) -> List[TrPin]:
    reader.verify_id(TokenID.TrPins)

    tr_pins: List[int] = []

    for sub_block in reader:
        sub_block.verify_id(TokenID.TrPin)

        link = sub_block.read_int()
        direction = sub_block.read_int()

        tr_pins.append(TrPin(
            link=link,
            direction=direction
        ))

    reader.skip()

    return tr_pins

# EmptyItem = 928 x
# SignalItem = 929 x
# PickupItem = 930
# PlatformItem = 931
# HazzardItem = 932
# CarSpawnerItem = 933
# SidingItem = 934
# LevelCrItem = 935
# SpeedPostItem = 936 x
# SoundRegionItem = 937
# CrossoverItem = 938 x


def read_tr_item_table(reader: BlockReader) -> List[TrItem]:

    with reader.sub_block(TokenID.TrItemTable) as tr_item_table_block:
        if tr_item_table_block is None:
            return []
        
        tr_items: List[TrItem] = []
        count = tr_item_table_block.read_uint()
        
        for sub_block in tr_item_table_block:
            tr_item = None

            if sub_block.id == TokenID.EmptyItem:
                tr_item = read_empty_item(sub_block)

            elif sub_block.id == TokenID.CrossoverItem:
                tr_item = read_crossover_item(sub_block)

            elif sub_block.id == TokenID.SignalItem:
                tr_item = read_signal_item(sub_block)

            elif sub_block.id == TokenID.SpeedPostItem:
                tr_item = read_speedpost_item(sub_block)

            else:
                logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
                sub_block.skip()
            
            if tr_item is not None:
                tr_items.append(tr_item)

        tr_item_table_block.verify_count(count, len(tr_items))

        return tr_items


def read_empty_item(reader: BlockReader) -> TrItem:

    reader.verify_id(TokenID.EmptyItem)

    empty_item = EmptyItem()
    
    for sub_block in reader:
        if sub_block.id == TokenID.TrItemId:
            empty_item = read_tr_item_id(sub_block, empty_item)
        
        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    return empty_item


def read_crossover_item(reader: BlockReader) -> TrItem:

    reader.verify_id(TokenID.CrossoverItem)

    crossover_item = CrossoverItem()
    
    for sub_block in reader:
        if sub_block.id == TokenID.TrItemId:
            crossover_item = read_tr_item_id(sub_block, crossover_item)

        elif sub_block.id == TokenID.TrItemRData:
            crossover_item = read_tr_item_rdata(sub_block, crossover_item)

        elif sub_block.id == TokenID.TrItemPData:
            crossover_item = read_tr_item_pdata(sub_block, crossover_item)

        elif sub_block.id == TokenID.TrItemSData:
            crossover_item = read_tr_item_sdata(sub_block, crossover_item)

        elif sub_block.id == TokenID.CrossoverTrItemData:
            crossover_item.track_node = sub_block.read_uint()
            crossover_item.shape_index = sub_block.read_uint()
            sub_block.skip()
        
        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    return crossover_item


def read_signal_item(reader: BlockReader) -> TrItem:

    reader.verify_id(TokenID.SignalItem)

    signal_item = SignalItem()

    for sub_block in reader:
        if sub_block.id == TokenID.TrItemId:
            signal_item = read_tr_item_id(sub_block, signal_item)

        elif sub_block.id == TokenID.TrItemRData:
            signal_item = read_tr_item_rdata(sub_block, signal_item)

        elif sub_block.id == TokenID.TrItemPData:
            signal_item = read_tr_item_pdata(sub_block, signal_item)

        elif sub_block.id == TokenID.TrItemSData:
            signal_item = read_tr_item_sdata(sub_block, signal_item)

        elif sub_block.id == TokenID.TrSignalType:
            signal_item.flags = sub_block.read_flags()
            signal_item.direction = sub_block.read_uint()
            signal_item.signal_data1 = sub_block.read_float()
            signal_item.signal_type = sub_block.read_string()
            sub_block.skip()
        
        elif sub_block.id == TokenID.TrSignalDirs:
            signal_item.signal_dirs = read_signal_directions(sub_block)
            sub_block.skip()
        
        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    return signal_item


def read_signal_directions(reader: BlockReader) -> List[SignalDirection]:

    reader.verify_id(TokenID.TrSignalDirs)

    signal_directions: List[SignalDirection] = []
    count = reader.read_uint()

    for signal_direction_block in reader:
        signal_direction_block.verify_id(TokenID.TrSignalDir)

        track_node = signal_direction_block.read_uint()
        sd1 = signal_direction_block.read_uint()
        link_lr_path = signal_direction_block.read_uint()
        sd3 = signal_direction_block.read_uint()

        signal_direction_block.skip()

        signal_direction = SignalDirection(
            track_node=track_node,
            sd1=sd1,
            link_lr_path=link_lr_path,
            sd3=sd3
        )
        signal_directions.append(signal_direction)

    reader.skip()
    reader.verify_count(count, len(signal_directions))

    return signal_directions


def read_speedpost_item(reader: BlockReader) -> TrItem:

    reader.verify_id(TokenID.SpeedPostItem)

    speedpost_item = SpeedPostItem()

    for sub_block in reader:
        if sub_block.id == TokenID.TrItemId:
            speedpost_item = read_tr_item_id(sub_block, speedpost_item)

        elif sub_block.id == TokenID.TrItemRData:
            speedpost_item = read_tr_item_rdata(sub_block, speedpost_item)

        elif sub_block.id == TokenID.TrItemPData:
            speedpost_item = read_tr_item_pdata(sub_block, speedpost_item)

        elif sub_block.id == TokenID.TrItemSData:
            speedpost_item = read_tr_item_sdata(sub_block, speedpost_item)

        elif sub_block.id == TokenID.SpeedpostTrItemData:
            flags = sub_block.read_flags()
            speedpost_item.flags = flags

            is_warning = (flags & 1) != 0
            is_limit = (flags & (1 << 1)) != 0

            if not is_warning and not is_limit:
                speedpost_item.is_mile_post = True
            else:
                speedpost_item.is_warning = is_warning
                speedpost_item.is_limit = is_limit

                if is_warning and is_limit:
                    speedpost_item.is_warning = False
                    speedpost_item.is_resume = True

                if (flags & (1 << 5)) != 0:
                    speedpost_item.is_passenger = True

                if (flags & (1 << 6)) != 0:
                    speedpost_item.is_freight = True

                if (flags & (1 << 7)) != 0:
                    speedpost_item.is_passenger = True
                    speedpost_item.is_freight = True

                if (flags & (1 << 8)) != 0:
                    speedpost_item.is_mph = True

                if (flags & (1 << 4)) != 0:
                    speedpost_item.show_number = True

                    if (flags & (1 << 9)) != 0:
                        speedpost_item.show_dot = True

            if not speedpost_item.is_resume:
                if speedpost_item.is_mile_post and ((flags & (1 << 9)) == 0):
                    speedpost_item.speed_ind = float(math.trunc(sub_block.read_float()))
                else:
                    speedpost_item.speed_ind = sub_block.read_float()

            if speedpost_item.show_number:
                speedpost_item.display_number = sub_block.read_int()

            speedpost_item.angle = (sub_block.read_float() + math.pi) % (2 * math.pi) - math.pi

            sub_block.skip()
        
        else:
            logger.warning(f"Unhandled sub block: {sub_block.id.name} (id: {sub_block.id})")
            sub_block.skip()

    return speedpost_item


def read_tr_item_id(reader: BlockReader, tr_item: TrItem) -> TrItem:

    reader.verify_id(TokenID.TrItemId)

    tr_item.tr_item_id = reader.read_uint()

    reader.skip()

    return tr_item


def read_tr_item_rdata(reader: BlockReader, tr_item: TrItem) -> TrItem:

    reader.verify_id(TokenID.TrItemRData)

    tr_item.x = reader.read_float()
    tr_item.y = reader.read_float()
    tr_item.z = reader.read_float()
    tr_item.tile_x = reader.read_int()
    tr_item.tile_z = reader.read_int()

    reader.skip()

    return tr_item


def read_tr_item_pdata(reader: BlockReader, tr_item: TrItem) -> TrItem:

    reader.verify_id(TokenID.TrItemPData)

    tr_item.px = reader.read_float()
    tr_item.pz = reader.read_float()
    tr_item.tile_px = reader.read_int()
    tr_item.tile_pz = reader.read_int()

    reader.skip()

    return tr_item


def read_tr_item_sdata(reader: BlockReader, tr_item: TrItem) -> TrItem:

    reader.verify_id(TokenID.TrItemSData)

    tr_item.sdata1 = reader.read_float()
    tr_item.sdata2 = reader.read_flags()

    reader.skip()

    return tr_item