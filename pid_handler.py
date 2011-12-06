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
# pid_handler.py
# Copyright (C) 2011 Simon Newton
# PID search / display handlers.

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')

import logging
import memcache_keys
import re
import sensor_types
import common
from model import *
from django.utils import simplejson
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class BaseSearchHandler(common.BasePageHandler):
  """The base class for PID searches."""
  def Init(self):
    pass

  def GetSearchData(self):
    return {}

  def GetTemplateData(self):
    self.Init()
    data = self.GetSearchData()
    data['pids'] = self.GetResults()
    return data


class SearchByManufacturer(BaseSearchHandler):
  """Search by Manfacturer."""
  TEMPLATE = 'templates/manufacturer_pid_search.tmpl'

  def Init(self):
    self._manufacturer_id = common.ConvertToInt(
        self.request.get('manufacturer'))

  def GetSearchData(self):
    manufacturer_list = memcache.get(memcache_keys.MANUFACTURER_PID_COUNTS)
    if not manufacturer_list:
      manufacturer_list = []
      query = Manufacturer.all()
      query.order('name')
      for manufacturer in query:
        pids = manufacturer.pid_set.count()
        if pids:
          manufacturer_list.append({
              'id': manufacturer.esta_id,
              'name': manufacturer.name,
              'pid_count': pids,
          })
      memcache.set(memcache_keys.MANUFACTURER_PID_COUNTS, manufacturer_list)

    return {
        'manufacturers': manufacturer_list,
        'current_id': self._manufacturer_id,
    }

  def GetResults(self):
    if self._manufacturer_id is not None:
      query = Manufacturer.all()
      query.filter('esta_id = ', self._manufacturer_id)

      for manufacturer in query.fetch(1):
        query = manufacturer.pid_set
        query.order('pid_id')
        return query
    return []


class SearchByName(BaseSearchHandler):
  """Search by PID name."""
  TEMPLATE = 'templates/name_pid_search.tmpl'

  def GetResults(self):
    name = self.request.get('name')
    if name is not None:
      name = name.strip().replace(' ', '_').upper()
      # do full string matching for now
      results = Pid.all()
      results.filter('name =' , name)

      return results
    return []


class SearchById(BaseSearchHandler):
  """Search PIDs by ID."""
  TEMPLATE = 'templates/id_pid_search.tmpl'

  def GetResults(self):
    pid_id = self.request.get('id')
    if pid_id is not None:
      int_id = None
      pid_id = pid_id.strip()
      if pid_id.startswith('0x'):
        try:
          int_id = int(pid_id, 16)
        except ValueError:
          pass
      else:
        try:
          int_id = int(pid_id)
        except ValueError:
          pass

      results = Pid.all()
      results.filter('pid_id =' , int_id)
      return results

    return []


class DisplayPid(webapp.RequestHandler):
  """Display information about a particular PID."""
  def LookupPIDFromRequest(self):
    pid_id = self.request.get('pid')
    try:
      pid_id = int(pid_id)
    except ValueError:
      return None

    manufacturer = common.GetManufacturer(self.request.get('manufacturer'))
    if manufacturer is None or pid_id is None:
      return None

    results = {}
    models = Pid.all()
    models.filter('pid_id = ', pid_id)
    models.filter('manufacturer = ', manufacturer.key())

    pid_data = models.fetch(1)
    if pid_data:
      return pid_data[0]
    else:
      return None

  def PopulateItem(self, item):
    """Build the data structure for an item."""
    item_output = {
        'name': item.name,
        'type': item.type,
    }
    if item.min_size:
      item_output['min_size'] = item.min_size
    if item.max_size:
      item_output['max_size'] = item.max_size
    if item.multiplier:
      item_output['multiplier'] = item.multiplier

    if item.type == 'group':
      children = []
      for child_key in item.items:
        child_item = MessageItem.get(child_key)
        child_item_output = self.PopulateItem(child_item)
        children.append(child_item_output)
      item_output['items'] = children

    enums = []
    for enum_key in item.enums:
      enum = EnumValue.get(enum_key)
      enum_output = {
        'value': enum.value,
        'label': enum.label,
      }
      enums.append(enum_output)
    if enums:
      item_output['enums'] = enums

    ranges = []
    for range in item.allowed_values:
      range = AllowedRange.get(range)
      range_output = {
        'min': range.min,
        'max': range.max,
      }
      ranges.append(range_output)
    if ranges:
      item_output['ranges'] = ranges
    return item_output

  def PopulateMessage(self, message_output, message):
    items = []
    for item_key in message.items:
      item = MessageItem.get(item_key)
      item_output = self.PopulateItem(item)
      items.append(item_output)

    message_output['items'] = items

  def BuildCommand(self, command):
    request = {}
    self.PopulateMessage(request, command.request)
    response = {}
    self.PopulateMessage(response, command.response)
    command = {
        'request_json': simplejson.dumps(request),
        'response_json': simplejson.dumps(response),
        'subdevice_range': SUBDEVICE_RANGE_DICT.get(
            command.sub_device_range, ''),
    }
    return command

  def get(self):
    pid = self.LookupPIDFromRequest()
    if not pid:
      self.error(404)
      return

    output = {
      'link': pid.link,
      'manufacturer_name': pid.manufacturer.name,
      'notes': pid.notes,
      'pid_id': pid.pid_id,
      'pid_name': pid.name,
    }

    if pid.get_command:
      command = self.BuildCommand(pid.get_command)
      output['get_command'] = command

    if pid.set_command:
      command = self.BuildCommand(pid.set_command)
      output['set_command'] = command

    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(
        template.render('templates/display_pid.tmpl',
                        output))


application = webapp.WSGIApplication(
  [
    ('/pid/manufacturer', SearchByManufacturer),
    ('/pid/name', SearchByName),
    ('/pid/id', SearchById),
    ('/pid/display', DisplayPid),
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
