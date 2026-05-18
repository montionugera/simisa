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
from datetime import datetime
from enum import Enum
from typing import Optional


class Interpolator:
    pass


class WorldPosition:
    pass


class Position:
    pass


class TrackSectionsFile:
    pass


class TrackShape:
    pass


class TrackSection:
    pass


class SectionIdx:
    pass


class InfoApiMap:
    pass


class LatLon:
    pass


class TrRouteFile:
    pass


@dataclass
class TrackDatabaseFile:
    track_db: Optional["TrackDB"] = None
    last_write_time: Optional[datetime] = None


@dataclass
class TrackDB:
    track_nodes: list["TrackNode"] = field(default_factory=list)
    tr_item_table: list["TrItem"] = field(default_factory=list)


@dataclass
class TrPin:
    link: int = 0
    direction: int = 0


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


@dataclass
class TrJunctionNode:
    selected_route: int = 0
    tn: Optional["TrackNode"] = None
    idx: int = 0
    shape_index: int = 0
    angle: float = float("inf")
    angle_computed: bool = False


@dataclass
class TrVectorSection:
    flag1: int = 0
    flag2: int = 0
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
    phys_elev_table: Interpolator = field(default_factory=Interpolator)
    vis_elev_table: Interpolator = field(default_factory=Interpolator)
    nom_elev_m: float = -1.0
    elev_offset_m: float = 0.0
    freight_speed_mps: float = float("-inf")
    pass_speed_mps: float = float("-inf")
    reduced: bool = False


@dataclass
class TrVectorNode:
    tr_vector_sections: list[TrVectorSection] = field(default_factory=list)
    tr_item_refs: list[int] = field(default_factory=list)
    no_item_refs: int = 0


@dataclass
class TrackNode:
    tr_junction_node: Optional[TrJunctionNode] = None
    tr_vector_node: Optional[TrVectorNode] = None
    tr_end_node: bool = False
    uid: Optional[UiD] = None
    tr_pins: list[TrPin] = field(default_factory=list)
    inpins: int = 0
    outpins: int = 0
    index: int = 0
    reduced: bool = False
    tc_cross_reference: Optional["TrackCircuitXRefList"] = None


class TrItemType(Enum):
    EMPTY = 0
    CROSSOVER = 1
    SIGNAL = 2
    SPEEDPOST = 3
    PLATFORM = 4
    SOUNDREGION = 5
    XING = 6
    SIDING = 7
    HAZARD = 8
    PICKUP = 9
    CARSPAWNER = 10


@dataclass
class TrItem(ABC):
    item_name: Optional[str] = None
    item_type: TrItemType = TrItemType.EMPTY
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
    sdata2: Optional[str] = None


@dataclass
class CrossoverItem(TrItem):
    track_node: int = 0
    shape_id: int = 0


@dataclass
class SignalDirection:
    track_node: int = 0
    sd1: int = 0
    link_lr_path: int = 0
    sd3: int = 0


@dataclass
class SignalItem(TrItem):
    flags1: Optional[str] = None
    direction: int = 0
    sig_obj: int = -1
    sig_data1: float = 0.0
    signal_type: Optional[str] = None
    no_sig_dirs: int = 0
    tr_signal_dirs: list[SignalDirection] = field(default_factory=list)


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
    world_position: Optional[WorldPosition] = None


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
class TrackCircuitSectionXref:
    length: float = 0.0
    offset_length: list[float] = field(default_factory=lambda: [0.0, 0.0])
    index: int = 0


class TrackCircuitXRefList(list[TrackCircuitSectionXref]):
    pass