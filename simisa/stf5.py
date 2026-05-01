
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
        self._read()
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
        cur = self.buffer
        self.buffer = self.lexer.next_token()
        return cur

    def peek(self) -> Token:
        return self.buffer

    def eof(self) -> bool:
        return self.buffer.is_eof


class Parser:
    def __init__(self, stream: TokenStream):
        self.stream = stream

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
        return float(self.next().value)

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

        Parser(token_stream).parse()

    def expect(self, value: str):
        t = self.next()
        if t.value.lower() != value.lower():
            raise RuntimeError(f"Expected {value}, got {t.value}")

    def parse(self):
        while not self.peek().is_eof:
            t = self.next()

            if t.value == "include":
                self.handle_include

            elif t.value == "skip":
                self.skip_block()

            else:
                self.handle_token(t)

    def handle_token(self, token: Token):
        pass


class TextFileReader(TextBlockReader):

    def __init__(self, input_stream: TextIO, filepath: str,
                 filetype: str, fileversion: int, encoding: str,
                 ctx: ParserContext):

        super().__init__()

        self.filepath = filepath
        self.filetype = filetype
        self.fileversion = fileversion
        self.encoding = encoding

        lexer = Lexer(input_stream, filepath)
        token_stream = TokenStream(lexer)

        self.parser = Parser(token_stream)
        self.ctx = ctx

    def read_sub_block(self) -> "BlockReader":
        block = TextFileReader(
            self.parser.stream.lexer.stream,
            self.filepath,
            self.filetype,
            self.fileversion,
            self.encoding,
            self.ctx
        )
        return block

    def skip(self):
        self.parser.skip_block()

    def end_of_block(self) -> bool:
        return self.parser.eof()

    def verify_end_of_block(self):
        if not self.end_of_block():
            logger.warning("Expected end of block but found extra tokens")

    def read_flags(self) -> int:
        return self.parser.read_hex()

    def read_int(self) -> int:
        return self.parser.read_int()

    def read_uint(self) -> int:
        return self.parser.read_uint()

    def read_float(self) -> float:
        return self.parser.read_float()

    def read_string(self) -> str:
        return self.parser.read_item()

    def close(self):
        pass