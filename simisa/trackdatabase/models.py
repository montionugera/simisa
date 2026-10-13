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
from typing import Optional, List


@dataclass
class TrItem(ABC):
    name: Optional[str] = None
    item_id: int = 0
    tile_x: int = 0
    tile_z: int = 0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    tile_px: int = 0
    tile_pz: int = 0
    px: float = 0.0
    pz: float = 0.0
    sdata1: float = 0.0
    sdata2: int = 0

    def _base_repr(self):
        return (
            f"name={self.name}, "
            f"item_id={self.item_id}, "
            f"tile_x={self.tile_x}, "
            f"tile_z={self.tile_z}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"z={self.z}, "
            f"tile_px={self.tile_px}, "
            f"tile_pz={self.tile_pz}, "
            f"px={self.px}, "
            f"pz={self.pz}, "
            f"sdata1={self.sdata1}, "
            f"sdata2={self.sdata2}"
        )
    
    def __repr__(self):
        return f"TrItem({self._base_repr()})"

@dataclass
class EmptyItem(TrItem):

    def __repr__(self):
        return f"EmptyItem({self._base_repr()})"

@dataclass
class CrossoverItem(TrItem):
    track_node: int = 0
    shape_index: int = 0

    def __repr__(self):
        return (
            "CrossoverItem("
            f"{self._base_repr()}, "
            f"track_node={self.track_node}, "
            f"shape_index={self.shape_index})"
        )

@dataclass
class SignalDirection:
    track_node: int = 0
    sd1: int = 0
    link_lr_path: int = 0
    sd3: int = 0

    def __repr__(self):
        return (
            f"SignalDirection(track_node={self.track_node}, "
            f"sd1={self.sd1}, "
            f"link_lr_path={self.link_lr_path}, "
            f"sd3={self.sd3}))"
        )

@dataclass
class SignalItem(TrItem):
    flags: int = 0
    direction: int = 0
    signal_data1: float = 0.0
    signal_type: Optional[str] = None
    signal_dirs: List[SignalDirection] = field(default_factory=list)

    def __repr__(self):
        return (
            "SignalItem("
            f"{self._base_repr()}, "
            f"flags={self.flags}, "
            f"direction={self.direction}, "
            f"signal_data1={self.signal_data1}, "
            f"signal_type={self.signal_type}, "
            f"signal_dirs (len={len(self.signal_dirs)}))"
        )

@dataclass
class SpeedPostItem(TrItem):
    flags: int = 0
    is_mile_post: bool = False
    is_warning: bool = False
    is_limit: bool = False
    is_resume: bool = False
    is_passenger: bool = False
    is_freight: bool = False
    is_mph: bool = False
    show_number: bool = False
    show_dot: bool = False
    speed_ind: float = 0.0
    angle: float = 0.0
    direction: int = 0
    display_number: int = 0

    def __repr__(self):
        return (
            "SpeedPostItem("
            f"{self._base_repr()}, "
            f"flags={self.flags}, "
            f"is_mile_post={self.is_mile_post}, "
            f"is_warning={self.is_warning}, "
            f"is_limit={self.is_limit}, "
            f"is_resume={self.is_resume}, "
            f"is_passenger={self.is_passenger}, "
            f"is_freight={self.is_freight}, "
            f"is_mph={self.is_mph}, "
            f"show_number={self.show_number}, "
            f"show_dot={self.show_dot}, "
            f"speed_ind={self.speed_ind}, "
            f"angle={self.angle}, "
            f"direction={self.direction}, "
            f"display_number={self.display_number})"
        )

@dataclass
class SoundRegionItem(TrItem):
    sr_data1: int = 0
    sr_data2: int = 0
    sr_data3: float = 0.0

    def __repr__(self):
        return (
            "SoundRegionItem("
            f"{self._base_repr()}, "
            f"sr_data1={self.sr_data1}, "
            f"sr_data2={self.sr_data2}, "
            f"sr_data3={self.sr_data3})"
        )

@dataclass
class LevelCrItem(TrItem):

    def __repr__(self):
        return f"LevelCrItem({self._base_repr()})"

@dataclass
class SidingItem(TrItem):
    flags: int = 0
    linked_siding_item_id: int = 0

    def __repr__(self):
        return (
            "SidingItem("
            f"{self._base_repr()}, "
            f"flags={self.flags}, "
            f"linked_siding_item_id={self.linked_siding_item_id})"
        )

