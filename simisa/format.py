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

from typing import Optional
from dataclasses import dataclass


@dataclass
class BlockFormat:
    """
    Parameters for configuring formatting of blocks.

    Used when writing files in text format. Ignored when writing binary files.

    Example:
        >>> UV_LIST = BlockFormat(
        ...     max_items_per_line=None,
        ...     disable_inner_indent=True,
        ...     newline_after_start=False,
        ...     newline_after_count=False,
        ...     newline_before_closing=False
        ... )
        >>>
        >>> with writer.sub_block(TokenID.vertex) as vertex_block:
        ...     vertex_block.write_flags(flags)
        ...     vertex_block.write_int(point_index)
        ...     vertex_block.write_int(normal_index)
        ...     vertex_block.write_flags(color1)
        ...     vertex_block.write_flags(color2)
        ...
        ...     with vertex_block.sub_block(TokenID.vertex_uvs, block_format=UV_LIST) as vertex_uvs_block:
        ...         vertex_uvs_block.write_count(len(uvs))
        ...         for uv_index in uvs:
        ...             vertex_uvs_block.write_int(uv_index)
    """
    max_items_per_line: Optional[int] = None
    disable_inner_indent: bool = False
    newline_before_start: bool = False
    newline_after_start: bool = False
    newline_before_count: bool = False
    newline_after_count: bool = True
    enable_zero_count_newline: bool = False
    newline_before_closing: bool = False
    newline_after_closing: bool = False
