"""
This file is part of Simisa.

This code is loosely based on `SBR.cs` from the `Orts.Parsers.Msts`
namespace within the Open Rails codebase.

Copyright (C) 2013, 2014, 2015 by the Open Rails project
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
import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional, Iterator, BinaryIO, TextIO

from .header import is_compressed
from .token_id import TokenID
from .stf import STFReader

logger = logging.getLogger(__name__)


class SimisaHeaderError(Exception):
    """Raised when a simisa header is missing or invalid."""
    pass


class SimisaSubheaderError(Exception):
    """Raised when a simisa subheader is missing or invalid."""
    pass


class BlockReaderError(Exception):
    """Raised when a block reader encounters an error or malformed data."""
    pass


class BlockReader(ABC):

    @staticmethod
    def open(filepath: str) -> "BlockReader":
        compressed = is_compressed(filepath)

        if compressed is None:
            raise SimisaHeaderError(f"Unrecognized header in {filepath}")

        f = open(filepath, "rb")

        bom = f.read(2)
        is_unicode = (bom == codecs.BOM_UTF16_LE)
        encoding = "utf-16-le" if is_unicode else "ascii"

        if is_unicode:
            header_bytes = f.read(32)
            header = header_bytes[:16].decode(encoding)
        else:
            header_bytes = bom + f.read(14)
            header = header_bytes[:8].decode(encoding, errors="ignore")

        if compressed:
            f.read(2)
            decompressor = zlib.decompressobj(wbits=-zlib.MAX_WBITS)
            stream = io.BytesIO(decompressor.decompress(f.read()))
        else:
            if header.startswith("\r\n"):
                f.read(4 if is_unicode else 2)
            stream = f

        subheader_bytes = stream.read(32 if is_unicode else 16)
        subheader = subheader_bytes[:16 if is_unicode else 8].decode(encoding, errors="ignore")

        if len(subheader) < 5:
            raise SimisaSubheaderError(f"Subheader '{subheader}' too short in {filepath}")

        filetype = subheader[5]
        fileversion = int(subheader[6])
        fileformat = subheader[7]

        if fileformat == "b":
            token_offset = 300 if filetype == "w" else 0
            return BinaryFileReader(stream, filepath, filetype, fileversion, token_offset)

        if fileformat != "t":
            raise SimisaSubheaderError(f"Unrecognized subheader '{subheader}' in {filepath}")
        
        return TextFileReader(stream, filepath, filetype, fileversion, encoding)

    @staticmethod
    def from_string(data: str) -> "BlockReader":
        if not isinstance(data, str):
            raise TypeError(f"Parameter 'data' must be str, but got {type(data).__name__}")

        data = data.lstrip("\ufeff")

        stream = io.StringIO(data)

        header = stream.read(16)
        header = header.lstrip("\r\n")

        valid_headers = [
            "SIMISA@@",
        ]

        if header.startswith("SIMISA@F"):
            raise SimisaHeaderError("Compressed data is not supported with 'from_string'")
        
        if not any(header.startswith(h) for h in valid_headers):
            raise SimisaHeaderError(f"Unrecognized header '{header}' in string input")

        subheader = stream.read(16)

        if len(subheader) < 5:
            raise SimisaSubheaderError("Subheader too short in string input")

        filetype = subheader[5]
        fileversion = int(subheader[6])
        fileformat = subheader[7]

        if fileformat == "b":
            raise SimisaSubheaderError("Binary data is not supported with 'from_string'")

        if fileformat != "t":
            raise SimisaSubheaderError(f"Unrecognized subheader '{subheader}' in string input")

        return TextFileReader(stream, "<string>", filetype, fileversion, "utf-8")

    def __iter__(self) -> Iterator["BlockReader"]:
        while not self.end_of_block():
            yield self.read_sub_block()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    @contextmanager
    def sub_block(self, expected_id: TokenID | None = None):
        """
        Read and validate a nested sub-block.
        """
        sub_block = self.read_sub_block()

        if expected_id is not None:
            sub_block.verify_id(expected_id)

        try:
            yield sub_block
        finally:
            sub_block.verify_end_of_block()

    def verify_id(self, desired_id: TokenID) -> None:
        if self.id != desired_id:
            logger.info(f"Expected block {desired_id}; got {self.id}")
    
    def expect_comment(self) -> None:
        if self.id == TokenID.comment:
            self.skip()
        else:
            logger.info(f"Expected block comment; got {self.id}")
            self.skip()

    @abstractmethod
    def read_sub_block(self) -> "BlockReader":
        pass

    @abstractmethod
    def skip(self) -> None:
        pass

    @abstractmethod
    def end_of_block(self) -> bool:
        pass

    @abstractmethod
    def verify_end_of_block(self) -> None:
        pass

    @abstractmethod
    def read_flags(self) -> int:
        pass

    @abstractmethod
    def read_int(self) -> int:
        pass

    @abstractmethod
    def read_uint(self) -> int:
        pass

    @abstractmethod
    def read_float(self) -> float:
        pass

    @abstractmethod
    def read_string(self) -> str:
        pass

    @abstractmethod
    def close(self):
        pass


class TextBlockReader(BlockReader):
    _token_table: dict[str, TokenID] | None = None

    def __init__(self):
        self.stfreader: STFReader | None = None
        self.at_end_of_block: bool = False
        self.id: TokenID | None = None
        self.label: str | None = None
    
    @classmethod
    def _init_token_table(cls):
        if cls._token_table is not None:
            return

        cls._token_table = {
            name.lower(): token
            for name, token in TokenID.__members__.items()
        }
    
    def _get_token_id(self, token: str) -> TokenID:
        if self._token_table is None:
            self._init_token_table()

        t = token.lower()

        token_id = self._token_table.get(t)
        if token_id is not None:
            return token_id

        if token.lower() == "skip":
            return TokenID.comment
        if token.lower() == "comment":
            return TokenID.comment
        if token.startswith("#"):
            return TokenID.comment

        logger.warning(f"Skipped unknown token {token}")
        return TokenID.comment

    def read_sub_block(self) -> BlockReader:
        block = TextBlockReader()
        block.f = self.stfreader

        token = self.stfreader.read_item()

        if token == "(":
            block.id = TokenID.comment
            return block

        block.id = self._get_token_id(token)

        if token == ")":
            logger.warning("Ignored extra close bracket")
            return block

        token = self.stfreader.read_item()

        if token != "(":
            block.label = token
            self.stfreader.verify_start_of_block()

        return block

    def skip(self):
        if self.at_end_of_block:
            return

        depth = 1

        while depth > 0:
            token = self.stfreader.read_item()

            if token == "":
                logger.warning("Unexpected end of file")
                self.at_end_of_block = True
                return

            if token == "(":
                depth += 1
            elif token == ")":
                depth -= 1

        self.at_end_of_block = True

    def end_of_block(self) -> bool:
        return (
            self.at_end_of_block
            or self.stfreader.peek_past_whitespace() == ")"
            or self.stfreader.eof()
        )

    def verify_end_of_block(self):
        if self.at_end_of_block:
            return

        s = self.stfreader.read_item()

        if s.startswith("#") or s.lower() == "comment":
            self.skip()
            return

        if s != ")":
            logger.warning(f"Expected end of block; got '{s}'")

        self.at_end_of_block = True

    def read_flags(self) -> int:
        return self.stfreader.read_hex(None)

    def read_int(self) -> int:
        return self.stfreader.read_int(None)

    def read_uint(self) -> int:
        return self.stfreader.read_uint(None)

    def read_float(self) -> float:
        return self.stfreader.read_float(None)

    def read_string(self) -> str:
        return self.stfreader.read_item()


class TextFileReader(TextBlockReader):

    def __init__(
        self,
        input_stream: TextIO,
        filepath: str,
        filetype: str,
        fileversion: int,
        encoding: str
    ):
        super().__init__()

        self.filepath = filepath
        self.filetype = filetype
        self.fileversion = fileversion
        self.encoding = encoding
        self.stream = input_stream

        self.is_closed = False
        self.at_end_of_block = False

        self.stfreader = STFReader(
            input_stream=input_stream,
            filename=filepath,
            encoding=encoding
        )

    def skip(self):
        if self.is_closed:
            return

        self.stfreader.close() if hasattr(self.stfreader, "close") else None
        self.is_closed = True
        self.at_end_of_block = True

    def verify_end_of_block(self):
        if self.is_closed:
            return

        s = self.stfreader.read_item()
        extra_data = s

        if s != "":
            while s != "":
                if s != ")":
                    logger.warning(
                        f"Expected end of file; got '{s}' in {self.filepath}"
                    )
                    return

                s = self.stfreader.read_item()

    def end_of_block(self) -> bool:
        if self.is_closed or self.at_end_of_block:
            return True

        if hasattr(self.stfreader, "peek_past_whitespace"):
            return self.stfreader.peek_past_whitespace() == -1

        if hasattr(self.stfreader, "eof"):
            return self.stfreader.eof()

        return False

    def close(self):
        if not self.is_closed:
            if self.stfreader:
                self.stfreader.close()
            self.is_closed = True


class BinaryBlockReader(BlockReader):

    def __init__(self):
        self.filepath: str = ""
        self.stream: BinaryIO | None = None
        self.token_offset = 0
        self.remaining_bytes = 0
        self.flags = 0
        self.id: TokenID | None = None
        self.label: str | None = None

    @classmethod
    def from_parent(cls, parent: "BinaryBlockReader", size: int) -> "BinaryBlockReader":
        sub = cls()

        sub.stream = parent.stream
        sub.filepath = parent.filepath
        sub.token_offset = parent.token_offset

        sub.remaining_bytes = size
        sub.flags = 0
        sub.id = None
        sub.label = None

        return sub

    def _read(self, n: int) -> bytes:
        if self.stream is None:
            raise RuntimeError("Stream is not initialized")

        data = self.stream.read(n)
        if len(data) != n:
            raise SimisaSubheaderError("Unexpected EOF in block")

        self.remaining_bytes -= n
        return data

    def read_sub_block(self) -> "BlockReader":
        if self.stream is None:
            raise RuntimeError("Stream is not initialized")

        if self.remaining_bytes < 8:
            raise SimisaSubheaderError("Not enough bytes for sub-block header")

        raw_id = int.from_bytes(self._read(2), "little")
        raw_flags = int.from_bytes(self._read(2), "little")
        size = int.from_bytes(self._read(4), "little")

        sub = BinaryFileReader.__new__(BinaryFileReader)

        sub.stream = self.stream
        sub.filepath = self.filepath

        sub.token_offset = self.token_offset
        sub.filetype = getattr(self, "filetype", "")
        sub.fileversion = getattr(self, "fileversion", 0)

        sub.id = TokenID(raw_id + self.token_offset)
        sub.flags = raw_flags
        sub.remaining_bytes = size

        if sub.remaining_bytes > 0:
            label_len = int.from_bytes(self._read(1), "little")

            if label_len > 0:
                raw = self._read(label_len * 2)
                sub.label = raw.decode("utf-16-le")

        return sub

    def read_flags(self) -> int:
        return int.from_bytes(self._read(4), "little")

    def read_int(self) -> int:
        return int.from_bytes(self._read(4), "little", signed=True)

    def read_uint(self) -> int:
        return int.from_bytes(self._read(4), "little", signed=False)

    def read_float(self) -> float:
        import struct
        return struct.unpack("<f", self._read(4))[0]

    def read_string(self) -> str:
        length = int.from_bytes(self._read(2), "little")
        if length == 0:
            return ""

        raw = self._read(length * 2)
        return raw.decode("utf-16-le")
    
    def skip(self):
        if self.remaining_bytes <= 0:
            return

        if self.stream is None:
            return

        self.stream.read(self.remaining_bytes)
        self.remaining_bytes = 0

    def end_of_block(self) -> bool:
        return self.remaining_bytes == 0

    def verify_end_of_block(self):
        if not self.end_of_block():
            logger.warning(f"Expected end of block {self.id}; got extra data")
            self.skip()

    def close(self):
        if self.stream:
            self.stream.close()
            self.stream = None


class BinaryFileReader(BinaryBlockReader):

    def __init__(self, input_stream: BinaryIO, filepath: str,
                 filetype: str, fileversion: int, token_offset: int):
        super().__init__()
        self.filepath = filepath
        self.stream = input_stream
        self.filetype = filetype
        self.fileversion = fileversion
        self.token_offset = token_offset
        self.remaining_bytes = float("inf")

    def skip(self):
        if self.stream is None:
            return

        while self.stream.read(1):
            pass

        self.remaining_bytes = 0
    
    def end_of_block(self) -> bool:
        if self.stream is None:
            return True

        pos = self.stream.tell()
        byte = self.stream.read(1)
        self.stream.seek(pos)

        return byte == b""
    
    def verify_end_of_block(self):
        if not self.end_of_block():
            logger.warning(
                f"Expected end of file; got extra data in {self.filepath}"
            )

    def close(self):
        if self.stream:
            self.stream.close()



"""
Example usage:

with reader.sub_block(TokenID.vertex):

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