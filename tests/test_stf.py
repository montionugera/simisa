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
import pytest

from simisa.stf import StfLexer, StfReader, StfReaderError


def tokenize(source):
    lexer = StfLexer(io.StringIO(source))
    tokens = []

    while True:
        token = lexer.next_token()
        tokens.append(token)

        if token.is_eof:
            break

    return tokens



@pytest.mark.parametrize(
    "keyword",
    [
        "skip", "SKIP", "Skip",
        "_skip", "_SKIP", "_Skip",
        "info", "INFO", "Info",
        "_info", "_INFO", "_Info",
    ],
)
def test_comments_are_consumed(keyword):
    tokens = tokenize(f"before {keyword}(comment text) after")

    assert [(t.kind, t.value) for t in tokens] == [
        ("word", "before"),
        ("word", "after"),
        ("eof", ""),
    ]


def test_comment_with_nested_parentheses_is_consumed():
    tokens = tokenize("before skip(outer (inner) text) after")

    assert [(t.kind, t.value) for t in tokens] == [
        ("word", "before"),
        ("word", "after"),
        ("eof", ""),
    ]


def test_comment_at_end_of_input_is_consumed():
    tokens = tokenize("before info(comment at end)")

    assert [(t.kind, t.value) for t in tokens] == [
        ("word", "before"),
        ("eof", ""),
    ]


def test_comment_keyword_requires_opening_parenthesis():
    lexer = StfLexer(io.StringIO("skip missing_parenthesis"))

    with pytest.raises(StfReaderError, match=r"Expected '\('"):
        lexer.next_token()


def test_unterminated_comment_raises_error():
    lexer = StfLexer(io.StringIO("skip(comment never ends"))

    with pytest.raises(StfReaderError, match="Unterminated comment"):
        lexer.next_token()


def test_parentheses_are_tokenized():
    tokens = tokenize("(hello (world))")

    assert [(t.kind, t.value) for t in tokens] == [
        ("(", "("),
        ("word", "hello"),
        ("(", "("),
        ("word", "world"),
        (")", ")"),
        (")", ")"),
        ("eof", ""),
    ]


def test_words_are_separated_by_whitespace_and_parentheses():
    tokens = tokenize("alpha beta(gamma)delta")

    assert [(t.kind, t.value) for t in tokens] == [
        ("word", "alpha"),
        ("word", "beta"),
        ("(", "("),
        ("word", "gamma"),
        (")", ")"),
        ("word", "delta"),
        ("eof", ""),
    ]


def test_eof_is_returned_for_empty_input():
    tokens = tokenize("")

    assert [(t.kind, t.value) for t in tokens] == [
        ("eof", ""),
    ]


def test_eof_is_returned_after_last_word():
    lexer = StfLexer(io.StringIO("hello"))

    assert lexer.next_token().value == "hello"
    assert lexer.next_token().is_eof


def test_whitespace_only_input_returns_eof():
    tokens = tokenize("   \t\n  ")

    assert [(t.kind, t.value) for t in tokens] == [
        ("eof", ""),
    ]


def test_strings_are_not_split_by_parentheses():
    tokens = tokenize('"hello (world)"')

    assert [(t.kind, t.value) for t in tokens] == [
        ("string", "hello (world)"),
        ("eof", ""),
    ]


def test_unterminated_string_raises_error():
    lexer = StfLexer(io.StringIO('"unterminated'))

    with pytest.raises(StfReaderError, match="Unterminated string"):
        lexer.next_token()


def test_include_requires_opening_parenthesis():
    reader = StfReader.from_stream(
        io.StringIO("include \"child.stf\")")
    )

    with pytest.raises(StfReaderError, match="Expected"):
        reader.read_item()


def test_include_requires_string_path():
    reader = StfReader.from_stream(
        io.StringIO("include(child.stf)")
    )

    with pytest.raises(StfReaderError, match="Expected string path"):
        reader.read_item()


def test_include_requires_closing_parenthesis():
    reader = StfReader.from_stream(
        io.StringIO('include("child.stf"')
    )

    with pytest.raises(StfReaderError, match="Expected"):
        reader.read_item()


def test_read_int():
    reader = StfReader.from_stream(
        io.StringIO("42 -17 0")
    )

    assert reader.read_int() == 42
    assert reader.read_int() == -17
    assert reader.read_int() == 0


def test_read_hex():
    reader = StfReader.from_stream(
        io.StringIO("FF 10 0x20")
    )

    assert reader.read_hex() == 255
    assert reader.read_hex() == 16
    assert reader.read_hex() == 32


def test_read_uint():
    reader = StfReader.from_stream(
        io.StringIO("0 1 4294967295")
    )

    assert reader.read_uint() == 0
    assert reader.read_uint() == 1
    assert reader.read_uint() == 4294967295


def test_read_float():
    reader = StfReader.from_stream(
        io.StringIO("3.14 -2.5 1e3 10")
    )

    assert reader.read_float() == pytest.approx(3.14)
    assert reader.read_float() == pytest.approx(-2.5)
    assert reader.read_float() == pytest.approx(1000.0)
    assert reader.read_float() == pytest.approx(10.0)


def test_read_different_types_in_sequence():
    reader = StfReader.from_stream(
        io.StringIO("42 FF 3.5 7")
    )

    assert reader.read_int() == 42
    assert reader.read_hex() == 255
    assert reader.read_float() == pytest.approx(3.5)
    assert reader.read_uint() == 7


@pytest.mark.parametrize("value", ["abc", "12.5", ""])
def test_read_int_rejects_invalid_values(value):
    reader = StfReader.from_stream(io.StringIO(value))

    with pytest.raises(StfReaderError):
        reader.read_int()


@pytest.mark.parametrize("value", ["xyz", "1.5", ""])
def test_read_hex_rejects_invalid_values(value):
    reader = StfReader.from_stream(io.StringIO(value))

    with pytest.raises(StfReaderError):
        reader.read_hex()


def test_read_uint_rejects_negative_values():
    reader = StfReader.from_stream(io.StringIO("-1"))

    with pytest.raises(StfReaderError, match="unsigned"):
        reader.read_uint()


@pytest.mark.parametrize("value", ["abc", "1.2.3", ""])
def test_read_float_rejects_invalid_values(value):
    reader = StfReader.from_stream(io.StringIO(value))

    with pytest.raises(StfReaderError):
        reader.read_float()


@pytest.mark.parametrize(
    ("method_name", "default", "expected"),
    [
        ("read_int", 123, 123),
        ("read_hex", 255, 255),
        ("read_uint", 10, 10),
        ("read_float", 1.5, 1.5),
    ],
)
def test_typed_readers_return_default_at_eof(method_name, default, expected):
    reader = StfReader.from_stream(io.StringIO(""))

    result = getattr(reader, method_name)(default=default)

    assert result == expected


@pytest.mark.parametrize(
    "method_name",
    ["read_int", "read_hex", "read_uint", "read_float"],
)
def test_typed_readers_raise_at_eof_without_default(method_name):
    reader = StfReader.from_stream(io.StringIO(""))

    with pytest.raises(StfReaderError, match="Unexpected EOF"):
        getattr(reader, method_name)()


def test_read_uint_returns_none_for_none_default_at_eof():
    reader = StfReader.from_stream(io.StringIO(""))

    # read_uint passes the default to read_int. Since None is
    # also the default sentinel, EOF raises rather than returning None.
    with pytest.raises(StfReaderError, match="Unexpected EOF"):
        reader.read_uint(default=None)