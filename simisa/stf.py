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

from __future__ import annotations

import io
from enum import IntFlag
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable, List, Dict, Tuple, Iterator

from .units import Units



class STFError(Exception):
    """Raised when an STF reader encounters an error or malformed data."""
    pass


TryParse = Callable[[str], Tuple[bool, any]]
ReadBlockFn = Callable[[any], any]


@dataclass(frozen=True)
class STFToken:
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

    @staticmethod
    def eof(source_name: str, line_number: int) -> "STFToken":
        return STFToken("", source_name, line_number, True)


class StreamReaderFactory(ABC):
    @abstractmethod
    def get_stream_reader(self, name: str) -> tuple[io.TextIOBase, Optional[str]]:
        """
        Returns:
            (stream_reader, simis_signature)
        """
        pass


class STFTokenStream(ABC):
    @abstractmethod
    def next_token(self) -> STFToken:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class STFTokenizer(STFTokenStream):
    def __init__(self, input_reader: io.TextIOBase, stream_name: str, line: int = 1):
        self.source_stream = input_reader
        self.stream_name = stream_name
        self.line_number = line

        self._builder: list[str] = []
        self._skip_whitespace()

    def next_token(self) -> STFToken:
        raise NotImplementedError

    def close(self) -> None:
        self.source_stream.close()

    def _read_char(self) -> str:
        raise NotImplementedError

    def _peek_char(self) -> str:
        raise NotImplementedError

    def _skip_whitespace(self) -> None:
        pass

    def _create_token(self) -> STFToken:
        return STFToken(
            "".join(self._builder),
            self.stream_name,
            self.line_number
        )


class STFTokenStreamBuffer(STFTokenStream):
    def __init__(self, source: STFTokenStream):
        self.source = source

        self.current_token: Optional[STFToken] = None
        self.upcoming_token: Optional[STFToken] = None
        self._buffered_token: Optional[STFToken] = None

        self._did_step_back = False

    def next_token(self) -> STFToken:
        raise NotImplementedError

    def move_next(self) -> None:
        pass

    def step_back(self) -> None:
        pass

    def close(self) -> None:
        self.source.close()


class STFTokenStreamBlockProcessor(STFTokenStreamBuffer):
    def skip_rest_of_block(self) -> None:
        pass

    def skip_block(self) -> None:
        pass

    def must_match(self, target: str) -> None:
        pass


class STFTokenStreamPreprocessor(STFTokenStreamBlockProcessor):
    def __init__(
        self,
        source: STFTokenStream,
        file_name: str,
        factory: StreamReaderFactory
    ):
        super().__init__(source)
        self.factory = factory
        self.file_name = file_name

        self._include_stream: Optional[STFTokenStream] = None
        self._include_raw: Optional[STFTokenStream] = None

        self._in_skip_mode = False
        self.directory_name: str = ""

    def next_token(self) -> STFToken:
        raise NotImplementedError

    def _handle_include(self) -> None:
        pass

    def _is_comment_or_skip(self) -> bool:
        return False

    def _starts_with_marker(self) -> bool:
        return False

    def close(self) -> None:
        pass


@dataclass
class TokenProcessor:
    token: str
    processor: Callable[[], None]


class STFReader(STFTokenStreamBlockProcessor):
    def __init__(self, file_name: str, use_tree: bool = False):
        super().__init__(source=None)
        self.file_name = file_name
        self.simis_signature: Optional[str] = None

        self._use_tree = use_tree
        self._tree_tokens: list[str] = []

    def read_item(self) -> str:
        raise NotImplementedError

    def eof(self) -> bool:
        raise NotImplementedError

    def end_of_block(self) -> bool:
        raise NotImplementedError

    def read_string(self) -> str:
        raise NotImplementedError

    def read_int(self, default: Optional[int]) -> int:
        raise NotImplementedError

    def read_uint(self, default: Optional[int]) -> int:
        raise NotImplementedError

    def read_float(self, units: Units, default: Optional[float]) -> float:
        raise NotImplementedError

    def parse_file(self, processors: List[TokenProcessor]) -> None:
        pass

    def parse_block(self, processors: List[TokenProcessor]) -> None:
        pass

    def tree(self) -> str:
        return ""

