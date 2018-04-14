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
# json_api.py
# Copyright (C) 2012 Simon Newton
# Version 1 and 2 of the JSON API.

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
  API_VERSION = 1
  CACHE_KEY = memcache_keys.MANUFACTURER_CACHE_KEY

  def get(self):
    if self.API_VERSION > 1:
      self.response.headers['Content-Type'] = 'application/json'
    else:
      self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'

    response = memcache.get(self.CACHE_KEY)
    if response is None:
      response = self.BuildResponse()
      if not memcache.add(self.CACHE_KEY, response):
        logging.error("Manufacturer Memcache set failed.")
    self.response.out.write(response)

  def BuildResponse(self):
    manufacturers = []
    query = Manufacturer.all()
    if self.API_VERSION > 1:
      query.order('name')
    for manufacturer in query:
      manufacturer_entry = {
        'name': manufacturer.name,
        'id': manufacturer.esta_id
      }
      if self.API_VERSION > 1 and manufacturer.link:
        manufacturer_entry['link'] = manufacturer.link
      manufacturers.append(manufacturer_entry)
    return json.dumps({'manufacturers': manufacturers})


class ManufacturerList2(ManufacturerList):
  API_VERSION = 2
  CACHE_KEY = memcache_keys.MANUFACTURER_CACHE_KEY_2


class ManufacturerLookup(webapp.RequestHandler):
  """Query on manufacturer ID."""
  API_VERSION = 1

  def get(self):
    manufacturer = common.GetManufacturer(self.request.get('manufacturer'))
    if manufacturer is None:
      self.error(404)
      return

    output = {
      'name': manufacturer.name,
      'esta_id': manufacturer.esta_id,
    }
    if self.API_VERSION > 1 and manufacturer.link:
      output['link'] = manufacturer.link
    if self.API_VERSION > 1:
      self.response.headers['Content-Type'] = 'application/json'
    else:
      self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'
    self.response.out.write(json.dumps(output))


class ManufacturerLookup2(ManufacturerLookup):
  API_VERSION = 2


class ResponderFirmware(webapp.RequestHandler):
  """Return the latest firmware for a responder."""
  API_VERSION = 1

  def get(self):
    responder = common.LookupModelFromRequest(self.request)
    if responder is None:
      self.error(404)
      return

    version = common.GetLatestSoftware(responder);
    if version is None:
      self.error(404)

    output = {
      'version': version.version_id,
      'label' : version.label,
    }
    # Standardise on link in API v2 upwards
    if self.API_VERSION > 1:
      output['link'] = None;
    else:
      output['URL'] = '';
    # Add other useful info in API v2 upwards
    if self.API_VERSION > 1:
      output['manufacturer_name'] = responder.manufacturer.name
      output['manufacturer_id'] = responder.manufacturer.esta_id
      output['device_model_id'] = responder.device_model_id
      output['model_description'] = responder.model_description
      if responder.manufacturer.link:
        output['manufacturer_link'] = responder.manufacturer.link
    if self.API_VERSION > 1:
      self.response.headers['Content-Type'] = 'application/json'
    else:
      self.response.headers['Content-Type'] = 'text/json'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'
    self.response.out.write(json.dumps(output))


class ResponderFirmware2(ResponderFirmware):
  API_VERSION = 2


class ResponderPersonalities(webapp.RequestHandler):
  """Returns the personalities for a responder."""
  API_VERSION = 1

  def get(self):
    responder = common.LookupModelFromRequest(self.request)
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
        if self.API_VERSION > 1 and personality.slot_count:
          personality_info['slot_count'] = personality.slot_count
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
    if self.API_VERSION > 1 and responder.manufacturer.link:
      output['manufacturer_link'] = responder.manufacturer.link
    if self.API_VERSION > 1:
      self.response.headers['Content-Type'] = 'application/json'
    else:
      self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'
    self.response.out.write(json.dumps(output))


class ResponderPersonalities2(ResponderPersonalities):
  API_VERSION = 2


class UpdateTimeHandler(webapp.RequestHandler):
  """Return the last update time for various parts of the index."""
  API_VERSION = 1

  def get(self):
    if self.API_VERSION > 1:
      self.response.headers['Content-Type'] = 'application/json'
    else:
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


