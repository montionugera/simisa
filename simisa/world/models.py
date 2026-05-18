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



class WorldObject(ABC):
    uid: int
    file_name: Optional[str]
    static_detail_level: int
    static_flags: int
    vdb_id: int
    position: Optional["STFPosition"]
    direction: Optional["STFQDirection"]
    matrix: Optional["Matrix3x3"]


class BaseWorldObject(WorldObject):
    pass


class TrackLinkedObject(WorldObject):
    tr_item_ids: List["TrItemId"]


class WorldFile:
    tile_x: int
    tile_z: int
    world: "TrWorldFile"


class TrWorldFile:
    objects: List[WorldObject]


class StaticObj(BaseWorldObject):
    pass


class PickupObj(BaseWorldObject):
    pickup_type: int
    pickup_anim_data: Optional["PickupAnimData"]
    speed_range: Optional["SpeedRange"]
    pickup_capacity: Optional["PickupCapacity"]
    tr_item_ids: List["TrItemId"]
    collide_flags: int
    max_stacked_containers: int
    stack_locations_length: float
    stack_locations: Optional["StackLocations"]
    picking_surface_y_offset: float
    picking_surface_relative_top_start_position: Optional["Vector3"]
    grabber_arms_parts: int
    crane_sound: Optional[str]
    location: Optional["WorldLocation"]


class TransferObj(WorldObject):
    width: float
    height: float


class TrackObj(WorldObject):
    section_idx: int
    elevation: float
    collide_flags: int
    jnode_position: Optional["JNodePosn"]


class DynTrackObj(WorldObject):
    section_idx: int
    elevation: float
    collide_flags: int
    track_sections: Optional["TrackSections"]


class ForestObj(WorldObject):
    is_yard: bool
    tree_texture: Optional[str]
    population: int
    scale_range: Optional["ScaleRange"]
    forest_area: Optional["ForestArea"]
    tree_size: Optional["TreeSize"]


class SignalObj(WorldObject):
    signal_sub_obj: int
    signal_units: Optional["SignalUnits"]


class SpeedPostObj(WorldObject):
    speed_digit_tex: Optional[str]
    text_size: Optional["SpeedTextSize"]
    sign_shape: Optional["SpeedSignShape"]
    tr_item_ids: List["TrItemId"]


class LevelCrossingObj(WorldObject):
    level_parameters: Optional["LevelCrParameters"]
    level_data: Optional["LevelCrData"]
    level_timing: Optional["LevelCrTiming"]
    tr_item_ids: List["TrItemId"]
    crash_probability: int
    visible: bool
    silent: bool
    sound_filename: str


class HazardObj(WorldObject):
    item_id: int


class CarSpawnerObj(WorldObject):
    tr_item_ids: List["TrItemId"]
    car_frequency: float
    car_avg_speed: float
    list_name: Optional[str]
    car_spawner_list_idx: int


class TrObject(TrackLinkedObject):
    pass


class SidingObj(TrObject):
    pass


class PlatformObj(TrObject):
    platform_data: int


class TrItemId:
    db: int
    db_id: int


class Matrix3x3:
    ax: float
    ay: float
    az: float
    bx: float
    by: float
    bz: float
    cx: float
    cy: float
    cz: float


class JNodePosn:
    tile_x: int
    tile_z: int
    x: float
    y: float
    z: float


class TWorldPosition:
    x: float
    y: float
    z: float


class STFPosition(TWorldPosition):
    pass


class TWorldDirection:
    a: float
    b: float
    c: float
    d: float


class STFQDirection(TWorldDirection):
    pass


class Vector3:
    x: float
    y: float
    z: float


class WorldLocation:
    pass


class SpeedRange:
    min_mps: float
    max_mps: float


class PickupAnimData:
    pickup_options: float
    animation_speed: float


class PickupCapacity:
    quantity_available_kg: float
    feed_rate_kg_per_s: float


class StackLocations:
    locations: List["StackLocation"]


class StackLocation:
    position: Optional[Vector3]
    max_stacked_containers: int
    length: float
    flipped: bool


class TrackSections:
    sections: List["TrackSection"]


class TrackSection:
    is_curved: bool
    uid: int
    param1: float
    param2: float
    delta_y: float


class ScaleRange:
    minimum: float
    maximum: float


class ForestArea:
    x: float
    z: float


class TreeSize:
    width: float
    height: float


class SignalUnits:
    units: List["SignalUnit"]


class SignalUnit:
    sub_obj: int
    tr_item: int


class SpeedSignShape:
    num_shapes: int
    shape_info: List[float]


class SpeedTextSize:
    size: float
    dx: float
    dy: float


class LevelCrParameters:
    warning_time: float
    minimum_distance: float


class LevelCrData:
    data1: int
    data2: int


class LevelCrTiming:
    initial_timing: float
    serious_timing: float
    animation_timing: float


class PlatformDataFlag(IntFlag):
    PLATFORM_LEFT = 0x00000002
    PLATFORM_RIGHT = 0x00000004


class StaticFlag(IntFlag):
    ROUND_SHADOW = 0x00002000
    RECTANGULAR_SHADOW = 0x00004000
    TREELINE_SHADOW = 0x00008000
    DYNAMIC_SHADOW = 0x00010000
    TERRAIN = 0x00040000
    ANIMATE = 0x00080000
    GLOBAL = 0x00200000