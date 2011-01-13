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

import logging
import re
import time
from model import Manufacturer, Command, Pid, MessageItem, Message
from model import SUBDEVICE_RANGE_DICT
from django.utils import simplejson
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class LastUpdateHandler(webapp.RequestHandler):
  """Return the last time the pids were updated."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    output = {'timestamp': None}
    results = Pid.all()
    results.order('-update_time')

    pids = results.fetch(1)
    if pids:
      timestamp = int(time.mktime(pids[0].update_time.timetuple()))
      output['timestamp'] = timestamp
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
    if not memcache.add(self.CACHE_KEY, response):
      logging.error("Memcache set failed.")
    return response

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'

    response = memcache.get(self.CACHE_KEY)
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
      pids.append({
        'manufacturer': pid.manufacturer.name,
        'manufacturer_id': pid.manufacturer.esta_id,
        'pid': pid.pid_id,
        'name': pid.name,
      })
    self.response.out.write(simplejson.dumps({'pids': pids}))


class PidHandler(webapp.RequestHandler):
  """Return a the description for a pid."""
  def PopulateMessage(self, message_output, message):
    message_output['is_repeated'] = message.is_repeated
    max_repeats = None
    if message.is_repeated and message.max_repeats is not None:
      max_repeats = message.max_repeats
    message_output['max_repeats'] = max_repeats

    items = []
    for item_key in message.items:
      item = MessageItem.get_by_id(item_key.id())

      item_output = {
          'name': item.name,
          'type': item.type,
      }
      if item.size:
        item_output['size'] = item.size
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
    if item.size is not None:
      self.Write('  size: %d' % item.size, indent)
    self.Write('}', indent)

  def WriteMessage(self, type, message, indent=0):
    self.Write('%s {' % type, indent)

    for item_key in message.items:
      item = MessageItem.get_by_id(item_key.id())
      self.WriteItem(item, indent+2)

    self.Write('  repeated_group: %s' % self.BOOL_MAPPING[message.is_repeated],
               indent)
    if message.is_repeated and message.max_repeats:
      self.Write('  max_repeats: %d' % message.max_repeats, indent)

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
      self.WriteManfacturer(manufacturers[manufacturer_id][0].manufacturer,
                            manufacturers[manufacturer_id])

    timestamp = int(time.mktime(update_time.timetuple()))
    self.Write('version: %d' % timestamp)


application = webapp.WSGIApplication(
  [
    ('/download', DownloadHandler),
    ('/manufacturers', ManufacturersHandler),
    ('/pid_search', SearchHandler),
    ('/pid', PidHandler),
    ('/update_time', LastUpdateHandler),
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
