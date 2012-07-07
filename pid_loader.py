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

  """
  def AddItem(self, item):
    item_data = MessageItem(name = item['name'], type = item['type'])
    if item.get('min_size'):
      item_data.min_size = item['min_size']
    if item.get('max_size'):
      item_data.max_size = item['max_size']

    if item['type'] == 'group':
      items = item.get('items')
      if item.get('range') or item.get('enums'):
        raise InvalidDataException(
            '%s: groups cannot have enum or range properties' % item['name'])
      if item.get('multiplier'):
        raise InvalidDataException(
            '%s: groups cannot have multiplier properties' % item['name'])

      if not items:
        raise MissingItemsException(item['name'])

      child_items = []
      for child_item_data in items:
        child_item = self.AddItem(child_item_data)
        child_items.append(child_item.key())
      item_data.items = child_items


    valid_ranges = []
    if item.get('range'):
      ranges = []
      for min, max in item.get('range'):
        valid_ranges.append((min, max))
        range = AllowedRange(min = min, max = max)
        range.put()
        ranges.append(range.key())
      item_data.allowed_values = ranges

    if item.get('enums'):
      enums = []
      for value, label in item.get('enums'):
        if valid_ranges:
          found = False
          for min, max in valid_ranges:
            if value >= min and value <= max:
              break
          else:
            raise OutOfRangeException('%d: %s' % (value, label))

        enum = EnumValue(value = value, label = label)
        enum.put()
        enums.append(enum.key())
      item_data.enums = enums

    if item.get('multiplier'):
      item_data.multiplier = item['multiplier']

    item_data.put()
    return item_data

  def AddMessage(self, message):
    items = []
    for item in message['items']:
      items.append(self.AddItem(item).key())

    message_data = Message(items = items)
    message_data.put()
    return message_data
  """

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
