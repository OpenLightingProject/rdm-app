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
# product_categories.py
# Copyright (C) 2011 Simon Newton

"""Constants defined in E1.20 (RDM)."""

__author__ = 'nomis52@gmail.com (Simon Newton)'


PRODUCT_CATEGORIES = [
  ('Not Declared', 0x0000),
  ('Fixture', 0x0100),
  ('Fixture Fixed', 0x0101),
  ('Fixture Moving Yoke', 0x0102),
  ('Fixture Moving Mirror', 0x0103),
  ('Fixture Other', 0x01FF),
  ('Fixture Accessory', 0x0200),
  ('Fixture Accessory Color', 0x0201),
  ('Fixture Accessory Yoke', 0x0202),
  ('Fixture Accessory Mirror', 0x0203),
  ('Fixture Accessory Effect', 0x0204),
  ('Fixture Accessory Beam', 0x0205),
  ('Fixture Accessory Other', 0x02FF),
  ('Projector', 0x0300),
  ('Projector Fixed', 0x0301),
  ('Projector Moving Yoke', 0x0302),
  ('Projector Moving Mirror', 0x0303),
  ('Projector Other', 0x03FF),
  ('Atmospheric', 0x0400),
  ('Atmospheric Effect', 0x0401),
  ('Atmospheric Pyro', 0x0402),
  ('Atmospheric Other', 0x04FF),
  ('Dimmer', 0x0500),
  ('Dimmer AC Incandescent', 0x0501),
  ('Dimmer AC Fluorescent', 0x0502),
  ('Dimmer AC Cold Cathode', 0x0503),
  ('Dimmer AC non-dim', 0x0504),
  ('Dimmer AC ELV', 0x0505),
  ('Dimmer AC Other', 0x0506),
  ('Dimmer DC Level', 0x0507),
  ('Dimmer DC PWM', 0x0508),
  ('Dimmer CS LED', 0x0509),
  ('Dimmer Other', 0x05FF),
  ('Power', 0x0600),
  ('Power Control', 0x0601),
  ('Power Source', 0x0602),
  ('Power Other', 0x06FF),
  ('Scenic', 0x0700),
  ('Scenic Drive', 0x0701),
  ('Scenic Other', 0x07FF),
  ('Data', 0x0800),
  ('Data Distribution', 0x0801),
  ('Data Conversion', 0x0802),
  ('Data Other', 0x08FF),
  ('AV', 0x0900),
  ('AV Audio', 0x0901),
  ('AV Video', 0x0902),
  ('AV Other', 0x09FF),
  ('Monitor', 0x0A00),
  ('Monitor AC Line Power', 0x0A01),
  ('Monitor DC Power', 0x0A02),
  ('Monitor Environmental', 0x0A03),
  ('Monitor Other', 0x0AFF),
  ('Control', 0x7000),
  ('Control Controller', 0x7001),
  ('Control Backup Device', 0x7002),
  ('Control Other', 0x70FF),
  ('Test', 0x7100),
  ('Test Equipment', 0x7101),
  ('Test Equipment Other', 0x71FF),
  ('Other', 0x7FFF),
]
