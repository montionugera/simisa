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
class SectionSkew:
    angle: float = 0.0

    def __repr__(self):
        return f"SectionSkew(angle={self.angle})"


@dataclass
class TrackSection:
    section_index: int
    section_size: Optional[SectionSize] = None
    section_curve: Optional[SectionCurve] = None
    section_skew: Optional[SectionSkew] = None
    water_scoop: bool = None

    def __repr__(self):
        return (
            f"TrackSection(section_index={self.section_index}, "
            f"section_size={self.section_size}, "
            f"section_curve={self.section_curve}, "
            f"section_skew={self.section_skew}, "
            f"water_scoop={self.water_scoop})"
        )


@dataclass
class RouteTrackSection(TrackSection):
    def __repr__(self):
        return (
            f"RouteTrackSection(section_index={self.section_index}, "
            f"section_size={self.section_size}, "
            f"section_curve={self.section_curve}, "
            f"section_skew={self.section_skew}, "
            f"water_scoop={self.water_scoop})"
        )


@dataclass
class TrackSections:
    track_sections: Dict[int, TrackSection] = field(default_factory=dict)
    max_section_index: Optional[int] = None

    def add(self, section: TrackSection):
        self.track_sections[section.section_index] = section
    
    def get(self, index: int) -> Optional[TrackSection]:
        if index in self.track_sections:
            return self.track_sections[index]
        
        return None
    
    def __add__(self, other):
        if not isinstance(other, TrackSections):
            raise TypeError(f"Cannot add TrackSections with {type(other).__name__}")

        merged_sections = {**self.track_sections, **other.track_sections}
        max_index = max(
            (v for v in [self.max_section_index, other.max_section_index] if v is not None),
            default=None,
        )

        return TrackSections(
            track_sections=merged_sections,
            max_section_index=max_index,
        )

    def __repr__(self):
        return (
            f"TrackSections(max_section_index={self.max_section_index}, "
            f"track_sections (len={len(self.track_sections)}))"
        )


@dataclass
class SectionIdx:
    x: float
    y: float
    z: float
    a: float
    track_sections: List[int]

    def __repr__(self):
        return (
            f"SectionIdx("
            f"x={self.x}, "
            f"y={self.y}, "
            f"z={self.z}, "
            f"a={self.a}, "
            f"track_sections (len={len(self.a)}))"
        )


@dataclass
class TrackPath:
    section_index: int
    track_sections: List[int]

    def __repr__(self):
        return (
            f"TrackPath(section_index={self.section_index}, "
            f"track_sections (len={len(self.track_sections)}))"
        )


@dataclass
class TSectionIdx:
    track_paths: Dict[int, TrackPath] = field(default_factory=dict)

    def add(self, path: TrackPath):
        self.track_paths[path.section_index] = path

    def __add__(self, other):
        if not isinstance(other, TSectionIdx):
            raise TypeError(f"Cannot add TSectionIdx with {type(other).__name__}")

        merged_paths = {**self.track_paths, **other.track_paths}

        return TSectionIdx(
            track_paths=merged_paths,
        )

    def __repr__(self):
        return (
            f"TSectionIdx(track_paths (len={len(self.track_paths)}))"
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

    def __repr__(self):
        return (
            f"TrackShape(shape_index={self.shape_index}, "
            f"file_name={self.file_name}, "
            f"num_paths={self.num_paths}, "
            f"main_route={self.main_route}, "
            f"clearance_distance={self.clearance_distance}, "
            f"section_idxs (len={len(self.section_idxs)}), "
            f"tunnel_shape={self.tunnel_shape}, "
            f"road_shape={self.road_shape})"
        )


@dataclass
class TrackShapes:
    track_shapes: Dict[int, TrackShape] = field(default_factory=dict)
    max_shape_index: Optional[int] = None

    def add(self, shape: TrackShape):
        self.track_shapes[shape.shape_index] = shape

    def get(self, index: int) -> TrackShape:
        if index not in self.track_shapes:
            raise ValueError("ShapeIndex not found")
        
        return self.track_shapes[index]
    
    def __add__(self, other):
        if not isinstance(other, TrackShapes):
            raise TypeError(f"Cannot add TrackShapes with {type(other).__name__}")
        
        merged_shapes = {**self.track_shapes, **other.track_shapes}
        max_index = max(
            (v for v in [self.max_shape_index, other.max_shape_index] if v is not None),
            default=None,
        )

        return TrackShapes(
            track_shapes=merged_shapes,
            max_shape_index=max_index,
        )

    def __repr__(self):
        return (
            f"TrackShapes(max_shape_index={self.max_shape_index}, "
            f"track_shapes (len={len(self.track_shapes)}))"
        )


@dataclass
class TSection:
    tracksections: Optional[TrackSections] = None
    trackshapes: Optional[TrackShapes] = None
    sectionidx: Optional[TSectionIdx] = None

    def __repr__(self):
        return (
            "TSection("
            f"tracksections={self.tracksections}, "
            f"trackshapes={self.trackshapes}, "
            f"sectionidx={self.sectionidx})"
        )