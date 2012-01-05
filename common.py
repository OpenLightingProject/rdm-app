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
# common.py
# Copyright (C) 2011 Simon Newton
# Common functions

from model import *
import logging
import memcache_keys
import time
import datetime
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


def GetManufacturer(manufacturer_id):
  """Lookup a manufacturer entity by manufacturer id.

  Returns:
    The entity object, or None if not found.
  """
  try:
    id = int(manufacturer_id)
  except ValueError:
    return None

  query = Manufacturer.all()
  query.filter('esta_id = ', id)
  for manufacturer in query.fetch(1):
    return manufacturer
  return None

def ConvertToInt(value):
  """Convert a value to an int."""
  if value:
    try:
      int_value = int(value)
    except ValueError:
      return None
    return int_value
  return None


class BasePageHandler(webapp.RequestHandler):
  """The base class for all page requests.

  This adds the index info snippit to the bottom of the page.
  """
  ESTA_ID = 0

  def GetTemplateData(self):
    """Subclasses override this."""
    return {}

  def get(self):
    output = self.IndexInfo()
    output.update(self.GetTemplateData())

    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(self.TEMPLATE, output))

  def ManufacturerPidCount(self):
    """Return the number of manufacturer PIDs."""
    manufacturer_pids = memcache.get(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
    if manufacturer_pids is None:
      manufacturer_pids = 0

      for pid in Pid.all():
        if pid.manufacturer.esta_id != self.ESTA_ID:
          manufacturer_pids += 1
      if not memcache.add(memcache_keys.MANUFACTURER_PID_COUNT_KEY,
                          manufacturer_pids):
        logging.error("Memcache set failed.")
    return manufacturer_pids

  def DeviceModelCount(self):
    """Return the number of models."""
    model_count = memcache.get(memcache_keys.MODEL_COUNT_KEY)
    if model_count is None:
      model_count = Responder.all().count()
      if not memcache.add(memcache_keys.MODEL_COUNT_KEY,
                          model_count):
        logging.error("Memcache set failed.")
    return model_count

  def IndexInfo(self):
    """Get the information about the index.

    Returns a dict in the form:
      {'last_updated':  ,
       'manufacturer_pid_count': ,
       'model_count': ,
      }
    """
    output = memcache.get(memcache_keys.INDEX_INFO)
    if not output:
      output = {'last_updated': None}
      results = Pid.all()
      results.order('-update_time')

      pids = results.fetch(1)
      if pids:
        stamp = datetime.datetime(*pids[0].update_time.timetuple()[0:6])
        output['last_updated'] = stamp
      output['manufacturer_pid_count'] = self.ManufacturerPidCount()
      output['model_count'] = self.DeviceModelCount()
      memcache.set(memcache_keys.INDEX_INFO, output)
    return output
