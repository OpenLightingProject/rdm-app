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
# json.py
# Copyright (C) 2012 Simon Newton
# Version 1 of the JSON API.

from model import *
import common
import json
import logging
import memcache_keys
import timestamp_keys
import utils
from google.appengine.api import memcache
from google.appengine.ext import webapp


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


class ManufacturerLookup(webapp.RequestHandler):
  """Query on manufacturer ID."""
  def get(self):
    manufacturer = common.GetManufacturer(self.request.get('manufacturer'))
    if manufacturer is None:
      self.error(404)
      return

    output = {
      'name': manufacturer.name,
      'esta_id': manufacturer.esta_id,
    }
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'
    self.response.out.write(json.dumps(output))


class ResponderFirmware(webapp.RequestHandler):
  """Return the latest firmware for a responder."""
  def get(self):
    responder = common.LookupModel(self.request.get('manufacturer'),
                                    self.request.get('model'))
    if responder is None:
      self.error(404)
      return

    max_version = None
    max_label = None
    for version in responder.software_version_set:
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


class ResponderPersonalities(webapp.RequestHandler):
  """Returns the personalities for a responder."""
  def get(self):
    responder = common.LookupModel(self.request.get('manufacturer'),
                                   self.request.get('model'))
    if responder is None:
      self.error(404)
      return

    versions = []
    for version_info in responder.software_version_set:
      personalities = []
      for personality in version_info.personality_set:
        personality_info = {
          'description': personality.description,
          'index': personality.index,
        }
        personalities.append(personality_info)

      version_output = {
          'version_id': version_info.version_id,
          'label': version_info.label,
          'personalities': personalities,
      }
      versions.append(version_output)

    output = {
      'manufacturer_name': responder.manufacturer.name,
      'manufacturer_id': responder.manufacturer.esta_id,
      'device_model_id': responder.device_model_id,
      'model_description': responder.model_description,
      'versions': versions,
    }
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'
    self.response.out.write(json.dumps(output))


class UpdateTimeHandler(webapp.RequestHandler):
  """Return the last update time for various parts of the index."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    # timestamp name : json key
    timestamp_pairs = {
        timestamp_keys.CONTROLLERS: 'controller_update_time',
        timestamp_keys.DEVICES: 'device_update_time',
        timestamp_keys.MANUFACTURERS: 'manufacturer_update_time',
        timestamp_keys.PIDS: 'pid_update_time',
        timestamp_keys.SOFTWARE: 'software_update_time',
        timestamp_keys.SPLITTERS: 'splitter_update_time',
    }

    output = {}
    for update_timestamp in LastUpdateTime.all():
      name = update_timestamp.name
      if name in timestamp_pairs:
        output[timestamp_pairs[name]] = utils.TimestampToInt(
            update_timestamp.update_time)
    self.response.out.write(json.dumps(output))


app = webapp.WSGIApplication(
  [
    ('/api/json/1/manufacturers', ManufacturerList),
    ('/api/json/1/manufacturer', ManufacturerLookup),
    ('/api/json/1/latest_responder_firmware', ResponderFirmware),
    ('/api/json/1/responder_personalities', ResponderPersonalities),
    ('/api/json/1/update_times', UpdateTimeHandler),
  ],
  debug=True)
