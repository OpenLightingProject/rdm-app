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
# The main handlers used by the app.

from model import *
import logging
import memcache_keys
import re
import sensor_types
import time
from django.utils import simplejson
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


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


class CacheableRequest(webapp.RequestHandler):
  """The base class for cachable requests.

  Subclasses provide:
    CACHE_KEY
    BuildResponse()
    AddHeaders()
  """
  def get(self):
    self.AddHeaders();

    response = memcache.get(self.CACHE_KEY)
    if response is None:
      response = self.BuildResponse()
      if not memcache.add(self.CACHE_KEY, response):
        logging.error("Memcache set failed.")
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

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    pid_id_str = self.request.get('pid')
    pid_id = None
    try:
      pid_id = int(pid_id_str)
    except ValueError:
      pass

    manufacturer = GetManufacturer(self.request.get('manufacturer'))

    if manufacturer and pid_id is not None:
      pids = Pid.all()
      pids.filter('pid_id = ', pid_id)
      pids.filter('manufacturer = ', manufacturer.key())

      for pid in pids:
        output = self.BuildPidStructure(pid)
        self.response.out.write(simplejson.dumps(output))


class ModelSearchHandler(webapp.RequestHandler):
  """Return all models for a manufacturer."""
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
    elif self.request.get('category'):
      query = ProductCategory.all()
      query.filter('id = ', int(self.request.get('category')))

      for category in query.fetch(1):
        results = category.responder_set
    elif self.request.get('tag'):
      query = ResponderTag.all()
      logging.info(self.request.get('tag'))
      query.filter('label = ', self.request.get('tag'))
      tags = query.fetch(1)
      logging.info(tags)
      if tags:
        tag_relationships = tags[0].responder_set
        results = [r.responder for r in tag_relationships]

    else:
      results = Responder.all()
      results.order('device_model_id')

    models = []
    for model in results:
      models.append({
        'model_id': model.device_model_id,
        'manufacturer_id': model.manufacturer.esta_id,
        'manufacturer_name': model.manufacturer.name,
        'model_description': model.model_description,
      })

    models.sort(key=lambda x: (x['manufacturer_name'], x['model_id']))
    self.response.out.write(simplejson.dumps({'models': models}))


class BaseModelHandler(webapp.RequestHandler):
  """The base class for requests involving particular models.

  Returns:
    The Responder entity if found, otherwise None.
  """
  def LookupModelFromRequest(self):
    model_id_str = self.request.get('model')
    model_id = None
    try:
      model_id = int(model_id_str)
    except ValueError:
      return None

    manufacturer = GetManufacturer(self.request.get('manufacturer'))
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


class ModelInfoHandler(BaseModelHandler):
  """Return information about a specific model."""
  def get(self):
    model = self.LookupModelFromRequest()
    if not model:
      self.error(404)
      return

    esta_manufacturer = GetManufacturer(0)
    if not esta_manufacturer:
      logging.error("Can't find ESTA manufacturer!")
      # 404 early here
      self.error(404)
      return

    self.response.headers['Content-Type'] = 'text/plain'

    # software version info
    software_versions = []
    for version_info in model.software_version_set:
      version_output = {
          'version_id': version_info.version_id,
          'label': version_info.label,
      }
      category = model.product_category
      if category:
        version_output['product_category'] = category.name

      supported_parameters = version_info.supported_parameters
      if supported_parameters is not None:
        param_output = []
        for param in supported_parameters:
          query = Pid.all()
          query.filter('pid_id =' , param)
          if param >= 0x8000:
            query.filter('manufacturer = ', model.manufacturer)
          else:
            query.filter('manufacturer = ', esta_manufacturer)

          results = query.fetch(1)
          if results:
            param_output.append('%s (0x%04hx)' % (results[0].name, param))
          else:
            param_output.append('0x%04hx' % param)

        version_output['supported_parameters'] = sorted(param_output)
      software_versions.append(version_output)

      personalities = []
      for personality in version_info.personality_set:
        personality_info = {
          'description': personality.description,
          'index': personality.index,
          'slot_count': personality.slot_count,
        }
        personalities.append(personality_info)

      if personalities:
        personalities.sort(key=lambda x: x['index'])
        version_output['personalities'] = personalities;

      sensors = []
      for sensor in version_info.sensor_set:
        sensor_info = {
            'description': sensor.description,
            'index': sensor.index,
            'type': sensor.type,
            'supports_recording': sensor.supports_recording,
        }
        type_str = sensor_types.SENSOR_TYPES.get(sensor.type)
        if type_str is not None:
          sensor_info['type_str'] = type_str
        sensors.append(sensor_info)

      if sensors:
        sensors.sort(key=lambda x: x['index'])
        version_output['sensors'] = sensors

    output = {
      'description': model.model_description,
      'manufacturer': model.manufacturer.name,
      'model_id': model.device_model_id,
      'software_versions': software_versions,
    }
    # link and product_category are optional
    if model.link:
      output['link'] = model.link
    category = model.product_category
    if category:
      output['product_category'] = category.name

    # tags
    for tag in model.tag_set:
      tags = output.setdefault('tags', [])
      tags.append(tag.tag.label)

    if model.image_data:
      output['image_key'] = images.get_serving_url(model.image_data.key())

    self.response.out.write(simplejson.dumps(output))


application = webapp.WSGIApplication(
  [
    ('/model_info', ModelInfoHandler),
    ('/model_search', ModelSearchHandler),
    ('/pid', PidHandler),
    ('/pid_search', SearchHandler),
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
