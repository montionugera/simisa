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


def load_file(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-16-le') as f:
        return f.read()


@pytest.fixture(scope="session")
def reader_from_body(body: str) -> BlockReader:
    return BlockReader.from_string(
        "SIMISA@@@@@@@@@@"
        "JINX0s0t______\n"
        + body
    )


@pytest.fixture(scope="session")
def global_storage():
    data = {
        "emptyfile_path": "./tests/data/empty.txt",
        "garbagefile_path": "./tests/data/garbage.txt",
        "roaddatabase_path": "./tests/data/DK24.rdb",
        "roaddatabase_empty_path": "./tests/data/DK24TEST.rdb",
        "shapefile_path": "./tests/data/DK10f_A1tPnt5dLft.s",
        "shapefile_compressed_path": "./tests/data/DK10f_A1tPnt5dLft_compressed.s",
        "trackdatabase_path": "./tests/data/DK24TEST.tdb",
        "tsectionext_path": "./tests/data/tsectionext.dat",
        "tsectionext_nested_path": "./tests/data/tsectionext_nested.dat",
        "tsectionext_blockbeforeinclude_path": "./tests/data/tsectionext_blockbeforeinclude.dat",
        "tsectionext_commentsbeforeinclude_path": "./tests/data/tsectionext_commentsbeforeinclude.dat",
        "tsectionglobal_path": "./tests/data/tsectionglobal.dat",
        "tsectionlocal_path": "./tests/data/tsectionlocal.dat",
        "terrainfile_compressed_path": "./tests/data/-11dc0894.t",
        "worldfile_path": "./tests/data/w-005655+015119.w",
        "worldfile2_path": "./tests/data/w-005579+015131.w",
        "worldfile_compressed_path": "./tests/data/w-005655+015119_compressed.w",
        "worldsoundfile_path": "./tests/data/w-005656+015119.ws"
    }
    data["shape"] = load_file(data["shapefile_path"])
    return data