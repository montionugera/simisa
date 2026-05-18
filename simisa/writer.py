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
import zlib
import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional, BinaryIO, TextIO, Callable, Any

from .format import BlockFormat
from .token_id import TokenID

logger = logging.getLogger(__name__)



class BlockWriterError(Exception):
    """Raised when a block writer encounters an error or malformed data."""
    pass


class CompressedStreamWriter(io.RawIOBase):
    """
    Wrapper to write to a raw zlib DEFLATE-compressed stream.

    Provides a file-like interface that compresses data on-the-fly.
    Compatible with Python IO wrappers such as `TextIOWrapper` and `BufferedWriter`.
    """
    CHUNK_SIZE = 65536

    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
        self._closed = False

    def writable(self):
        return True

    def closed(self):
        return self._closed

    def write(self, data: bytes):
        if self._closed:
            raise ValueError("write to closed file")

        if not data:
            return 0

        compressed = self.compressor.compress(data)

        if compressed:
            self.fileobj.write(compressed)
        
        return len(data)

    def flush(self):
        if self._closed:
            return

        tail = self.compressor.flush(zlib.Z_SYNC_FLUSH)

        if tail:
            self.fileobj.write(tail)
        
        self.fileobj.flush()

    def close(self):
        if not self._closed:
            try:
                tail = self.compressor.flush(zlib.Z_FINISH)

                if tail:
                    self.fileobj.write(tail)
                
                self.fileobj.flush()
            finally:
                self.fileobj.close()
                self.compressor = None
                self._closed = True
        
        super().close()


class BlockWriter(ABC):
    """
    Structured streaming writer for SIMISA block files.

    Supports writing streams that are:
    - Compressed (zlib DEFLATE) or uncompressed
    - UTF-16 LE or ASCII encoded
    - Binary or text formatted
    """

    @staticmethod
    def open(
        filepath: str,
        *,
        filetype: str,
        fileversion: str,
        is_binary: bool = False,
        is_unicode: bool = True,
        is_compressed: bool = False
    ):
        check_params = (
            ("filepath", filepath, str),
            ("filetype", filetype, str),
            ("fileversion", fileversion, str),
            ("is_binary", is_binary, bool),
            ("is_unicode", is_unicode, bool),
            ("is_compressed", is_compressed, bool),
        )

        for name, value, typ in check_params:
            if isinstance(value, typ):
                continue

            raise TypeError(
                f"Parameter '{name}' must be {typ.__name__}, "
                f"but got {type(value).__name__}"
            )
        
        fileformat = 'b' if is_binary else 't'
        subheader = f"JINX0{filetype}{fileversion}{fileformat}______\r\n"
        encoding = "utf-16-le" if is_unicode else "ascii"

        f = open(filepath, "wb")

        if is_compressed:
            f.write(b"SIMISA@F")
            f.write(b"\x97\x86\r\x00")
            f.write(b"@@@@")
            stream = CompressedStreamWriter(f)
        else:
            if is_unicode:
                f.write(codecs.BOM_UTF16_LE)
            f.write(("SIMISA@@@@@@@@@@").encode(encoding))
            stream = f

        stream.write(subheader.encode(encoding))

        if is_binary:
            token_offset = 300 if filetype == "w" else 0
            return BinaryFileWriter(stream, filepath, token_offset)

        return TextFileWriter(stream, filepath, encoding)
    
    @staticmethod
    def to_string(
        write_fn: Callable[["BlockWriter"], Any],
        *,
        filetype: str,
        fileversion: str
    ) -> str:

        stream = io.StringIO()

        writer = TextFileWriter(stream, filepath="<string>", encoding="utf-8")

        header = "SIMISA@@@@@@@@@@"
        subheader = f"JINX0{filetype}{fileversion}t______\r\n"

        stream.write(header)
        stream.write(subheader)
        write_fn(writer)

        writer.close()
        return stream.getvalue()

    @abstractmethod
    def begin_block(self, block_id: TokenID, label: Optional[str] = None):
        pass

    @abstractmethod
    def end_block(self):
        pass

    @contextmanager
    def block(self, block_id: TokenID, label: Optional[str] = None):
        self.begin_block(block_id, label)

        try:
            yield self
        finally:
            self.end_block()

    @abstractmethod
    def write_flags(self, value: int):
        pass

    @abstractmethod
    def write_int(self, value: int):
        pass

    @abstractmethod
    def write_uint(self, value: int):
        pass

    @abstractmethod
    def write_float(self, value: float):
        pass

    @abstractmethod
    def write_string(self, value: str):
        pass

    @abstractmethod
    def write_comment(self, text: str):
        pass

    #@abstractmethod # TODO Use this along with begin_block and end_block to manage text list formats
    def write_count(self, text: str):
        pass

    @abstractmethod # TODO delete this
    def write_list(
        self,
        block_id: TokenID,
        values,
        *,
        format: BlockFormat,
        item_writer: Optional[Callable[["BlockWriter", Any], None]] = None,
    ):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def flush(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.flush()
        self.close()


class TextBlockWriter(BlockWriter):

    def __init__(self):
        self.stream: TextIO | None = None
        self.depth = 0

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
            self.stream.write("    " * self.depth)

    def write_list(
        self,
        block_id: TokenID,
        values,
        *,
        format: BlockFormat,
        item_writer: Optional[Callable] = None,
    ):
        self.begin_block(block_id)

        count = int(len(values) * format.count_multiplier)
        self.write_int(count)

        if format.newline_after_header and self.stream:
            self.stream.write("\n")

        self.depth += 1

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

        self.depth -= 1

        if format.newline_before_closing and self.stream:
            self.stream.write("\n")

        self.end_block()


class TextFileWriter(TextBlockWriter):

    def __init__(self, output_stream: TextIO, filename: str, encoding="utf-8"):
        super().__init__()
        self.filename = filename
        self.stream = output_stream
        self.encoding = encoding
        self.is_closed = False

    def flush(self):
        if not self.is_closed and self.stream:
            self.stream.flush()
    
    def close(self):
        if not self.is_closed and self.stream:
            self.stream.close()
            self.is_closed = True


class BinaryBlockWriter(BlockWriter):

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
        format: BlockFormat,
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
        self.is_closed = False

    def flush(self):
        if not self.is_closed and self.stream:
            self.stream.flush()
    
    def close(self):
        if not self.is_closed and self.stream:
            self.stream.close()
            self.is_closed = True


class BlockWriterException(Exception):

    def __init__(self, writer: BlockWriter, message: str):
        super().__init__(message)
        self.writer = writer

