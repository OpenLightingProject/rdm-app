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
from model import Pid, Responder


class PidIndexBuilder():
  """We need to be smart about this, my first attempt blew through my write
     budget when I built the index.
  """
  def __init__(self):
    self._pid_cache = {}
    self._esta = common.GetManufacturer(0)

  def LoadCurrentIndex(self):
    """Load the current PID to responder map. Also populates the pid_cache.

    Returns:
      A dict in the form {
        (manufacturer_id, pid_id) : set(responder_keys),
      }
    """
    index = {}
    for pid in Pid.all():
      key = (pid.manufacturer.esta_id, pid.pid_id)
      responders = set()
      for responder in pid.responders:
        responders.add(responder)
      index[key] = responders
      self._pid_cache[key] = pid
    return index

  def KeyFromPID(self, manufacturer, pid_id):
    """Determine the key from a manufacturer and pid_id."""
    if pid_id < 0x8000:
      manufacturer = self._esta
    return (manufacturer.esta_id, pid_id)

  def BuildIndex(self):
    current_index = self.LoadCurrentIndex()
    new_index = {}

    for responder in Responder.all():
      version = common.GetLatestSoftware(responder)
      if not version:
        continue
      for param in version.supported_parameters:
        key = self.KeyFromPID(responder.manufacturer, param)
        pid = self._pid_cache.get(key, None)
        if not pid:
          continue

        new_index.setdefault(key, set()).add(responder.key())

    # now diff the old and new
    for key, responders in new_index.iteritems():
      if key in current_index:
        if current_index[key] != responders:
          logging.info('Responder set changed for %s' % str(key))
          pid = self._pid_cache[key]
          pid.responders = list(responders)
          pid.put()
        del current_index[key]
      else:
        # this should never happen
        logging.warn('Missing key for %s' % str(key))

    for key, responders in current_index.iteritems():
      if responders:
        logging.info('Removed %s' % responders)
        pid = self._pid_cache[key]
        pid.responders = []
        pid.put()
