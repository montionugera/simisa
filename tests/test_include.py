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


def test_peek_first_include_emptyfile(global_storage):
    first_include = simisa.peek_first_include(global_storage["emptyfile_path"])
    assert first_include is None


def test_peek_first_include_garbagefile(global_storage):
    first_include = simisa.peek_first_include(global_storage["garbagefile_path"])
    assert first_include is None


def test_peek_first_include_shapefile(global_storage):
    first_include = simisa.peek_first_include(global_storage["shapefile_path"])
    assert first_include is None


def test_peek_first_include_worldfile_compressed(global_storage):
    first_include = simisa.peek_first_include(global_storage["worldfile_compressed_path"])
    assert first_include is None


def test_peek_first_include_tsectionext(global_storage):
    first_include = simisa.peek_first_include(global_storage["tsectionext_path"])
    assert first_include == "../../../GLOBAL/tsection.dat"


def test_peek_first_include_tsectionext_blockbeforeinclude(global_storage):
    first_include = simisa.peek_first_include(global_storage["tsectionext_blockbeforeinclude_path"])
    assert first_include is None


def test_peek_first_include_tsectionext_commentsbeforeinclude(global_storage):
    first_include = simisa.peek_first_include(global_storage["tsectionext_commentsbeforeinclude_path"])
    assert first_include == "../../../GLOBAL/tsection.dat"


def test_peek_first_include_tsectionglobal(global_storage):
    first_include = simisa.peek_first_include(global_storage["tsectionglobal_path"])
    assert first_include is None