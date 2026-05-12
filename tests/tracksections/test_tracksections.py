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

import math
import pytest
from simisa import tracksections


# def test_tracksections_load(global_storage):
#     s = tracksections.load(global_storage["tracksectionsfile_path"])
#     assert False


# def test_tracksections_loads_uncompressed(global_storage):
#     tracksectionsfile_path = global_storage["tracksectionsfile_path"]
#     with open(tracksectionsfile_path, 'r', encoding='utf-16-le') as f:
#         tracksections_string = f.read()
#         s = tracksections.loads(tracksections_string)
#     assert False


def test_tracksections_load_tsectionlocal(global_storage):
    t = tracksections.load(global_storage["tsectionlocal_path"])
    print(t)
    assert False


def test_tracksections_load_tsectionglobal(global_storage):
    t = tracksections.load(global_storage["tsectionglobal_path"])
    print(t)
    assert False


# def test_tracksections_load_compare(global_storage):
#     expected = tracksections.load(global_storage["tracksectionsfile_path"])
#     actual = tracksections.load(global_storage["tracksectionsfile_compressed_path"])

#     stack = [(expected, actual, "root")]

#     while stack:
#         left, right, path = stack.pop()

#         if isinstance(left, float) or isinstance(right, float):
#             if not math.isclose(float(left), float(right), rel_tol=1e-5, abs_tol=1e-5):
#                 print(f"Float mismatch at {path}: {left} != {right}")
#                 assert False
#             continue

#         if isinstance(left, (int, str, bool)) or left is None:
#             if left != right:
#                 print(f"Value mismatch at {path}: {left} != {right}")
#                 assert False
#             continue

#         if isinstance(left, (list, tuple)):
#             if len(left) != len(right):
#                 print(f"Length mismatch at {path}: {len(left)} != {len(right)}")
#                 assert False
#             for i, (l_item, r_item) in enumerate(zip(left, right)):
#                 stack.append((l_item, r_item, f"{path}[{i}]"))
#             continue

#         if isinstance(left, dict):
#             if left.keys() != right.keys():
#                 print(f"Key mismatch at {path}")
#                 assert False
#             for key in left:
#                 stack.append((left[key], right[key], f"{path}.{key}"))
#             continue

#         if hasattr(left, "__dict__"):
#             stack.append((left.__dict__, right.__dict__, path))
#             continue

#         if left != right:
#             print(f"Mismatch at {path}: {left} != {right}")
#             assert False

#     assert True


# def test_tracksections_loads_compressed(global_storage):
#     tracksectionsfile_compressed_path = global_storage["tracksectionsfile_compressed_path"]
#     with open(tracksectionsfile_compressed_path, 'rb') as f:
#         tracksections_bytes = f.read()
        
#         with pytest.raises(TypeError):
#             tracksections.loads(tracksections_bytes)