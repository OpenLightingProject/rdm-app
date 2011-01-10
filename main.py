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
from model import Manufacturer, Command, Pid, MessageItem, Message
from model import SUBDEVICE_RANGE_DICT
from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class ManufacturersHandler(webapp.RequestHandler):
  """Return the list of all manufacturers."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    manufacturers = []
    for manufacturer in Manufacturer.all():
      manufacturers.append({
        'name': manufacturer.name,
        'id': manufacturer.esta_id
      })
    self.response.out.write(simplejson.dumps({'manufacturers': manufacturers}))


class SearchHandler(webapp.RequestHandler):
  """Return a list of pids that match some criteria."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    results = []
    if self.request.get('pid'):
      match = re.search('((?:0x)?\d{1,4})', self.request.get('pid'))

      if match is not None:
        search_str = match.groups()[0]
        if search_str.startswith('0x'):
          pid_id = int(search_str[2:], 16)
        else:
          pid_id = int(search_str)

        logging.info(pid_id)
        results = Pid.all()
        results.filter('pid_id =' , pid_id)

    elif self.request.get('manufacturer'):
      match = re.search('\[(\d{4})\]', self.request.get('manufacturer'))

      if match is not None:
        query = Manufacturer.all()
        query.filter('esta_id = ', int(match.groups()[0], 16))

        for manufacturer in query.fetch(1):
          results = manufacturer.pid_set
    else:
      results = Pid.all()

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

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    pids = Pid.all()
    pids.filter('pid_id = ', 0x8000)

    for pid in pids:
      output = self.BuildPidStructure(pid)
      self.response.out.write(simplejson.dumps(output))

application = webapp.WSGIApplication(
  [
    ('/manufacturers', ManufacturersHandler),
    ('/pid_search', SearchHandler),
    ('/pid', PidHandler)
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
