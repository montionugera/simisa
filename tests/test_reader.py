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
from simisa import StructuredBlockReader

def test_is_compressed_uncompressed_shape(global_storage):
    shape_path = global_storage["shape_path"]
    obj = StructuredBlockReader.open(shape_path)
    print(obj)
    with open(shape_path, "rb") as f:
        data = f.read(40)

    print(data)
    print(data.hex(" "))
    assert False


def test_is_compressed_compressed_shape(global_storage):
    shape_compressed_path = global_storage["shape_compressed_path"]
    obj = StructuredBlockReader.open(shape_compressed_path)
    print(obj)
    with open(shape_compressed_path, "rb") as f:
        data = f.read(40)

    print(data)
    print(data.hex(" "))
    assert False