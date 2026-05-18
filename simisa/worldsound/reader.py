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

from typing import List

from .. import TokenID
from ..reader import BlockReader
from .models import *


# def load(filepath: str) -> Shape:
#     with BlockReader.open(filepath) as reader:
#         return read_shape(reader)


# def loads(shape_string: str) -> Shape:
#     reader = BlockReader.from_string(shape_string)
#     return read_shape(reader)


# def read_rit(reader: BlockReader) -> Shape:
#     # TODO
#     raise NotImplementedError()