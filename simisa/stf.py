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

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional, TextIO, Tuple

from .units import Units


class StfError(Exception):
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





