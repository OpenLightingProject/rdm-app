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
# product_category_test.py
# Copyright (C) 2015 Simon Newton

import unittest


class TestProductCategoryData(unittest.TestCase):
  """ Test the product category data file is valid."""
  def setUp(self):
    globals = {}
    locals = {}
    execfile("data/product_categories.py", globals, locals)
    self.data = locals['PRODUCT_CATEGORIES']

  def test_ProductCategoryData(self):
    seen_category_ids = set()
    seen_category_names = set()

    for data in self.data:
      self.assertEqual(tuple, type(data))
      self.assertEqual(2, len(data))
      category, category_id = data
      self.assertEqual(str, type(category))
      self.assertEqual(int, type(category_id))

      self.assertNotIn(category_id, seen_category_ids)
      seen_category_ids.add(category_id)

      self.assertNotIn(category, seen_category_names)
      seen_category_names.add(category)


if __name__ == '__main__':
  unittest.main()
