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
from utils import StringToInt
import logging
import memcache_keys
import datetime
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


def GetManufacturer(manufacturer_id):
  """Lookup a manufacturer entity by manufacturer id. The manufacturer id can
     be a string in decimal or hex (prepend with 0x), or an int

  Returns:
    The Manufacturer entity object, or None if not found.
  """
  if type(manufacturer_id) != int:
    manufacturer_id = StringToInt(manufacturer_id)
  query = Manufacturer.all()
  query.filter('esta_id = ', manufacturer_id)
  for manufacturer in query.fetch(1):
    return manufacturer
  return None

def LookupModelFromRequest(request):
  return LookupModel(request.get('manufacturer'),
                     request.get('model'))

def LookupModel(manufacturer, model_id):
  """Lookup a model based on the URL params."""
  if type(model_id) != int:
    model_id = StringToInt(model_id)
  manufacturer = GetManufacturer(manufacturer)
  if manufacturer is None or model_id is None:
    return None

  results = {}
  models = Responder.all()
  models.filter('device_model_id = ', model_id)
  models.filter('manufacturer = ', manufacturer.key())

  model_data = models.fetch(1)
  if not model_data:
    return None
  return model_data[0]


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
    page_data = self.GetTemplateData()
    if page_data is not None:
      output.update(page_data)
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
      results = LastUpdateTime.all()
      results.order('-update_time')
      update_timestamp = results.fetch(1)
      if update_timestamp:
        output['last_updated'] = datetime.datetime(
            *update_timestamp[0].update_time.timetuple()[0:6])
      output['manufacturer_pid_count'] = self.ManufacturerPidCount()
      output['model_count'] = self.DeviceModelCount()
      memcache.set(memcache_keys.INDEX_INFO, output)
    return output
