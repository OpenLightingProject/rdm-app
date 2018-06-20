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
# missing_manufacturer_links.py
# Copyright (C) 2018 Peter Newman

# Tidy with:
# sed -i '/^##/d' manufacturer_links.py

import pprint
import textwrap

def Header():
  print textwrap.dedent("""\
  # -*- coding: utf-8 -*-
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
  # manufacturer_links.py
  # Copyright (C) 2017 Peter Newman
  # The links for Manufacturers
  
  MANUFACTURER_LINKS = [""")

def Footer():
  print textwrap.dedent("""\
  ]""")

if __name__ == '__main__':
  globals = {}
  locals = {}
  execfile("data/manufacturer_data.py", globals, locals)
  raw_manufacturers = locals['MANUFACTURER_DATA']
  globals = {}
  locals = {}
  execfile("data/manufacturer_links.py", globals, locals)
  raw_links = locals['MANUFACTURER_LINKS']

  manufacturers = {}
  for id, name in raw_manufacturers:
    manufacturers[id] = name

  links = {}
  for id, link in raw_links:
    links[id] = link

  Header()

  for id in sorted(manufacturers):
    if id not in links:
      print "## Missing link for %s (0x%04X)" % (manufacturers[id], id)
      print "## (0x%04X, \"\")," % (id)
    else:
      print "(0x%04X, \"%s\")," % (id, links[id])

  Footer()
