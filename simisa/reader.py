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


class StructuredBlockReader:
    id: TokenID = None
    label: str | None = None

    @staticmethod
    def open(filename: str):
        raise NotImplementedError

    def read_sub_block(self):
        raise NotImplementedError

    def skip(self):
        raise NotImplementedError

    def verify_end_of_block(self):
        raise NotImplementedError

    def read_flags(self):
        raise NotImplementedError

    def read_int(self):
        raise NotImplementedError

    def read_uint(self):
        raise NotImplementedError

    def read_float(self):
        raise NotImplementedError

    def read_string(self):
        raise NotImplementedError

    def end_of_block(self):
        raise NotImplementedError

    def read_vector3(self):
        raise NotImplementedError

    def verify_id(self, desired_id: TokenID):
        raise NotImplementedError

    def expect_comment(self):
        raise NotImplementedError

    def trace_information(self, message):
        raise NotImplementedError

    def trace_warning(self, message):
        raise NotImplementedError

    def throw_exception(self, message):
        raise NotImplementedError

    def dispose(self):
        raise NotImplementedError


class UnicodeBlockReader(StructuredBlockReader):
    def __init__(self):
        self.f = None
        self.at_end_of_block = False
        self.id = None
        self.label = None

    def read_sub_block(self):
        raise NotImplementedError

    def skip(self):
        raise NotImplementedError

    def end_of_block(self):
        raise NotImplementedError

    def verify_end_of_block(self):
        raise NotImplementedError

    def read_flags(self):
        raise NotImplementedError

    def read_int(self):
        raise NotImplementedError

    def read_uint(self):
        raise NotImplementedError

    def read_float(self):
        raise NotImplementedError

    def read_string(self):
        raise NotImplementedError

    def trace_information(self, message):
        raise NotImplementedError

    def trace_warning(self, message):
        raise NotImplementedError

    def throw_exception(self, message):
        raise NotImplementedError


class UnicodeFileReader(UnicodeBlockReader):
    def __init__(self, input_stream, filename, encoding):
        super().__init__()
        self.is_closed = False
        self.f = None

    def skip(self):
        raise NotImplementedError

    def verify_end_of_block(self):
        raise NotImplementedError

    def end_of_block(self):
        raise NotImplementedError


class BinaryBlockReader(StructuredBlockReader):
    def __init__(self):
        self.filename = ""
        self.input_stream: io.BufferedReader | None = None
        self.token_offset = 0
        self.remaining_bytes = 0
        self.flags = 0

    def read_sub_block(self):
        raise NotImplementedError

    def skip(self):
        raise NotImplementedError

    def end_of_block(self):
        raise NotImplementedError

    def verify_end_of_block(self):
        raise NotImplementedError

    def read_flags(self):
        raise NotImplementedError

    def read_int(self):
        raise NotImplementedError

    def read_uint(self):
        raise NotImplementedError

    def read_float(self):
        raise NotImplementedError

    def read_string(self):
        raise NotImplementedError

    def trace_information(self, message):
        raise NotImplementedError

    def trace_warning(self, message):
        raise NotImplementedError

    def throw_exception(self, message):
        raise NotImplementedError


class BinaryFileReader(BinaryBlockReader):
    def __init__(self, input_stream, filename, token_offset):
        super().__init__()
        self.filename = filename
        self.input_stream = None
        self.token_offset = token_offset
        self._size = 0

    def skip(self):
        raise NotImplementedError

    def end_of_block(self):
        raise NotImplementedError

    def verify_end_of_block(self):
        raise NotImplementedError


class StructuredBlockReaderException(Exception):
    @staticmethod
    def trace_warning(reader, message):
        raise NotImplementedError

    @staticmethod
    def trace_information(reader, message):
        raise NotImplementedError

    def __init__(self, reader, message):
        super().__init__(message)


class STFReader:
    end_block_comment_sentinel = "#\u00b6"

    def __init__(self, filename=None, use_tree=False, input_stream=None, encoding="utf-8"):
        self.block_depth = 0
        self.tree = [] if use_tree else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def dispose(self, disposing=True):
        pass

    def read_item(self):
        raise NotImplementedError

    def step_back_one_item(self):
        raise NotImplementedError

    def must_match(self, target):
        raise NotImplementedError

    def end_of_block(self):
        raise NotImplementedError

    def skip_block(self):
        raise NotImplementedError

    def skip_rest_of_block(self):
        raise NotImplementedError

    def read_string(self):
        raise NotImplementedError

    def read_hex(self, default_value=None):
        raise NotImplementedError

    def read_int(self, default_value=None):
        raise NotImplementedError

    def read_uint(self, default_value=None):
        raise NotImplementedError

    def read_float(self, valid_units, default_value=None):
        raise NotImplementedError

    def read_double(self, default_value=None):
        raise NotImplementedError




