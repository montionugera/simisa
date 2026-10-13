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
import pytest
from simisa import trackdatabase, SimisaSubheaderError


def test_tdb_load(global_storage):
    tdb = trackdatabase.load(global_storage["trackdatabase_path"])

    assert tdb.serial == 0
    assert len(tdb.track_nodes) == 151
    assert len(tdb.tr_item_table) == 24
    assert tdb.track_nodes[23].index == 24
    assert tdb.track_nodes[23].uid.tile_x == -5655
    assert tdb.track_nodes[23].uid.tile_z == 15119
    assert tdb.track_nodes[23].uid.x == 755.2383
    assert tdb.track_nodes[23].uid.y == 2.472422
    assert tdb.track_nodes[23].uid.z == -405.1773
    assert tdb.track_nodes[23].tr_end_node == True
    assert tdb.track_nodes[23].tr_vector_node is None
    assert len(tdb.track_nodes[23].tr_pins) == 1
    assert tdb.track_nodes[23].tr_pins[0].link == 23
    assert tdb.track_nodes[23].tr_pins[0].direction == 0


def test_tdb_load_shape_raises(global_storage):
    shapefile_path = global_storage["shapefile_path"]

    with pytest.raises(SimisaSubheaderError):
        trackdatabase.load(shapefile_path)


def test_tdb_loads_bytes_raises(global_storage):
    trackdatabase_path = global_storage["trackdatabase_path"]

    with open(trackdatabase_path, 'rb') as f:
        trackdatabase_bytes = f.read()
        
        with pytest.raises(TypeError):
            trackdatabase.loads(trackdatabase_bytes)