class UpdateTimeHandler2(UpdateTimeHandler):
  API_VERSION = 2


class ProductTags(webapp.RequestHandler):
  """Return the tags and number of products for each."""
  API_VERSION = 1

  def get(self):
    if self.API_VERSION > 1:
      self.response.headers['Content-Type'] = 'application/json'
    else:
      self.response.headers['Content-Type'] = 'text/plain'
    tag_list = memcache.get(self.MemcacheKey())
    if not tag_list:
      tag_list = []
      query = ProductTag.all()
      query.filter('product_type = ', self.ProductType().class_name())
      query.order('label')
      for tag in query:
        products = tag.product_set.count()
        if products and not tag.exclude_from_search:
          tag_list.append({
              'label': tag.label,
              'count': products,
          })
      memcache.set(self.MemcacheKey(), tag_list)
    self.response.out.write(json.dumps(tag_list))

class ProductManufacturers(webapp.RequestHandler):
  """Return the manufactures and number of products for each."""
  API_VERSION = 1

  def get(self):
    if self.API_VERSION > 1:
      self.response.headers['Content-Type'] = 'application/json'
    else:
      self.response.headers['Content-Type'] = 'text/plain'
    manufacturer_list = memcache.get(self.MemcacheKey())
    if not manufacturer_list:
      query = self.ProductType().all()
      manufacturer_by_id = {}
      for product in query:
        manufacturer = product.manufacturer
        if manufacturer.esta_id not in manufacturer_by_id:
          manufacturer_by_id[manufacturer.esta_id] = {
            'id': manufacturer.esta_id,
            'name': manufacturer.name,
            'count': 0,
          }
          if self.API_VERSION > 1 and manufacturer.link:
            manufacturer_by_id[manufacturer.esta_id]['link'] = manufacturer.link
        manufacturer_by_id[manufacturer.esta_id]['count'] += 1
      manufacturer_list = manufacturer_by_id.values()
      manufacturer_list.sort(key=lambda x: x['name'])
      memcache.set(self.MemcacheKey(), manufacturer_list)
    self.response.out.write(json.dumps(manufacturer_list))


# The classes for each Product type.
# Controllers
class ControllerManufacturers(ProductManufacturers):
  def ProductType(self):
    return Controller

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_CONTROLLER_COUNTS


class ControllerManufacturers2(ControllerManufacturers):
  API_VERSION = 2

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_CONTROLLER_COUNTS_2


class ControllerTags(ProductTags):
  def ProductType(self):
    return Controller

  def MemcacheKey(self):
    return memcache_keys.TAG_CONTROLLER_COUNTS


class ControllerTags2(ControllerTags):
  API_VERSION = 2


# Nodes
class NodeManufacturers(ProductManufacturers):
  def ProductType(self):
    return Node

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_NODE_COUNTS


class NodeManufacturers2(NodeManufacturers):
  API_VERSION = 2

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_NODE_COUNTS_2


class NodeTags(ProductTags):
  def ProductType(self):
    return Node

  def MemcacheKey(self):
    return memcache_keys.TAG_NODE_COUNTS


class NodeTags2(NodeTags):
  API_VERSION = 2


# Software
class SoftwareManufacturers(ProductManufacturers):
  def ProductType(self):
    return Software

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_SOFTWARE_COUNTS


class SoftwareManufacturers2(SoftwareManufacturers):
  API_VERSION = 2

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_SOFTWARE_COUNTS_2


class SoftwareTags(ProductTags):
  def ProductType(self):
    return Software

  def MemcacheKey(self):
    return memcache_keys.TAG_SOFTWARE_COUNTS


class SoftwareTags2(SoftwareTags):
  API_VERSION = 2


# Splitters
class SplitterManufacturers(ProductManufacturers):
  def ProductType(self):
    return Splitter

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_SPLITTER_COUNTS


class SplitterManufacturers2(SplitterManufacturers):
  API_VERSION = 2

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_SPLITTER_COUNTS_2


class SplitterTags(ProductTags):
  def ProductType(self):
    return Splitter

  def MemcacheKey(self):
    return memcache_keys.TAG_SPLITTER_COUNTS


