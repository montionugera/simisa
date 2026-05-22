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
from enum import IntEnum
from typing import Optional, List


@dataclass
class WorldSoundFile:
    world_sound: Optional["TrWorldSoundFile"]

@dataclass
class TrWorldSoundFile:
    sound_sources: List["WorldSoundSource"]
    sound_regions: List["WorldSoundRegion"]

@dataclass
class SoundEntity(ABC):
    pass

@dataclass
class WorldSoundSource(SoundEntity):
    x: float
    y: float
    z: float
    sound_source_filename: Optional[str]

@dataclass
class WorldSoundRegion(SoundEntity):
    sound_region_track_type: int
    rot_y: float
    track_nodes: List[int]

@dataclass
class Position3D:
    x: float
    y: float
    z: float

@dataclass
class TrackNodeReference:
    tr_item_id: int