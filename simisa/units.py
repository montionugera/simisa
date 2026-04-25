"""
This file is part of Simisa.

This code was ported from C# to Python. The original code is from
the `Orts.Parsers.Msts` namespace within the Open Rails codebase.

Copyright (C) 2013, 2014, 2015 by the Open Rails project
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

from enum import IntFlag

class Units(IntFlag):
    Compulsory = 1 << 0

    # kg, t, lb
    Mass = 1 << 1

    # m, cm, mm, km, ft, ', in, "
    Distance = 1 << 2

    # *(ft^2)
    AreaDefaultFT2 = 1 << 3

    # gal, l
    Volume = 1 << 4

    # *(ft^3)
    VolumeDefaultFT3 = 1 << 5
    
    # s, m, h
    Time = 1 << 6
    TimeDefaultM = 1 << 7
    TimeDefaultH = 1 << 8

    # a, amps
    Current = 1 << 9

    # v, kv
    Voltage = 1 << 10
    
    # lb/h
    MassRateDefaultLBpH = 1 << 11

    # m/s, mph, kph, kmh, km/h
    Speed = 1 << 12
    SpeedDefaultMPH = 1 << 13

    # Hz, rps, rpm
    Frequency = 1 << 14

    # n, kn, lbf
    Force = 1 << 15

    # w, kw, hp
    Power = 1 << 16

    # n/m
    Stiffness = 1 << 17

    # n/m/s (+ '/m/s' in case the newtons is missed), lbf/mph
    Resistance = 1 << 18

    # psi, bar, inhg, kpa
    PressureDefaultPSI = 1 << 19
    PressureDefaultInHg = 1 << 20

    # psi/s, psi/min, bar/s, bar/min, inhg/s, kpa/s
    PressureRateDefaultPSIpS = 1 << 21
    PressureRateDefaultInHgpS = 1 << 22

    # kj/kg, j/g, btu/lb
    EnergyDensity = 1 << 23

    # degc, degf
    TemperatureDifference = 1 << 24

    # kgm^2
    RotationalInertia = 1 << 25

    # Nm/s^2, lbf/mph^2
    ResistanceDavisC = 1 << 26

    # "Any" is all bits set except the Compulsory bit
    Any = ~Compulsory

# Patch the "None" enum value into Units since None is a reserved keyword in Python.
# We can't define None directly in the Units enum structure.
# When using this value access it with 'Units["None"]'. Using 'Units.None' will also result in an error.
Units = IntFlag("Units", {**{m.name: m.value for m in Units}, "None": 0})