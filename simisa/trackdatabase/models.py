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
from enum import IntEnum
from typing import Optional, List


@dataclass
class TrItem(ABC):
    item_name: Optional[str] = None
    tr_item_id: int = 0
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

@dataclass
class CrossoverItem(TrItem):
    track_node: int = 0
    shape_index: int = 0

@dataclass
class SignalDirection:
    track_node: int = 0
    sd1: int = 0
    link_lr_path: int = 0
    sd3: int = 0

@dataclass
class SignalItem(TrItem):
    flags1: Optional[int] = None
    direction: int = 0
    sig_obj: int = -1
    sig_data1: float = 0.0
    signal_type: Optional[str] = None
    no_sig_dirs: int = 0
    tr_signal_dirs: List[SignalDirection] = field(default_factory=list)

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
    sig_obj: int = -1
    angle: float = 0.0
    direction: int = 0
    display_number: int = 0

@dataclass
class TempSpeedPostItem(SpeedPostItem):
    pass # TODO world position?

@dataclass
class SoundRegionItem(TrItem):
    sr_data1: int = 0
    sr_data2: int = 0
    sr_data3: float = 0.0

@dataclass
class EmptyItem(TrItem):
    pass

@dataclass
class LevelCrItem(TrItem):
    pass

@dataclass
class SidingItem(TrItem):
    flags1: Optional[str] = None
    linked_siding_id: int = 0

@dataclass
class PlatformItem(TrItem):
    station: Optional[str] = None
    flags1: Optional[str] = None
    platform_min_waiting_time: int = 0
    platform_num_passengers_waiting: int = 0
    linked_platform_item_id: int = 0

@dataclass
class HazzardItem(TrItem):
    pass

@dataclass
class PickupItem(TrItem):
    pass

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
    world_file_uid: int = 0
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
            f"world_file_uid={self.world_file_uid}), "
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
            f"tile_z={self.tile_z}), "
            f"x={self.x}), "
            f"y={self.y}), "
            f"z={self.z}), "
            f"ax={self.ax}), "
            f"ay={self.ay}), "
            f"az={self.az}), "
            f"world_tile_x={self.world_tile_x}), "
            f"world_tile_z={self.world_tile_z}), "
            f"world_id={self.world_id}))"
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
