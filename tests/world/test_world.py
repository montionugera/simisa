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
from simisa import world
from tests import compare_objects


def test_world_loads_compressed_bytes_raises(global_storage):
    worldfile_compressed_path = global_storage["worldfile_compressed_path"]
    
    with open(worldfile_compressed_path, 'rb') as f:
        worldfile_bytes = f.read()
        
        with pytest.raises(TypeError):
            world.loads(worldfile_bytes)


def test_world_roundtrip_uncompressed(global_storage, tmp_path):
    original = world.load(global_storage["worldfile2_path"])
    output_path = tmp_path / "w-005579+015131.w"
    
    world.dump(original, str(output_path), compressed=False)
    roundtripped = world.load(str(output_path))
    
    if not compare_objects(original, roundtripped):
        assert False


def test_world_roundtrip_compressed(global_storage, tmp_path):
    original = world.load(global_storage["worldfile2_path"])
    output_path = tmp_path / "w-005579+015131.w"
    
    world.dump(original, str(output_path), compressed=True)
    roundtripped = world.load(str(output_path))
    
    if not compare_objects(original, roundtripped):
        assert False

