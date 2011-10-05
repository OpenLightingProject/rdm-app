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
# admin.py
# Copyright (C) 2011 Simon Newton
# The handlers for the admin page.

import logging
import manufacturer_data
import memcache_keys
import model_data
import os
import pid_data
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import *
from pid_loader import PidLoader


class AdminPageHandler(webapp.RequestHandler):
  """Admin functions."""
  def ClearManufacturers(self):
    for item in Manufacturer.all():
      item.delete()

  def LoadManufacturers(self):
    for id, name in manufacturer_data.MANUFACTURER_DATA:
      logging.info('%d, %s' % (id, name))
      manufacturer = Manufacturer(esta_id = id, name = name)
      manufacturer.put()
    memcache.delete(memcache_keys.MANUFACTURER_CACHE_KEY)

  def ClearPids(self):
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
    for item in MessageItem.all():
      item.delete()

    for item in Message.all():
      item.delete()

    for item in Command.all():
      item.delete()

    for item in Pid.all():
      item.delete()

    for item in EnumValue.all():
      item.delete()

    for item in AllowedRange.all():
      item.delete()

  def LoadPids(self):
    loader = PidLoader()
    for pid in pid_data.ESTA_PIDS:
      loader.AddPid(pid)

  def LoadManufacturerPids(self):
    loader = PidLoader()
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
    for manufacturer in pid_data.MANUFACTURER_PIDS:
      for pid in manufacturer['pids']:
        loader.AddPid(pid, manufacturer['id'])

  def ClearModels(self):
    memcache.delete(memcache_keys.DEVICE_MODEL_COUNT_KEY)
    for item in Responder.all():
      item.delete()

  def LoadModels(self):
    memcache.delete(memcache_keys.DEVICE_MODEL_COUNT_KEY)
    manufacturers = {}
    def getManufacturer(manufacturer_id):
      if manufacturer_id not in manufacturers:
        manufacturer_q = Manufacturer.all()
        manufacturer_q.filter('esta_id =', manufacturer_id)
        manufacturers[manufacturer_id] = manufacturer_q.fetch(1)[0]
      return manufacturers[manufacturer_id]

    for manufacturer_id, models in model_data.DEVICE_MODEL_DATA.iteritems():
      manufacturer = getManufacturer(manufacturer_id)
      for info in models:
        device = Responder(manufacturer = manufacturer,
                           device_model_id = info['device_model'],
                           model_description = info['model_description'])

        if 'product_category' in info:
          device.product_category = info['product_category']
        device.put()

  def get(self):
    ACTIONS = {
        'clear_m': self.ClearManufacturers,
        'load_m': self.LoadManufacturers,
        'clear_p': self.ClearPids,
        'load_p': self.LoadPids,
        'load_mp': self.LoadManufacturerPids,
        'clear_models': self.ClearModels,
        'load_models': self.LoadModels,
    }

    ALLOWED_USERS = [
        'nomis52@gmail.com',
        'simon@nomis52.net',
    ]

    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    if user.email() not in ALLOWED_USERS:
      self.error(403)
      return

    action = self.request.get('action')
    if action in ACTIONS:
      ACTIONS[action]()

    template_data = {
        'logout_url': users.create_logout_url("/"),
    }
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render('templates/admin.tmpl',
                                            template_data))


application = webapp.WSGIApplication(
  [
    ('/admin', AdminPageHandler),
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
