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

import pytest
from simisa import BlockReader
from simisa import shape


# def test_shape_load(global_storage):
#     shape_path = global_storage["shape_path"]
#     s = shape.load(shape_path)
#     print(s)
#     assert False


# def test_shape_loads_uncompressed(global_storage):
#     shape_path = global_storage["shape_path"]
#     with open(shape_path, 'r', encoding='utf-16-le') as f:
#         shape_string = f.read()
#         s = shape.loads(shape_string)
#         print(s)
#     assert False


def test_shape_load_compressed(global_storage):
    shape_compressed_path = global_storage["shape_compressed_path"]
    s = shape.load(shape_compressed_path)
    print(s)
    assert False


def test_shape_loads_compressed(global_storage):
    shape_compressed_path = global_storage["shape_compressed_path"]
    with open(shape_compressed_path, 'rb') as f:
        shape_bytes = f.read()
        #for i, b in enumerate(shape_bytes[:50]):
        #    print(f"{i:04x}: {b:02x}")
        #assert False
        
        with pytest.raises(TypeError):
            shape.loads(shape_bytes)

# def test_is_compressed_uncompressed_shape(global_storage):
#     shape_path = global_storage["shape_path"]
#     obj = BlockReader.open(shape_path)
#     raw = obj.stream.read(100)
#     #text = raw.decode("utf-16-le")
#     #first_x_chars = text[:x]
#     print(raw)
#     assert False


# def test_is_compressed_compressed_shape(global_storage):
#     shape_compressed_path = global_storage["shape_compressed_path"]
#     obj = BlockReader.open(shape_compressed_path)
#     raw = obj.stream.read(100)
#     #text = raw.decode("utf-16-le")
#     #first_x_chars = text[:x]
#     print(raw)
#     assert False