@dataclass
class PlatformItem(TrItem):
    station: Optional[str] = None
    flags: int = 0
    min_waiting_time: int = 0
    num_passengers_waiting: int = 0
    linked_platform_item_id: int = 0

    def __repr__(self):
        return (
            "PlatformItem("
            f"{self._base_repr()}, "
            f"station={self.station}, "
            f"flags={self.flags}, "
            f"min_waiting_time={self.min_waiting_time}, "
            f"num_passengers_waiting={self.num_passengers_waiting}, "
            f"linked_platform_item_id={self.linked_platform_item_id})"
        )

@dataclass
class HazzardItem(TrItem):

    def __repr__(self):
        return f"HazzardItem({self._base_repr()})"

@dataclass
class PickupItem(TrItem):

    def __repr__(self):
        return f"PickupItem({self._base_repr()})"

@dataclass
class CarSpawnerItem(TrItem):

    def __repr__(self):
        return f"CarSpawnerItem({self._base_repr()})"

@dataclass
class TrPin:
    link: int = 0
    direction: int = 0

    def __repr__(self):
        return (
            f"TrPin(link={self.link}, "
            f"direction={self.direction}))"
        )

@dataclass
class TrVectorSection:
    flags1: int = 0
    flags2: int = 0
    section_index: int = 0
    shape_index: int = 0
    tile_x: int = 0
    tile_z: int = 0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    az: float = 0.0
    wf_uid: int = 0
    wf_name_x: int = 0
    wf_name_z: int = 0

    def __repr__(self):
        return (
            f"TrVectorSection(flags1={self.flags1}, "
            f"flags2={self.flags2}), "
            f"section_index={self.section_index}), "
            f"shape_index={self.shape_index}), "
            f"tile_x={self.tile_x}), "
            f"tile_z={self.tile_z}), "
            f"x={self.x}), "
            f"y={self.y}), "
            f"z={self.z}), "
            f"ax={self.ax}), "
            f"ay={self.ay}), "
            f"az={self.az}), "
            f"wf_uid={self.wf_uid}), "
            f"wf_name_x={self.wf_name_x}), "
            f"wf_name_z={self.wf_name_z}))"
        )

@dataclass
class TrVectorNode:
    tr_vector_sections: List[TrVectorSection] = field(default_factory=list)
    tr_item_refs: List[int] = field(default_factory=list)

    def __repr__(self):
        return (
            "TrVectorNode("
            f"tr_vector_sections (len={len(self.tr_vector_sections)}), "
            f"tr_item_refs (len={len(self.tr_item_refs)}))"
        )

@dataclass
class TrJunctionNode:
    shape_index: int = 0

    def __repr__(self):
        return (
            "TrJunctionNode("
            f"shape_index={self.shape_index}))"
        )

@dataclass
class UiD:
    tile_x: int = 0
    tile_z: int = 0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    az: float = 0.0
    world_tile_x: int = 0
    world_tile_z: int = 0
    world_id: int = 0

    def __repr__(self):
        return (
            f"UiD(tile_x={self.tile_x}, "
            f"tile_z={self.tile_z}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"z={self.z}, "
            f"ax={self.ax}, "
            f"ay={self.ay}, "
            f"az={self.az}, "
            f"world_tile_x={self.world_tile_x}, "
            f"world_tile_z={self.world_tile_z}, "
            f"world_id={self.world_id})"
        )

@dataclass
class TrackNode:
    index: int
    uid: Optional[UiD] = None
    tr_junction_node: Optional[TrJunctionNode] = None
    tr_vector_node: Optional[TrVectorNode] = None
    tr_end_node: bool = False
    tr_pins: List[TrPin] = field(default_factory=list)
    inpins: int = 0
    outpins: int = 0

    def __repr__(self):
        return (
            f"TrackNode(index={self.index}, "
            f"uid={self.uid}, "
            f"tr_junction_node={self.tr_junction_node}, "
            f"tr_vector_node={self.tr_vector_node}, "
            f"tr_end_node={self.tr_end_node}, "
            f"tr_pins (len={len(self.tr_pins)}), "
            f"inpins={self.inpins}, "
            f"outpins={self.outpins})"
        )

@dataclass
class TrackDB:
    serial: int = 0
    track_nodes: List[TrackNode] = field(default_factory=list)
    tr_item_table: List[TrItem] = field(default_factory=list)

    def __repr__(self):
        return (
            f"TrackDB(serial={self.serial}, "
            f"track_nodes (len={len(self.track_nodes)}), "
            f"tr_item_table (len={len(self.tr_item_table)}))"
        )
