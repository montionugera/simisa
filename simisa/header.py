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


def is_unicode(filepath: str) -> Optional[bool]:
    """
    Checks whether a file is encoded in UTF-16 LE based on its BOM.

    The function reads the first two bytes of the file and determines
    whether they match the UTF-16 LE byte order mark.

    Args:
        filepath: Path to the file to inspect.

    Returns:
        True if the file is UTF-16 LE encoded, otherwise False.
    """
    with open(filepath, "rb") as f:
        bom = f.read(2)
        is_unicode = (bom == codecs.BOM_UTF16_LE)

        return is_unicode


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

