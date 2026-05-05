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
import struct
import codecs
import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional, Iterator, BinaryIO, TextIO, Dict

from .header import is_compressed
from .token_id import TokenID
from .stf import StfReader

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
        if not isinstance(filepath, str):
            raise TypeError(f"Parameter 'filepath' must be str, but got {type(filepath).__name__}")
    
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

        if len(subheader) < 8:
            raise SimisaSubheaderError(f"Subheader '{subheader}' too short in {filepath}")

        filetype = subheader[5]
        fileversion = int(subheader[6])
        fileformat = subheader[7]

        if fileformat == "b":
            token_offset = 300 if filetype == "w" else 0
            return BinaryFileReader(stream, filepath, filetype, fileversion, token_offset)

        if fileformat != "t":
            raise SimisaSubheaderError(f"Unrecognized subheader '{subheader}' in {filepath}")
        
        text_stream = io.TextIOWrapper(stream, encoding=encoding)

        return TextFileReader(text_stream, filepath, filetype, fileversion, encoding)

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

        if len(subheader) < 8:
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
        return self.sub_blocks()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    @contextmanager
    def sub_block(self, expected_id: TokenID | None = None) -> "BlockReader":
        sub_block = self.read_sub_block()

        if expected_id is not None:
            sub_block.verify_id(expected_id)

        try:
            yield sub_block
        finally:
            sub_block.verify_end_of_block()
    
    def sub_blocks(self, expected_id: TokenID | None = None) -> Iterator["BlockReader"]:
        while not self.end_of_block():
            sub_block = self.read_sub_block()

            if expected_id is not None:
                sub_block.verify_id(expected_id)

            try:
                yield sub_block
            finally:
                sub_block.verify_end_of_block()

        self.verify_end_of_block()

    def verify_id(self, desired_id: TokenID) -> None:
        if self.id != desired_id:
            logger.warning(
                f"Expected block '{desired_id.name}' (id {desired_id}), "
                f"but got '{self.id.name}' (id {self.id})"
            )
    
    def verify_count(self, expected: int, actual: int) -> None:
        block_name = self.id.name if self.id else "<unknown>"

        if actual < expected:
            logger.warning(
                f"Too few items in block '{block_name}', "
                f"read {actual} items but expected {expected}"
            )
        elif actual > expected:
            logger.warning(
                f"Too many items in block '{block_name}', "
                f"read {actual} items but expected {expected}"
            )

    def expect_comment(self) -> None:
        if self.id == TokenID.comment:
            self.skip()
        else:
            logger.warning(
                f"Expected comment block, "
                f"but got '{self.id.name}' (id {self.id})"
            )
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
    _token_table: Dict[str, TokenID] | None = None

    def __init__(self):
        self.stf_reader: StfReader | None = None
        self.at_end_of_block: bool = False
        self.id: TokenID | None = None
        self.label: str | None = None
        self.start_depth: int = 0
        self.is_closed: bool = False

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

        if t in ("skip", "comment") or token.startswith("#"):
            return TokenID.comment

        logger.warning(f"Skipped unknown token {token}")
        return TokenID.comment

    def read_sub_block(self) -> BlockReader:
        sub_block = TextBlockReader()
        sub_block.stf_reader = self.stf_reader

        token = self.stf_reader.read_item()

        if token == "":
            self.at_end_of_block = True
            return sub_block

        if token == ")":
            self.at_end_of_block = True
            return sub_block

        sub_block.id = self._get_token_id(token)

        token = self.stf_reader.read_item()

        if token != "(":
            sub_block.label = token
            token = self.stf_reader.read_item()
            if token != "(":
                raise StfReaderError(f"Expected '(' after label, but got '{token}'")

        sub_block.start_depth = self.stf_reader.depth
        
        return sub_block

    def skip(self):
        if self.at_end_of_block:
            return

        while self.depth > self.start_depth:
            token = self.stf_reader.read_item()

            if token == "":
                logger.warning("Unexpected end of file")
                self.at_end_of_block = True
                return

        self.at_end_of_block = True

    def end_of_block(self) -> bool:
        #if self.at_end_of_block:
        #    return True

        token = self.stf_reader.peek().value

        return (
            token == ")" and
            self.stf_reader.depth == self.start_depth
        )

    # def verify_end_of_block(self):
    #     if self.at_end_of_block:
    #         return

    #     token = self.stf_reader.read_item()

    #     if token.startswith("#") or token.lower() == "comment":
    #         self.skip()
    #         return

    #     if token != ")":
    #         logger.warning(f"Expected end of block, but got '{token}'")

    #     self.at_end_of_block = True
    def verify_end_of_block(self):
        if self.at_end_of_block:
            return

        if not self.end_of_block():
            logger.warning(f"Expected end of block, but got '{self.stf_reader.peek().value}'")

        self.at_end_of_block = True

    def read_flags(self) -> int:
        return self.stf_reader.read_hex(None)

    def read_int(self) -> int:
        return self.stf_reader.read_int(None)

    def read_uint(self) -> int:
        return self.stf_reader.read_uint(None)

    def read_float(self) -> float:
        return self.stf_reader.read_float(None)

    def read_string(self) -> str:
        return self.stf_reader.read_item()

    def close(self):
        if not self.is_closed:
            if self.stf_reader:
                self.stf_reader.close()
            self.is_closed = True


