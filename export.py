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

from model import *
from utils import TimestampToInt
import common
import json
import logging
import memcache_keys
import time
import timestamp_keys
from google.appengine.api import memcache
from google.appengine.ext import webapp


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
    self.Write('  type: %s' % item['type'].upper(), indent)
    self.Write('  name: "%s"' % item['name'], indent)
    if 'min_size' in item:
      self.Write('  min_size: %d' % item['min_size'], indent)
    if 'max_size' in item:
      self.Write('  max_size: %d' % item['max_size'], indent)
    if 'multiplier' in item:
      self.Write('  multiplier: %d' % item['multiplier'], indent)

    if item['type'] == 'group':
      for child_item in item['items']:
        self.WriteItem(child_item, indent + 2)

    for value, label in item.get('labels', []):
      self.Write('  label {', indent)
      self.Write('    value: %d' % value, indent)
      self.Write('    label: "%s"' % label, indent)
      self.Write('  }', indent)

    for min_value, max_value in item.get('range', []):
      self.Write('  range {', indent)
      self.Write('    min: %d' % min_value, indent)
      self.Write('    max: %d' % max_value, indent)
      self.Write('  }', indent)

    self.Write('}', indent)

  def WriteMessage(self, type, message_str, indent=0):
    message = eval(message_str)
    self.Write('%s {' % type, indent)
    for item in message['items']:
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

    if pid.discovery_command:
      self.WriteMessage('discovery_request',
                        pid.discovery_command.request, indent + 2)
      self.WriteMessage('discovery_response',
                        pid.discovery_command.response, indent + 2)
      self.Write(
          '  discovery_sub_device_range: %s' %
          self.SUB_DEVICE_RANGE_TO_ENUM[pid.discovery_command.sub_device_range],
          indent)

    if pid.set_command:
      self.WriteMessage('set_request', pid.set_command.request, indent + 2)
      self.WriteMessage('set_response', pid.set_command.response, indent + 2)
      self.Write('  set_sub_device_range: %s' %
                 self.SUB_DEVICE_RANGE_TO_ENUM[pid.set_command.sub_device_range],
                 indent)

    self.Write('}', indent)

  def WriteManufacturer(self, manufacturer, pids):
    self.Write('manufacturer {')
    self.Write('  manufacturer_id: %d' % manufacturer.esta_id)
    self.Write('  manufacturer_name: "%s"' % manufacturer.name.replace('"', '\\"'))
    for pid in pids:
      self.WritePid(pid, indent=2)

    self.Write('}')

  def get(self):
    esta_manufacturer = common.GetManufacturer(self.ESTA_ID)
    self.response.headers['Content-Type'] = 'text/plain'

    # Can be '', 'esta', 'esta-draft', 'manufacturers' or 'manufacturer-names'
    pid_selection = self.request.get('pids')
    if pid_selection == 'manufacturer-names':
      manufacturers = []
      query = Manufacturer.all()
      query.order('name')
      for manufacturer in query:
        if manufacturer.esta_id in [self.ESTA_ID, 0xffff]:
          continue

        self.WriteManufacturer(manufacturer, [])
    else:
      pids = Pid.all()

      if pid_selection == 'esta':
        pids.filter('draft =', False)
        pids.filter('manufacturer = ', esta_manufacturer)
      elif pid_selection == 'esta-draft':
        pids.filter('draft =', True)
        pids.filter('manufacturer = ', esta_manufacturer)
      elif pid_selection == "manufacturers":
        pids.filter('manufacturer != ', esta_manufacturer)

      manufacturers = {}
      esta_pids = []
      for pid in pids:
        if pid.manufacturer.esta_id == self.ESTA_ID:
          esta_pids.append(pid)
        else:
          # Build the hash of manufacturer pids by manufacturer
          manufacturers.setdefault(pid.manufacturer.esta_id, []).append(pid)

      esta_pids.sort(key=lambda p: p.pid_id)
      for pid in esta_pids:
        self.WritePid(pid)

      for manufacturer_id in sorted(manufacturers):
        manufacturer_pids = manufacturers[manufacturer_id]
        manufacturer_pids.sort(key=lambda p: p.pid_id)
        self.WriteManufacturer(manufacturers[manufacturer_id][0].manufacturer,
                               manufacturer_pids)

    query = LastUpdateTime.all()
    if pid_selection == 'manufacturer-names':
      query.filter('name = ', timestamp_keys.MANUFACTURERS)
    else:
      query.filter('name = ', timestamp_keys.PIDS)
    update_time = query.fetch(1)
    if update_time:
      timestamp = TimestampToInt(update_time[0].update_time)
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
        'manufacturer_id': model.manufacturer.esta_id,
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
    self.response.out.write(json.dumps({'models': models}))


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
        'key': str(controller.key()),
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
    self.response.out.write(json.dumps({'controllers': controllers}))


class MissingModelsHandler(webapp.RequestHandler):
  """Return all device models that are missing info / image urls in csv."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    results = Responder.all()
    results.order('device_model_id')

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

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    output = {}
    # update timestamps for pids & devices
    for update_timestamp in LastUpdateTime.all():
      if update_timestamp.name == timestamp_keys.CONTROLLERS:
        output['controller_update_time'] = TimestampToInt(
            update_timestamp.update_time)
      elif update_timestamp.name == timestamp_keys.DEVICES:
        output['device_update_time'] = TimestampToInt(
            update_timestamp.update_time)
      elif update_timestamp.name == timestamp_keys.PIDS:
        output['pid_update_time'] = TimestampToInt(
            update_timestamp.update_time)
      elif update_timestamp.name == timestamp_keys.MANUFACTURERS:
        output['manufacturer_update_time'] = TimestampToInt(
            update_timestamp.update_time)

    self.response.out.write(json.dumps(output))


class ModelInfoHandler(webapp.RequestHandler):
  """Return responder model info."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    results = Responder.all()

    models = []
    for model in results:
      model_output = {
        'manufacturer_name': model.manufacturer.name,
        'manufacturer_id': model.manufacturer.esta_id,
        'device_model_id': model.device_model_id,
        'model_description': model.model_description,
        'software_versions': [],
      }
      models.append(model_output)
      for software in model.software_version_set:
        software_output = {
          'id': software.version_id,
          'label': software.label,
          'personalities': [],
        }
        for personality in software.personality_set:
          personality_output = {
            'description': personality.description,
            'index': personality.index,
            'slot_count': personality.slot_count,
          }
          software_output['personalities'].append(personality_output)
        model_output['software_versions'].append(software_output)

    self.response.out.write(json.dumps({'models': models}))


export_application = webapp.WSGIApplication(
  [
    ('/index_info', InfoHandler),
    ('/download', PidDefinitionsAsProto),
    ('/export_models', ExportModelsHandler),
    ('/export_controllers', ExportControllersHandler),
    ('/missing_models', MissingModelsHandler),
    ('/model_info', ModelInfoHandler),
  ],
  debug=True)
