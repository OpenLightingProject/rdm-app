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
# main.py
# Copyright (C) 2011 Simon Newton
# The handlers for /pid /pid_search and /manufacturers

from model import *
import logging
import memcache_keys
import re
import time
from django.utils import simplejson
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class InfoHandler(webapp.RequestHandler):
  """Return the information about the index.

  This returns:
   - the last uptime time
   - the number of manufacturer pids
   - the number of device models
  """
  ESTA_ID = 0

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
    """Return the number of device models."""
    model_count = memcache.get(memcache_keys.DEVICE_MODEL_COUNT_KEY)
    if model_count is None:
      model_count = 0

      for pid in Responder.all():
        model_count += 1
      if not memcache.add(memcache_keys.DEVICE_MODEL_COUNT_KEY,
                          model_count):
        logging.error("Memcache set failed.")
    return model_count

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    output = {'timestamp': None}
    results = Pid.all()
    results.order('-update_time')

    pids = results.fetch(1)
    if pids:
      timestamp = int(time.mktime(pids[0].update_time.timetuple()))
      output['timestamp'] = timestamp
    output['manufacturer_pid_count'] = self.ManufacturerPidCount()
    output['device_model_count'] = self.DeviceModelCount()
    self.response.out.write(simplejson.dumps(output))


class ManufacturersHandler(webapp.RequestHandler):
  """Return the list of all manufacturers."""
  CACHE_KEY = 'manufacturers'

  def BuildResponse(self):
    manufacturers = []
    for manufacturer in Manufacturer.all():
      manufacturers.append({
        'name': manufacturer.name,
        'id': manufacturer.esta_id
      })
    response = simplejson.dumps({'manufacturers': manufacturers})
    if not memcache.add(memcache_keys.MANUFACTURER_CACHE_KEY, response):
      logging.error("Memcache set failed.")
    return response

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'

    response = memcache.get(memcache_keys.MANUFACTURER_CACHE_KEY)
    if response is None:
      response = self.BuildResponse()
    self.response.out.write(response)


