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

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntFlag
from typing import Optional, List

from abc import ABC
from dataclasses import dataclass, field
from typing import Optional, List

# @dataclass
# class TrackLinkedObject(WorldObject):
#     tr_item_ids: List["TrItemId"]

# @dataclass
# class StaticObj(BaseWorldObject):
#     pass

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
# class TrackObj(WorldObject):
#     section_idx: int
#     elevation: float
#     collide_flags: int
#     jnode_position: Optional["JNodePosn"]

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
# class CarSpawnerObj(WorldObject):
#     tr_item_ids: List["TrItemId"]
#     car_frequency: float
#     car_avg_speed: float
#     list_name: Optional[str]
#     car_spawner_list_idx: int

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
# class Matrix3x3:
#     ax: float
#     ay: float
#     az: float
#     bx: float
#     by: float
#     bz: float
#     cx: float
#     cy: float
#     cz: float

# @dataclass
# class JNodePosn:
#     tile_x: int
#     tile_z: int
#     x: float
#     y: float
#     z: float

# @dataclass
# class TWorldPosition:
#     x: float
#     y: float
#     z: float

# @dataclass
# class STFPosition(TWorldPosition):
#     pass

# @dataclass
# class TWorldDirection:
#     a: float
#     b: float
#     c: float
#     d: float

# @dataclass
# class STFQDirection(TWorldDirection):
#     pass

# @dataclass
# class Vector3:
#     x: float
#     y: float
#     z: float

# @dataclass
# class WorldLocation:
#     pass

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
class WorldObject(ABC):
    uid: int = 0
    file_name: Optional[str] = None
    vdb_id: Optional[int] = None
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    qx: float = 0.0
    qy: float = 0.0
    qz: float = 0.0
    qw: float = 0.0

    def _base_repr(self):
        return (
            f"uid={self.uid}, "
            f"file_name={self.file_name}, "
            f"vdb_id={self.vdb_id}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"z={self.z}, "
            f"qx={self.qx}, "
            f"qy={self.qy}, "
            f"qz={self.qz}, "
            f"qw={self.qw}"
        )
    
    def __repr__(self):
        return f"WorldObject({self._base_repr()})"

@dataclass
class World:
    file_name: Optional[str] = None
    objects: List[WorldObject] = field(default_factory=list)

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