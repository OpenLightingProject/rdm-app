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
# manufacturer_test.py
# Copyright (C) 2015 Simon Newton

import unittest

class TestManufacturerData(unittest.TestCase):
  """ Test the manufacturer data file is valid."""
  def setUp(self):
    globals = {}
    locals = {}
    execfile("data/manufacturer_data.py", globals, locals)
    self.data = locals['MANUFACTURER_DATA']

  def test_Data(self):
    seen_ids = set()

    for manufacturer_data in self.data:
      self.assertEqual(tuple, type(manufacturer_data))
      self.assertEqual(2, len(manufacturer_data))
      esta_id, name = manufacturer_data
      self.assertEqual(int, type(esta_id))
      self.assertEqual(str, type(name))

      self.assertNotIn(esta_id, seen_ids)
      seen_ids.add(esta_id)

    # check that PLASA exists
    self.assertIn(0, seen_ids)


if __name__ == '__main__':
  unittest.main()
