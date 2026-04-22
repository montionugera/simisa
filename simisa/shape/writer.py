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

from .. import TokenID, Units
from ..writer import BlockWriter
from ..format import ListBlockFormat
from .models import *


def dump(
    shape: Shape,
    filepath: str,
    compressed: bool = False
) -> None:
    if not isinstance(shape, Shape):
        raise TypeError(f"Parameter 'shape' must be Shape, but got {type(shape).__name__}")

    with BlockWriter.open(
        filepath,
        filetype="s",
        fileversion="0",
        is_binary=compressed,
        is_unicode=not compressed,
        is_compressed=compressed,
    ) as writer:
        write_shape(writer, shape)


def dumps(
    shape: Shape
) -> str:
    if not isinstance(shape, Shape):
        raise TypeError(f"Parameter 'shape' must be Shape, but got {type(shape).__name__}")

    lambda writer: write_shape(writer, shape)

    shape_text = BlockWriter.to_string(
        writer,
        filetype="s",
        fileversion="0"
    )
    return shape_text



def write_shape(reader: BlockWriter, shape: Shape) -> None:
    pass