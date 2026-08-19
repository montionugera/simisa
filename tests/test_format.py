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
from simisa import shape, BlockFormat, BlockWriter, TokenID
from simisa.shape import Vector


DEFAULT_FORMAT = BlockFormat()



def write_empty_block(writer, _):
    with writer.sub_block(TokenID.normals) as normals_block:
        pass


def write_empty_count_block(writer, _):
    with writer.sub_block(TokenID.normals) as normals_block:
        normals_block.write_count(0)


def write_list_item_block(writer, _):
    with writer.sub_block(TokenID.normals) as normals_block:
        normals_block.write_count(3)

        normals = [
            Vector(0.0, 0.0, 1.0),
            Vector(0.0, 1.0, 0.0),
            Vector(1.0, 0.0, 0.0)
        ]

        for vector in normals:
            with normals_block.sub_block(TokenID.vector) as vector_block:
                vector_block.write_float(vector.x)
                vector_block.write_float(vector.y)
                vector_block.write_float(vector.z)


def test_shape_default_format(global_storage, tmp_path):
    original = shape.load(global_storage["shapefile_path"])
    output_path = "./tests/data/default_format.s"
    
    shape.dump(original, str(output_path), compressed=False)
    
    assert True


@pytest.mark.parametrize(
    ("block_format", "expected_output"),
    [
        (DEFAULT_FORMAT, "normals (\n)"),
    ],
)
def test_empty_block(global_storage, block_format, expected_output):
    formatted_text = BlockWriter.to_string(
        lambda writer: write_empty_block(writer, None),
        filetype="s",
        fileversion=1
    )
    print(expected_output)

    assert formatted_text[32:] == expected_output


@pytest.mark.parametrize(
    ("block_format", "expected_output"),
    [
        (DEFAULT_FORMAT, "normals ( 0 \n)"),
    ],
)
def test_empty_count_block(global_storage, block_format, expected_output):
    formatted_text = BlockWriter.to_string(
        lambda writer: write_empty_count_block(writer, None),
        filetype="s",
        fileversion=1
    )
    print(expected_output)

    assert formatted_text[32:] == expected_output


@pytest.mark.parametrize(
    ("block_format", "expected_output"),
    [
        (DEFAULT_FORMAT, "normals ( 3 \n\tvector ( 0.0 0.0 1.0 )\n\tvector ( 0.0 1.0 0.0 )\n\tvector ( 1.0 0.0 0.0 )\n)"),
    ],
)
def test_list_item_block(global_storage, block_format, expected_output):
    formatted_text = BlockWriter.to_string(
        lambda writer: write_list_item_block(writer, None),
        filetype="s",
        fileversion=1
    )

    print(expected_output)

    assert formatted_text[32:] == expected_output