class SplitterTags2(SplitterTags):
  API_VERSION = 2


class PidCounts(webapp.RequestHandler):
  """Return the count of PID usage."""
  API_VERSION = 1

  def get(self):
    if self.API_VERSION > 1:
      self.response.headers['Content-Type'] = 'application/json'
    else:
      self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'
    self.response.out.write(self.BuildResponse())

  def BuildResponse(self):
    param_counts = {}
    responders = 0
    max_manufacturer_pids = 0
    if self.API_VERSION > 1:
      max_manufacturer_responder = None
    else:
      max_manufacturer_responder = ''
    max_pids = 0
    if self.API_VERSION > 1:
      max_pids_responder = None
    else:
      max_pids_responder = ''
    for responder in Responder.all():
      params = []
      version = common.GetLatestSoftware(responder)
      if version:
        params = version.supported_parameters

      manufacturer_pids = 0
      for param in params:
        param_counts.setdefault(param, 0)
        param_counts[param] += 1
        if param >= 0x8000:
          manufacturer_pids += 1
      if params:
        responders += 1
      if manufacturer_pids > max_manufacturer_pids:
        if responder.model_description:
          max_manufacturer_responder = responder.model_description
        else:
          max_manufacturer_responder = responder.device_model_id
        max_manufacturer_pids = manufacturer_pids
      if len(params) > max_pids:
        if responder.model_description:
          max_pids_responder = responder.model_description
        else:
          max_pids_responder = responder.device_model_id
        max_pids = len(params)

    pids = []
    for param, count in param_counts.iteritems():
      param_info = {
        'id': param,
        'count': count,
      }
      if param < 0x8000:
        query = Pid.all()
        query.filter('pid_id = ', param)
        pid = query.fetch(1)
        if pid:
          param_info['name'] = pid[0].name
      pids.append(param_info)

    output = {
        'count': responders,
        'max_manufacturer_pids': (max_manufacturer_responder,
                                  max_manufacturer_pids),
        'max_pids': (max_pids_responder, max_pids),
        'pids': pids,
    }
    return json.dumps(output)


class PidCounts2(PidCounts):
  API_VERSION = 2


app = webapp.WSGIApplication(
  [
    ('/api/json/1/manufacturers', ManufacturerList),
    ('/api/json/1/manufacturer', ManufacturerLookup),
    ('/api/json/1/latest_responder_firmware', ResponderFirmware),
    ('/api/json/1/responder_personalities', ResponderPersonalities),
    ('/api/json/1/update_times', UpdateTimeHandler),
    ('/api/json/1/controller_tags', ControllerTags),
    ('/api/json/1/controller_manufacturers', ControllerManufacturers),
    ('/api/json/1/node_tags', NodeTags),
    ('/api/json/1/node_manufacturers', NodeManufacturers),
    ('/api/json/1/software_tags', SoftwareTags),
    ('/api/json/1/software_manufacturers', SoftwareManufacturers),
    ('/api/json/1/splitter_tags', SplitterTags),
    ('/api/json/1/splitter_manufacturers', SplitterManufacturers),
    ('/api/json/1/pid_counts', PidCounts),
    ('/api/json/2/manufacturers', ManufacturerList2),
    ('/api/json/2/manufacturer', ManufacturerLookup2),
    ('/api/json/2/latest_responder_firmware', ResponderFirmware2),
    ('/api/json/2/responder_personalities', ResponderPersonalities2),
    ('/api/json/2/update_times', UpdateTimeHandler2),
    ('/api/json/2/controller_tags', ControllerTags2),
    ('/api/json/2/controller_manufacturers', ControllerManufacturers2),
    ('/api/json/2/node_tags', NodeTags2),
    ('/api/json/2/node_manufacturers', NodeManufacturers2),
    ('/api/json/2/software_tags', SoftwareTags2),
    ('/api/json/2/software_manufacturers', SoftwareManufacturers2),
    ('/api/json/2/splitter_tags', SplitterTags2),
    ('/api/json/2/splitter_manufacturers', SplitterManufacturers2),
    ('/api/json/2/pid_counts', PidCounts2),
  ],
  debug=True)
