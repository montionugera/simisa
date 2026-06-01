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
from .. import TokenID
from ..writer import BlockWriter
from .models import *


def write_local_tracksections(writer: BlockWriter, tracksections: TrackSections) -> None:
    writer.write_uint(tracksections.max_section_index)

    for section_index, tracksection in sorted(tracksections.track_sections.items()):
        with writer.sub_block(TokenID.TrackSection):
            with writer.sub_block(TokenID.SectionCurve):
                writer.write_int(0)

            writer.write_uint(tracksection.section_index)

            if tracksection.section_size is not None:
                writer.write_float(tracksection.section_size.length)
                writer.write_float(0.0)
            
            elif tracksection.section_curve is not None:
                writer.write_float(math.radians(tracksection.section_curve.angle))
                writer.write_float(tracksection.section_curve.radius)
