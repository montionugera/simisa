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

import codecs
import struct
import zlib
import pytest

from simisa.reader import (
    BlockReader,
    BinaryFileReader,
    TextFileReader,
    SimisaHeaderError,
    SimisaSubheaderError,
    UnresolvableIncludeError,
)


def ascii_file(filetype="s", fileversion=1, fileformat="t", payload=b""):
    header = b"SIMISA@@@@@@@@@@"
    subheader = f"JINX0{filetype}{fileversion}{fileformat}".encode("ascii")

    return header + subheader + payload


def unicode_file(filetype="s", fileversion=1, fileformat="t", payload=""):
    header = "SIMISA@@@@@@@@@@"
    subheader = f"JINX0{filetype}{fileversion}{fileformat}"

    return (
        codecs.BOM_UTF16_LE
        + header.encode("utf-16-le")
        + subheader.encode("utf-16-le")
        + payload.encode("utf-16-le")
    )


def write_file(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content) 

    return str(path)



@pytest.mark.parametrize(
    ("content", "expected_class"),
    [
        (ascii_file(fileformat="t"), TextFileReader),
        (unicode_file(fileformat="t"), TextFileReader),
        (ascii_file(fileformat="b"), BinaryFileReader),
        (unicode_file(fileformat="b"), BinaryFileReader),
    ],
)
def test_open_selects_reader_from_encoding_and_format(tmp_path, content, expected_class):
    path = write_file(tmp_path, "sample.s", content)

    reader = BlockReader.open(path)
    try:
        assert isinstance(reader, expected_class)
    finally:
        reader.close()


def test_from_string_returns_text_reader():
    reader = BlockReader.from_string(ascii_file().decode("ascii"))

    try:
        assert isinstance(reader, TextFileReader)
    finally:
        reader.close()


def test_from_string_accepts_leading_whitespace_and_bom():
    data = "\ufeff\r\n\t " + ascii_file().decode("ascii")

    reader = BlockReader.from_string(data)
    try:
        assert isinstance(reader, TextFileReader)
    finally:
        reader.close()


@pytest.mark.parametrize("value", [None, 1, b"not a str", [], {}])
def test_open_rejects_non_string_filepath(value):
    with pytest.raises(TypeError):
        BlockReader.open(value)


@pytest.mark.parametrize("value", [None, 1, b"SIMISA@@", [], {}])
def test_from_string_rejects_non_string_data(value):
    with pytest.raises(TypeError):
        BlockReader.from_string(value)


def test_open_missing_file_raises_os_error(tmp_path):
    with pytest.raises(OSError):
        BlockReader.open(str(tmp_path / "missing.s"))


def test_open_rejects_invalid_header(tmp_path):
    path = write_file(tmp_path, "invalid.s", b"INVALID_HEADER")

    with pytest.raises(SimisaHeaderError):
        BlockReader.open(path)


def test_from_string_rejects_invalid_header():
    with pytest.raises(SimisaHeaderError):
        BlockReader.from_string("INVALID_HEADER")


def test_from_string_rejects_compressed_header():
    with pytest.raises(SimisaHeaderError):
        BlockReader.from_string("SIMISA@F\x00\x00\x00\x00@@@@")


def test_open_rejects_short_subheader(tmp_path):
    path = write_file(tmp_path, "short.s", b"SIMISA@@")

    with pytest.raises(SimisaSubheaderError):
        BlockReader.open(path)


def test_from_string_rejects_short_subheader():
    with pytest.raises(SimisaSubheaderError):
        BlockReader.from_string("SIMISA@@@@@@@@@@short")


def test_from_string_rejects_binary_format():
    data = "SIMISA@@@@@@@@@@JINX0s1b"

    with pytest.raises(SimisaSubheaderError):
        BlockReader.from_string(data)


def test_from_string_rejects_unknown_format():
    data = "SIMISA@@@@@@@@@@JINX0s1x"

    with pytest.raises(SimisaSubheaderError):
        BlockReader.from_string(data)


def test_from_string_rejects_unresolvable_includes():
    data = "SIMISA@@@@@@@@@@JINX0s1t\ninclude ( \"missing.s\" )"

    with pytest.raises(UnresolvableIncludeError):
        BlockReader.from_string(data)

# TODO test more error handling cases
# TODO test actually reading opened binary/text
# TODO Does writing values of different types work for text/binary?
# TODO error handling in reading different values