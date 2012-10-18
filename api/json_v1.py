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
# json_app.py
# Copyright (C) 2012 Simon Newton
# The handlers for exporting information to third parties.

from model import *
import common
import json
import logging
import memcache_keys
from google.appengine.api import memcache
from google.appengine.ext import webapp


class ResponderFirmware(webapp.RequestHandler):
  """Return the latest firmware for a responder."""

  def LookupModelFromRequest(self):
    model_id_str = self.request.get('model')
    model_id = None
    try:
      model_id = int(model_id_str)
    except ValueError:
      return None

    manufacturer = common.GetManufacturer(self.request.get('manufacturer'))
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

  def get(self):
    model_data = self.LookupModelFromRequest()
    if model_data is None:
      self.error(404)
      return

    max_version = None
    max_label = None
    for version in model_data.software_version_set:
      if max_version is None or version.version_id > max_version:
        max_version = version.version_id
        max_label = version.label

    if max_version is None:
      self.error(404)

    output = {
      'version': max_version,
      'label' : max_label,
      'URL': '',
    }
    self.response.headers['Content-Type'] = 'text/json'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'
    self.response.out.write(json.dumps(output))

class ManufacturerList(webapp.RequestHandler):
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
    return json.dumps({'manufacturers': manufacturers})


app = webapp.WSGIApplication(
  [
    ('/api/json/1/newest_responder_firmware', ResponderFirmware),
    ('/api/json/1/manufacturers', ManufacturerList),
  ],
  debug=True)
