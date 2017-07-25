#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# sensor_types.py
# Copyright (C) 2011 Simon Newton
# The sensor type enums. These aren't stored in the datastore because I'm lazy
# and for now we don't have to search on them

SENSOR_UNITS = {
    0x00 : "None",
    0x01 : "Centigrade",
    0x02 : "Volts_dc",
    0x03 : "Volts_ac_peak",
    0x04 : "Volts_ac_rms",
    0x05 : "Ampere_dc",
    0x06 : "Ampere_ac_peak",
    0x07 : "Ampere_ac_rms",
    0x08 : "Hertz",
    0x09 : "Ohm",
    0x0a : "Watt",
    0x0b : "Kilogram",
    0x0c : "Meters",
    0x0d : "Meters_squared",
    0x0e : "Meters_cubed",
    0x0f : "Kilogrammes_per_meter_cubed",
    0x10 : "Meters_per_second",
    0x11 : "Meters_per_second_squared",
    0x12 : "Newton",
    0x13 : "Joule",
    0x14 : "Pascal",
    0x15 : "Second",
    0x16 : "Degree",
    0x17 : "Steradian",
    0x18 : "Candela",
    0x19 : "Lumen",
    0x1a : "Lux",
    0x1b : "Ire",
    0x1c : "Byte",
}
