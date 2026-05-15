"""
Simisa

A Python module to read and write files used with MSTS and Open Rails.

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

__version__ = '0.0.1b2'
__all__ = [
    'is_unicode', 'peek_header', 'peek_subheader',
    'is_compressed', 'is_binary', 'is_text',
    'read_filetype', 'read_fileversion',
    'SimisaHeaderError', 'SimisaSubheaderError',
    'has_includes', 'peek_first_include',
    'resolve_include', 'resolve_includes',
    'UnresolvableIncludeError',
    'TokenID', 'Units', 'StfReader',
    'BlockReader', 'BlockWriter', 'BlockFormat',
    'BlockReaderError', 'StfReaderError',
    'roaddatabase', 'shape', 'terrain',
    'tracksections', 'trackdatabase',
    'world', 'worldsound'
]

__author__ = 'Peter Grønbæk Andersen <peter@grnbk.io>'

from .header import is_unicode, peek_header, peek_subheader
from .header import is_compressed, is_binary, is_text
from .header import read_filetype, read_fileversion
from .header import SimisaHeaderError, SimisaSubheaderError
from .include import has_includes, peek_first_include
from .include import resolve_include, resolve_includes
from .include import UnresolvableIncludeError
from .token_id import TokenID
from .units import Units
from .stf import StfReader, StfReaderError
from .reader import BlockReader, BlockReaderError
from .writer import BlockWriter
from .format import BlockFormat

from . import roaddatabase
from . import shape
from . import terrain
from . import trackdatabase
from . import tracksections
from . import world
from . import worldsound
