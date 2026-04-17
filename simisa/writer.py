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
from typing import Optional

from .token_id import TokenID


class StructuredBlockWriter:
    id: Optional[TokenID] = None
    label: Optional[str] = None

    @staticmethod
    def open(filename: str):
        raise NotImplementedError

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

    def write_vector3(self, x: float, y: float, z: float):
        raise NotImplementedError

    def write_comment(self, text: str):
        raise NotImplementedError

    def trace_information(self, message: str):
        raise NotImplementedError

    def trace_warning(self, message: str):
        raise NotImplementedError

    def throw_exception(self, message: str):
        raise NotImplementedError

    def dispose(self):
        raise NotImplementedError


class UnicodeBlockWriter(StructuredBlockWriter):
    def __init__(self):
        self.stream: Optional[io.TextIOBase] = None
        self.block_depth = 0

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

    def trace_information(self, message: str):
        raise NotImplementedError

    def trace_warning(self, message: str):
        raise NotImplementedError

    def throw_exception(self, message: str):
        raise NotImplementedError


class UnicodeFileWriter(UnicodeBlockWriter):
    def __init__(self, output_stream, filename, encoding="utf-8"):
        super().__init__()
        self.filename = filename
        self.stream = output_stream
        self.encoding = encoding
        self.is_closed = False

    def dispose(self):
        raise NotImplementedError


class BinaryBlockWriter(StructuredBlockWriter):
    def __init__(self):
        self.filename = ""
        self.output_stream: Optional[io.BufferedWriter] = None
        self.token_offset = 0
        self.block_stack = []

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

    def trace_information(self, message: str):
        raise NotImplementedError

    def trace_warning(self, message: str):
        raise NotImplementedError

    def throw_exception(self, message: str):
        raise NotImplementedError


class BinaryFileWriter(BinaryBlockWriter):
    def __init__(self, output_stream, filename, token_offset=0):
        super().__init__()
        self.filename = filename
        self.output_stream = output_stream
        self.token_offset = token_offset

    def dispose(self):
        raise NotImplementedError


class StructuredBlockWriterException(Exception):
    @staticmethod
    def trace_warning(writer, message: str):
        raise NotImplementedError

    @staticmethod
    def trace_information(writer, message: str):
        raise NotImplementedError

    def __init__(self, writer, message: str):
        super().__init__(message)