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
# html_differ.py
# Copyright (C) 2012 Simon Newton
# Diff a string and mark up the changes with html span elements

import difflib
import logging


class HTMLDiffer(object):
  def __init__(self, left_class, right_class):
    """

    Args:
      left_class: the css class to use from strings unique to the left side
      right_class: the css class to use from strings unique to the right side
    """
    self._differ = difflib.Differ()
    self._left_class = left_class
    self._right_class = right_class

  def Diff(self, s1, s2):
    """Returns html for the diff of s1 and s2."""
    left = []
    right = []
    left_open = False
    right_open = False
    for atom in self._differ.compare(s1, s2):
      if atom.startswith('  ') or atom.startswith('? '):
        if left_open:
          left.append('</span>')
          left_open = False
        left.append(atom[2])

        if right_open:
          right.append('</span>')
          right_open = False
        right.append(atom[2])
      elif atom.startswith('- '):
        if not left_open:
          left.append('<span class="%s">' % self._left_class)
        left_open = True
        left.append(atom[2])
      elif atom.startswith('+ '):
        if not right_open:
          right.append('<span class="%s">' % self._right_class)
        right_open = True
        right.append(atom[2])
      else:
        logging.error('Unknown diff output: "%s"' % atom)
    return ''.join(left), ''.join(right)
