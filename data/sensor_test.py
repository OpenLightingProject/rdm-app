#!/usr/bin/python
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# sensor_test.py
# Copyright (C) 2017 Peter Newman

import unittest


class TestSensorTypes(unittest.TestCase):
  """ Test the sensor types data file is valid."""
  def setUp(self):
    globals = {}
    locals = {}
    execfile("data/sensor_types.py", globals, locals)
    self.data = locals['SENSOR_TYPES']

  def test_SensorTypeData(self):
    seen_names = set()

    for sensor_type_id in self.data:
      name = self.data[sensor_type_id]
      self.assertEqual(int, type(sensor_type_id))
      self.assertEqual(str, type(name))

      self.assertNotIn(name, seen_names,
                       "Sensor Name %s is present twice" % name)
      seen_names.add(name)

    # check that some sensors exist
    self.assertGreater(len(seen_names), 30)


if __name__ == '__main__':
  unittest.main()
