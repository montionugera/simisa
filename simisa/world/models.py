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

from abc import ABC
from dataclasses import dataclass, field
from enum import IntFlag
from typing import Optional, List

# @dataclass
# class TrackLinkedObject(WorldObject):
#     tr_item_ids: List["TrItemId"]

# @dataclass
# class PickupObj(BaseWorldObject):
#     pickup_type: int
#     pickup_anim_data: Optional["PickupAnimData"]
#     speed_range: Optional["SpeedRange"]
#     pickup_capacity: Optional["PickupCapacity"]
#     tr_item_ids: List["TrItemId"]
#     collide_flags: int
#     max_stacked_containers: int
#     stack_locations_length: float
#     stack_locations: Optional["StackLocations"]
#     picking_surface_y_offset: float
#     picking_surface_relative_top_start_position: Optional["Vector3"]
#     grabber_arms_parts: int
#     crane_sound: Optional[str]
#     location: Optional["WorldLocation"]

# @dataclass
# class TransferObj(WorldObject):
#     width: float
#     height: float

# @dataclass
# class DynTrackObj(WorldObject):
#     section_idx: int
#     elevation: float
#     collide_flags: int
#     track_sections: Optional["TrackSections"]

# @dataclass
# class ForestObj(WorldObject):
#     is_yard: bool
#     tree_texture: Optional[str]
#     population: int
#     scale_range: Optional["ScaleRange"]
#     forest_area: Optional["ForestArea"]
#     tree_size: Optional["TreeSize"]

# @dataclass
# class SignalObj(WorldObject):
#     signal_sub_obj: int
#     signal_units: Optional["SignalUnits"]

# @dataclass
# class SpeedPostObj(WorldObject):
#     speed_digit_tex: Optional[str]
#     text_size: Optional["SpeedTextSize"]
#     sign_shape: Optional["SpeedSignShape"]
#     tr_item_ids: List["TrItemId"]

# @dataclass
# class LevelCrossingObj(WorldObject):
#     level_parameters: Optional["LevelCrParameters"]
#     level_data: Optional["LevelCrData"]
#     level_timing: Optional["LevelCrTiming"]
#     tr_item_ids: List["TrItemId"]
#     crash_probability: int
#     visible: bool
#     silent: bool
#     sound_filename: str

# @dataclass
# class HazardObj(WorldObject):
#     item_id: int

# @dataclass
# class TrObject(TrackLinkedObject):
#     pass

# @dataclass
# class SidingObj(TrObject):
#     pass

# @dataclass
# class PlatformObj(TrObject):
#     platform_data: int

# @dataclass
# class TrItemId:
#     db: int
#     db_id: int

# @dataclass
# class SpeedRange:
#     min_mps: float
#     max_mps: float

# @dataclass
# class PickupAnimData:
#     pickup_options: float
#     animation_speed: float

# @dataclass
# class PickupCapacity:
#     quantity_available_kg: float
#     feed_rate_kg_per_s: float

# @dataclass
# class StackLocations:
#     locations: List["StackLocation"]

# @dataclass
# class StackLocation:
#     position: Optional[Vector3]
#     max_stacked_containers: int
#     length: float
#     flipped: bool


# @dataclass
# class TrackSections:
#     sections: List["TrackSection"]

# @dataclass
# class TrackSection:
#     is_curved: bool
#     uid: int
#     param1: float
#     param2: float
#     delta_y: float

# @dataclass
# class ScaleRange:
#     minimum: float
#     maximum: float

# @dataclass
# class ForestArea:
#     x: float
#     z: float

# @dataclass
# class TreeSize:
#     width: float
#     height: float

# @dataclass
# class SignalUnits:
#     units: List["SignalUnit"]

# @dataclass
# class SignalUnit:
#     sub_obj: int
#     tr_item: int

# @dataclass
# class SpeedSignShape:
#     num_shapes: int
#     shape_info: List[float]

# @dataclass
# class SpeedTextSize:
#     size: float
#     dx: float
#     dy: float

# @dataclass
# class LevelCrParameters:
#     warning_time: float
#     minimum_distance: float

# @dataclass
# class LevelCrData:
#     data1: int
#     data2: int

# @dataclass
# class LevelCrTiming:
#     initial_timing: float
#     serious_timing: float
#     animation_timing: float

# class PlatformDataFlag(IntFlag):
#     PLATFORM_LEFT = 0x00000002
#     PLATFORM_RIGHT = 0x00000004

# class StaticFlag(IntFlag):
#     ROUND_SHADOW = 0x00002000
#     RECTANGULAR_SHADOW = 0x00004000
#     TREELINE_SHADOW = 0x00008000
#     DYNAMIC_SHADOW = 0x00010000
#     TERRAIN = 0x00040000
#     ANIMATE = 0x00080000
#     GLOBAL = 0x00200000

