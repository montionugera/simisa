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
from typing import Optional, Iterator, BinaryIO, TextIO

from .header import is_compressed
from .token_id import TokenID

logger = logging.getLogger(__name__)


class InvalidSimisaHeaderError(Exception):
    """Raised when a simisa header is invalid."""
    pass


class InvalidSimisaSubheaderError(Exception):
    """Raised when a simisa subheader is invalid."""
    pass


class StructuredBlockReader:

    @staticmethod
    def open(filepath: str) -> "StructuredBlockReader":
        compressed = is_compressed(filepath)

        if compressed is None:
            raise InvalidSimisaHeaderError()

        with open(filepath, "rb") as f:
            bom = f.read(2)
            is_unicode = (bom == codecs.BOM_UTF16_LE)

            if is_unicode:
                header_bytes = f.read(32)
                header = header_bytes[:16].decode("utf-16-le")
            else:
                header_bytes = bom + f.read(14)
                header = header_bytes[:8].decode("ascii", errors="ignore")

            if compressed:
                f.read(2)
                decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
                file_stream = io.BytesIO(decompressor.decompress(f.read()))
            elif header.startswith("\r\n"):
                if is_unicode:
                    f.read(4)
                else:
                    f.read(2)
                file_stream = f
            else:
                file_stream = f

            if is_unicode:
                subheader_bytes = file_stream.read(32)
                subheader = subheader_bytes[:16].decode("utf-16-le")
            else:
                subheader_bytes = file_stream.read(16)
                subheader = subheader_bytes[:8].decode("ascii", errors="ignore")

            if len(subheader) < 5:
                raise InvalidSimisaSubheaderError()

            self.filetype = subheader[7]

            if subheader[7] == 't':
                return UnicodeFileReader(fb, filepath, "utf-16-le" if is_unicode else "ascii");
            elif subheader[7] != 'b':
                raise Exception("Unrecognized subheader \"" + subheader + "\" in " + filepath);

            if subheader[5] == 'w':
                return BinaryFileReader(fb, filepath, 300);
            else:
                return BinaryFileReader(fb, filepath, 0);

    def read_sub_block(self) -> "StructuredBlockReader":
        raise NotImplementedError

    def skip(self) -> None:
        raise NotImplementedError

    def end_of_block(self) -> bool:
        raise NotImplementedError

    def verify_end_of_block(self) -> None:
        raise NotImplementedError

    def verify_id(self, desired_id: TokenID) -> None:
        raise NotImplementedError

    @contextmanager
    def block(self, expected_id: TokenID | None = None):
        """
        Context manager that verifies ID and end-of-block automatically.
        """
        if expected_id is not None:
            self.verify_id(expected_id)

        try:
            yield self
        finally:
            self.verify_end_of_block()

    @contextmanager
    def sub_block(self, expected_id: TokenID | None = None):
        """
        Read and validate a nested sub-block.
        """
        sub = self.read_sub_block()

        if expected_id is not None:
            sub.verify_id(expected_id)

        try:
            yield sub
        finally:
            sub.verify_end_of_block()

    def __iter__(self) -> Iterator["StructuredBlockReader"]:
        while not self.end_of_block():
            yield self.read_sub_block()

    def read_flags(self) -> int:
        raise NotImplementedError

    def read_int(self) -> int:
        raise NotImplementedError

    def read_uint(self) -> int:
        raise NotImplementedError

    def read_float(self) -> float:
        raise NotImplementedError

    def read_string(self) -> str:
        raise NotImplementedError

    def read_vector3(self):
        raise NotImplementedError

    def expect_comment(self):
        raise NotImplementedError

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


