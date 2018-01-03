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
# utils.py
# Copyright (C) 2011 Simon Newton
# Various functions to make things easier.

import time


def StringToInt(value, allow_hex=True):
  """Convert a string value to an int

    Args:
      allow_hex: Enable support for hex values that start with 0x

    Returns:
      The value, or None if the value wasn't valid.
  """
  if value is None:
    return None

  if type(value) == int:
    return value

  if type(value) not in [str, unicode]:
    return None

  int_value = None
  value = value.strip()
  if value.startswith('0x') and allow_hex:
    try:
      int_value = int(value, 16)
    except ValueError:
      pass
  else:
    try:
      int_value = int(value)
    except ValueError:
      pass
  return int_value


def TimestampToInt(timestamp):
  """Convert a DateTimeProperty to an int."""
  return int(time.mktime(timestamp.timetuple()))
