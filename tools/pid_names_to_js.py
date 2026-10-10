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
# pid_names_to_js.py
# Copyright (C) 2025 Peter Newman

'''Convert rdm-app PID data in Python dict format to JS.'''

__author__ = 'nomis52@gmail.com (Simon Newton)'

import sys


def main():
  if len(sys.argv) != 2:
    print('Usage: %s <python_pid_file>' % sys.argv[0])
    sys.exit()

  locals_dict = {}
  # Python 2 and 3 compatible version of execfile
  exec(open(sys.argv[1]).read(), {}, locals_dict)
  raw_esta_pids = locals_dict['ESTA_PIDS']

  esta_pids = {}
  for pid in raw_esta_pids:
    esta_pids[pid['value']] = pid['name']

  print("    'PIDS': {")

  for id in sorted(esta_pids):
    ending_comma = ","
    if id == sorted(esta_pids)[-1]:
      ending_comma = ""
    print("      '%s': 0x%04x%s" % (esta_pids[id], id, ending_comma))

  print("    },")


if __name__ == '__main__':
  main()