class UnicodeBlockReader(StructuredBlockReader):

    def __init__(self):
        self.stream: TextIO | None = None
        self.at_end_of_block = False
        self.id: TokenID | None = None
        self.label: str | None = None

    def read_sub_block(self) -> StructuredBlockReader:
        raise NotImplementedError

    def skip(self):
        raise NotImplementedError

    def end_of_block(self) -> bool:
        raise NotImplementedError

    def verify_end_of_block(self):
        raise NotImplementedError

    def read_flags(self) -> int:
        raise NotImplementedError

    def read_int(self) -> int:
        raise NotImplementedError

    def read_uint(self) -> int:
        raise NotImplementedError

    def read_float(self) -> float:
        raise NotImplementedError

    def read_string(self) -> str:
        raise NotImplementedError


class UnicodeFileReader(UnicodeBlockReader):

    def __init__(self, input_stream: TextIO, filename: str, encoding: str):
        super().__init__()
        self.filename = filename
        self.stream = input_stream
        self.encoding = encoding
        self.is_closed = False

    def skip(self):
        raise NotImplementedError

    def verify_end_of_block(self):
        raise NotImplementedError

    def end_of_block(self) -> bool:
        raise NotImplementedError

    def close(self):
        if not self.is_closed and self.stream:
            self.stream.close()
            self.is_closed = True


class BinaryBlockReader(StructuredBlockReader):

    def __init__(self):
        self.filename: str = ""
        self.stream: BinaryIO | None = None
        self.token_offset = 0
        self.remaining_bytes = 0
        self.flags = 0

    def read_sub_block(self) -> StructuredBlockReader:
        raise NotImplementedError

    def skip(self):
        raise NotImplementedError

    def end_of_block(self) -> bool:
        raise NotImplementedError

    def verify_end_of_block(self):
        raise NotImplementedError

    def read_flags(self) -> int:
        raise NotImplementedError

    def read_int(self) -> int:
        raise NotImplementedError

    def read_uint(self) -> int:
        raise NotImplementedError

    def read_float(self) -> float:
        raise NotImplementedError

    def read_string(self) -> str:
        raise NotImplementedError


class BinaryFileReader(BinaryBlockReader):

    def __init__(self, input_stream: BinaryIO, filename: str, token_offset: int):
        super().__init__()
        self.filename = filename
        self.stream = input_stream
        self.token_offset = token_offset
        self._size = 0

    def skip(self):
        raise NotImplementedError

    def end_of_block(self) -> bool:
        raise NotImplementedError

    def verify_end_of_block(self):
        raise NotImplementedError

    def close(self):
        if self.stream:
            self.stream.close()


class StructuredBlockReaderException(Exception):

    def __init__(self, reader: StructuredBlockReader, message: str):
        super().__init__(message)
        self.reader = reader


class STFReader:
    end_block_comment_sentinel = "#\u00b6"

    def __init__(self, filename=None, use_tree=False, input_stream=None, encoding="utf-8"):
        self.block_depth = 0
        self.tree = [] if use_tree else None
        self.encoding = encoding
        self.filename = filename
        self.stream = input_stream

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        pass

    def read_item(self):
        raise NotImplementedError

    def step_back_one_item(self):
        raise NotImplementedError

    def must_match(self, target):
        raise NotImplementedError

    def end_of_block(self):
        raise NotImplementedError

    def skip_block(self):
        raise NotImplementedError

    def skip_rest_of_block(self):
        raise NotImplementedError

    def read_string(self):
        raise NotImplementedError

    def read_hex(self, default_value=None):
        raise NotImplementedError

    def read_int(self, default_value=None):
        raise NotImplementedError

    def read_uint(self, default_value=None):
        raise NotImplementedError

    def read_float(self, valid_units=None, default_value=None):
        raise NotImplementedError

    def read_double(self, default_value=None):
        raise NotImplementedError

"""
Example usage:

with reader.block(TokenID.vertex):

    flags = reader.read_flags()
    ipoint = reader.read_int()
    inormal = reader.read_int()
    color1 = reader.read_flags()
    color2 = reader.read_flags()

    with reader.sub_block(TokenID.vertex_uvs) as sub:
        count = sub.read_int()
        uvs = [sub.read_int() for _ in range(count)]



Example of iteration over blocks:

for block in reader:
    if block.id == TokenID.vertex:
        ...
    else:
        block.skip()


"""