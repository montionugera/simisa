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


def read_header(filepath: str) -> str:
    with open(filepath, "rb") as f:
        bom = f.read(2)
        is_unicode = (bom == codecs.BOM_UTF16_LE)

        if is_unicode:
            buffer = f.read(32)
            header = buffer.decode("utf-16-le")
        else:
            buffer = bom + f.read(14)
            header = buffer.decode("ascii", errors="ignore")

        return header


def is_compressed(filepath: str) -> Optional[bool]:
    header = read_header(filepath)

    if header.startswith("SIMISA@F") or header.startswith("\r\nSIMISA@F"):
        return True
    elif header.startswith("SIMISA@@") or header.startswith("\r\nSIMISA@@"):
        return False

    return None


def read_subheader(filepath: str) -> str:
    compressed = is_compressed(filepath)

    if compressed is None:
        # TODO throw error, did not contain a proper header
        pass

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
            # TODO throw error, did not contain a proper subheader
            pass
        
        return subheader