class SearchHandler(webapp.RequestHandler):
  """Return a list of pids that match some criteria."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    results = []
    if self.request.get('pid'):
      match = re.search('((?:0x)?[\da-f]{1,4})', self.request.get('pid'))

      if match is not None:
        search_str = match.groups()[0]
        if search_str.startswith('0x'):
          pid_id = int(search_str[2:], 16)
        else:
          pid_id = int(search_str)

        results = Pid.all()
        results.filter('pid_id =' , pid_id)

    elif self.request.get('manufacturer'):
      match = re.search('\[([\da-f]{4})\]', self.request.get('manufacturer'))

      if match is not None:
        query = Manufacturer.all()
        query.filter('esta_id = ', int(match.groups()[0], 16))

        for manufacturer in query.fetch(1):
          results = manufacturer.pid_set

    elif self.request.get('pid_name'):
      name = self.request.get('pid_name').strip()
      name = name.replace(' ', '_').upper()
      # do full string matching for now
      results = Pid.all()
      results.filter('name =' , name)

    else:
      results = Pid.all()
      results.order('pid_id')

    pids = []
    for pid in results:
      get_valid = False
      set_valid = False
      if pid.get_command:
        get_valid = True
      if pid.set_command:
        set_valid = True
      pids.append({
        'get_valid': get_valid,
        'manufacturer': pid.manufacturer.name,
        'manufacturer_id': pid.manufacturer.esta_id,
        'name': pid.name,
        'pid': pid.pid_id,
        'set_valid': set_valid,
      })
    self.response.out.write(simplejson.dumps({'pids': pids}))


class PidHandler(webapp.RequestHandler):
  """Return a the description for a pid."""
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

  def PopulateCommand(self, output, prefix, command):
    if command is None:
      output['%s_subdevice_range' % prefix] = None
      output['%s_request' % prefix] = None
      output['%s_response' % prefix] = None
      return

    output['%s_subdevice_range' % prefix] = (
        SUBDEVICE_RANGE_DICT.get(command.sub_device_range, ''))

    get_request = {}
    self.PopulateMessage(get_request, command.request)
    output['%s_request' % prefix] = get_request

    get_response = {}
    self.PopulateMessage(get_response, command.response)
    output['%s_response' % prefix] = get_response


  def BuildPidStructure(self, pid):
    """Build the pid json structure."""
    output = {}
    output['name'] = pid.name
    output['value'] = pid.pid_id
    output['manufacturer'] = pid.manufacturer.name
    output['link'] = pid.link
    output['notes'] = pid.notes

    self.PopulateCommand(output, 'get', pid.get_command)
    self.PopulateCommand(output, 'set', pid.set_command)
    return output

  def GetManufacturer(self, manufacturer_id):
    try:
      id = int(manufacturer_id)
    except ValueError:
      return None

    query = Manufacturer.all()
    query.filter('esta_id = ', id)
    for manufacturer in query.fetch(1):
      return manufacturer
    return None

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    pid_id_str = self.request.get('pid')
    pid_id = None
    try:
      pid_id = int(pid_id_str)
    except ValueError:
      pass

    manufacturer = self.GetManufacturer(self.request.get('manufacturer'))

    if manufacturer and pid_id is not None:
      pids = Pid.all()
      pids.filter('pid_id = ', pid_id)
      pids.filter('manufacturer = ', manufacturer.key())

      for pid in pids:
        output = self.BuildPidStructure(pid)
        self.response.out.write(simplejson.dumps(output))


class DownloadHandler(webapp.RequestHandler):
  """Dump the datastore in protobuf format."""

  ESTA_ID = 0

  SUB_DEVICE_RANGE_TO_ENUM = {
    0: 'ROOT_DEVICE',
    1: 'ROOT_OR_ALL_SUBDEVICE',
    2: 'ROOT_OR_SUBDEVICE',
    3: 'ONLY_SUBDEVICES',
  }

  BOOL_MAPPING = {
    True: 'true',
    False: 'false',
  }

  def Write(self, line, indent=0):
    self.response.out.write('%s%s\n' % (' ' * indent, line))

  def WriteItem(self, item, indent=0):
    self.Write('field {', indent)
    self.Write('  type: %s' % item.type.upper(), indent)
    self.Write('  name: "%s"' % item.name, indent)
    if item.min_size is not None:
      self.Write('  min_size: %d' % item.min_size, indent)
    if item.max_size is not None:
      self.Write('  max_size: %d' % item.max_size, indent)
    if item.multiplier is not None:
      self.Write('  multiplier: %d' % item.multiplier, indent)

    if item.type == 'group':
      for child_key in item.items:
        child_item = MessageItem.get(child_key)
        self.WriteItem(child_item, indent+2)

    for enum_key in item.enums:
      enum = EnumValue.get(enum_key)
      self.Write('  label {', indent)
      self.Write('    value: %d' % enum.value, indent)
      self.Write('    label: "%s"' % enum.label, indent)
      self.Write('  }', indent)

    for range_key in item.allowed_values:
      range = AllowedRange.get(range_key)
      self.Write('  range {', indent)
      self.Write('    min: %d' % range.min, indent)
      self.Write('    max: %d' % range.max, indent)
      self.Write('  }', indent)

    self.Write('}', indent)

  def WriteMessage(self, type, message, indent=0):
    self.Write('%s {' % type, indent)
    for item_key in message.items:
      item = MessageItem.get(item_key)
      self.WriteItem(item, indent+2)
    self.Write('}', indent)

  def WritePid(self, pid, indent=0):
    self.Write('pid {', indent)
    self.Write('  name: "%s"' % pid.name, indent)
    self.Write('  value: %d' % pid.pid_id, indent)

    if pid.get_command:
      self.WriteMessage('get_request', pid.get_command.request, indent + 2)
      self.WriteMessage('get_response', pid.get_command.response, indent + 2)
      self.Write('  get_sub_device_range: %s' %
                 self.SUB_DEVICE_RANGE_TO_ENUM[pid.get_command.sub_device_range],
                 indent)

    if pid.set_command:
      self.WriteMessage('set_request', pid.set_command.request, indent + 2)
      self.WriteMessage('set_response', pid.set_command.response, indent + 2)
      self.Write('  set_sub_device_range: %s' %
                 self.SUB_DEVICE_RANGE_TO_ENUM[pid.set_command.sub_device_range],
                 indent)

    self.Write('}', indent)

  def WriteManfacturer(self, manufacturer, pids):
    self.Write('manufacturer {')
    self.Write('  manufacturer_id: %d' % manufacturer.esta_id)
    self.Write('  manufacturer_name: "%s"' % manufacturer.name)
    for pid in pids:
      self.WritePid(pid, indent=2)

    self.Write('}')

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    esta_pids = []
    manufacturers = {}
    pids = Pid.all()
    update_time = None

    for pid in pids:
      if update_time is None or pid.update_time > update_time:
        update_time = pid.update_time

      if pid.manufacturer.esta_id == self.ESTA_ID:
        esta_pids.append(pid)
      else:
        pid_list = manufacturers.setdefault(pid.manufacturer.esta_id, [])
        pid_list.append(pid)

    esta_pids.sort(key=lambda p: p.pid_id)
    for pid in esta_pids:
      self.WritePid(pid)

    manufacturer_ids = sorted(manufacturers)
    for manufacturer_id in manufacturer_ids:
      manufacturer_pids = manufacturers[manufacturer_id]
      manufacturer_pids.sort(key=lambda p: p.pid_id)
      self.WriteManfacturer(manufacturers[manufacturer_id][0].manufacturer,
                            manufacturer_pids)

    timestamp = int(time.mktime(update_time.timetuple()))
    self.Write('version: %d' % timestamp)


class ModelSearchHandler(webapp.RequestHandler):
  """Return all device models for a manufacturer."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    results = []
    if self.request.get('manufacturer'):
      match = re.search('\[([\da-f]{4})\]', self.request.get('manufacturer'))

      if match is not None:
        query = Manufacturer.all()
        query.filter('esta_id = ', int(match.groups()[0], 16))

        for manufacturer in query.fetch(1):
          results = manufacturer.responder_set

    else:
      results = Responder.all()
      results.order('device_model_id')

    models = []
    for model in results:
      models.append({
        'manufacturer_name': model.manufacturer.name,
        'device_model_id': model.device_model_id,
        'model_description': model.model_description,
      })
    self.response.out.write(simplejson.dumps({'models': models}))


