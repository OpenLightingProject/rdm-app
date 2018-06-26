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

SENSOR_TYPES = {
    0x00: "Temperature",
    0x01: "Voltage",
    0x02: "Current",
    0x03: "Frequency",
    0x04: "Resistance",
    0x05: "Power",
    0x06: "Mass",
    0x07: "Length",
    0x08: "Area",
    0x09: "Volume",
    0x0a: "Density",
    0x0b: "Velocity",
    0x0c: "Acceleration",
    0x0d: "Force",
    0x0e: "Energy",
    0x0f: "Pressure",
    0x10: "Time",
    0x11: "Angle",
    0x12: "Position X",
    0x13: "Position Y",
    0x14: "Position Z",
    0x15: "Angular velocity",
    0x16: "Luminous intensity",
    0x17: "Luminous flux",
    0x18: "Illuminance",
    0x19: "Chrominance red",
    0x1a: "Chrominance green",
    0x1b: "Chrominance blue",
    0x1c: "Contacts",
    0x1d: "Memory",
    0x1e: "Items",
    0x1f: "Humidity",
    0x20: "16 bit counter",
    0x7f: "Other",
}
