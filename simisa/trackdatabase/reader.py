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

            for sub_block in track_node_block:
                if sub_block.id == TokenID.ManualJunctionShape:
                    pass
                    #manual_junction_shape = True

                elif sub_block.id == TokenID.ManualJunctionShape:
                    pass
                    #manual_junction_shape = True
                
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


def read_tr_item_table(reader: BlockReader) -> List[TrItem]:
    reader.skip()
    return []