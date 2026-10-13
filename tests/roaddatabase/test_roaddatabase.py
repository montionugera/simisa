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
from simisa import roaddatabase, SimisaSubheaderError


def test_rdb_load(global_storage):
    rdb = roaddatabase.load(global_storage["roaddatabase_path"])

    assert rdb.serial == 0
    assert len(rdb.track_nodes) == 297
    assert len(rdb.tr_item_table) == 0
    assert rdb.track_nodes[23].index == 24
    assert rdb.track_nodes[23].uid.tile_x == -5636
    assert rdb.track_nodes[23].uid.tile_z == 15116
    assert rdb.track_nodes[23].uid.x == -455.34
    assert rdb.track_nodes[23].uid.y == 1.650479
    assert rdb.track_nodes[23].uid.z == -929.7409
    assert rdb.track_nodes[23].tr_end_node == True
    assert rdb.track_nodes[23].tr_vector_node is None
    assert len(rdb.track_nodes[23].tr_pins) == 1
    assert rdb.track_nodes[23].tr_pins[0].link == 23
    assert rdb.track_nodes[23].tr_pins[0].direction == 1


def test_rdb_load_shape_raises(global_storage):
    shapefile_path = global_storage["shapefile_path"]

    with pytest.raises(SimisaSubheaderError):
        roaddatabase.load(shapefile_path)


def test_rdb_loads_bytes_raises(global_storage):
    roaddatabase_path = global_storage["roaddatabase_path"]

    with open(roaddatabase_path, 'rb') as f:
        roaddatabase_bytes = f.read()
        
        with pytest.raises(TypeError):
            roaddatabase.loads(roaddatabase_bytes)
