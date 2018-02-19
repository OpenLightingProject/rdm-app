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
# software_test.py
# Copyright (C) 2017 Peter Newman

import unittest

class TestSoftwareData(unittest.TestCase):
  """ Test the software data files are valid."""
  def setUp(self):
    globals = {}
    locals = {}
    execfile("data/software_data.py", globals, locals)
    self.data = locals['SOFTWARE_DATA']

  def test_SoftwareData(self):
    # Check the type
    self.assertEqual(type(self.data), dict)

    for esta_id in self.data:
      self.assertEqual(int, type(esta_id))
      self.assertEqual(list, type(self.data[esta_id]))

      seen_names = set()

      for software in self.data[esta_id]:
        name = software['name']
        self.assertNotIn(name, seen_names,
                         "Name %s for ESTA ID 0x%04x is present twice" % (name, esta_id))
        seen_names.add(name)


if __name__ == '__main__':
  unittest.main()
