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
import simisa


def test_has_includes_emptyfile(global_storage):
    with open(global_storage["emptyfile_path"], "r") as f:
        text = f.read()

    has_includes = simisa.has_includes(text)

    assert has_includes == False


def test_has_includes_garbagefile(global_storage):
    with open(global_storage["garbagefile_path"], "r", errors="ignore") as f:
        text = f.read()

    has_includes = simisa.has_includes(text)

    assert has_includes == False


def test_has_includes_shapefile(global_storage):
    with open(global_storage["shapefile_path"], "r", errors="ignore") as f:
        text = f.read()

    has_includes = simisa.has_includes(text)

    assert has_includes == False


def test_has_includes_worldfile_compressed(global_storage):
    with open(global_storage["worldfile_compressed_path"], "r", errors="ignore") as f:
        text = f.read()

    has_includes = simisa.has_includes(text)

    assert has_includes == False


def test_has_includes_include_tsectionext(global_storage):
    with open(global_storage["tsectionext_path"], "r", encoding="utf-16-le") as f:
        text = f.read()

    has_includes = simisa.has_includes(text)

    assert has_includes == True


def test_peek_first_include_emptyfile(global_storage):
    filepath = global_storage["emptyfile_path"]

    first_include = simisa.peek_first_include(filepath)
    
    assert first_include is None


def test_peek_first_include_garbagefile(global_storage):
    filepath = global_storage["garbagefile_path"]

    first_include = simisa.peek_first_include(filepath)

    assert first_include is None


def test_peek_first_include_shapefile(global_storage):
    filepath = global_storage["shapefile_path"]

    first_include = simisa.peek_first_include(filepath)

    assert first_include is None


def test_peek_first_include_worldfile_compressed(global_storage):
    filepath = global_storage["worldfile_compressed_path"]

    first_include = simisa.peek_first_include(filepath)

    assert first_include is None


def test_peek_first_include_tsectionext(global_storage):
    filepath = global_storage["tsectionext_path"]

    first_include = simisa.peek_first_include(filepath)

    assert first_include == "./tsectionglobal.dat"


def test_peek_first_include_tsectionext_blockbeforeinclude(global_storage):
    filepath = global_storage["tsectionext_blockbeforeinclude_path"]

    first_include = simisa.peek_first_include(filepath)

    assert first_include is None


def test_peek_first_include_tsectionext_commentsbeforeinclude(global_storage):
    filepath = global_storage["tsectionext_commentsbeforeinclude_path"]

    first_include = simisa.peek_first_include(filepath)

    assert first_include == "./tsectionglobal.dat"


def test_peek_first_include_tsectionglobal(global_storage):
    filepath = global_storage["tsectionglobal_path"]

    first_include = simisa.peek_first_include(filepath)

    assert first_include is None


def test_resolve_includes_noincludes(global_storage):
    filepath = global_storage["tsectionglobal_path"]

    with open(filepath, "r", encoding="utf-16-le") as f:
        text = f.read()

    resolved = simisa.resolve_includes(text, filepath)

    assert resolved == text


def test_resolve_includes_singleinclude(global_storage):
    filepath = global_storage["tsectionext_path"]

    with open(filepath, "r", encoding="utf-16-le") as f:
        text = f.read()

    resolved = simisa.resolve_includes(text, filepath)
    print(resolved)

    assert "TrackSections" in resolved
    assert "include ( \"./tsectionglobal.dat\" )" not in resolved.lower()


def test_resolve_includes_commentsbeforeinclude(global_storage):
    filepath = global_storage["tsectionext_commentsbeforeinclude_path"]

    with open(filepath, "r", encoding="utf-16-le") as f:
        text = f.read()

    resolved = simisa.resolve_includes(text, filepath)

    assert "TrackSections" in resolved
    assert "include ( \"./tsectionglobal.dat\" )" not in resolved.lower()


def test_resolve_includes_nestedincludes(global_storage):
    filepath = global_storage["tsectionext_nested_path"]

    with open(filepath, "r", encoding="utf-16-le") as f:
        text = f.read()

    resolved = simisa.resolve_includes(text, filepath)

    assert "TrackSections" in resolved
    assert "include ( \"./tsectionglobal.dat\" )" not in resolved.lower()
    assert "include ( \"./tsectionext.dat\" )" not in resolved.lower()
