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
# pid_index_builder.py
# Copyright (C) 2012 Simon Newton
# Build the index of PIDs to responders.

import logging
import common
from model import *


class PidIndexBuilder():
  def __init__(self):
    self._manufacturer_cache = {}
    self._pid_cache = {}
    self._esta = common.GetManufacturer(0)

  def LookupPid(self, manufacturer, pid_id):
    key = (manufacturer.esta_id, pid_id)
    if key not in self._pid_cache:
      query = Pid.all()
      if pid_id < 0x8000:
        query.filter('manufacturer = ', self._esta.key())
      else:
        query.filter('manufacturer = ', manufacturer.key())
      query.filter('pid_id = ', pid_id)
      pids = query.fetch(1)
      pid = None
      if pids:
        pid = pids[0]
      self._manufacturer_cache[key] = pid
    return self._manufacturer_cache[key]

  def BuildIndex(self):
    for item in PIDResponderRelationship.all():
      item.delete()

    for responder in Responder.all():
      params = []
      version = common.GetLatestSoftware(responder)
      if not version:
        continue
      for param in version.supported_parameters:
        pid = self.LookupPid(responder.manufacturer, param)
        if pid:
          mapping = PIDResponderRelationship(
            pid = pid,
            responder = responder)
          mapping.put()
    return 'ok'
