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
from typing import Optional, BinaryIO, TextIO, Callable, Any

from .format import ListFormat
from .token_id import TokenID

logger = logging.getLogger(__name__)


class CompressedWriteStream:
    def __init__(self, file, compressor):
        self.file = file
        self.compressor = compressor

    def write(self, data: bytes):
        chunk = self.compressor.compress(data)
        if chunk:
            self.file.write(chunk)

    def flush(self):
        chunk = self.compressor.flush()
        if chunk:
            self.file.write(chunk)


class StructuredBlockWriter:
    @staticmethod
    def open(filepath: str,
            *,
            filetype: str,
            filetype_version: str,
            is_binary: bool = False,
            is_unicode: bool = True,
            is_compressed: bool = False
        ):

        subheader = (
            "JINX0",
            filetype,
            filetype_version,
            f"{'b' if is_binary else 't'}",
            "______"
        )

        f = open(filepath, "wb")
        encoding = "utf-16-le" if is_unicode else "ascii"

        if is_compressed:
            f.write(b"SIMISA@F")
            f.write(b"\x97\x86\r\x00")
            f.write(b"@@@@")
            compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
            stream = CompressedWriteStream(f, compressor)
        else:
            if is_unicode:
                f.write(codecs.BOM_UTF16_LE)
            f.write(("SIMISA@@@@@@@@@@").encode(encoding))
            stream = f

        stream.write(subheader.encode(encoding))

        if subheader[7] == "t":
            return UnicodeFileWriter(stream, filepath, encoding)

        return BinaryFileWriter(
            stream,
            filepath,
            300 if subheader[5] == "w" else 0
        )

    def begin_block(self, block_id: TokenID, label: Optional[str] = None):
        raise NotImplementedError

    def end_block(self):
        raise NotImplementedError

    @contextmanager
    def block(self, block_id: TokenID, label: Optional[str] = None):
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

    def write_list(
        self,
        block_id: TokenID,
        values,
        *,
        format: ListFormat,
        item_writer: Optional[Callable[["StructuredBlockWriter", Any], None]] = None,
    ):
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

    def _indent(self):
        if self.stream:
            self.stream.write("    " * self.block_depth)

    def write_list(
        self,
        block_id: TokenID,
        values,
        *,
        format: ListFormat,
        item_writer: Optional[Callable] = None,
    ):
        self.begin_block(block_id)

        count = int(len(values) * format.count_multiplier)
        self.write_int(count)

        if format.newline_after_header and self.stream:
            self.stream.write("\n")

        self.block_depth += 1

        if item_writer is None:
            item_writer = self.write_int

        items_per_line = format.items_per_line
        line_count = 0

        for item in values:

            if items_per_line is not None and line_count >= items_per_line:
                if self.stream:
                    self.stream.write("\n")
                line_count = 0

            if not format.disable_inner_indent:
                self._indent()

            item_writer(self, item)

            line_count += 1

        self.block_depth -= 1

        if format.newline_before_closing and self.stream:
            self.stream.write("\n")

        self.end_block()


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

    def write_list(
        self,
        block_id: TokenID,
        values,
        *,
        format: ListFormat,
        item_writer: Optional[Callable] = None,
    ):
        self.begin_block(block_id)

        self.write_int(len(values))

        if item_writer is None:
            for v in values:
                self.write_int(v)
        else:
            for v in values:
                item_writer(self, v)

        self.end_block()


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

writer.write_list(
    TokenID.vertex_uvs,
    uvs,
    format=UV_LIST
)

writer.write_list(
    TokenID.vertices,
    vertices,
    format=VERTEX_LIST,
    item_writer=lambda w, v: (
        w.begin_block(TokenID.vertex),
        w.write_int(v.point),
        w.write_int(v.normal),
        w.write_flags(v.color),
        w.end_block()
    )
)

"""
