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
# model_handler.py
# Copyright (C) 2011 Simon Newton
# Model search / display handlers

import common
import json
import logging
import memcache_keys
import re
import sensor_types
from model import *
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class BrowseModels(common.BasePageHandler):
  """Show models & pictures."""
  TEMPLATE = 'templates/browse_models.tmpl'
  ROWS = 4
  COLUMNS = 4
  RESULTS_PER_PAGE = ROWS * COLUMNS

  def GetTemplateData(self):
    page = common.ConvertToInt(self.request.get('page'))
    if page is None:
      page = 1
    # 0 offset
    page -= 1

    query = Responder.all()
    query.order('-score')
    total = query.count()
    models = query.fetch(limit=self.RESULTS_PER_PAGE,
                         offset=page * self.RESULTS_PER_PAGE)
    rows = []
    for model, index in zip(models, range(len(models))):
      if index % self.COLUMNS == 0:
        rows.append([])

      output = {
          'name': model.model_description,
          'manufacturer_id': model.manufacturer.esta_id,
          'model_id': model.device_model_id,
      }
      if model.image_data:
        serving_url = model.image_serving_url
        if not serving_url:
          serving_url = images.get_serving_url(model.image_data.key())
          model.image_serving_url = serving_url
          model.put()
          logging.info('saving %s' % serving_url)
        output['image_key'] = serving_url

      rows[-1].append(output)

    start = page * self.RESULTS_PER_PAGE
    data= {
        'end': start + len(models),
        'model_rows': rows,
        'page_number': page + 1,  # back to 1 offset
        'start': start + 1,
        'total' : total,
    }
    if page:
      data['previous'] = page
    if start + len(models) < total:
      data['next'] = page + 2
    return data


class BaseSearchHandler(common.BasePageHandler):
  """The base class for model searches."""
  def Init(self):
    pass

  def ConvertToInt(self, value):
    if value:
      try:
        int_value = int(value)
      except ValueError:
        return None
      return int_value
    return None

  def GetTemplateData(self):
    self.Init()
    data = self.GetSearchData()
    data['models'] = self.GetResults()
    return data


class SearchByManufacturer(BaseSearchHandler):
  """Search by Manfacturer."""
  TEMPLATE = 'templates/manufacturer_model_search.tmpl'

  def Init(self):
    self._manufacturer_id = self.ConvertToInt(self.request.get('manufacturer'))

  def GetSearchData(self):
    manufacturer_list = memcache.get(memcache_keys.MANUFACTURER_MODEL_COUNTS)
    if not manufacturer_list:
      manufacturer_list = []
      query = Manufacturer.all()
      query.order('name')
      for manufacturer in query:
        responders = manufacturer.responder_set.count()
        if responders:
          manufacturer_list.append({
              'id': manufacturer.esta_id,
              'name': manufacturer.name,
              'responder_count': responders,
          })
      memcache.set(memcache_keys.MANUFACTURER_MODEL_COUNTS, manufacturer_list)

    return {
        'manufacturers': manufacturer_list,
        'current_id': self._manufacturer_id,
    }

  def GetResults(self):
    if self._manufacturer_id is not None:
      query = Manufacturer.all()
      query.filter('esta_id = ', self._manufacturer_id)

      for manufacturer in query.fetch(1):
        responder_query = manufacturer.responder_set
        responder_query.order('device_model_id')
        return responder_query
    return []


class SearchByCategory(BaseSearchHandler):
  """Search by Category."""
  TEMPLATE = 'templates/category_model_search.tmpl'

  def Init(self):
    self._category_id = self.ConvertToInt(self.request.get('category'))

  def GetSearchData(self):
    category_list = memcache.get(memcache_keys.CATEGORY_MODEL_COUNTS)
    if not category_list:
      category_list = []
      query = ProductCategory.all()
      query.order('name')
      for category in query:
        responders = category.responder_set.count()
        if responders:
          category_list.append({
              'id': category.id,
              'name': category.name,
              'responder_count': responders,
          })
      memcache.set(memcache_keys.CATEGORY_MODEL_COUNTS, category_list)

    return {
        'categories': category_list,
        'current_id': self._category_id,
    }

  def GetResults(self):
    if self._category_id is not None:
      query = ProductCategory.all()
      query.filter('id = ', self._category_id)

      for category in query.fetch(1):
        return category.responder_set
    return []


