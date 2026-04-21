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
import simisa


def test_peek_header_uncompressed_shape(global_storage):
    shape_path = global_storage["shape_path"]
    header = simisa.peek_header(shape_path)
    assert header.startswith("SIMISA@@")


def test_peek_header_compressed_shape(global_storage):
    shape_compressed_path = global_storage["shape_compressed_path"]
    header = simisa.peek_header(shape_compressed_path)
    assert header.startswith("SIMISA@F")


def test_peek_header_emptyfile(global_storage):
    emptyfile_path = global_storage["emptyfile_path"]
    header = simisa.peek_header(emptyfile_path)
    assert header is None


def test_peek_header_garbagefile(global_storage):
    garbagefile_path = global_storage["garbagefile_path"]
    header = simisa.peek_header(garbagefile_path)
    assert header is None


def test_is_compressed_uncompressed_shape(global_storage):
    shape_path = global_storage["shape_path"]
    is_compressed = simisa.is_compressed(shape_path)
    assert not is_compressed


def test_is_compressed_compressed_shape(global_storage):
    shape_compressed_path = global_storage["shape_compressed_path"]
    is_compressed = simisa.is_compressed(shape_compressed_path)
    assert is_compressed


def test_is_compressed_uncompressed_worldfile(global_storage):
    worldfile_path = global_storage["worldfile_path"]
    is_compressed = simisa.is_compressed(worldfile_path)
    assert not is_compressed


def test_is_compressed_compressed_worldfile(global_storage):
    worldfile_compressed_path = global_storage["worldfile_compressed_path"]
    is_compressed = simisa.is_compressed(worldfile_compressed_path)
    assert is_compressed


def test_is_compressed_emptyfile(global_storage):
    emptyfile_path = global_storage["emptyfile_path"]
    is_compressed = simisa.is_compressed(emptyfile_path)
    assert is_compressed is None


def test_is_compressed_garbagefile(global_storage):
    garbagefile_path = global_storage["garbagefile_path"]
    is_compressed = simisa.is_compressed(garbagefile_path)
    assert is_compressed is None


def test_read_subheader_uncompressed_shape(global_storage):
    shape_path = global_storage["shape_path"]
    subheader = simisa.read_subheader(shape_path)
    assert subheader == "JINX0s1t"


def test_read_subheader_compressed_shape(global_storage):
    shape_compressed_path = global_storage["shape_compressed_path"]
    subheader = simisa.read_subheader(shape_compressed_path)
    assert subheader == "JINX0s1b"


def test_read_subheader_uncompressed_worldfile(global_storage):
    worldfile_path = global_storage["worldfile_path"]
    subheader = simisa.read_subheader(worldfile_path)
    assert subheader == "JINX0w0t"


def test_read_subheader_compressed_worldfile(global_storage):
    worldfile_compressed_path = global_storage["worldfile_compressed_path"]
    subheader = simisa.read_subheader(worldfile_compressed_path)
    assert subheader == "JINX0w0b"