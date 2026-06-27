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

import json
import memcache_keys
import common
import itertools
from model import Manufacturer, Pid, Responder, SUBDEVICE_RANGE_DICT
from utils import StringToInt
from google.appengine.api import memcache
from google.appengine.ext import webapp


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
    self._manufacturer_id = StringToInt(self.request.get('manufacturer'))

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
        query.filter('draft = ', False)
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
      results.filter('draft = ', False)
      results.filter('name =', name)

      return results
    return []


class SearchById(BaseSearchHandler):
  """Search PIDs by ID."""
  TEMPLATE = 'templates/id_pid_search.tmpl'

  def GetResults(self):
    pid_id = StringToInt(self.request.get('id'))
    if pid_id is not None:
      results = Pid.all()
      results.filter('pid_id =', pid_id)
      results.filter('draft = ', False)
      return results
    return []


class PidRoute(webapp.RequestHandler):
  def LookupPIDFromRequest(self):
    pid_id = self.request.get('pid')
    try:
      pid_id = int(pid_id)
    except ValueError:
      return None

    manufacturer = common.GetManufacturer(self.request.get('manufacturer'))
    if manufacturer is None or pid_id is None:
      return None

    models = Pid.all()
    models.filter('pid_id = ', pid_id)
    models.filter('manufacturer = ', manufacturer.key())

    pid_data = models.fetch(1)
    if pid_data:
      return pid_data[0]
    else:
      return None


class DisplayPid(common.BasePageHandler, PidRoute):
  """Display information about a particular PID."""

  TEMPLATE = 'templates/display_pid.tmpl'

  def CopyToDict(self, input_d, output_d, keys):
    for key in keys:
      if key in input_d:
        output_d[key] = input_d[key]

  def PopulateItem(self, item):
    """Build the data structure for an item."""
    item_output = {}
    self.CopyToDict(item,
                    item_output,
                    ['name', 'type', 'min_size', 'max_size', 'multiplier'])

    if item['type'] == 'group':
      children = []
      for child_item in item['items']:
        child_item_output = self.PopulateItem(child_item)
        children.append(child_item_output)
      item_output['items'] = children

    labeled_values = []
    for value, label in item.get('labels', []):
      labeled_value_output = {
        'value': value,
        'label': label,
      }
      labeled_values.append(labeled_value_output)
    if labeled_values:
      item_output['enums'] = labeled_values

    ranges = []
    for min_value, max_value in item.get('range', []):
      range_output = {
        'min': min_value,
        'max': max_value,
      }
      ranges.append(range_output)
    if ranges:
      item_output['ranges'] = ranges
    return item_output

  def PopulateMessage(self, message_output, message_str):
    message_data = eval(message_str)
    items = []
    for item in message_data['items']:
      item_output = self.PopulateItem(item)
      items.append(item_output)

    message_output['items'] = items

  def BuildCommand(self, command):
    request = {}
    self.PopulateMessage(request, command.request)
    response = {}
    self.PopulateMessage(response, command.response)
    command = {
        'request_json': json.dumps(request),
        'response_json': json.dumps(response),
        'subdevice_range': SUBDEVICE_RANGE_DICT.get(
            command.sub_device_range, ''),
    }
    return command

  def GetTemplateData(self):
    pid = self.LookupPIDFromRequest()
    if not pid:
      self.error(404)
      return

    supported_by = []
    for responder_key in pid.responders:
      responder = Responder.get(responder_key)
      if responder:
        supported_by.append({
          'name': responder.model_description,
          'manufacturer': responder.manufacturer.esta_id,
          'model': responder.device_model_id,
        })
    supported_by.sort(key=lambda x: x['name'])

    output = {
      'link': pid.link,
      'manufacturer_name': pid.manufacturer.name,
      'manufacturer_id': pid.manufacturer.esta_id,
      'notes': pid.notes,
      'pid_id': pid.pid_id,
      'pid_name': pid.name,
      'supported_by': supported_by,
    }

    if pid.get_command:
      command = self.BuildCommand(pid.get_command)
      output['get_command'] = command

    if pid.discovery_command:
      command = self.BuildCommand(pid.discovery_command)
      output['discovery_command'] = command

    if pid.set_command:
      command = self.BuildCommand(pid.set_command)
      output['set_command'] = command
    return output