class SearchByTag(BaseSearchHandler):
  """Search by Tag."""
  TEMPLATE = 'templates/tag_model_search.tmpl'

  def Init(self):
    self._tag = self.request.get('tag')

  def GetSearchData(self):
    tag_list = memcache.get(memcache_keys.TAG_MODEL_COUNTS)
    if not tag_list:
      tag_list = []
      query = ResponderTag.all()
      query.order('label')
      for tag in query:
        responders = tag.responder_set.count()
        if responders and not tag.exclude_from_search:
          tag_list.append({
              'label': tag.label,
              'responder_count': responders,
          })
      memcache.set(memcache_keys.TAG_MODEL_COUNTS, tag_list)

    return {
        'tags': tag_list,
        'current_tag': self._tag,
    }

  def GetResults(self):
    if self._tag is not None:
      query = ResponderTag.all()
      query.filter('label = ', self._tag)
      tags = query.fetch(1)

      if tags:
        tag_relationships = tags[0].responder_set
        return [r.responder for r in tag_relationships]
    return []


class DisplayModel(common.BasePageHandler):
  """Display information about a particular model."""

  TEMPLATE = 'templates/display_model.tmpl'

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

  def GetTemplateData(self):
    model = self.LookupModelFromRequest()
    if not model:
      self.error(404)
      return

    esta_manufacturer = common.GetManufacturer(0)
    if not esta_manufacturer:
      logging.error("Can't find ESTA manufacturer!")
      # 404 early here
      self.error(404)
      return

    self.response.headers['Content-Type'] = 'text/plain'

    # software version info
    software_versions = []
    for version_info in model.software_version_set:
      version_output = {
          'version_id': version_info.version_id,
          'label': version_info.label,
      }

      supported_parameters = version_info.supported_parameters
      if supported_parameters is not None:
        param_output = []
        for param in supported_parameters:
          param_dict = {
              'id': param,
          }

          query = Pid.all()
          query.filter('pid_id =' , param)
          if param >= 0x8000:
            query.filter('manufacturer = ', model.manufacturer)
            param_dict['manufacturer_id'] = model.manufacturer.esta_id
          else:
            query.filter('manufacturer = ', esta_manufacturer)
            param_dict['manufacturer_id'] = esta_manufacturer.esta_id

          results = query.fetch(1)
          if results:
            param_dict['name'] = results[0].name
          param_output.append(param_dict)

        version_output['supported_parameters'] = sorted(
            param_output,
            key=lambda x: x['id'])
      software_versions.append(version_output)

      personalities = []
      for personality in version_info.personality_set:
        personality_info = {
          'description': personality.description,
          'index': personality.index,
          'slot_count': personality.slot_count,
        }
        personalities.append(personality_info)

      if personalities:
        personalities.sort(key=lambda x: x['index'])
        version_output['personalities'] = personalities;

      sensors = []
      for sensor in version_info.sensor_set:
        sensor_info = {
            'description': sensor.description,
            'index': sensor.index,
            'type': sensor.type,
            'supports_recording': sensor.supports_recording,
        }
        type_str = sensor_types.SENSOR_TYPES.get(sensor.type)
        if type_str is not None:
          sensor_info['type_str'] = type_str
        sensors.append(sensor_info)

      if sensors:
        sensors.sort(key=lambda x: x['index'])
        version_output['sensors'] = sensors

    output = {
      'description': model.model_description,
      'manufacturer': model.manufacturer.name,
      'model_id': model.device_model_id,
      'software_versions': software_versions,
      'software_versions_json': json.dumps(software_versions),
    }
    # link and product_category are optional
    if model.link:
      output['link'] = model.link
    category = model.product_category
    if category:
      output['product_category'] = category.name

    # tags
    for tag in model.tag_set:
      tags = output.setdefault('tags', [])
      tags.append(tag.tag.label)

    if model.image_data:
      serving_url = model.image_serving_url
      if not serving_url:
        serving_url = images.get_serving_url(model.image_data.key())
        model.image_serving_url = serving_url
        model.put()
      output['image_key'] = serving_url
    return output


model_application = webapp.WSGIApplication(
  [
    ('/', BrowseModels),
    ('/model/browse', BrowseModels),
    ('/model/manufacturer', SearchByManufacturer),
    ('/model/category', SearchByCategory),
    ('/model/tag', SearchByTag),
    ('/model/display', DisplayModel),
  ],
  debug=True)
