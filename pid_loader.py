# -*- coding: utf-8 -*-
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
# loader.py
# Copyright (C) 2011 Simon Newton
# The handlers for /pid /pid_search and /manufacturers

import logging
from model import Pid, MessageItem, Command, Message, Manufacturer
from model import SUBDEVICE_RANGE_DICT
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import data


class LoadHandler(webapp.RequestHandler):
  """Return the list of all manufacturers."""

  def AddItem(self, item):
    item_data = MessageItem(name = item['name'], type = item['type'])
    if item.get('size'):
      item_data.size = item['size']
    item_data.put()
    return item_data

  def AddMessage(self, message):
    items = []
    for item in message['items']:
      items.append(self.AddItem(item).key())

    message_data = Message(is_repeated = message['is_repeated'], items = items)

    if message['is_repeated'] and message.get('max_repeats') is not None:
      message_data.max_repeats = message['max_repeats']
    message_data.put()
    return message_data

  def AddPid(self, pid, manufacturer_id = 0):
    manufacturer_q = Manufacturer.all()
    manufacturer_q.filter('esta_id =', manufacturer_id)
    manufacturer = manufacturer_q.fetch(1)[0]

    pid_data = Pid(manufacturer = manufacturer,
                   pid_id = pid['value'],
                   name = pid['name'])

    if pid.get('link'):
      pid_data.link = pid['link']
    elif manufacturer_id == 0:
      pid_data.link = 'http://tsp.plasa.org/tsp/documents/published_docs.php'


    if pid.get('notes'):
      pid_data.notes = pid['notes']

    if pid.get('get_request'):
      get_request = self.AddMessage(pid['get_request'])
      get_response = self.AddMessage(pid['get_response'])

      command = Command(sub_device_range = pid['get_sub_device_range'],
                        request = get_request,
                        response = get_response)
      command.put()
      pid_data.get_command = command

    logging.info(pid['name'])

    if pid.get('set_request'):
      set_request = self.AddMessage(pid['set_request'])
      set_response = self.AddMessage(pid['set_response'])

      command = Command(sub_device_range = pid['set_sub_device_range'],
                        request = set_request,
                        response = set_response)
      command.put()
      pid_data.set_command = command

    pid_data.put()



  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    for pid in data.pids:
      self.AddPid(pid)

    for manufacturer in data.manufacturers:
      for pid in manufacturer['pids']:
        self.AddPid(pid, manufacturer['id'])

    self.response.out.write('ok')


class ClearHandler(webapp.RequestHandler):
  """Return the list of all manufacturers."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    for item in MessageItem.all():
      item.delete()

    for item in Message.all():
      item.delete()

    for item in Command.all():
      item.delete()

    for item in Pid.all():
      item.delete()

    self.response.out.write('ok')


class PrintHandler(webapp.RequestHandler):
  """Return the list of all manufacturers."""
  def WriteItem(self, item):
    self.response.out.write('  Name: %s, type %s\n' % (item.name, item.type))

  def WriteMessage(self, message):
    self.response.out.write(' Repeated %s\n' % message.is_repeated)
    if message.is_repeated and message.max_repeats is not None:
      self.response.out.write(' Max Repeats %s\n' % message.max_repeats)

    for item_key in message.items:
      item = MessageItem.get_by_id(item_key.id())
      logging.info(item)
      self.WriteItem(item)

  def WriteCommand(self, command):
    if command is None:
      self.response.out.write('not supported\n')
      return

    self.response.out.write('Sub device Range: %s\n' %
        SUBDEVICE_RANGE_DICT.get(command.sub_device_range, ''))

    self.response.out.write('Request\n')
    self.WriteMessage(command.request)

    self.response.out.write('Response\n')
    self.WriteMessage(command.response)


  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    pids = Pid.all()

    for pid in pids:
      self.response.out.write('id: %hx\n' % pid.pid_id)
      self.response.out.write('name: %s\n' % pid.name)
      self.response.out.write('manufacturer: %s\n' % pid.manufacturer.name)

      self.response.out.write('\nGET:\n')
      self.response.out.write('----\n')
      self.WriteCommand(pid.get_command)

      self.response.out.write('\nSET:\n')
      self.response.out.write('----\n')
      self.WriteCommand(pid.set_command)





application = webapp.WSGIApplication(
  [
    ('/add', LoadHandler),
    ('/remove', ClearHandler),
    ('/print', PrintHandler),
  ],
  debug=True)

def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
