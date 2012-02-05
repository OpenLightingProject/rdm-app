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
# export.py
# Copyright (C) 2011 Simon Newton
# The handlers for exporting information to third parties.

from google.appengine.dist import use_library
use_library('django', '1.2')

from model import *
import logging
import memcache_keys
import time
import timestamp_keys
from django.utils import simplejson
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class PidDefinitionsAsProto(webapp.RequestHandler):
  """Dump the PID definitions in protobuf format."""
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


class ExportModelsHandler(webapp.RequestHandler):
  """Return all device models for the RDM Protocol Site.

  This is used by the rdmprotocol.org site. Don't change the format without
  checking in with Peter Kirkup.
  """
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    results = Responder.all()

    models = []
    for model in results:
      model_output = {
        'manufacturer_name': model.manufacturer.name,
        'device_model_id': model.device_model_id,
        'model_description': model.model_description,
      }
      if model.link:
        model_output['link'] = model.link
      if model.image_url:
        model_output['image_url'] = model.image_url
      tags = list(model.tag_set)
      if tags:
        tags = []
        for tag in model.tag_set:
          tags.append(tag.tag.label)
        model_output['tags'] = tags

      models.append(model_output)
    self.response.out.write(simplejson.dumps({'models': models}))


class ExportControllersHandler(webapp.RequestHandler):
  """Return all controllers for the RDM Protocol Site.

  This is used by the rdmprotocol.org site. Don't change the format without
  checking in with Peter Kirkup.
  """
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    results = Controller.all()

    controllers = []
    for controller in Controller.all():
      controller_output = {
        'manufacturer_name': controller.manufacturer.name,
        'name': controller.name,
      }
      if controller.link:
        controller_output['link'] = controller.link
      if controller.image_url:
        controller_output['image_url'] = controller.image_url
      tags = list(controller.tag_set)
      if tags:
        tags = []
        for tag in controller.tag_set:
          tags.append(tag.tag.label)
        controller_output['tags'] = tags

      controllers.append(controller_output)
    self.response.out.write(simplejson.dumps({'controllers': controllers}))


class MissingModelsHandler(webapp.RequestHandler):
  """Return all device models that are missing info / image urls in csv."""
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


class InfoHandler(webapp.RequestHandler):
  """Return the information about the index.

  This returns:
   - the last uptime time
   - the number of manufacturer pids
   - the number of models
  """
  ESTA_ID = 0

  def TimestampToInt(self, timestamp):
    """Convert a DateTimeProperty to an int."""
    return int(time.mktime(timestamp.timetuple()))

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    output = {}
    # update timestamps for pids & devices
    for update_timestamp in LastUpdateTime.all():
      if update_timestamp.name == timestamp_keys.CONTROLLERS:
        output['controller_update_time'] = self.TimestampToInt(
            update_timestamp.update_time)
      elif update_timestamp.name == timestamp_keys.DEVICES:
        output['device_update_time'] = self.TimestampToInt(
            update_timestamp.update_time)
      elif update_timestamp.name == timestamp_keys.PIDS:
        output['pid_update_time'] = self.TimestampToInt(
            update_timestamp.update_time)
      elif update_timestamp.name == timestamp_keys.MANUFACTURERS:
        output['manufacturer_update_time'] = self.TimestampToInt(
            update_timestamp.update_time)

    self.response.out.write(simplejson.dumps(output))


class ExportManufacturers(webapp.RequestHandler):
  """Return the list of all manufacturers."""
  CACHE_KEY = memcache_keys.MANUFACTURER_CACHE_KEY

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'

    response = memcache.get(memcache_keys.MANUFACTURER_CACHE_KEY)
    if response is None:
      response = self.BuildResponse()
      if not memcache.add(self.CACHE_KEY, response):
        logging.error("Manufacturer Memcache set failed.")
    self.response.out.write(response)

  def BuildResponse(self):
    manufacturers = []
    for manufacturer in Manufacturer.all():
      manufacturers.append({
        'name': manufacturer.name,
        'id': manufacturer.esta_id
      })
    return simplejson.dumps({'manufacturers': manufacturers})


application = webapp.WSGIApplication(
  [
    ('/index_info', InfoHandler),
    ('/download', PidDefinitionsAsProto),
    ('/export_models', ExportModelsHandler),
    ('/export_controllers', ExportControllersHandler),
    ('/manufacturers', ExportManufacturers),
    ('/missing_models', MissingModelsHandler),
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
