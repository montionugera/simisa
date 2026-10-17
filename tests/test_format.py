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
from simisa import shape, world, terrain, BlockFormat, BlockWriter, TokenID
from simisa.shape import Vector


DEFAULT_FORMAT = BlockFormat()
MAX_ONE_ITEM_PER_LINE = BlockFormat(max_items_per_line=1)
MAX_ONE_ITEM_PER_LINE_ALLOW_SPACES = BlockFormat(max_items_per_line=1, allow_space_at_line_end=True)
MAX_TWO_ITEMS_PER_LINE = BlockFormat(max_items_per_line=2)
MAX_TEN_ITEMS_PER_LINE = BlockFormat(max_items_per_line=10)
MAX_ONE_ITEM_FIRST_LINE = BlockFormat(max_items_per_line=2, max_items_first_line=1)
NEWLINE_BEFORE_BLOCK = BlockFormat(newline_before_block=True)
NEWLINE_BEFORE_START = BlockFormat(newline_before_start=True)
NEWLINE_AFTER_START = BlockFormat(newline_after_start=True)
NEWLINE_AFTER_START_NO_INDENT = BlockFormat(newline_after_start=True, disable_inner_indent=True)
NEWLINE_AFTER_START_NO_INCREMENT = BlockFormat(newline_after_start=True, disable_inner_depth_increment=True)
NEWLINE_BEFORE_COUNT = BlockFormat(newline_before_count=True)
NEWLINE_AFTER_COUNT = BlockFormat(newline_after_count=True)
ENABLE_ZERO_COUNT_NEWLINE = BlockFormat(enable_zero_count_newline=True, newline_after_count=True)
NEWLINE_BEFORE_CLOSING = BlockFormat(newline_before_closing=True)
NEWLINE_AFTER_CLOSING = BlockFormat(newline_after_closing=True)



def write_empty_block(writer, block_format):
    with writer.sub_block(TokenID.normals, block_format=block_format) as normals_block:
        pass


def write_empty_count_block(writer, block_format):
    with writer.sub_block(TokenID.normals, block_format=block_format) as normals_block:
        normals_block.write_count(0)


def write_list_item_block(writer, block_format):
    with writer.sub_block(TokenID.normals, block_format=block_format) as normals_block:
        normals_block.write_count(3)

        normals = [
            Vector(0.1, 0.1, 1.1),
            Vector(0.1, 1.1, 0.1),
            Vector(1.1, 0.1, 0.1)
        ]

        for vector in normals:
            with normals_block.sub_block(TokenID.vector, block_format=block_format) as vector_block:
                vector_block.write_float(vector.x)
                vector_block.write_float(vector.y)
                vector_block.write_float(vector.z)


@pytest.mark.parametrize(
    ("block_format", "expected_output"),
    [
        (DEFAULT_FORMAT, "normals ( )"),
        (MAX_ONE_ITEM_PER_LINE, "normals ( )"),
        (MAX_ONE_ITEM_PER_LINE_ALLOW_SPACES, "normals ( )"),
        (MAX_TWO_ITEMS_PER_LINE, "normals ( )"),
        (MAX_TEN_ITEMS_PER_LINE, "normals ( )"),
        (MAX_ONE_ITEM_FIRST_LINE, "normals ( )"),
        (NEWLINE_BEFORE_BLOCK, "\r\nnormals ( )"),
        (NEWLINE_BEFORE_START, "normals\r\n( )"),
        (NEWLINE_AFTER_START, "normals (\r\n\t)"),
        (NEWLINE_AFTER_START_NO_INDENT, "normals (\r\n)"),
        (NEWLINE_AFTER_START_NO_INCREMENT, "normals (\r\n\t)"),
        (NEWLINE_BEFORE_COUNT, "normals ( )"),
        (NEWLINE_AFTER_COUNT, "normals ( )"),
        (ENABLE_ZERO_COUNT_NEWLINE, "normals ( )"),
        (NEWLINE_BEFORE_CLOSING, "normals ( )"),
        (NEWLINE_AFTER_CLOSING, "normals ( )"),
    ],
)
def test_empty_block(block_format, expected_output):
    formatted_text = BlockWriter.to_string(
        lambda writer: write_empty_block(writer, block_format),
        filetype="s",
        fileversion=1
    )

    assert formatted_text[32:] == expected_output


