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


class TestManufacturers(unittest.TestCase):
  """ Test the manufacturer data files are valid."""
  def setUp(self):
    globals = {}
    locals = {}
    execfile("data/manufacturer_data.py", globals, locals)
    self.data = locals['MANUFACTURER_DATA']
    globals = {}
    locals = {}
    execfile("data/manufacturer_links.py", globals, locals)
    self.links = locals['MANUFACTURER_LINKS']

  def test_ManufacturerData(self):
    seen_ids = set()

    for manufacturer_data in self.data:
      self.assertEqual(tuple, type(manufacturer_data))
      self.assertEqual(2, len(manufacturer_data))
      esta_id, name = manufacturer_data
      self.assertEqual(int, type(esta_id))
      self.assertEqual(str, type(name))

      self.assertNotIn(esta_id, seen_ids,
                       "ESTA ID 0x%04x is present twice" % esta_id)
      seen_ids.add(esta_id)

    # check that ESTA exists
    self.assertIn(0, seen_ids)

  def test_ManufacturerLinks(self):
    esta_ids = set()
    seen_ids = set()
    for manufacturer_data in self.data:
      esta_id, name = manufacturer_data
      esta_ids.add(esta_id)

    for manufacturer_link in self.links:
      self.assertEqual(tuple, type(manufacturer_link))
      self.assertEqual(2, len(manufacturer_link))
      esta_id, link = manufacturer_link
      self.assertEqual(int, type(esta_id))
      self.assertEqual(str, type(link))

      # Check we have a corresponding entry in the manufacturer data
      self.assertIn(esta_id, esta_ids,
                    ("ESTA ID 0x%04x is not present in the manufacturer data" %
                     esta_id))

      # Check we've not seen this URL before
      self.assertNotIn(esta_id, seen_ids,
                       "ESTA ID 0x%04x is present twice" % esta_id)
      seen_ids.add(esta_id)

    # optional, check that ESTA exists
    self.assertIn(0, seen_ids)


if __name__ == '__main__':
  unittest.main()
