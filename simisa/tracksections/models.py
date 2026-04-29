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

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class SectionCurve:
    radius: float = 0.0
    angle: float = 0.0

    def __repr__(self):
        return f"SectionCurve(radius={self.radius}, angle={self.angle})"


@dataclass
class SectionSize:
    width: float = 1.5
    length: float = 0.0

    def __repr__(self):
        return f"SectionSize(width={self.width}, length={self.length})"


@dataclass
class TrackSection:
    section_index: int
    section_size: Optional[SectionSize] = None
    section_curve: Optional[SectionCurve] = None

    def __repr__(self):
        return (
            f"TrackSection(index={self.section_index}, "
            f"size={self.section_size}, "
            f"curve={self.section_curve})"
        )


@dataclass
class RouteTrackSection(TrackSection):
    def __repr__(self):
        return (
            f"RouteTrackSection(index={self.section_index}, "
            f"size={self.section_size}, "
            f"curve={self.section_curve})"
        )


@dataclass
class TrackSections:
    sections: Dict[int, TrackSection] = field(default_factory=dict)
    max_section_index: Optional[int] = None
    missing_track_section_warnings: int = 0

    def add_section(self, section: TrackSection):
        self.sections[section.section_index] = section

    def get(self, index: int) -> Optional[TrackSection]:
        if index in self.sections:
            return self.sections[index]

        if self.missing_track_section_warnings < 5:
            print(f"Warning: missing TrackSection {index}")
            self.missing_track_section_warnings += 1

        return None

    def __repr__(self):
        return (
            f"TrackSections(count={len(self.sections)}, "
            f"max_index={self.max_section_index})"
        )


@dataclass
class SectionIdx:
    no_sections: int
    x: float
    y: float
    z: float
    a: float
    track_sections: List[int]

    def __repr__(self):
        return (
            f"SectionIdx(n={self.no_sections}, "
            f"offset=({self.x}, {self.y}, {self.z}), "
            f"a={self.a})"
        )


@dataclass
class TrackPath:
    dynamic_section_index: int
    no_sections: int
    track_sections: List[int]

    def __repr__(self):
        return (
            f"TrackPath(index={self.dynamic_section_index}, "
            f"n={self.no_sections})"
        )


@dataclass
class TSectionIdx:
    no_sections: int
    track_paths: Dict[int, TrackPath] = field(default_factory=dict)

    def add_path(self, path: TrackPath):
        self.track_paths[path.dynamic_section_index] = path

    def __repr__(self):
        return (
            f"TSectionIdx(n={self.no_sections}, "
            f"paths={len(self.track_paths)})"
        )


@dataclass
class TrackShape:
    shape_index: int
    file_name: Optional[str] = None
    num_paths: Optional[int] = None
    main_route: Optional[int] = None
    clearance_distance: float = 0.0
    section_idxs: Optional[List[SectionIdx]] = None
    tunnel_shape: bool = False
    road_shape: bool = False
    rack_shape: bool = False

    def __repr__(self):
        return (
            f"TrackShape(index={self.shape_index}, "
            f"paths={self.num_paths}, "
            f"file='{self.file_name}')"
        )


@dataclass
class TrackShapes:
    shapes: Dict[int, TrackShape] = field(default_factory=dict)
    max_shape_index: Optional[int] = None

    def add(self, shape: TrackShape):
        self.shapes[shape.shape_index] = shape

    def get(self, index: int) -> TrackShape:
        if index not in self.shapes:
            raise ValueError("ShapeIndex not found")
        return self.shapes[index]

    def __repr__(self):
        return (
            f"TrackShapes(count={len(self.shapes)}, "
            f"max_index={self.max_shape_index})"
        )


@dataclass
class TrackSectionsFile:
    track_sections: Optional[TrackSections] = None
    track_shapes: Optional[TrackShapes] = None
    tsection_idx: Optional[TSectionIdx] = None

    def __repr__(self):
        return (
            "TrackSectionsFile("
            f"sections={self.track_sections}, "
            f"shapes={self.track_shapes})"
        )