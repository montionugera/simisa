"""
This file is part of Simisa.

This code is loosely based on `STFReader.cs` from the `Orts.Parsers.Msts`
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

import logging
from dataclasses import dataclass
from typing import Optional

from .include import resolve_include
from .units import Units

logger = logging.getLogger(__name__)

# TODO Handle units


class StfReaderError(Exception):
    """Raised when an STF reader encounters an error or malformed data."""
    pass


@dataclass(frozen=True)
class StfToken:
    kind: str # "word", "string", "(", ")", "eof"
    value: str
    line: int
    source: str

    @property
    def is_eof(self) -> bool:
        return self.kind == "eof"

    @property
    def is_block_start(self) -> bool:
        return self.kind == "("

    @property
    def is_block_end(self) -> bool:
        return self.kind == ")"


class StfLexer:
    def __init__(self, stream, source_name: str):
        self.stream = stream
        self.source = source_name
        self.line = 1
        self._buffer = self.stream.read(1)

    def next_token(self) -> StfToken:
        self._skip_whitespace()

        c = self._peek()

        if c == "":
            return StfToken("eof", "", self.line, self.source)

        if c == "(":
            self._read()
            return StfToken("(", "(", self.line, self.source)

        if c == ")":
            self._read()
            return StfToken(")", ")", self.line, self.source)

        if c == '"':
            return self._read_string()

        token = self._read_word()
        token_value = token.value.lower()

        COMMENT_KEYWORDS = [
            "_skip",
            "_info",
            "info"
        ]   

        if token_value in COMMENT_KEYWORDS:
            self._consume_comment()
            return self.next_token()

        return token

    def _read(self):
        c = self._buffer
        self._buffer = self.stream.read(1)

        if c == "\n":
            self.line += 1

        return c
    
    def _peek(self):
        return self._buffer

    def _skip_whitespace(self):
        while True:
            c = self._peek()

            if c == "" or c > " ":
                return

            self._read()

    def _consume_comment(self):
        self._skip_whitespace()

        if self._peek() != "(":
            raise StfReaderError("Expected '(' after comment keyword")

        self._read() # opening parenthesis

        depth = 1

        while depth > 0:
            c = self._read()

            if c == "":
                raise StfReaderError("Unterminated comment")

            if c == "(":
                depth += 1
            
            elif c == ")":
                depth -= 1

    def _read_word(self) -> StfToken:
        start_line = self.line
        buf = []

        while True:
            c = self._peek()

            if c == "" or c.isspace() or c in "()":
                break

            buf.append(self._read())

        return StfToken("word", "".join(buf), start_line, self.source)

    def _read_string(self) -> StfToken:
        start_line = self.line
        self._read() # opening quote
        buf = []

        while True:
            c = self._read()

            if c == "" or c == '"':
                break

            buf.append(c)

        return StfToken("string", "".join(buf), start_line, self.source)

class StfTokenStream:
    def __init__(self, lexer: StfLexer):
        self.lexer = lexer
        self.buffer = self.lexer.next_token()
        self.current = None

    def next(self) -> StfToken:
        self.current = self.buffer
        self.buffer = self.lexer.next_token()
        return self.current

    def peek(self) -> StfToken:
        return self.buffer

    def eof(self) -> bool:
        return self.buffer.is_eof


class StfReader:

    @classmethod
    def from_stream(cls, stream, source_name="<stream>"):
        lexer = StfLexer(stream, source_name)
        token_stream = StfTokenStream(lexer)

        return cls(token_stream)
    
    def __init__(self, stream: StfTokenStream):
        self.stream = stream
        self.injected: Optional["StfReader"] = None
        self.id = None
        self.label = None
        self.depth = 0
        self._ended = False

    def next(self) -> StfToken:
        while self.injected is not None:
            if self.injected.eof():
                self.injected = None
                continue
            return self.injected.next()

        token = self.stream.next()

        if token.kind == "word" and token.value == "include":
            return self._handle_include()

        return token

    def peek(self) -> StfToken:
        while self.injected is not None:
            if self.injected.eof():
                self.injected = None
                continue

            return self.injected.peek()

        return self.stream.peek()

    def inject(self, reader: "StfReader"):
        if self.injected is not None:
            reader.inject(self.injected)

        self.injected = reader

    def _expect(self, value: str):
        t = self.next()
        if t.value.lower() != value.lower():
            raise StfReaderError(f"Expected {value}, but got {t.value}")
    
    def _handle_include(self) -> StfToken:
        self._expect("(")

        include_path = self.next()

        if path.kind != "string":
            raise StfReaderError("include expects string path")

        self._expect(")")

        include_text = resolve_include(include_path)
        sub_reader = StfReader.from_stream(io.StringIO(include_text), include_path)

        self.inject(sub_reader)

        return self.next()

    def eof(self):
        return self.injected is None and self.stream.eof()

    def read_item(self):
        token = self.next()

        if token.is_eof:
            return ""

        if token.value == "(":
            self.depth += 1

        elif token.value == ")":
            self.depth -= 1
            if self.depth < 0:
                raise StfReaderError("Unbalanced ')' detected")

        #print(f"[READ] token={token.value}, depth={self.depth}")

        return token.value

    def read_hex(self, default=None):
        s = self.read_item()
        if s == "":
            if default is not None:
                return default
            raise StfReaderError("Unexpected EOF while reading hex")

        try:
            return int(s, 16)
        except ValueError:
            raise StfReaderError(f"Invalid hex value: {s}")

    def read_int(self, default=None):
        s = self.read_item()
        if s == "":
            if default is not None:
                return default
            raise StfReaderError("Unexpected EOF while reading int")

        try:
            return int(s, 10)
        except ValueError:
            raise StfReaderError(f"Invalid int value: {s}")

    def read_uint(self, default=None):
        value = self.read_int(default)

        if value is None:
            return None

        if value < 0:
            raise StfReaderError(f"Expected unsigned int, but got {value}")

        return value

    def read_float(self, default=None):
        s = self.read_item()
        if s == "":
            if default is not None:
                return default
            raise StfReaderError("Unexpected EOF while reading float")

        try:
            return float(s)
        except ValueError:
            raise StfReaderError(f"Invalid float value: {s}")

    def close(self):
        self._ended = True