@pytest.mark.parametrize(
    ("block_format", "expected_output"),
    [
        (DEFAULT_FORMAT, "normals ( 0 )"),
        (MAX_ONE_ITEM_PER_LINE, "normals ( 0 )"),
        (MAX_ONE_ITEM_PER_LINE_ALLOW_SPACES, "normals ( 0 )"),
        (MAX_TWO_ITEMS_PER_LINE, "normals ( 0 )"),
        (MAX_TEN_ITEMS_PER_LINE, "normals ( 0 )"),
        (MAX_ONE_ITEM_FIRST_LINE, "normals ( 0 )"),
        (NEWLINE_BEFORE_BLOCK, "\r\nnormals ( 0 )"),
        (NEWLINE_BEFORE_START, "normals\r\n( 0 )"),
        (NEWLINE_AFTER_START, "normals (\r\n\t0 )"),
        (NEWLINE_AFTER_START_NO_INDENT, "normals (\r\n0 )"),
        (NEWLINE_AFTER_START_NO_INCREMENT, "normals (\r\n\t0 )"),
        (NEWLINE_BEFORE_COUNT, "normals ( 0 )"),
        (NEWLINE_AFTER_COUNT, "normals ( 0 )"),
        (ENABLE_ZERO_COUNT_NEWLINE, "normals ( 0\r\n\t)"),
        (NEWLINE_BEFORE_CLOSING, "normals ( 0 )"),
        (NEWLINE_AFTER_CLOSING, "normals ( 0 )"),
    ],
)
def test_empty_count_block(block_format, expected_output):
    formatted_text = BlockWriter.to_string(
        lambda writer: write_empty_count_block(writer, block_format),
        filetype="s",
        fileversion=1
    )

    assert formatted_text[32:] == expected_output



