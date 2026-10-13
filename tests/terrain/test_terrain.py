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
from simisa import terrain
from tests import compare_objects


def test_terrain_loads_bytes_raises(global_storage):
    terrainfile_binary_path = global_storage["terrainfile_binary_path"]
    
    with open(terrainfile_binary_path, 'rb') as f:
        terrain_bytes = f.read()
        
        with pytest.raises(TypeError):
            terrain.loads(terrain_bytes)


def test_terrain_roundtrip_uncompressed(global_storage, tmp_path):
    original = terrain.load(global_storage["terrainfile_binary_path"])
    output_path = tmp_path / "roundtrip.t"
    
    terrain.dump(original, str(output_path), compressed=False)
    roundtripped = terrain.load(str(output_path))
    
    if not compare_objects(original, roundtripped):
        assert False


def test_terrain_roundtrip_compressed(global_storage, tmp_path):
    original = terrain.load(global_storage["terrainfile_binary_path"])
    output_path = tmp_path / "roundtrip_compressed.t"
    
    terrain.dump(original, str(output_path), compressed=True)
    roundtripped = terrain.load(str(output_path))
    
    if not compare_objects(original, roundtripped):
        assert False