class DisplayPidJSON(PidRoute):
  """Fetch E1.37-5 format JSON about a PID."""

  CUSTOM_CAPITALIZE_TESTS = [
    ("dmx_start_address", "DMX Start Address"),
    ("foo-dmx", "Foo DMX"),
    ("mini_dmxter_device", "Mini Dmxter Device"),
    ("this-is_a_test", "This Is A Test"),
    ("ip_address", "IP Address"),
    ("controller_ip_address", "Controller IP Address"),
    ("dazzled_led_type", "Dazzled LED Type"),
    ("device_rdm_uid", "Device RDM UID"),
    ("dns_via_ipv4_dhcp", "DNS Via IPv4 DHCP"),
  ]

  @staticmethod
  def CustomCapitalizeLabel(label):
    TRANSFORMS = {
      'asc',
      'dhcp',
      'dmx',
      'dns',
      'ip',
      'json',
      'led',
      'nsc',
      'pdl',
      'pid',
      'rdm',
      'uid',
      'url',
    }
    TRANSFORMS = {x:x.upper() for x in TRANSFORMS}
    TRANSFORMS['ipv4'] = 'IPv4'
    TRANSFORMS['ipv6'] = 'IPv6'
    TRANSFORMS['mdmx'] = 'mDMX'

    label = label.replace('-', ' ').replace('_', ' ').strip()
    if len(label) == 0: return ''
    
    end = []
    for part in label.split(' '):
      if TRANSFORMS.get(part.lower()):
        end.append(TRANSFORMS[part.lower()])
      elif len(part) > 0:
        end.append(part[0].upper() + part[1:])
      else:
        end.append('')
    
    return ' '.join(end)

  @staticmethod
  def ConvertItems(items):
    out = []
    for item in items:
      a = {'name':item['name'], 'displayName':DisplayPidJSON.CustomCapitalizeLabel(item['name'])}
      if item['type'] == 'bool':
        a['type'] = 'boolean'
        out.append(a)
      elif item['type'] in ['uint8', 'uint16', 'uint32', 'uint64', 'int8', 'int16', 'int32', 'int64']:
        a['type'] = item['type']
        if item.get('multiplier'):
          a['prefixPower'] = item['multiplier']
        if item.get('range'):
          a['ranges'] = [{'minimum':r[0], 'maximum':r[1]} for r in item['range']]
        if item.get('labels'):
          a['labels'] = [{'value':l[0], 'name':l[1]} for l in item['labels']]
          if not item.get('ranges'):
            a['restrictToLabeled'] = True
        out.append(a)
      elif item['type'] == 'string':
        a['type'] = item['type']
        if item.get('max_size'): a['maxBytes'] = item['max_size']
        if item.get('min_size'): a['minBytes'] = item['min_size']
        # could restrictToASCII here??
        out.append(a)
      elif item['type'] == 'ipv4':
        a['type'] = 'bytes'
        a['format'] = 'ipv4'
        out.append(a)
      elif item['type'] == 'ipv6':
        a['type'] = 'bytes'
        a['format'] = 'ipv6'
        out.append(a)
      elif item['type'] == 'mac':
        a['type'] = 'bytes'
        a['format'] = 'mac-address'
        out.append(a)
      elif item['type'] == 'uid':
        a['type'] = 'bytes'
        a['format'] = 'uid'
        out.append(a)
      elif item['type'] == 'group':
        a['type'] = 'list'
        if item.get('max_size'): a['minItems'] = item['max_size']
        if item.get('min_size'): a['maxItems'] = item['min_size']
        converted = DisplayPidJSON.ConvertItems(item['items'])
        if len(converted) == 1:
          a['itemType'] = converted[0]
        else:
          a['itemType'] = {
            'type': 'compound',
            'subtypes': converted
          }
        out.append(a)
      else:
        # WARNING: invalid item type??
        pass
    return out

  @staticmethod
  def SubDeviceRange(subs):
    if subs == 0:
      return ['root']
    elif subs == 1:
      return ['root', 'subdevices', 'broadcast']
    elif subs == 2:
      return ['root', 'subdevices']
    elif subs == 3:
      return ['subdevices']
    else: # should never happen
      return []

  @staticmethod
  def BuildCommand(output, command, prefix):
    request = eval(command.request)
    response = eval(command.response)
    output[prefix+'_request'] = DisplayPidJSON.ConvertItems(request['items'])
    output[prefix+'_response'] = DisplayPidJSON.ConvertItems(response['items'])
    output[prefix+'_request_subdevice_range'] = DisplayPidJSON.SubDeviceRange(command.sub_device_range)
    # response subdevices are always 'match' which is the default

  @staticmethod
  def CollapseMessages(output, message_a, message_b):
    if isinstance(output.get(message_a), list) and isinstance(output.get(message_b), list):
      if output[message_a] == output[message_b] and len(output[message_a]) != 0:
        output[message_b] = message_a

  @staticmethod
  def ConvertPid(pid):
    output = {
      'name': pid.name,
      'manufacturer_id': pid.manufacturer.esta_id,
      'pid': pid.pid_id,
      'version': 0,
    }
    if pid.notes:
      output['notes'] = pid.notes
    if pid.link:
      output['resources'] = [pid.link]

    # add get information
    if pid.get_command:
      DisplayPidJSON.BuildCommand(output, pid.get_command, 'get')
    if pid.set_command:
      DisplayPidJSON.BuildCommand(output, pid.set_command, 'set')

    # collapse repeated commands
    message_names = ['get_request', 'get_response', 'set_request', 'set_response']
    for (a, b) in itertools.combinations(message_names, 2):
      DisplayPidJSON.CollapseMessages(output, a, b)

    # collapse repeated properties
    # we get a list of them all
    #   and because python objects are references,
    #   we can just update this list in-place
    prop_list = []
    for m in message_names:
      if output.get(m) and isinstance(output[m], list):
        prop_list += [('#/'+m+'/'+str(i), prop) for (i, prop) in enumerate(output[m])]
    for i in xrange(1, len(prop_list)):
      for j in xrange(0, i):
        if prop_list[i][1] == prop_list[j][1]:
          prop_list[i][1].clear()
          prop_list[i][1]['$ref'] = prop_list[j][0]

    return output

  def get(self):
    pid = self.LookupPIDFromRequest()
    if not pid:
      self.error(404)
      return
    
    converted = DisplayPidJSON.ConvertPid(pid)

    # use the Content-Type recommended in E1.37-5
    self.response.headers['Content-Type'] = 'application/schema-instance+json'
    self.response.out.write(json.dumps(converted, indent=2))

pid_application = webapp.WSGIApplication(
  [
    ('/pid/manufacturer', SearchByManufacturer),
    ('/pid/name', SearchByName),
    ('/pid/id', SearchById),
    ('/pid/display', DisplayPid),
    ('/pid/display.json', DisplayPidJSON),
  ],
  debug=True)
