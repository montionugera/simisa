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

__version__ = '0.0.1b0'
__all__ = [
    'is_unicode', 'peek_header', 'is_compressed',
    'InvalidSimisaHeaderError', 'InvalidSimisaSubheaderError',
    'ListFormat', 'TokenID', 'Units'
    'StructuredBlockReader', 'StructuredBlockWriter',
    'shape'
]

__author__ = 'Peter Grønbæk Andersen <peter@grnbk.io>'

from .header import is_unicode, peek_header, is_compressed
from .format import ListFormat
from .token_id import TokenID
from .units import Units
from .reader import InvalidSimisaHeaderError, InvalidSimisaSubheaderError
from .reader import StructuredBlockReader
from .writer import StructuredBlockWriter
from . import shape
