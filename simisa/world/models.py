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

from ..tracksections.models import TrackSections



class StaticFlag(IntFlag):
    ROUND_SHADOW = 0x00002000
    RECTANGULAR_SHADOW = 0x00004000
    TREELINE_SHADOW = 0x00008000
    DYNAMIC_SHADOW = 0x00010000
    TERRAIN = 0x00040000
    ANIMATE = 0x00080000
    GLOBAL = 0x00200000

class PlatformDataFlag(IntFlag):
    PLATFORM_LEFT = 0x00000002
    PLATFORM_RIGHT = 0x00000004

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
class JNodePosition:
    tile_x: int = 0
    tile_z: int = 0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __repr__(self):
        return (
            "JNodePosition("
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
    jnode_position: Optional[JNodePosition] = None

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
            f"tr_item_ids (len={len(self.tr_item_ids)}))"
        )

@dataclass
class SidingObj(WorldObj):
    tr_item_ids: List[TrItemId] = field(default_factory=list)

    def __repr__(self):
        return (
            "SidingObj("
            f"{self._base_repr()}, "
            f"tr_item_ids (len={len(self.tr_item_ids)}))"
        )

@dataclass
class PlatformObj(WorldObj):
    platform_data: int = 0
    tr_item_ids: List[TrItemId] = field(default_factory=list)

    def __repr__(self):
        return (
            "PlatformObj("
            f"{self._base_repr()}, "
            f"platform_data={self.platform_data}, "
            f"tr_item_ids (len={len(self.tr_item_ids)}))"
        )

@dataclass
class ScaleRange:
    minimum: float = 0.0
    maximum: float = 0.0

    def __repr__(self):
        return (
            "ScaleRange("
            f"minimum={self.minimum}, "
            f"maximum={self.maximum})"
        )

@dataclass
class ForestArea:
    x: float = 0.0
    z: float = 0.0

    def __repr__(self):
        return (
            "ForestArea("
            f"x={self.x}, "
            f"z={self.z})"
        )

@dataclass
class TreeSize:
    width: float = 0.0
    height: float = 0.0

    def __repr__(self):
        return (
            "TreeSize("
            f"width={self.width}, "
            f"height={self.height})"
        )

@dataclass
class ForestObj(WorldObj):
    is_yard: bool = False
    tree_texture: Optional[str] = None
    population: int = 0
    scale_range: Optional[ScaleRange] = None
    forest_area: Optional[ForestArea] = None
    tree_size: Optional[TreeSize] = None

    def __repr__(self):
        return (
            "ForestObj("
            f"{self._base_repr()}, "
            f"is_yard={self.is_yard}, "
            f"tree_texture={self.tree_texture}, "
            f"population={self.population}, "
            f"scale_range={self.scale_range}, "
            f"forest_area={self.forest_area}, "
            f"tree_size={self.tree_size})"
        )

@dataclass
class LevelCrParams:
    warning_time: float = 0.0
    minimum_distance: float = 0.0

    def __repr__(self):
        return (
            "LevelCrParams("
            f"warning_time={self.warning_time}, "
            f"minimum_distance={self.minimum_distance})"
        )

@dataclass
class LevelCrData:
    data1: int = 0
    data2: int = 0

    def __repr__(self):
        return (
            "LevelCrData("
            f"data1={self.data1}, "
            f"data2={self.data2})"
        )

@dataclass
class LevelCrTiming:
    initial_timing: float = 0.0
    serious_timing: float = 0.0
    animation_timing: float = 0.0

    def __repr__(self):
        return (
            "LevelCrTiming("
            f"initial_timing={self.initial_timing}, "
            f"serious_timing={self.serious_timing}, "
            f"animation_timing={self.animation_timing})"
        )

@dataclass
class LevelCrObj(WorldObj):
    crash_probability: int = 0
    visible: bool = True
    silent: bool = False
    sound_filename: str = ""
    levelcr_params: Optional[LevelCrParams] = None
    levelcr_data: Optional[LevelCrData] = None
    levelcr_timing: Optional[LevelCrTiming] = None
    tr_item_ids: List[TrItemId] = field(default_factory=list)

    def __repr__(self):
        return (
            "LevelCrObj("
            f"{self._base_repr()}, "
            f"crash_probability={self.crash_probability}, "
            f"visible={self.visible}, "
            f"silent={self.silent}, "
            f"sound_filename={self.sound_filename}, "
            f"levelcr_params={self.levelcr_params}, "
            f"levelcr_data={self.levelcr_data}, "
            f"levelcr_timing={self.levelcr_timing}, "
            f"tr_item_ids (len={len(self.tr_item_ids)}))"
        )

@dataclass
class DynTrackObj(WorldObj):
    section_index: int = 0
    elevation: float = 0.0
    collide_flags: int = 0
    track_sections: Optional[TrackSections] = None

    def __repr__(self):
        return (
            "DynTrackObj("
            f"{self._base_repr()}, "
            f"section_index={self.section_index}, "
            f"elevation={self.elevation}, "
            f"collide_flags={self.collide_flags}, "
            f"track_sections={self.track_sections})"
        )

@dataclass
class TransferObj(WorldObj):
    width: float = 0.0
    height: float = 0.0

    def __repr__(self):
        return (
            "TransferObj("
            f"{self._base_repr()}, "
            f"width={self.width}, "
            f"height={self.height})"
        )

