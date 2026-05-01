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

import pytest

import io
from simisa.stf3 import Lexer, TokenStream, Parser, ParserContext, IncludeResolver, UnitParser


def test_parse_real_file():
    file_path = "./data/DK10f_A1tPnt5dLft.sd"

    include_resolver = IncludeResolver()
    unit_parser = UnitParser()
    context = ParserContext(include_resolver, unit_parser)

    with open(file_path, "r", encoding="utf-16-le", errors="replace") as f:
        lexer = Lexer(f, file_path)
        stream = TokenStream(lexer)
        parser = Parser(stream, context)

        parser.parse()

    assert False  # replace with real assertions later
