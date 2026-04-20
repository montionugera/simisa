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

import io
import logging
from contextlib import contextmanager
from typing import Optional, BinaryIO, TextIO

from .token_id import TokenID

logger = logging.getLogger(__name__)


class StructuredBlockWriter:
    id: Optional[TokenID] = None
    label: Optional[str] = None

    @staticmethod
    def open(filename: str) -> "StructuredBlockWriter":
        raise NotImplementedError

    def begin_block(self, block_id: TokenID, label: Optional[str] = None):
        raise NotImplementedError

    def end_block(self):
        raise NotImplementedError

    @contextmanager
    def block(self, block_id: TokenID, label: Optional[str] = None):
        """
        Context manager for writing blocks safely.
        """

        self.begin_block(block_id, label)

        try:
            yield self
        finally:
            self.end_block()

    def write_flags(self, value: int):
        raise NotImplementedError

    def write_int(self, value: int):
        raise NotImplementedError

    def write_uint(self, value: int):
        raise NotImplementedError

    def write_float(self, value: float):
        raise NotImplementedError

    def write_string(self, value: str):
        raise NotImplementedError

    def write_vector3(self, x: float, y: float, z: float):
        raise NotImplementedError

    def write_comment(self, text: str):
        raise NotImplementedError

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


class UnicodeBlockWriter(StructuredBlockWriter):

    def __init__(self):
        self.stream: TextIO | None = None
        self.block_depth = 0

    def begin_block(self, block_id: TokenID, label: Optional[str] = None):
        raise NotImplementedError

    def end_block(self):
        raise NotImplementedError

    def write_flags(self, value: int):
        raise NotImplementedError

    def write_int(self, value: int):
        raise NotImplementedError

    def write_uint(self, value: int):
        raise NotImplementedError

    def write_float(self, value: float):
        raise NotImplementedError

    def write_string(self, value: str):
        raise NotImplementedError

    def write_comment(self, text: str):
        raise NotImplementedError


class UnicodeFileWriter(UnicodeBlockWriter):

    def __init__(self, output_stream: TextIO, filename: str, encoding="utf-8"):
        super().__init__()
        self.filename = filename
        self.stream = output_stream
        self.encoding = encoding
        self.is_closed = False

    def close(self):
        if not self.is_closed and self.stream:
            self.stream.close()
            self.is_closed = True


class BinaryBlockWriter(StructuredBlockWriter):

    def __init__(self):
        self.filename = ""
        self.stream: BinaryIO | None = None
        self.token_offset = 0
        self.block_stack: list[int] = []

    def begin_block(self, block_id: TokenID, label: Optional[str] = None):
        raise NotImplementedError

    def end_block(self):
        raise NotImplementedError

    def write_flags(self, value: int):
        raise NotImplementedError

    def write_int(self, value: int):
        raise NotImplementedError

    def write_uint(self, value: int):
        raise NotImplementedError

    def write_float(self, value: float):
        raise NotImplementedError

    def write_string(self, value: str):
        raise NotImplementedError


class BinaryFileWriter(BinaryBlockWriter):

    def __init__(self, output_stream: BinaryIO, filename: str, token_offset=0):
        super().__init__()
        self.filename = filename
        self.stream = output_stream
        self.token_offset = token_offset

    def close(self):
        if self.stream:
            self.stream.close()


class StructuredBlockWriterException(Exception):

    def __init__(self, writer: StructuredBlockWriter, message: str):
        super().__init__(message)
        self.writer = writer


"""
Example usage:

with writer.block(TokenID.vertex):

    writer.write_flags(flags)
    writer.write_int(ipoint)
    writer.write_int(inormal)
    writer.write_flags(color1)
    writer.write_flags(color2)

    with writer.block(TokenID.vertex_uvs):
        writer.write_int(len(uvs))
        for uv in uvs:
            writer.write_int(uv)
"""