@dataclass
class GantryObj(WorldObj):

    def __repr__(self):
        return f"GantryObj({self._base_repr()})"

@dataclass
class SpeedRange:
    min_mps: float = 0.0
    max_mps: float = 0.0

    def __repr__(self):
        return (
            "SpeedRange("
            f"min_mps={self.min_mps}, "
            f"max_mps={self.max_mps})"
        )

@dataclass
class PickupAnimData:
    pickup_options: float = 0.0
    animation_speed: float = 0.0

    def __repr__(self):
        return (
            "PickupAnimData("
            f"pickup_options={self.pickup_options}, "
            f"animation_speed={self.animation_speed})"
        )

@dataclass
class PickupCapacity:
    quantity_available_kg: float = 0.0
    feed_rate_kg_per_s: float = 0.0

    def __repr__(self):
        return (
            "PickupCapacity("
            f"quantity_available_kg={self.quantity_available_kg}, "
            f"feed_rate_kg_per_s={self.feed_rate_kg_per_s})"
        )

@dataclass
class StackLocation:
    position: Optional[Position] = None
    max_stacked_containers: int = 0
    length: float = 0.0
    flipped: bool = False

    def __repr__(self):
        return (
            "StackLocation("
            f"position={self.position}, "
            f"max_stacked_containers={self.max_stacked_containers}, "
            f"length={self.length}, "
            f"flipped={self.flipped})"
        )

@dataclass
class PickupObj(WorldObj):
    pickup_type: int = 0
    pickup_anim_data: Optional[PickupAnimData] = None
    pickup_capacity: Optional[PickupCapacity] = None
    speed_range: Optional[SpeedRange] = None
    collide_flags: int = 0
    unknown: int = 0
    max_stacked_containers: int = 0
    stack_locations_length: float = 12.19
    stack_locations: List[StackLocation] = field(default_factory=list)
    picking_surface_y_offset: float = 0.0
    picking_surface_relative_top_start_position: Optional[Position] = None
    grabber_arms_parts: int = 2
    crane_sound: Optional[str] = None
    tr_item_ids: List[TrItemId] = field(default_factory=list)

    def __repr__(self):
        return (
            "PickupObj("
            f"{self._base_repr()}, "
            f"pickup_type={self.pickup_type}, "
            f"pickup_anim_data={self.pickup_anim_data}, "
            f"pickup_capacity={self.pickup_capacity}, "
            f"speed_range={self.speed_range}, "
            f"collide_flags={self.collide_flags}, "
            f"unknown={self.unknown}, "
            f"max_stacked_containers={self.max_stacked_containers}, "
            f"stack_locations_length={self.stack_locations_length}, "
            f"stack_locations (len={len(self.stack_locations)}), "
            f"picking_surface_y_offset={self.picking_surface_y_offset}, "
            f"picking_surface_relative_top_start_position={self.picking_surface_relative_top_start_position}, "
            f"grabber_arms_parts={self.grabber_arms_parts}, "
            f"crane_sound={self.crane_sound}, "
            f"tr_item_ids (len={len(self.tr_item_ids)}))"
        )

@dataclass
class HazardObj(WorldObj):
    tr_item_id: Optional[TrItemId] = None

    def __repr__(self):
        return (
            "HazardObj("
            f"{self._base_repr()}, "
            f"tr_item_id={self.tr_item_id})"
        )

@dataclass
class SignalUnit:
    sub_obj: int = 0
    tr_item_id: Optional[TrItemId] = None

    def __repr__(self):
        return (
            "SignalUnit("
            f"sub_obj={self.sub_obj}, "
            f"tr_item_id={self.tr_item_id})"
        )

@dataclass
class SignalObj(WorldObj):
    signal_sub_obj: int = 0
    signal_units: List[SignalUnit] = field(default_factory=list)

    def __repr__(self):
        return (
            "SignalObj("
            f"{self._base_repr()}, "
            f"signal_sub_obj={self.signal_sub_obj}, "
            f"signal_units (len={len(self.signal_units)}))"
        )

@dataclass
class SpeedSignShape:
    num_shapes: int = 0
    shape_info: List[float] = field(default_factory=list)

    def __repr__(self):
        return (
            "SpeedSignShape("
            f"num_shapes={self.num_shapes}, "
            f"shape_info={self.shape_info})"
        )

@dataclass
class SpeedTextSize:
    size: float = 0.0
    dx: float = 0.0
    dy: float = 0.0

    def __repr__(self):
        return (
            "SpeedTextSize("
            f"size={self.size}, "
            f"dx={self.dx}, "
            f"dy={self.dy})"
        )

@dataclass
class SpeedPostObj(WorldObj):
    speed_digit_tex: Optional[str] = None
    text_size: Optional[SpeedTextSize] = None
    sign_shape: Optional[SpeedSignShape] = None
    tr_item_ids: List[TrItemId] = field(default_factory=list)

    def __repr__(self):
        return (
            "SpeedPostObj("
            f"{self._base_repr()}, "
            f"speed_digit_tex={self.speed_digit_tex}, "
            f"text_size={self.text_size}, "
            f"sign_shape={self.sign_shape}, "
            f"tr_item_ids (len={len(self.tr_item_ids)}))"
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