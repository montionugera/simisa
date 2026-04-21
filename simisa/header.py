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
from typing import Optional


class InvalidSimisaHeaderError(Exception):
    """Raised when a simisa header is invalid."""
    pass


class InvalidSimisaSubheaderError(Exception):
    """Raised when a simisa subheader is invalid."""
    pass


def peek_header(filepath: str) -> Optional[str]:
    """
    Reads the beginning of a file and extracts a SIMISA header if present.

    The function detects whether the file is UTF-16 LE encoded via BOM,
    decodes an initial portion of the file accordingly, and checks whether
    the resulting text starts with a known valid SIMISA header.

    Args:
        filepath: Path to the file to inspect.

    Returns:
        The detected header string if it starts with a valid SIMISA header,
        otherwise None.
    """
    with open(filepath, "rb") as f:
        bom = f.read(2)
        is_unicode = (bom == codecs.BOM_UTF16_LE)

        if is_unicode:
            buffer = f.read(32)
            header = buffer.decode("utf-16-le")
        else:
            buffer = bom + f.read(14)
            header = buffer.decode("ascii", errors="ignore")

        header = header.lstrip("\r\n")

        valid_headers = [
            "SIMISA@@",
            "SIMISA@F",
        ]

        if not any(header.startswith(h) for h in valid_headers):
            return None
        
        return header


def is_compressed(filepath: str) -> Optional[bool]:
    """
    Determines whether a file is compressed based on its SIMISA header.

    This function reads the file header using `peek_header` and infers
    compression from known SIMISA header markers.

    Args:
        filepath: Path to the file to inspect.

    Returns:
        True if the file is compressed,
        False if it is uncompressed,
        None if the header is missing or unrecognized.
    """
    header = peek_header(filepath)

    if header is None:
        return None
    elif header.startswith("SIMISA@F"):
        return True
    elif header.startswith("SIMISA@@"):
        return False

    return None


def read_subheader(filepath: str) -> str:
    """
    Reads the SIMISA subheader from a file, handling compression and encoding.

    The function first determines whether the file is compressed and then
    reads the appropriate header structure depending on encoding (ASCII or
    UTF-16 LE). If compressed, the file content is decompressed before
    reading the subheader.

    Args:
        filepath: Path to the SIMISA file.

    Returns:
        The decoded subheader string.

    Raises:
        InvalidSimisaHeaderError: If the file header is missing or invalid.
        InvalidSimisaSubheaderError: If the extracted subheader is invalid.
    """
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
        
        return subheader