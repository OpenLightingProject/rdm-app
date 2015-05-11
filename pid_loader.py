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

import common
import logging
from model import *


class UnknownManufacturerException(Exception):
  """Raised when the manufacturer ID doesn't exist."""


class PidLoader():
  """Load pids."""

  def LookupPid(self, pid_id, manufacturer_id):
    """
    Lookup a PID

    Returns:
      A tuple of (manufacturer, pid) data objects.
    """
    manufacturer = common.GetManufacturer(manufacturer_id)
    if manufacturer is None:
      raise UnknownManufacturerException(manufacturer_id)

    pid_query = Pid.all()
    pid_query.filter('pid_id = ', pid_id)
    pid_query.filter('manufacturer = ', manufacturer.key())

    result_set = pid_query.fetch(1)
    if result_set:
      return manufacturer, result_set[0]
    else:
      return manufacturer, None

  def UpdateCommand(self, pid, new_pid_data, command_type):
    """Update a command if required.

    Returns:
     True if the command was updated, False otherwise.
    """
    command_attr = '%s_command' % command_type
    request_attr = '%s_request' % command_type
    response_attr = '%s_response' % command_type
    sub_device_attr = '%s_sub_device_range' % command_type

    # We assume the pull request validator has run and checked the consistency
    # of the PID data.
    has_command = (request_attr in new_pid_data and
                   response_attr in new_pid_data and
                   sub_device_attr in new_pid_data)

    existing_command = getattr(pid, command_attr)
    if existing_command and has_command:
      save = False

      if existing_command.sub_device_range != new_pid_data[sub_device_attr]:
        existing_command.sub_device_range = new_pid_data[sub_device_attr]
        save = True

      request = new_pid_data.get(request_attr)
      if eval(existing_command.request) != request:
        existing_command.request = str(request)
        save = True

      response = new_pid_data.get(response_attr)
      if eval(existing_command.response) != response:
        existing_command.response = str(response)
        save = True

      if save:
        existing_command.put()
        logging.info('Updated existing %s:%s' %
                     (new_pid_data['name'], command_type))
      return save

    elif existing_command and not has_command:
      # remove the existing command
      existing_command.delete()
      setattr(pid, command_attr, None)
      logging.info('Removed existing %s:%s' %
                   (command_type, new_pid_data['name']))
      return True

    elif has_command:
      command = Command(sub_device_range = new_pid_data[sub_device_attr],
                        request = str(new_pid_data.get(request_attr)),
                        response = str(new_pid_data.get(response_attr)))
      command.put()
      setattr(pid, command_attr, command)
      logging.info('Set %s:%s' % 
                   (command_type, new_pid_data['name']))
      return True
    else:
      return False


  def UpdateIfRequired(self, new_pid_data, manufacturer_id = 0):
    """
    Check if we need to update the data for this PID.

    Args:
      pid: The PID data
      manufacturer_id: The manufacturer_id for the PID data.

    Returns:
      True if the PID was updated, false otherwise.
    """
    manufacturer, pid = self.LookupPid(new_pid_data['value'], manufacturer_id)
    save = False

    if not pid:
      pid = Pid(manufacturer = manufacturer,
                pid_id = new_pid_data['value'],
                name = new_pid_data['name'])

    if pid.link != new_pid_data.get('link'):
      pid.link = new_pid_data.get('link')
      save = True

    if pid.notes != new_pid_data.get('notes'):
      pid.notes = new_pid_data.get('notes')
      save = True

    if pid.draft != new_pid_data.get('draft', False):
      pid.draft = new_pid_data.get('draft', False)
      save = True

    save |= self.UpdateCommand(pid, new_pid_data, 'discovery')
    save |= self.UpdateCommand(pid, new_pid_data, 'get')
    save |= self.UpdateCommand(pid, new_pid_data, 'set')

    if save:
      logging.info('Updated %s' % new_pid_data['name'])
      pid.put()
    return save