class TextFileReader(TextBlockReader):

    def __init__(
        self,
        stream: TextIO,
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
        self.stream = stream

        self.is_closed = False
        self.at_end_of_block = False

        self.stf_reader = StfReader.from_stream(stream)

    def skip(self):
        if self.is_closed:
            return

        self.stf_reader.close() if hasattr(self.stf_reader, "close") else None
        self.is_closed = True
        self.at_end_of_block = True

    def verify_end_of_block(self):
        if self.is_closed:
            return

        s = self.stf_reader.read_item()
        extra_data = s

        if s != "":
            while s != "":
                if s != ")":
                    logger.warning(f"Expected end of file, but got '{s}' in {self.filepath}")
                    return

                s = self.stf_reader.read_item()

    def end_of_block(self) -> bool:
        if self.is_closed or self.at_end_of_block:
            return True

        if hasattr(self.stf_reader, "peek_past_whitespace"):
            return self.stf_reader.peek_past_whitespace() == -1

        if hasattr(self.stf_reader, "eof"):
            return self.stf_reader.eof()

        return False

    def close(self):
        if not self.is_closed:
            if self.stf_reader:
                self.stf_reader.close()
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

    def _read(self, n: int) -> bytes:
        if self.stream is None:
            raise RuntimeError("Stream is not initialized")

        data = self.stream.read(n)
        if len(data) != n:
            raise BlockReaderError("Unexpected EOF in block")

        self.remaining_bytes -= n
        return data

    def read_sub_block(self) -> "BlockReader":
        if self.stream is None:
            raise RuntimeError("Stream is not initialized")

        if self.remaining_bytes < 8:
            raise BlockReaderError("Not enough bytes for sub-block header")

        raw_id = int.from_bytes(self._read(2), "little")
        raw_flags = int.from_bytes(self._read(2), "little")
        size = int.from_bytes(self._read(4), "little")

        sub_block = BinaryBlockReader()
        sub_block.stream = self.stream
        sub_block.filepath = self.filepath
        sub_block.token_offset = self.token_offset
        sub_block.filetype = self.filetype
        sub_block.fileversion = self.fileversion

        sub_block.id = TokenID(raw_id + self.token_offset)
        sub_block.flags = raw_flags
        sub_block.remaining_bytes = size

        self.remaining_bytes -= size

        if sub_block.remaining_bytes > 0:
            label_length = int.from_bytes(sub_block._read(1), "little")

            if label_length > 0:
                raw_label = sub_block._read(label_length * 2)
                sub_block.label = raw_label.decode("utf-16-le")

        return sub_block

    def read_flags(self) -> int:
        return int.from_bytes(self._read(4), "little")

    def read_int(self) -> int:
        return int.from_bytes(self._read(4), "little", signed=True)

    def read_uint(self) -> int:
        return int.from_bytes(self._read(4), "little", signed=False)

    def read_float(self) -> float:
        return struct.unpack("<f", self._read(4))[0]

    def read_string(self) -> str:
        length = int.from_bytes(self._read(2), "little")
        if length == 0:
            return ""

        raw_string = self._read(length * 2)
        return raw_string.decode("utf-16-le")
    
    def skip(self):
        if self.remaining_bytes <= 0:
            return

        if self.stream is None:
            return

        skipped_bytes = self.stream.read(self.remaining_bytes)

        if self.remaining_bytes <= 1000:
            logger.warning(f"Skipped data: {skipped_bytes.hex().upper()}")
        else:
            logger.warning(f"Length of skipped data: {len(skipped_bytes)}")

        self.remaining_bytes = 0

    def end_of_block(self) -> bool:
        return self.remaining_bytes == 0

    def verify_end_of_block(self):
        if not self.end_of_block():
            logger.warning(
                f"Expected end of block '{self.id.name}' (id {self.id}), "
                f"but got extra data"
            )
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
                f"Expected end of file, but got extra data in {self.filepath}"
            )

    def close(self):
        if self.stream:
            self.stream.close()

