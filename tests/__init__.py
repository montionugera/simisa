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


def compare_objects(left, right, path="root"):
    stack = [(left, right, path)]

    while stack:
        left, right, path = stack.pop()

        if isinstance(left, float) or isinstance(right, float):
            if not math.isclose(float(left), float(right), rel_tol=1e-5, abs_tol=1e-5):
                print(f"Float mismatch at {path}: {left} != {right}")
                return False
            continue

        if isinstance(left, (int, str, bool)) or left is None:
            if left != right:
                print(f"Value mismatch at {path}: {left} != {right}")
                return False
            continue

        if isinstance(left, (list, tuple)):
            if len(left) != len(right):
                print(f"Length mismatch at {path}: {len(left)} != {len(right)}")
                return False
            for i, (l_item, r_item) in enumerate(zip(left, right)):
                stack.append((l_item, r_item, f"{path}[{i}]"))
            continue

        if isinstance(left, dict):
            if left.keys() != right.keys():
                print(f"Key mismatch at {path}")
                return False
            for key in left:
                stack.append((left[key], right[key], f"{path}.{key}"))
            continue

        if hasattr(left, "__dict__"):
            stack.append((left.__dict__, right.__dict__, path))
            continue

        if left != right:
            print(f"Mismatch at {path}: {left} != {right}")
            return False

    return True
