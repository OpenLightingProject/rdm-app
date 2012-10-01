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
# pid_loader.py
# Copyright (C) 2011 Simon Newton
# Load PID data.

import logging
from model import *


class OutOfRangeException(Exception):
  """Raised when an enum valid isn't within the allowed ranges."""

class MissingItemsException(Exception):
  """Raised when an item is defined as a group, but no child items exist."""

class InvalidDataException(Exception):
  """Raised when the input data is invalid."""


class PidLoader():
  """Load pids."""
  def AddPid(self, pid, manufacturer_id = 0):
    manufacturer_q = Manufacturer.all()
    manufacturer_q.filter('esta_id =', manufacturer_id)
    manufacturer = manufacturer_q.fetch(1)[0]

    pid_data = Pid(manufacturer = manufacturer,
                   pid_id = pid['value'],
                   name = pid['name'])

    if pid.get('link'):
      pid_data.link = pid['link']
    elif manufacturer_id == 0:
      pid_data.link = 'http://tsp.plasa.org/tsp/documents/published_docs.php'

    if pid.get('notes'):
      pid_data.notes = pid['notes']

    pid_data.draft = pid.get('draft', False)

    logging.info(pid['name'])

    if pid.get('discovery_request'):
      discovery_request = str(pid.get('discovery_request', {}))
      discovery_response = str(pid.get('discovery_response', {}))

      command = Command(sub_device_range = pid['discovery_sub_device_range'],
                        request = discovery_request,
                        response = discovery_response)
      command.put()
      pid_data.discovery_command = command

    if pid.get('get_request'):
      get_request = str(pid.get('get_request', {}))
      get_response = str(pid.get('get_response', {}))

      command = Command(sub_device_range = pid['get_sub_device_range'],
                        request = get_request,
                        response = get_response)
      command.put()
      pid_data.get_command = command


    if pid.get('set_request'):
      set_request = str(pid.get('set_request', {}))
      set_response = str(pid.get('set_response', {}))

      command = Command(sub_device_range = pid['set_sub_device_range'],
                        request = set_request,
                        response = set_response)
      command.put()
      pid_data.set_command = command

    pid_data.put()