@pytest.mark.parametrize(
    ("block_format", "expected_output"),
    [
        (DEFAULT_FORMAT, "normals ( 3 vector ( 0.1 0.1 1.1 ) vector ( 0.1 1.1 0.1 ) vector ( 1.1 0.1 0.1 ) )"),
        (MAX_ONE_ITEM_PER_LINE, "normals ( 3 vector ( 0.1\r\n\t\t0.1\r\n\t\t1.1 )\r\n\tvector ( 0.1\r\n\t\t1.1\r\n\t\t0.1 )\r\n\tvector ( 1.1\r\n\t\t0.1\r\n\t\t0.1 ) )"),
        (MAX_ONE_ITEM_PER_LINE_ALLOW_SPACES, "normals ( 3 vector ( 0.1 \r\n\t\t0.1 \r\n\t\t1.1 ) \r\n\tvector ( 0.1 \r\n\t\t1.1 \r\n\t\t0.1 ) \r\n\tvector ( 1.1 \r\n\t\t0.1 \r\n\t\t0.1 ) )"),
        (MAX_TWO_ITEMS_PER_LINE, "normals ( 3 vector ( 0.1 0.1\r\n\t\t1.1 ) vector ( 0.1 1.1\r\n\t\t0.1 )\r\n\tvector ( 1.1 0.1\r\n\t\t0.1 ) )"),
        (MAX_TEN_ITEMS_PER_LINE, "normals ( 3 vector ( 0.1 0.1 1.1 ) vector ( 0.1 1.1 0.1 ) vector ( 1.1 0.1 0.1 ) )"),
        (MAX_ONE_ITEM_FIRST_LINE, "normals ( 3 vector ( 0.1\r\n\t\t0.1 1.1 )\r\n\tvector ( 0.1\r\n\t\t1.1 0.1 ) vector ( 1.1\r\n\t\t0.1 0.1 ) )"),
        (NEWLINE_BEFORE_BLOCK, "\r\nnormals ( 3\r\n\tvector ( 0.1 0.1 1.1 )\r\n\tvector ( 0.1 1.1 0.1 )\r\n\tvector ( 1.1 0.1 0.1 ) )"),
        (NEWLINE_BEFORE_START, "normals\r\n( 3 vector\r\n\t( 0.1 0.1 1.1 ) vector\r\n\t( 0.1 1.1 0.1 ) vector\r\n\t( 1.1 0.1 0.1 ) )"),
        (NEWLINE_AFTER_START, "normals (\r\n\t3 vector (\r\n\t\t0.1 0.1 1.1 ) vector (\r\n\t\t0.1 1.1 0.1 ) vector (\r\n\t\t1.1 0.1 0.1 ) )"),
        (NEWLINE_AFTER_START_NO_INDENT, "normals (\r\n3 vector (\r\n0.1 0.1 1.1 ) vector (\r\n0.1 1.1 0.1 ) vector (\r\n1.1 0.1 0.1 ) )"),
        (NEWLINE_AFTER_START_NO_INCREMENT, "normals (\r\n\t3 vector (\r\n\t0.1 0.1 1.1 ) vector (\r\n\t0.1 1.1 0.1 ) vector (\r\n\t1.1 0.1 0.1 ) )"),
        (NEWLINE_BEFORE_COUNT, "normals (\r\n\t3 vector ( 0.1 0.1 1.1 ) vector ( 0.1 1.1 0.1 ) vector ( 1.1 0.1 0.1 ) )"),
        (NEWLINE_AFTER_COUNT, "normals ( 3\r\n\tvector ( 0.1 0.1 1.1 ) vector ( 0.1 1.1 0.1 ) vector ( 1.1 0.1 0.1 ) )"),
        (ENABLE_ZERO_COUNT_NEWLINE, "normals ( 3\r\n\tvector ( 0.1 0.1 1.1 ) vector ( 0.1 1.1 0.1 ) vector ( 1.1 0.1 0.1 ) )"),
        (NEWLINE_BEFORE_CLOSING, "normals ( 3 vector ( 0.1 0.1 1.1\r\n\t) vector ( 0.1 1.1 0.1\r\n\t) vector ( 1.1 0.1 0.1\r\n\t)\r\n)"),
        (NEWLINE_AFTER_CLOSING, "normals ( 3 vector ( 0.1 0.1 1.1 )\r\n\tvector ( 0.1 1.1 0.1 )\r\n\tvector ( 1.1 0.1 0.1 )\r\n\t)"),
    ],
)
def test_list_item_block(block_format, expected_output):
    formatted_text = BlockWriter.to_string(
        lambda writer: write_list_item_block(writer, block_format),
        filetype="s",
        fileversion=1
    )

    assert formatted_text[32:] == expected_output



# For manual inspection of the output formatting
SKIP_MANUAL_INSPECTION_TESTS = False

def test_shapefile_default_format(global_storage, tmp_path):
    if SKIP_MANUAL_INSPECTION_TESTS:
        pytest.skip("Skipping tests for manual inspection of formats")
    
    original = shape.load(global_storage["shapefile_path"])
    output_path = "./tests/data/default_format.s"
    
    shape.dump(original, str(output_path), compressed=False)


def test_terrainfile_default_format(global_storage, tmp_path):
    if SKIP_MANUAL_INSPECTION_TESTS:
        pytest.skip("Skipping tests for manual inspection of formats")
    
    original = terrain.load(global_storage["terrainfile_binary_path"])
    output_path = "./tests/data/default_format.t"
    
    terrain.dump(original, str(output_path), compressed=False)


def test_worldfile_default_format(global_storage, tmp_path):
    if SKIP_MANUAL_INSPECTION_TESTS:
        pytest.skip("Skipping tests for manual inspection of formats")
    
    original = world.load(global_storage["worldfile2_path"])
    output_path = "./tests/data/default_format.w"
    
    world.dump(original, str(output_path), compressed=False)