class ExportModelsHandler(webapp.RequestHandler):
  """Return all device models for the RDM Protocol Site."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    results = Responder.all()
    results.order('device_model_id')

    models = []
    for model in results:
      models.append({
        'manufacturer_name': model.manufacturer.name,
        'device_model_id': model.device_model_id,
        'model_description': model.model_description,
        'link': model.link,
        'image_url': model.image_url,
      })
    self.response.out.write(simplejson.dumps({'models': models}))


class MissingModelsHandler(webapp.RequestHandler):
  """Return all device models that are missing info / image urls."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    results = Responder.all()
    results.order('device_model_id')

    models = []
    self.response.out.write(
        'Manufacturer ID,Manufacturer Name,Device ID,Model Name,Info Url,'
        'Image Url\n')
    for model in results:
      if model.link and model.image_url:
        continue
      fields = []
      fields.append('0x%hx' % model.manufacturer.esta_id)
      fields.append(model.manufacturer.name)
      fields.append('0x%hx' % model.device_model_id)
      fields.append(model.model_description)
      if model.link:
        fields.append(model.link)
      else:
        fields.append('')
      if model.image_url:
        fields.append(model.image_url)
      else:
        fields.append('')
      self.response.out.write(','.join(fields))
      self.response.out.write('\n')


application = webapp.WSGIApplication(
  [
    ('/download', DownloadHandler),
    ('/manufacturers', ManufacturersHandler),
    ('/pid', PidHandler),
    ('/pid_search', SearchHandler),
    ('/model_search', ModelSearchHandler),
    ('/export_models', ExportModelsHandler),
    ('/missing_models', MissingModelsHandler),
    ('/index_info', InfoHandler),
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
