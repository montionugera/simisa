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

from .reader import load, loads
#from .writer import dump, dumps
from .models import *
from ..tracksections.models import (
    SectionCurve,
    SectionSize,
    TrackSection,
    RouteTrackSection,
    TrackSections
)

__all__ = [
    "load",
    "loads",
    #"dump",
    #"dumps",
    "StaticFlag",
    "PlatformDataFlag",
    "Position",
    "QDirection",
    "Matrix3x3",
    "WorldObj",
    "StaticObj",
    "JNodePosition",
    "TrackObj",
    "TrItemId",
    "CarSpawnerObj",
    "SidingObj",
    "PlatformObj",
    "ScaleRange",
    "ForestArea",
    "TreeSize",
    "ForestObj",
    "LevelCrParams",
    "LevelCrData",
    "LevelCrTiming",
    "LevelCrObj",
    "SectionCurve",
    "SectionSize",
    "TrackSection",
    "RouteTrackSection",
    "TrackSections",
    "DynTrackObj",
    "TransferObj",
    "GantryObj",
    "SpeedRange",
    "PickupAnimData",
    "PickupCapacity",
    "StackLocation",
    "PickupObj",
    "HazardObj",
    "SignalUnit",
    "SignalObj",
    "SpeedSignShape",
    "SpeedTextSize",
    "SpeedPostObj",
    "World"
]

