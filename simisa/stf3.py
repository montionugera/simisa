from dataclasses import dataclass
from typing import Optional


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
            if c == "":
                break
            if c == '"':
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
    def __init__(self, stream: StfTokenStream, context: StfReaderContext):
        self.stream = stream
        self.ctx = context

    def next(self) -> StfToken:
        return self.stream.next()

    def peek(self) -> StfToken:
        return self.stream.peek()

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

    def expect(self, value: str):
        t = self.next()
        if t.value.lower() != value.lower():
            raise RuntimeError(f"Expected {value}, got {t.value}")

    def read_word(self) -> str:
        return self.next().value

    def read_string(self) -> str:
        return self.next().value

    def handle_include(self):
        # include ( filename )

        self.expect("(")

        name = self.read_word()

        self.expect(")")

        stream = self.ctx.includes.open(name)

        lexer = StfLexer(stream, name)
        token_stream = StfTokenStream(lexer)

        subparser = StfReader(token_stream, self.ctx)
        subparser.parse()

    def read_float(self, valid_units: int):
        token = self.next()

        value, scale = self.ctx.units.parse(token.value, valid_units)

        try:
            return float(value) * scale
        except ValueError:
            raise RuntimeError(f"Invalid float: {token.value}")

    def parse(self):
        while not self.peek().is_eof:
            t = self.next()

            print(t)

            if t.value == "include":
                self.handle_include()

            elif t.value == "skip":
                self.skip_block()

            else:
                self.handle_token(t)

    def handle_token(self, token: StfToken):
        pass


class StfIncludeResolver:
    def open(self, path: str):
        return open(path, "r", encoding="utf-16-le", errors="replace")


class StfUnitParser:
    def parse(self, value: str, valid_units: int):
        return value, 1.0