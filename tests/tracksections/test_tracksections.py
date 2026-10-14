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
from simisa import tracksections, SimisaSubheaderError


def test_global_tsection_load(global_storage):
    tsection = tracksections.load(global_storage["tsectionglobal_path"])

    assert tsection.tracksections.max_section_index == 40000
    assert len(tsection.tracksections.track_sections) == 7433
    assert len(tsection.trackshapes.track_shapes) == 14934
    assert tsection.sectionidx is None
    assert tsection.tracksections.track_sections[1].section_index == 1
    assert tsection.tracksections.track_sections[1].section_size.width == 1.5
    assert tsection.tracksections.track_sections[1].section_size.length == 50.0
    assert tsection.tracksections.track_sections[1].section_curve is None
    assert tsection.tracksections.track_sections[1].section_skew is None
    assert tsection.tracksections.track_sections[1].water_scoop == False
    assert tsection.trackshapes.track_shapes[1].shape_index == 1
    assert tsection.trackshapes.track_shapes[1].file_name == "A1t50mStrt.s"
    assert tsection.trackshapes.track_shapes[1].num_paths == 1
    assert tsection.trackshapes.track_shapes[1].main_route is None
    assert len(tsection.trackshapes.track_shapes[1].section_idxs) == 1


def test_globalext_tsection_load(global_storage):
    tsection = tracksections.load(global_storage["tsectionext_path"])

    assert tsection.tracksections.max_section_index == 50000
    assert len(tsection.tracksections.track_sections) == 7441
    assert len(tsection.trackshapes.track_shapes) == 14952
    assert tsection.sectionidx is None
    assert tsection.tracksections.track_sections[1].section_index == 1
    assert tsection.tracksections.track_sections[1].section_size.width == 1.5
    assert tsection.tracksections.track_sections[1].section_size.length == 50.0
    assert tsection.tracksections.track_sections[1].section_curve is None
    assert tsection.tracksections.track_sections[1].section_skew is None
    assert tsection.tracksections.track_sections[1].water_scoop == False
    assert tsection.tracksections.track_sections[40003].section_index == 40003
    assert tsection.tracksections.track_sections[40003].section_size.width == 1.5
    assert tsection.tracksections.track_sections[40003].section_size.length == 0.0
    assert tsection.tracksections.track_sections[40003].section_curve.radius == 29997.5
    assert tsection.tracksections.track_sections[40003].section_curve.angle == 0.019097
    assert tsection.tracksections.track_sections[40003].section_skew is None
    assert tsection.tracksections.track_sections[40003].water_scoop == False
    assert tsection.trackshapes.track_shapes[1].shape_index == 1
    assert tsection.trackshapes.track_shapes[1].file_name == "A1t50mStrt.s"
    assert tsection.trackshapes.track_shapes[1].num_paths == 1
    assert tsection.trackshapes.track_shapes[1].main_route is None
    assert len(tsection.trackshapes.track_shapes[1].section_idxs) == 1
    assert tsection.trackshapes.track_shapes[40013].shape_index == 40013
    assert tsection.trackshapes.track_shapes[40013].file_name == "DB22f_a1t30000r0_25d_i.s"
    assert tsection.trackshapes.track_shapes[40013].num_paths == 1
    assert tsection.trackshapes.track_shapes[40013].main_route is None
    assert len(tsection.trackshapes.track_shapes[40013].section_idxs) == 1


def test_local_tsection_load(global_storage):
    tsection = tracksections.load(global_storage["tsectionlocal_path"])

    assert tsection.tracksections.max_section_index == 78
    assert len(tsection.tracksections.track_sections) == 77
    assert tsection.trackshapes is None
    assert len(tsection.sectionidx.track_paths) == 39
    assert tsection.tracksections.track_sections[50002].section_index == 50002
    assert tsection.tracksections.track_sections[50002].section_size is None
    assert tsection.tracksections.track_sections[50002].section_curve.radius == 15000.0
    assert tsection.tracksections.track_sections[50002].section_curve.angle == -0.24980959867703895
    assert tsection.tracksections.track_sections[50002].section_skew is None
    assert tsection.tracksections.track_sections[50002].water_scoop is None
    assert tsection.sectionidx.track_paths[50009].section_index == 50009
    assert tsection.sectionidx.track_paths[50009].track_sections == [50019]


def test_tsection_load_shape_raises(global_storage):
    shapefile_path = global_storage["shapefile_path"]

    with pytest.raises(SimisaSubheaderError):
        tracksections.load(shapefile_path)


def test_tsection_loads_bytes_raises(global_storage):
    tracksections_path = global_storage["tsectionglobal_path"]

    with open(tracksections_path, 'rb') as f:
        tracksections_bytes = f.read()
        
        with pytest.raises(TypeError):
            tracksections.loads(tracksections_bytes)
