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

from dataclasses import dataclass
from typing import Optional

from .units import Units

logger = logging.getLogger(__name__)


class StfReaderError(Exception):
    """Raised when an stf reader encounters an error or malformed data."""
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

        return self._read_word()

    def _read(self) -> str:
        c = self.stream.read(1)
        if c == "\n":
            self.line += 1
        return c

    def _peek(self) -> str:
        pos = self.stream.tell()
        c = self.stream.read(1)
        self.stream.seek(pos)
        return c

    def _skip_whitespace(self):
        while True:
            c = self._peek()
            if c == "" or c > " ":
                return
            self._read()

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


class StfReaderContext:
    def __init__(self, include_resolver, unit_parser):
        self.includes = include_resolver
        self.units = unit_parser


class StfReader:

    def __init__(self, stream: StfTokenStream, context: StfReaderContext,
                 parent: Optional["StfReader"] = None):

        self.stream = stream
        self.ctx = context
        self.parent = parent

        self.id = None
        self.label = None

        self._ended = False

    def next(self) -> StfToken:
        return self.stream.next()

    def peek(self) -> StfToken:
        return self.stream.peek()

    def read_sub_block(self) -> "StfReader": # TODO: Belongs in textblockreader

        token = self.next()

        if token.is_eof:
            raise RuntimeError("Unexpected EOF while reading sub-block")

        if token.is_block_end:
            return self.read_sub_block()

        child = StfReader(self.stream, self.ctx, parent=self)

        # block id
        child.id = self._get_token_id(token.value)

        nxt = self.next()

        # optional label or direct '('
        if nxt.is_block_start:
            return child

        child.label = nxt.value

        nxt = self.next()

        if not nxt.is_block_start:
            raise RuntimeError(f"Expected '(' after block header, got {nxt.value}")

        return child

    def __iter__(self): # TODO: Belongs in textblockreader
        while not self.end_of_block():
            yield self.read_sub_block()

        self.verify_end_of_block()

    def end_of_block(self) -> bool: # TODO: Belongs in textblockreader
        t = self.peek()
        return t.is_eof or t.is_block_end

    def verify_end_of_block(self): # TODO: Belongs in textblockreader
        if self._ended:
            return

        t = self.next()

        if not t.is_block_end:
            raise RuntimeError(
                f"Expected end of block {self.id}, got {t.value}"
            )

        self._ended = True

    def skip(self): # TODO: Belongs in textblockreader
        self.skip_block()

    def skip_block(self): # TODO: Belongs in textblockreader
        depth = 0

        while True:
            t = self.next()

            if t.is_eof:
                return

            if t.is_block_start:
                depth += 1

            elif t.is_block_end:
                if depth == 0:
                    return
                depth -= 1

    def read_word(self) -> str:
        return self.next().value

    def read_string(self) -> str:
        return self.next().value

    def read_int(self) -> int:
        return int(self.next().value)

    def read_uint(self) -> int:
        return int(self.next().value)

    def read_float(self) -> float:
        return float(self.next().value)

    def read_flags(self) -> int:
        return int(self.next().value, 16)

    def _expect(self, value: str):
        t = self.next()
        if t.value.lower() != value.lower():
            raise RuntimeError(f"Expected {value}, got {t.value}")

    def _handle_include(self):
        self.expect("(")
        name = self.read_word()
        self.expect(")")

        stream = self.ctx.includes.open(name)

        lexer = StfLexer(stream, name)
        token_stream = StfTokenStream(lexer)

        subreader = StfReader(token_stream, self.ctx)


    ######################
    # Methods actually used directly from reader.py
    ########################

    def peek_past_whitespace(self):
        pass
    
    def eof(self):
        pass

    def verify_start_of_block(self):
        pass

    def read_item(self):
        pass

    def read_hex(self):
        pass

    def read_int(self):
        pass

    def read_uint(self):
        pass

    def read_float(self):
        pass

    def close(self):
        pass