###########################


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __repr__(self):
        return (
            "Position("
            f"x={self.z}, "
            f"y={self.y}, "
            f"z={self.z})"
        )

@dataclass
class QDirection:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0

    def __repr__(self):
        return (
            "QDirection("
            f"x={self.z}, "
            f"y={self.y}, "
            f"z={self.z}, "
            f"w={self.w})"
        )

@dataclass
class Matrix3x3:
    ax: float = 0.0
    ay: float = 0.0
    az: float = 0.0
    bx: float = 0.0
    by: float = 0.0
    bz: float = 0.0
    cx: float = 0.0
    cy: float = 0.0
    cz: float = 0.0

    def __repr__(self):
        return (
            "Matrix3x3("
            f"ax={self.ax}, "
            f"ay={self.ay}, "
            f"az={self.az}, "
            f"bx={self.bx}, "
            f"by={self.by}, "
            f"bz={self.bz}, "
            f"cx={self.cx}, "
            f"cy={self.cy}, "
            f"cz={self.cz})"
        )

@dataclass
class WorldObj(ABC):
    uid: int = 0
    file_name: Optional[str] = None
    vdb_id: Optional[int] = None
    static_detail_level: int = 0
    static_flags: int = 0
    position: Position = field(default_factory=lambda: Position(0.0, 0.0, 0.0))
    direction: QDirection = field(default_factory=lambda: QDirection(0.0, 0.0, 0.0, 1.0))
    matrix3x3: Optional[Matrix3x3] = None

    def _base_repr(self):
        return (
            f"uid={self.uid}, "
            f"file_name={self.file_name}, "
            f"vdb_id={self.vdb_id}, "
            f"static_detail_level={self.static_detail_level}, "
            f"static_flags={self.static_flags}, "
            f"position={self.position}, "
            f"direction={self.direction}, "
            f"matrix3x3={self.matrix3x3}"
        )
    
    def __repr__(self):
        return f"WorldObj({self._base_repr()})"

@dataclass
class StaticObj(WorldObj):

    def __repr__(self):
        return f"StaticObj({self._base_repr()})"

@dataclass
class JNodePosn:
    tile_x: int = 0
    tile_z: int = 0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __repr__(self):
        return (
            "JNodePosn("
            f"tile_x={self.tile_x}, "
            f"tile_z={self.tile_z}, "
            f"x={self.z}, "
            f"y={self.y}, "
            f"z={self.z})"
        )

@dataclass
class TrackObj(WorldObj):
    section_index: int = 0
    elevation: float = 0.0
    collide_flags: int = 0x00200180
    jnode_position: Optional[JNodePosn] = None

    def __repr__(self):
        return (
            "TrackObj("
            f"{self._base_repr()}, "
            f"section_index={self.section_index}, "
            f"elevation={self.elevation}, "
            f"collide_flags={self.collide_flags}, "
            f"jnode_position={self.jnode_position})"
        )

@dataclass
class TrItemId:
    db: int = 0
    db_id: int = 0

    def __repr__(self):
        return (
            "TrItemId("
            f"db={self.db}, "
            f"db_id={self.db_id})"
        )

@dataclass
class CarSpawnerObj(WorldObj):
    list_name: Optional[str] = None
    car_frequency: float = 5.0
    car_avg_speed: float = 20.0
    car_spawner_list_index: int = 0
    tr_item_ids: List[TrItemId] = field(default_factory=list)

    def __repr__(self):
        return (
            "CarSpawnerObj("
            f"{self._base_repr()}, "
            f"list_name={self.list_name}, "
            f"car_frequency={self.car_frequency}, "
            f"car_avg_speed={self.car_avg_speed}, "
            f"car_spawner_list_index={self.car_spawner_list_index}, "
            f"tr_item_ids (len={self.tr_item_ids}))"
        )

@dataclass
class World:
    file_name: Optional[str] = None
    objects: List[WorldObj] = field(default_factory=list)

    @property
    def tile_x(self) -> Optional[int]:
        if self.file_name is None:
            return None
        
        try:
            return int(self.file_name[1:8])
        except ValueError:
            return None

    @property
    def tile_z(self):
        if self.file_name is None:
            return None
        
        try:
            return int(self.file_name[8:15])
        except ValueError:
            return None
    
    def __repr__(self):
        return (
            f"World(file_name={self.file_name}, "
            f"tile_x={self.tile_x}, "
            f"tile_z={self.tile_z}, "
            f"objects (len={len(self.objects)}))"
        )