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
from simisa import BlockWriter, TokenID


def test_writer_text(global_storage):

    with BlockWriter.open("./tests/data/output.txt", fileversion=0, filetype='s') as writer:
        with writer.sub_block(TokenID.shape) as shape_block:
            shape_block.write_int(2134)
            with shape_block.sub_block(TokenID.shape) as shape_block2:
                shape_block2.write_int(2134)

    assert False


def test_writer_text_compressed(global_storage):

    with BlockWriter.open("./tests/data/output_compressed.txt", fileversion=0, filetype='s', is_unicode=False, is_compressed=True) as writer:
        with writer.sub_block(TokenID.shape) as shape_block:
            shape_block.write_int(2134)

    assert False


def test_writer_binary(global_storage):

    with BlockWriter.open("./tests/data/output.bin", fileversion=0, filetype='s', is_binary=True, is_unicode=False) as writer:
        with writer.sub_block(TokenID.shape) as shape_block:
            shape_block.write_int(2134)
            with shape_block.sub_block(TokenID.shape) as shape_block2:
                shape_block2.write_int(2134)

    assert False



def test_writer_binary_compressed(global_storage):

    with BlockWriter.open("./tests/data/output_compressed.bin", fileversion=0, filetype='s', is_binary=True, is_unicode=False, is_compressed=True) as writer:
        with writer.sub_block(TokenID.shape) as shape_block:
            shape_block.write_int(2134)

    assert False