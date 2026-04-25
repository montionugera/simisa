"""
This file is part of Simisa.

This code is based on `STFReader.cs` from the `Orts.Parsers.Msts`
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

import os
import warnings
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import (
    Optional,
    TextIO,
    Tuple,
    Iterator,
    TypeVar,
    Callable,
    List,
    Any
)

from .units import Units


class StfReaderError(Exception):
    """Raised when an stf reader encounters an error or malformed data."""
    pass


class StfTokenStream(ABC):

    def __enter__(self) -> "StfTokenStream":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    @abstractmethod
    def next_token(self) -> "StfToken":
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class StreamReaderFactory(ABC):

    @abstractmethod
    def get_stream_reader(self, name: str) -> Tuple[TextIO, Optional[str]]:
        raise NotImplementedError


@dataclass(frozen=True)
class StfToken:
    contents: str
    source_name: str
    source_line_number: int
    is_eof: bool = False

    @property
    def is_block_start(self) -> bool:
        return self.contents == "("

    @property
    def is_block_end(self) -> bool:
        return self.contents == ")"

    @classmethod
    def eof_token(cls, source_name: str, line_number: int) -> "StfToken":
        return cls(
            contents="",
            source_name=source_name,
            source_line_number=line_number,
            is_eof=True,
        )

    def __str__(self) -> str:
        return f"token: {self.contents}"



class STFTokenizer(StfTokenStream):
    def __init__(self, input_reader: TextIO, stream_name: str, current_line_in_stream: int):
        self.source_stream = input_reader
        self.stored_stream_name = stream_name
        self.line_number = current_line_in_stream

        self.item_builder = []
        self._peeked: Optional[str] = None

        self._skip_whitespace()

    def next_token(self) -> StfToken:
        line_at_start = self.line_number
        self.item_builder = []

        peek_char = self.source_stream.peek(1) if hasattr(self.source_stream, "peek") else self._peek_fallback()

        if self._is_eof(peek_char):
            return StfToken.eof_token(self.stored_stream_name, line_at_start)

        if self._is_single(peek_char):
            return self._next_single(line_at_start)

        if self._is_quote(peek_char):
            return self._next_quoted(line_at_start)

        return self._next_normal(line_at_start)

    def close(self) -> None:
        self.source_stream.close()

    def _next_normal(self, line_at_start: int) -> StfToken:
        while True:
            c = self._read()

            if self._is_eof(c):
                break

            if self._is_whitespace(c):
                self._skip_whitespace()
                break

            if self._is_quote(c):
                self._skip_whitespace()
                break

            self.item_builder.append(chr(c))

            if self._is_single(self._peek()):
                break

        return self._create(line_at_start)

    def _next_quoted(self, line_at_start: int) -> StfToken:
        self._append_quoted_stream(line_at_start)

        while self._is_concat(self._peek()):
            self._read()  # '+'
            self._skip_whitespace()

            peek = self._peek()
            if not self._is_quote(peek):
                print(
                    f"WARNING {self.stored_stream_name}:{self.line_number} "
                    "expected quoted string after '+'"
                )
                break

            self._append_quoted_stream(self.line_number)

        return self._create(line_at_start)

    def _append_quoted_stream(self, line_at_start: int):
        self._read()

        while True:
            c = self._read()

            if self._is_eof(c):
                print(
                    f"WARNING {self.stored_stream_name}:{line_at_start} "
                    "unexpected EOF in quoted string"
                )
                break

            if self._is_quote(c):
                self._skip_whitespace()
                break

            if self._is_escape(c):
                self._handle_escape()
            else:
                self.item_builder.append(chr(c))

    def _handle_escape(self):
        c = self._read()

        if c == ord('n'):
            self.item_builder.append('\n')
        elif c == ord('t'):
            self.item_builder.append('\t')
        else:
            self.item_builder.append(chr(c))

    def _next_single(self, line_at_start: int) -> StfToken:
        c = self._read()
        self.item_builder.append(chr(c))
        self._skip_whitespace()
        return self._create(line_at_start)

    def _read(self) -> int:
        c = self.source_stream.read(1)

        if c == "":
            return -1

        if c == "\n":
            self.line_number += 1

        return ord(c)

    def _peek(self) -> int:
        pos = self.source_stream.tell()
        c = self.source_stream.read(1)
        self.source_stream.seek(pos)

        if c == "":
            return -1

        return ord(c)

    def _skip_whitespace(self):
        while True:
            c = self._peek()
            if self._is_eof(c) or not self._is_whitespace(c):
                break
            self._read()

    def _peek_fallback(self) -> str:
        return self.source_stream.read(1)

    def _create(self, line_at_start: int) -> StfToken:
        return StfToken(
            contents="".join(self.item_builder),
            source_name=self.stored_stream_name,
            source_line_number=line_at_start,
        )

    @staticmethod
    def _is_eof(c: int) -> bool:
        return c == -1

    @staticmethod
    def _is_whitespace(c: int) -> bool:
        return c >= 0 and c <= ord(' ')

    @staticmethod
    def _is_single(c: int) -> bool:
        return c in (ord('('), ord(')'))

    @staticmethod
    def _is_quote(c: int) -> bool:
        return c == ord('"')

    @staticmethod
    def _is_escape(c: int) -> bool:
        return c == ord('\\')

    @staticmethod
    def _is_concat(c: int) -> bool:
        return c == ord('+')


class StfTokenStreamBuffer(ABC):
    def __init__(self):
        self.upcoming_token = None
        self.current_token = None
        self.source = None

        self._buffered_token = None
        self._did_step_back = False

    def move_next(self):
        if self._did_step_back:
            self.current_token = self.upcoming_token
            self.upcoming_token = self._buffered_token
            self._did_step_back = False
            return

        self.current_token = self.upcoming_token
        self.upcoming_token = self.source.next_token()

    def step_back(self):
        if self._did_step_back:
            raise RuntimeError(
                "cannot call step_back twice without reading a token in between"
            )

        self._buffered_token = self.upcoming_token
        self.upcoming_token = self.current_token
        self._did_step_back = True

    @abstractmethod
    def next_token(self):
        raise NotImplementedError


class StfTokenStreamBlockProcessor(StfTokenStreamBuffer):
    def skip_rest_of_block(self):
        depth = 0

        while True:
            token = self.next_token()

            if token.is_eof:
                break

            if token.is_block_end:
                if depth == 0:
                    break
                depth -= 1

            if token.is_block_start:
                depth += 1

    def skip_block(self):
        if self.upcoming_token and self.upcoming_token.is_block_end:
            self._warn(
                self.upcoming_token,
                "Found a close parenthesis, rather than the expected block of data",
            )
            return

        token = self.next_token()

        if not token.is_block_start:
            raise RuntimeError(
                f"SkipBlock() expected an open block but found: '{token.contents}'"
            )

        self.skip_rest_of_block()

    def must_match(self, target: str):
        for attempt in (1, 2):
            token = self.next_token()

            if token.is_eof:
                self._warn(token, f"Unexpected end of file instead of {target}")
                return

            if token.contents.lower() == target.lower():
                return

            if attempt == 1:
                self._warn(
                    token,
                    f'"{target}" not found - instead found "{token.contents}"',
                )
            else:
                raise RuntimeError(
                    f'"{target}" not found - instead found "{token.contents}"'
                )

    def token_stream_from_reader(self, file_name, input_reader, current_line):
        tokenizer = StfTokenizer(input_reader, file_name, current_line)
        preprocessor = StfTokenStreamPreprocessor(
            tokenizer, file_name, self.stream_reader_factory
        )
        return preprocessor

    def _warn(self, token, message: str):
        warnings.warn(f"{token.source_name}:{token.source_line_number} {message}")


class StfTokenStreamPreprocessor(StfTokenStreamBlockProcessor):
    def __init__(self, source_token_stream, file_name: str, factory):
        super().__init__()

        self.stream_reader_factory = factory
        self.source = source_token_stream

        self.upcoming_token = self.source.next_token()
        self.current_token = None

        self.directory_name = ""
        if os.path.isabs(file_name):
            self.directory_name = os.path.dirname(file_name) + os.sep

        self._include_stream = None
        self._include_raw = None
        self._in_skip_mode = False

    def next_token(self):
        return self._next_token()

    def _next_token(self):
        if self._include_stream is not None:
            token = self._include_stream.next_token()

            if not token.is_eof:
                return token

            self._dispose_include_streams()

        self.move_next()

        if self.current_token.is_eof:
            return self.current_token

        if (not self._in_skip_mode) and self._is_comment_or_skip():
            self._in_skip_mode = True
            self.skip_block()
            self._in_skip_mode = False
            return self._next_token()

        if (not self._in_skip_mode) and self._starts_with_hash_or_underscore():
            if self.upcoming_token.is_block_start:
                self._in_skip_mode = True
                self.skip_block()
                self._in_skip_mode = False
            else:
                if self.upcoming_token.is_eof:
                    self._warn(
                        self.current_token,
                        "Found a # marker immediately followed by EOF.",
                    )

                self.move_next()

            return self._next_token()

        if (not self._in_skip_mode) and self._is_include():
            self._handle_include()
            return self._next_token()

        return self.current_token

    def _handle_include(self):
        self.must_match("(")

        token = self.next_token()

        self.must_match(")")

        if self.current_token.is_eof:
            raise RuntimeError(
                f"Unexpected EOF during include statement at {token.contents}"
            )

        include_name = token.contents
        full_path = self.directory_name + include_name

        stream_reader, simis_signature = self.stream_reader_factory.get_stream_reader(
            full_path
        )

        current_line = 2 if simis_signature is not None else 1

        self._include_stream = StfTokenStreamPreprocessor(
            StfTokenizer(stream_reader, full_path, current_line),
            full_path,
            self.stream_reader_factory,
        )

    def _is_comment_or_skip(self):
        c = self.current_token.contents.lower()
        return c == "skip" or c == "comment"

    def _starts_with_hash_or_underscore(self):
        c = self.current_token.contents
        return bool(c) and (c[0] == "#" or c[0] == "_")

    def _is_include(self):
        return self.current_token.contents.lower() == "include"

    def _dispose_include_streams(self):
        if self._include_stream is not None:
            self._include_stream.close()
            self._include_stream = None

        if self._include_raw is not None:
            self._include_raw.close()
            self._include_raw = None

    def close(self):
        self._dispose_include_streams()

        if self.source is not None:
            self.source.close()
            self.source = None



class StfReader(StfTokenStreamBlockProcessor):

    @property
    def eof(self) -> bool:
        return self.upcoming_token.is_eof

    @property
    def line_number(self) -> int:
        return self.current_token.source_line_number if self.current_token else 1

    @property
    def file_name(self) -> str:
        return self.upcoming_token.source_name

    @property
    def simis_signature(self) -> Optional[str]:
        return self._simis_signature

    _next_stream_reader_factory = None

    @classmethod
    def next_stream_reader_factory(cls):
        if cls._next_stream_reader_factory is None:
            return StreamReaderFactoryFromFile()
        result = cls._next_stream_reader_factory
        cls._next_stream_reader_factory = None
        return result

    @classmethod
    def set_next_stream_reader_factory(cls, value):
        cls._next_stream_reader_factory = value

    def __init__(self):
        super().__init__()
        self.stream_reader_factory = STFReader.next_stream_reader_factory()

        self._simis_signature = None

    @classmethod
    def from_file(cls, file_name: str, use_tree: bool):
        self = cls()

        reader, simis_signature = self.stream_reader_factory.get_stream_reader(
            file_name
        )

        self._simis_signature = simis_signature
        self._init_reader(file_name, use_tree, reader)

        return self

    @classmethod
    def from_stream(cls, input_stream, file_name: str, encoding, use_tree: bool):
        import io

        self = cls()

        reader = io.TextIOWrapper(input_stream, encoding=encoding)

        self._init_reader(file_name, use_tree, reader)

        return self

    def _init_reader(self, file_name: str, use_tree: bool, input_reader):
        current_line = 2 if self._simis_signature is not None else 1

        token_stream = self.token_stream_from_reader(
            file_name, input_reader, current_line
        )

        self.source = token_stream
        self.upcoming_token = self.source.next_token()

        self._init_buffer()
        self._init_tree(use_tree)

    def close(self):
        if getattr(self, "_disposed", False):
            return

        self._disposed = True

        early_eof = not self.eof

        if self.source is not None:
            self.source.close()
            self.source = None

        if early_eof:
            self._warn(self.upcoming_token, "Expected end of file")

    def init_buffer(self):
        self.upcoming_token = self.source.next_token()
        self.current_token = self.upcoming_token


    def move_next(self):
        super().move_next()
        self._update_tree()


    def next_token(self):
        self.move_next()
        return self.current_token


    def read_item(self):
        self.move_next()
        return self.current_token.contents


    def end_of_block(self):
        if self.eof:
            return True

        if self.upcoming_token.is_block_end:
            self.read_item()
            return True

        return False

    def init_tree(self, use_tree: bool):
        self.tree_is_maintained = use_tree
        if self.tree_is_maintained:
            self.tree_tokens = []
            self.tree_tokens.append("")


    def _update_tree(self):
        if not self.tree_is_maintained:
            return

        token = self.current_token

        if token.is_block_start:
            self.tree_tokens.append("")

        elif token.is_block_end:
            if self.tree_tokens:
                self.tree_tokens.pop()
            if self.tree_tokens:
                self.tree_tokens.pop()
            self.tree_tokens.append(")")

        elif token.is_eof:
            self.tree_tokens.clear()
            self.tree_tokens.append("")

        else:
            if self.tree_tokens:
                self.tree_tokens.pop()
            self.tree_tokens.append(token.contents)


    @property
    def tree(self):
        assert self.tree_is_maintained
        return "(" .join(reversed(self.tree_tokens))

        from typing import Tuple


    def parse_unit_suffix(constant: str, valid_units: int, token_for_warnings):
        if valid_units == Units["None"]:
            return constant, 1.0

        beg = end = i = 0

        while i < len(constant):
            c = constant[i]
            end = i

            if i == 0 and c == '+':
                beg += 1
                i += 1
                continue

            if i == 0 and c == '-':
                i += 1
                continue

            if c in ('.', ','):
                i += 1
                continue

            # NOTE: C# precedence bug is preserved exactly:
            # (c == 'e') || (c == 'E' && i < len-1)
            if (c == 'e') or (c == 'E' and i < len(constant) - 1):
                nxt = constant[i + 1]
                if nxt in ('+', '-'):
                    i += 2
                    continue

            if not ('0' <= c <= '9'):
                break

            i += 1

        suffix = ""

        if i == len(constant):
            if valid_units & Units.Compulsory:
                #STFException.trace_warning(
                #    token_for_warnings,
                #    "Missing a suffix for data expecting " + str(valid_units) + " units",
                #)
                pass
        else:
            while i < len(constant) and constant[i] == ' ':
                i += 1

            suffix_start = i
            suffix_length = len(constant) - suffix_start

            comment_start = constant.find('#', suffix_start)
            if comment_start != -1:
                suffix_length = comment_start - suffix_start

            suffix = constant[suffix_start:suffix_start + suffix_length].lower().strip()

            constant = constant[beg:end]

        if valid_units & Units.Mass:
            if suffix == "": return constant, 1.0
            if suffix == "kg": return constant, 1.0
            if suffix == "lb": return constant, 0.45359237
            if suffix == "t": return constant, 1e3
            if suffix == "t-uk": return constant, 1016.05
            if suffix == "t-us": return constant, 907.18474

        if valid_units & Units.Distance:
            if suffix == "": return constant, 1.0
            if suffix == "m": return constant, 1.0
            if suffix == "cm": return constant, 0.01
            if suffix == "mm": return constant, 0.001
            if suffix == "km": return constant, 1e3
            if suffix == "ft": return constant, 0.3048
            if suffix == "in": return constant, 0.0254
            if suffix == "in/2": return constant, 0.0127

        if valid_units & Units.AreaDefaultFT2:
            if suffix == "": return constant, 0.09290304
            if suffix in ("*(m^2)", "m^2"): return constant, 1.0
            if suffix in ("*(ft^2)", "ft^2"): return constant, 0.09290304

        if valid_units & Units.Volume:
            if suffix == "": return constant, 1.0
            if suffix in ("*(ft^3)", "ft^3"): return constant, 28.3168
            if suffix in ("*(in^3)", "in^3"): return constant, 0.0163871
            if suffix in ("*(m^3)", "m^3"): return constant, 1000.0
            if suffix == "l": return constant, 1.0
            if suffix == "g-uk": return constant, 4.54609
            if suffix in ("g-us", "gal", "gals"): return constant, 3.78541

        if valid_units & Units.VolumeDefaultFT3:
            if suffix == "": return constant, 1.0
            if suffix in ("*(ft^3)", "ft^3"): return constant, 1.0
            if suffix in ("*(in^3)", "in^3"): return constant, 0.000578703704
            if suffix in ("*(m^3)", "m^3"): return constant, 35.3146667
            if suffix == "l": return constant, 0.0353146667
            if suffix == "g-uk": return constant, 0.16054372
            if suffix in ("g-us", "gal", "gals"): return constant, 0.133680556

        if valid_units & Units.Time:
            if suffix == "": return constant, 1.0
            if suffix == "s": return constant, 1.0
            if suffix == "m": return constant, 60.0
            if suffix == "h": return constant, 3600.0

        if valid_units & Units.TimeDefaultM:
            if suffix == "": return constant, 60.0
            if suffix == "s": return constant, 1.0
            if suffix == "m": return constant, 60.0
            if suffix == "h": return constant, 3600.0

        if valid_units & Units.TimeDefaultH:
            if suffix == "": return constant, 3600.0
            if suffix == "s": return constant, 1.0
            if suffix == "m": return constant, 60.0
            if suffix == "h": return constant, 3600.0

        if valid_units & Units.Current:
            if suffix == "": return constant, 1.0
            if suffix in ("amps", "a"): return constant, 1.0

        if valid_units & Units.Voltage:
            if suffix == "": return constant, 1.0
            if suffix == "v": return constant, 1.0
            if suffix == "kv": return constant, 1000.0

        if valid_units & Units.MassRateDefaultLBpH:
            if suffix == "": return constant, 1.0
            if suffix == "lb/h": return constant, 1.0
            if suffix == "kg/h": return constant, 2.20462
            if suffix == "g/h": return constant, 0.00220462

        if valid_units & Units.Speed:
            if suffix == "": return constant, 1.0
            if suffix == "m/s": return constant, 1.0
            if suffix == "mph": return constant, 0.44704
            if suffix in ("kph", "km/h", "kmph", "kmh"): return constant, 0.27777778

        if valid_units & Units.SpeedDefaultMPH:
            if suffix == "": return constant, 0.44704
            if suffix == "m/s": return constant, 1.0
            if suffix == "mph": return constant, 0.44704
            if suffix in ("kph", "km/h", "kmph", "kmh"): return constant, 0.27777778

        if valid_units & Units.Frequency:
            if suffix == "": return constant, 1.0
            if suffix == "hz": return constant, 1.0
            if suffix == "rps": return constant, 1.0
            if suffix == "rpm": return constant, 1.0 / 60.0

        if valid_units & Units.Force:
            if suffix == "": return constant, 1.0
            if suffix == "n": return constant, 1.0
            if suffix == "kn": return constant, 1e3
            if suffix in ("lbf", "lb"): return constant, 4.44822162

        if valid_units & Units.Power:
            if suffix == "": return constant, 1.0
            if suffix == "w": return constant, 1.0
            if suffix == "kw": return constant, 1e3
            if suffix == "hp": return constant, 745.699872

        if valid_units & Units.Stiffness:
            if suffix == "": return constant, 1.0
            if suffix == "n/m": return constant, 1.0

        if valid_units & Units.Resistance:
            if suffix == "": return constant, 1.0
            if suffix == "n/m/s": return constant, 1.0
            if suffix == "ns/m": return constant, 1.0
            if suffix == "lbf/mph": return constant, 9.9503884

        if valid_units & Units.PressureDefaultPSI:
            if suffix == "": return constant, 1.0
            if suffix == "psi": return constant, 1.0
            if suffix == "bar": return constant, 14.5037738
            if suffix == "inhg": return constant, 0.4911542
            if suffix == "kpa": return constant, 0.145037738

        if valid_units & Units.PressureDefaultInHg:
            if suffix == "": return constant, 0.4911542
            if suffix == "psi": return constant, 1.0
            if suffix == "bar": return constant, 14.5037738
            if suffix == "inhg": return constant, 0.4911542
            if suffix == "kpa": return constant, 0.145037738

        if valid_units & Units.PressureRateDefaultPSIpS:
            if suffix == "": return constant, 1.0
            if suffix == "psi/s": return constant, 1.0
            if suffix == "psi/min": return constant, 1.0 / 60.0
            if suffix == "inhg/s": return constant, 0.4911542
            if suffix == "bar/s": return constant, 14.5037738
            if suffix == "bar/min": return constant, 14.5037738 / 60.0
            if suffix == "kpa/s": return constant, 0.145

        if valid_units & Units.PressureRateDefaultInHgpS:
            if suffix == "": return constant, 0.4911542
            if suffix == "psi/s": return constant, 1.0
            if suffix == "psi/min": return constant, 1.0 / 60.0
            if suffix == "inhg/s": return constant, 0.4911542
            if suffix == "bar/s": return constant, 14.5037738
            if suffix == "bar/min": return constant, 14.5037738 / 60.0
            if suffix == "kpa/s": return constant, 0.145

        if valid_units & Units.EnergyDensity:
            if suffix == "": return constant, 1.0
            if suffix in ("kj/kg", "j/g"): return constant, 1.0
            if suffix == "btu/lb": return constant, 2.326

        if valid_units & Units.TemperatureDifference:
            if suffix == "": return constant, 1.0
            if suffix == "degc": return constant, 1.0
            if suffix == "degf": return constant, 100.0 / 180.0

        if valid_units & Units.RotationalInertia:
            if suffix == "": return constant, 1.0

        if valid_units & Units.ResistanceDavisC:
            if suffix == "": return constant, 1.0
            if suffix == "Nm/s^2": return constant, 1.0
            if suffix == "lbf/mph^2": return constant, 22.2583849

        #STFException.trace_warning(
        #    token_for_warnings,
        #    "Found a suffix '" + suffix + "' which could not be parsed as a " + str(valid_units) + " unit",
        #)

        return constant, 1.0

    T = TypeVar("T")
    NullableT = TypeVar("NullableT")


    PARSE_NUM = "allow_leading_white | allow_leading_sign | allow_thousands | allow_decimal | allow_exponent | allow_trailing_white"
    PARSE_HEX = "allow_leading_white | allow_hex_specifier | allow_trailing_white"
    PARSE_NFI = None


    TryParseCode = Callable[[str], tuple[bool, Optional[T]]]
    ReadValueCode = Callable[[NullableT], T]


    def read_value_struct(self, description: str, default_value: Optional[T], parse_code: TryParseCode):
        if self.upcoming_token.is_block_end:
            self._warn(
                self.upcoming_token,
                f"When expecting a {description}, we found a ) marker. Using the default {default_value}"
            )
            return default_value if default_value is not None else T()

        self.move_next()

        item = self.current_token.contents

        if item is None or item == "":
            return T()

        if item.endswith(","):
            item = item.rstrip(",")

        ok, parsed_value = parse_code(item)
        if ok:
            return parsed_value

        self._warn(self.current_token, f"Cannot parse the constant number {item}")

        return default_value if default_value is not None else T()

    def read_block_struct(self, default_value: Optional[T], code_doing_reading: ReadValueCode):
        return self.read_block(
            default_value,
            default_value if default_value is not None else T(),
            code_doing_reading
        )

    def read_block(self, default_value: Optional[T], value_of_default: T, code_doing_reading: ReadValueCode):
        if self.upcoming_token.is_eof:
            self._warn(self.current_token, "Unexpected end of file")
            return value_of_default

        if self.upcoming_token.is_block_end and default_value is not None:
            return value_of_default

        self.move_next()

        if self.current_token.is_block_start:
            result = code_doing_reading(default_value)
            self.skip_rest_of_block()
            return result

        self._warn(
            self.current_token,
            "Block not found - instead found " + self.current_token.contents
        )
        return value_of_default
    
    def read_string(self):
        self.move_next()
        return self.current_token.contents


    def read_int(self, default_value):
        return self.read_value_struct(
            "int",
            default_value,
            lambda item: self._try_parse_int(item)
        )


    def read_uint(self, default_value):
        return self.read_value_struct(
            "uint",
            default_value,
            lambda item: self._try_parse_uint(item)
        )


    def read_hex(self, default_value):
        return self.read_value_struct(
            "hex",
            default_value,
            lambda item: self._try_parse_hex(item)
        )


    def read_double(self, default_value):
        return self.read_value_struct(
            "double",
            default_value,
            lambda item: self._try_parse_double(item)
        )


    def read_bool(self, default_value):
        actual_default = default_value if default_value is not None else False

        if self.upcoming_token.is_block_end:
            return default_value if default_value is not None else False

        self.move_next()

        item = self.current_token.contents

        if not item:
            return actual_default

        if item == "true":
            return True
        if item == "false":
            return False

        try:
            parsed_int = int(item)
            return parsed_int != 0
        except ValueError:
            return actual_default


    def read_float(self, valid_units, default_value):
        def parser(item):
            scale = self.parse_unit_suffix(item, valid_units, self.current_token)

            try:
                parsed_value = float(item)
                return True, scale * parsed_value
            except ValueError:
                return False, 1.0

        return self.read_value_struct("float", default_value, parser)


    def read_string_block(self, default_value: str):
        return self.read_block_struct(
            default_value,
            lambda _: self.read_string()
        )


    def read_int_block(self, default_value):
        return self.read_block_struct(
            default_value,
            lambda x: self.read_int(x)
        )


    def read_uint_block(self, default_value):
        return self.read_block_struct(
            default_value,
            lambda x: self.read_uint(x)
        )


    def read_hex_block(self, default_value):
        return self.read_block_struct(
            default_value,
            lambda x: self.read_hex(x)
        )


    def read_double_block(self, default_value):
        return self.read_block_struct(
            default_value,
            lambda x: self.read_double(x)
        )


    def read_bool_block(self, default_value):
        return self.read_block_struct(
            default_value,
            lambda x: self.read_bool(x)
        )


    def read_float_block(self, valid_units, default_value):
        return self.read_block_struct(
            default_value,
            lambda x: self.read_float(valid_units, x)
        )


    def read_vector2_block(self, valid_units, default_value):
        return self.read_block_struct(
            default_value,
            lambda x: self.Vector2(
                self.read_float(valid_units, x.value.x),
                self.read_float(valid_units, x.value.y),
            )
        )


    def read_vector3_block(self, valid_units, default_value):
        return self.read_block_struct(
            default_value,
            lambda x: self.Vector3(
                self.read_float(valid_units, x.value.x),
                self.read_float(valid_units, x.value.y),
                self.read_float(valid_units, x.value.z),
            )
        )


    def read_vector4_block(self, valid_units, default_value):
        return self.read_block_struct(
            default_value,
            lambda x: self.Vector4(
                self.read_float(valid_units, x.value.x),
                self.read_float(valid_units, x.value.y),
                self.read_float(valid_units, x.value.z),
                self.read_float(valid_units, x.value.w),
            )
        )

    def parse_file(self, processors):
        self.parse_file_or_block(lambda: self.eof, lambda: False, processors)


    def parse_file_with_break(self, breakout, processors):
        self.parse_file_or_block(lambda: self.eof, breakout, processors)


    def parse_block(self, processors):
        self.parse_file_or_block(lambda: self.end_of_block(), lambda: False, processors)


    def parse_block_with_break(self, breakout, processors):
        self.parse_file_or_block(lambda: self.end_of_block(), breakout, processors)


    def parse_file_or_block(self, end_condition, breakout, processors):
        while not end_condition():

            if breakout():
                self.skip_rest_of_block()
                break

            token = self.read_item().lower()

            if token == "(":
                self.skip_rest_of_block()
                continue

            for tp in processors:
                if tp.token == token:
                    tp.processor()


Processor = Callable[[], None]
ParsingBreak = Callable[[], bool]


class TokenProcessor:
    def __init__(self, token: str, processor: Processor):
        self.token = token
        self.processor = processor


    def eof_fn(self):
        return self.eof


    def verify_start_of_block(self):
        self.must_match("(")


    def peek_past_whitespace(self):
        if self.upcoming_token.is_eof:
            return -1

        if self.upcoming_token.is_block_end:
            return 41  # ')'
        
        return 0
    
class StreamReaderFactoryFromFile:

    def get_stream_reader(self, file_name: str):
        directory = os.path.dirname(file_name)

        if not os.path.exists(directory):
            raise FileNotFoundError(directory)

        stream = open(file_name, "r", encoding="utf-8", errors="replace")

        simis_signature = stream.readline().rstrip("\n")

        return stream, simis_signature