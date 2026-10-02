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
import codecs
import struct
import logging
import inspect
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
    File-like wrapper that compresses data on-the-fly using the DEFLATE algorithm via zlib.

    Compatible with Python IO wrappers such as `TextIOWrapper` and `BufferedWriter`.
    """
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.compressor = zlib.compressobj(level=6, wbits=zlib.MAX_WBITS)
        self._closed = False

    def writable(self):
        return True
    
    @property
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
    ) -> "BlockWriter":

        check_params = (
            ("filepath", filepath, str),
            ("filetype", filetype, str),
            ("fileversion", fileversion, int),
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

        if is_unicode:
            f.write(codecs.BOM_UTF16_LE)
        
        if is_compressed:
            f.write("SIMISA@F\x00\x00\x00\x00@@@@".encode(encoding))
            stream = CompressedStreamWriter(f)
        else:
            f.write("SIMISA@@@@@@@@@@".encode(encoding))
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
        fileversion: int
    ) -> str:

        check_params = (
            ("filetype", filetype, str),
            ("fileversion", fileversion, int),
        )

        for name, value, typ in check_params:
            if isinstance(value, typ):
                continue

            raise TypeError(
                f"Parameter '{name}' must be {typ.__name__}, "
                f"but got {type(value).__name__}"
            )
        
        write_fn_params = list(inspect.signature(write_fn).parameters.values())

        positional_params = (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )

        if not write_fn_params or write_fn_params[0].kind not in positional_params:
            raise TypeError("'write_fn' must accept a BlockWriter as its first parameter")

        stream = io.StringIO()

        writer = TextFileWriter(stream, filepath="<string>", encoding="utf-8")

        header = "SIMISA@@@@@@@@@@"
        subheader = f"JINX0{filetype}{fileversion}t______\r\n"

        stream.write(header)
        stream.write(subheader)

        write_fn(writer)
        writer.flush()

        text = stream.getvalue()
        writer.close()

        return text

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.flush()
        self.close()

    @contextmanager
    def sub_block(self, block_id: TokenID, block_label: Optional[str] = None, block_format: Optional[BlockFormat] = None):
        sub_block = self.begin_sub_block(block_id, block_label, block_format)

        try:
            yield sub_block
        finally:
            sub_block.end_sub_block()

    @abstractmethod
    def begin_sub_block(self, block_id: TokenID, block_label: Optional[str] = None, block_format: Optional[BlockFormat] = None):
        pass

    @abstractmethod
    def end_sub_block(self):
        pass
    
    @abstractmethod
    def write_count(self, value: int):
        pass

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

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def flush(self):
        pass


class TextBlockWriter(BlockWriter):

    def __init__(
        self,
        stream: Optional[io.TextIOBase | io.StringIO] = None,
        parent: Optional['TextBlockWriter'] = None,
        encoding: str = "utf-8"
    ):
        self.stream = stream
        self.parent = parent
        self.encoding = encoding
        self.depth = parent.depth if parent else 0
        self.indent_char = "\t"
        self.block_format: Optional[BlockFormat] = BlockFormat()
        self._buffer: List[str] = []
        self._writing_block = False
        self._items_on_line = 0
        self._closed = False

    def _trim_trailing_whitespace(self):
        while self._buffer:
            trimmed = self._buffer[-1].rstrip()

            if trimmed:
                self._buffer[-1] = trimmed
                break

            self._buffer.pop()

    def _write_indent(self):
        if not self.block_format.disable_inner_indent:
            self._buffer.append(f"{self.indent_char * self.depth}")

    def _write_newline(self):
        #self.parent._trim_trailing_whitespace()
        self._trim_trailing_whitespace()
        self._buffer.append("\n")
        self._write_indent()
        self._items_on_line = 0
        print(f"write newline, current buffer = {self._buffer}")

    def _write_value(self, text: str):
        if not isinstance(text, str):
            raise TypeError(f"Parameter 'text' must be str, but got {type(value).__name__}")
        
        if self.block_format.max_items_per_line is not None:
            if self._items_on_line >= self.block_format.max_items_per_line:
                self._write_newline()

        self._write_token(text)

        self._items_on_line += 1

        print(f"[value] _items_on_line: {self._items_on_line}")

    def _write_token(self, text: str):
        if not isinstance(text, str):
            raise TypeError(f"Parameter 'text' must be str, but got {type(value).__name__}")
        
        self._buffer.append(text)
        self._buffer.append(" ")
        
    def begin_sub_block(
        self,
        block_id: TokenID,
        block_label: Optional[str] = None,
        block_format: Optional[BlockFormat] = None
    ):
        if self._closed:
            raise ValueError("Cannot begin sub-block on a closed writer")

        self._items_on_line = self._items_on_line + 1

        sub_block = TextBlockWriter(stream=self.stream, parent=self, encoding=self.encoding)
        sub_block.block_format = block_format or BlockFormat()
        sub_block._writing_block = True
        sub_block._items_on_line = 0
        
        sub_block._write_token(f"{block_id.name}")

        print(f"{block_id.name} _items_on_line: {self._items_on_line}")

        if block_label is not None:
            sub_block._write_token(f"{block_label}")

        if sub_block.block_format.newline_before_start:
            sub_block._write_newline()

        sub_block._write_token("(")
        
        if sub_block.block_format.newline_after_start:
            sub_block._write_newline()

        sub_block.depth = self.depth + 1

        return sub_block
        
    def end_sub_block(self):
        if not self._writing_block or self._closed:
            return

        self.depth = self.depth - 1
        
        if self.block_format.newline_before_closing:
            self._write_newline()

        self._write_token(")")

        end_with_newline = False

        if self.block_format.max_items_per_line is not None:
            if self._items_on_line >= self.block_format.max_items_per_line:
                end_with_newline = True
        
        if self.block_format.newline_after_closing:
            end_with_newline = True
        
        if end_with_newline:
            self._write_newline()

        self._writing_block = False
        self._closed = True

        block_text = "".join(self._buffer)
        self._buffer = []

        if self.parent is not None:
            self.parent._buffer.append(block_text)
        elif self.stream is not None:
            if isinstance(self.stream, io.TextIOBase):
                self.stream.write(block_text)
            else:
                self.stream.write(block_text.encode(self.encoding))
        else:
            raise BlockWriterError("No output stream set for root writer, and no parent-writer.")

    def write_count(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        enable_count_newlines = (
            value == 0 and
            self.block_format.enable_zero_count_newline
        )

        if enable_count_newlines and self.block_format.newline_before_count:
            self._write_newline()

        self._write_token(str(value))

        if enable_count_newlines and self.block_format.newline_after_count:
            self._write_newline()

    def write_flags(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write_value(f"{value:08x}")

    def write_int(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write_value(str(value))

    def write_uint(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write_value(str(value))

    def write_float(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Parameter 'value' must be float or int, but got {type(value).__name__}")
        
        self._write_value(str(value))

    def write_string(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Parameter 'value' must be str, but got {type(value).__name__}")
        
        self._write_value(value)

    def write_comment(self, text: str):
        if not isinstance(text, str):
            raise TypeError(f"Parameter 'text' must be str, but got {type(text).__name__}")
        
        self._write_token("_SKIP")

        if self.block_format.newline_before_start:
            self._write_newline()

        self._write_token("(")
        
        if self.block_format.newline_after_start:
            self._write_newline()
        
        self._write_token(f"{text}")

        if self.block_format.newline_before_closing:
            self._write_newline()

        self._write_token(")")

        if self.block_format.newline_after_closing:
            self._write_newline()

    def flush(self):
        if self._closed:
            return

        if self.stream is not None and self._buffer:
            self._trim_trailing_whitespace()

            content = "".join(self._buffer)
            self._buffer = []

            if isinstance(self.stream, io.TextIOBase):
                self.stream.write(content)
            else:
                self.stream.write(content.encode(self.encoding))
                
            self.stream.flush()

    def close(self):
        if self._closed:
            return

        self.flush()
        self._closed = True


class TextFileWriter(TextBlockWriter):

    def __init__(
        self,
        stream: io.TextIOBase | io.StringIO,
        filepath: str,
        encoding="utf-8"
    ):
        super().__init__(stream=stream, parent=None, encoding=encoding)
        self.stream = stream
        self.filepath = filepath
        self.is_closed = False

    def flush(self):
        super().flush()
        self.is_closed = self._closed

    def close(self):
        super().close()
        
        if self.stream is not None and not self.stream.closed:
            # TODO patch size in header if compressed
            # with open(filepath, "r+b") as f:
            #     f.seek(8)  # after "SIMISA@F"
            #     f.write(writer._simisa_size.to_bytes(4, "little"))
            self.stream.close()
        
        self.is_closed = self._closed


class BinaryBlockWriter(BlockWriter):
    _UINT32 = struct.Struct("<I")
    _INT32 = struct.Struct("<i")
    _UINT16 = struct.Struct("<H")
    _FLOAT32 = struct.Struct("<f")
    _BLOCK_HEADER = struct.Struct("<HHI")

    def __init__(self):
        self.filename: str = ""
        self.stream: Optional[BinaryIO] = None
        self.token_offset: int = 0
        self.id: Optional[TokenID] = None
        self.flags: int = 0
        self.label: Optional[str] = None
        self.parent: Optional["BinaryBlockWriter"] = None
        self._buffer = io.BytesIO()
        self._writing_block: bool = False
        self._written_bytes: int = 0

    def _write_bytes(self, data: bytes) -> None:
        self._buffer.write(data)
        self._written_bytes += len(data)

    def begin_sub_block(self, block_id: TokenID, block_label: Optional[str] = None, block_format=None):
        sub_block = BinaryBlockWriter()
        sub_block.stream = self.stream
        sub_block.token_offset = self.token_offset
        sub_block.label = block_label
        sub_block.id = block_id
        sub_block.parent = self
        sub_block._buffer = io.BytesIO()
        sub_block._writing_block = True

        return sub_block

    def end_sub_block(self):
        if not self._writing_block:
            return

        self._writing_block = False

        payload = self._buffer.getvalue()

        if self.label:
            encoded_label = self.label.encode("utf-16-le")
            label_bytes = bytes([len(self.label)]) + encoded_label
        else:
            label_bytes = b"\x00"

        size = len(label_bytes) + len(payload)
        raw_id = self.id.value - self.token_offset

        header_bytes = self._BLOCK_HEADER.pack(raw_id, self.flags, size)
        block_bytes = header_bytes + label_bytes + payload

        self._written_bytes += len(block_bytes)

        if self.parent is not None:
            self.parent._buffer.write(block_bytes)
        elif self.stream is not None:
            self.stream.write(block_bytes)
        else:
            raise BlockWriterError("No output stream set for root writer, and no parent-writer.")

    def write_count(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self.write_int(value)

    def write_flags(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write_bytes(self._UINT32.pack(value))

    def write_int(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write_bytes(self._INT32.pack(value))

    def write_uint(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write_bytes(self._UINT32.pack(value))

    def write_float(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"Parameter 'value' must be float or int, but got {type(value).__name__}")
        
        self._write_bytes(self._FLOAT32.pack(value))

    def write_string(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"Parameter 'value' must be str, but got {type(value).__name__}")
        
        if not value:
            self._write_bytes(self._UINT16.pack(0))
            return
        
        encoded = value.encode("utf-16-le")
        self._write_bytes(self._UINT16.pack(len(value)))
        self._write_bytes(encoded)

    def write_comment(self, text: str):
        pass

    def flush(self):
        if self.stream:
            self.stream.flush()

    def close(self):
        if self.stream and not self.stream.closed:
            self.stream.close()


class BinaryFileWriter(BinaryBlockWriter):

    def __init__(self, stream: BinaryIO, filename: str, token_offset=0):
        super().__init__()
        self.filename = filename
        self.stream = stream
        self.token_offset = token_offset
        self.is_closed = False

    def _write(self, data: bytes) -> None:
        if self.stream is None:
            raise BlockWriterError("No output stream set")
        
        self.stream.write(data)
        self._written_bytes += len(data)

    def flush(self):
        if not self.is_closed and self.stream:
            self.stream.flush()

    def close(self):
        if self.is_closed or self.stream is None:
            return

        if self._buffer:
            # TODO patch size in header if compressed
            # with open(filepath, "r+b") as f:
            #     f.seek(8)  # after "SIMISA@F"
            #     f.write(writer._simisa_size.to_bytes(4, "little"))
            self.stream.write(self._buffer.getvalue())

        self.stream.close()
