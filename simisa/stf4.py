from dataclasses import dataclass
from typing import Iterator, Optional, TextIO, Any, Protocol
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class Token:
    kind: str # word, string, (, ), eof
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


class Lexer:
    def __init__(self, stream: TextIO, source_name: str):
        self.stream = stream
        self.source = source_name
        self.line = 1

    def next_token(self) -> Token:
        self._skip_whitespace()

        c = self._peek()

        if c == "":
            return Token("eof", "", self.line, self.source)

        if c == "(":
            self._read()
            return Token("(", "(", self.line, self.source)

        if c == ")":
            self._read()
            return Token(")", ")", self.line, self.source)

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

    def _read_word(self) -> Token:
        start_line = self.line
        buf = []

        while True:
            c = self._peek()
            if c == "" or c.isspace() or c in "()":
                break
            buf.append(self._read())

        return Token("word", "".join(buf), start_line, self.source)

    def _read_string(self) -> Token:
        start_line = self.line
        self._read()  # opening quote
        buf = []

        while True:
            c = self._read()
            if c == "" or c == '"':
                break
            buf.append(c)

        return Token("string", "".join(buf), start_line, self.source)


class TokenStream:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.buffer = lexer.next_token()

    def next(self) -> Token:
        current = self.buffer
        self.buffer = self.lexer.next_token()
        return current

    def peek(self) -> Token:
        return self.buffer

    def eof(self) -> bool:
        return self.buffer.is_eof


class IncludeResolver:
    def open(self, path: str):
        return open(path, "r", encoding="utf-16-le", errors="replace")


class UnitParser:
    def parse(self, value: str, valid_units: int):
        return value, 1.0


class ParserContext:
    def __init__(self, include_resolver, unit_parser):
        self.includes = include_resolver
        self.units = unit_parser



class Parser:
    def __init__(self, stream: TokenStream, ctx: ParserContext):
        self.stream = stream
        self.ctx = ctx

    def next(self) -> Token:
        return self.stream.next()

    def peek(self) -> Token:
        return self.stream.peek()

    def eof(self) -> bool:
        return self.stream.eof()


    def read_item(self) -> str:
        return self.next().value


    def read_int(self, _=None) -> int:
        return int(self.next().value)

    def read_uint(self, _=None) -> int:
        return int(self.next().value)

    def read_float(self, _=None) -> float:
        token = self.next()
        value, scale = self.ctx.units.parse(token.value, 0)
        return float(value) * scale

    def read_hex(self, _=None) -> int:
        return int(self.next().value, 16)


    def skip_block(self):
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

    def peek_past_whitespace(self):
        return self.peek().value


    def handle_include(self, ctx):
        self.expect("(")
        name = self.read_item()
        self.expect(")")

        stream = ctx.includes.open(name)

        lexer = Lexer(stream, name)
        token_stream = TokenStream(lexer)
        Parser(token_stream, ctx).parse()

    def expect(self, value: str):
        t = self.next()
        if t.value.lower() != value.lower():
            raise RuntimeError(f"Expected {value}, got {t.value}")



class TextBlockReader:
    def __init__(self, stream: TextIO, source: str, ctx: ParserContext):
        lexer = Lexer(stream, source)
        token_stream = TokenStream(lexer)

        self.parser = Parser(token_stream, ctx)

    def parse(self):
        return self.parser.parse()