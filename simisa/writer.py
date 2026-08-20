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
    ):
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
        fileversion: str
    ) -> str:

        stream = io.StringIO()

        writer = TextFileWriter(stream, filepath="<string>", encoding="utf-8")

        header = "SIMISA@@@@@@@@@@"
        subheader = f"JINX0{filetype}{fileversion}t______\r\n"

        stream.write(header)
        stream.write(subheader)
        write_fn(writer)

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

    def __init__(self, output_stream: Optional[TextIO] = None, parent: Optional['TextBlockWriter'] = None, encoding: str = "utf-8"):
        self._stream = output_stream
        self._parent = parent
        self._encoding = encoding
        self.depth = (parent.depth + 1) if parent else 0
        self.indent = "\t"
        self._block_format: Optional[BlockFormat] = None

        self._buffer = io.StringIO()
        self._writing_block = False
        self._items_on_line = 0
        self._closed = False

    def _emit(self, text: str):
        self._buffer.write(text)

    def begin_sub_block(self, block_id: TokenID, block_label: Optional[str] = None, block_format: Optional[BlockFormat] = None):
        if self._closed:
            raise ValueError("Cannot begin sub-block on a closed writer")

        sub_block = TextBlockWriter(output_stream=self._stream, parent=self, encoding=self._encoding)
        sub_block._block_format = block_format or BlockFormat()
        sub_block._writing_block = True
        
        #self._items_on_line = 0

        #if self._block_format.newline_before_start:
        #    self._emit("\n")

        #indent = "" if self._block_format.disable_inner_indent else self.indent * self.depth

        # if block_label is None:
        #     sub_block._emit(f"{indent}{block_id.name} (")
        # else:
        #     sub_block._emit(f"{indent}{block_id.name} {block_label} (")

        if block_label is None:
            sub_block._emit(f"{block_id.name} ( ")
        else:
            sub_block._emit(f"{block_id.name} {block_label} ( ")

        #if self._block_format.newline_after_start:
        #    sub_block._emit("\n")

        return sub_block

    def end_sub_block(self):
        if not self._writing_block or self._closed:
            return

        self._writing_block = False
        self._closed = True

        #if block_format.newline_before_closing:
        #    self._emit("\n")

        #indent = "" if block_format.disable_inner_indent else self.indent * self.depth
        #self._emit(f"{indent})")
        self._emit(f") ")

        #if block_format.newline_after_closing:
        #    self._emit("\n")

        #    #self._items_on_line = 0

        block_content = self._buffer.getvalue()
        self._buffer.close()

        if self._parent is not None:
            self._parent._emit(block_content)
        elif self._stream is not None:
            self._stream.write(block_content)
        else:
            raise BlockWriterError("No output stream set for root writer, and no parent for sub-writer.")

    def _write_token(self, text: str):
        if not self._writing_block:
            raise BlockWriterError("Cannot write token outside of an active block.")
        
        # if block_format.max_items_per_line is not None:
        #     if self._items_on_line > 0:
        #         self._emit(" ")

        #     self._emit(text)
        #     self._items_on_line += 1

        #     if self._items_on_line >= block_format.max_items_per_line:
        #         self._emit("\n")
        #         self._items_on_line = 0
        # else:
        #     self._emit(text + " ")

        self._emit(text + " ")

    def write_count(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        #if block_format.newline_before_count:
        #    self._emit("\n")

        self._write_token(str(value))

        #if block_format.newline_after_count:
        #    self._emit("\n")
        #    self._items_on_line = 0

    def write_flags(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write_token(f"{value:08x}")

    def write_int(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write_token(str(value))

    def write_uint(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write_token(str(value))

    def write_float(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Parameter 'value' must be float or int, but got {type(value).__name__}")
        
        self._write_token(str(value))

    def write_string(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Parameter 'value' must be str, but got {type(value).__name__}")
        
        self._write_token(value)

    def write_comment(self, text: str):
        if not isinstance(text, str):
            raise TypeError(f"Parameter 'text' must be str, but got {type(text).__name__}")
        
        self._emit("_SKIP ( " + text + " )\n")

    def flush(self):
        if self._closed:
            return

        if self._stream is not None:
            content = self._buffer.getvalue()
            self._buffer.close()
            self._buffer = io.StringIO()

            if content:
                if isinstance(self._stream, io.TextIOBase):
                    self._stream.write(content)
                else:
                    self._stream.write(content.encode(self._encoding))
                
            self._stream.flush()

    def close(self):
        if self._closed:
            return

        self.flush()
        self._closed = True


class TextFileWriter(TextBlockWriter):

    def __init__(self, output_stream: TextIO, filepath: str, encoding="utf-8"):
        super().__init__(output_stream=output_stream, parent=None, encoding=encoding)
        self.filepath = filepath
        self.is_closed = False

    def flush(self):
        super().flush()
        self.is_closed = self._closed

    def close(self):
        super().close()
        
        if self._stream is not None and not self._stream.closed:
            # TODO patch size in header if compressed
                # with open(filepath, "r+b") as f:
                #     f.seek(8)  # after "SIMISA@F"
                #     f.write(writer._simisa_size.to_bytes(4, "little"))
            self._stream.close()
        
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

        self._parent: Optional[BlockWriter] = None
        self._buffer = io.BytesIO()
        self._writing_block: bool = False
        self._written_bytes: int = 0

    def begin_sub_block(self, block_id: TokenID, block_label: Optional[str] = None, block_format=None):
        sub_block = BinaryBlockWriter()
        sub_block.stream = self.stream
        sub_block.token_offset = self.token_offset
        sub_block.label = block_label
        sub_block.id = block_id
        sub_block._parent = self
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

        if self._parent is not None:
            self._parent._buffer.write(block_bytes)
            return
        else:
            if self.stream is None:
                raise BlockWriterError("No output stream set")
            self.stream.write(block_bytes)

    def _write(self, data: bytes) -> None:
        self._buffer.write(data)
        self._written_bytes += len(data)

    def write_count(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self.write_int(value)

    def write_flags(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write(self._UINT32.pack(value))

    def write_int(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write(self._INT32.pack(value))

    def write_uint(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be int, but got {type(value).__name__}")
        
        self._write(self._UINT32.pack(value))

    def write_float(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"Parameter 'value' must be float or int, but got {type(value).__name__}")
        
        self._write(self._FLOAT32.pack(value))

    def write_string(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"Parameter 'value' must be str, but got {type(value).__name__}")
        
        if not value:
            self._write(self._UINT16.pack(0))
            return
        
        encoded = value.encode("utf-16-le")
        self._write(self._UINT16.pack(len(value)))
        self._write(encoded)

    def write_comment(self, text: str):
        pass

    def flush(self):
        if self.stream:
            self.stream.flush()

    def close(self):
        if self.stream and not self.stream.closed:
            self.stream.close()


class BinaryFileWriter(BinaryBlockWriter):

    def __init__(self, output_stream: BinaryIO, filename: str, token_offset=0):
        super().__init__()
        self.filename = filename
        self.stream = output_stream
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
            self.stream.write(self._buffer.getvalue())

        self.stream.close()
