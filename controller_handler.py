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
# controller_handler.py
# Copyright (C) 2012 Simon Newton
# Controller search / display handlers

import common
import logging
import memcache_keys
import re
import sensor_types
from model import *
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class BrowseControllers(common.BasePageHandler):
  """Show controllers & pictures."""
  TEMPLATE = 'templates/browse_controllers.tmpl'
  ROWS = 4
  COLUMNS = 4
  RESULTS_PER_PAGE = ROWS * COLUMNS

  def GetTemplateData(self):
    page = common.ConvertToInt(self.request.get('page'))
    if page is None:
      page = 1
    # 0 offset
    page -= 1

    query = Controller.all()
    query.order('-image_url')
    total = query.count()
    controllers = query.fetch(limit=self.RESULTS_PER_PAGE,
                              offset=page * self.RESULTS_PER_PAGE)
    rows = []
    for controller, index in zip(controllers, range(len(controllers))):
      if index % self.COLUMNS == 0:
        rows.append([])

      output = {
          'name': controller.name,
          'key': controller.key(),
      }
      if controller.image_data:
        serving_url = controller.image_serving_url
        if not serving_url:
          serving_url = images.get_serving_url(controller.image_data.key())
          controller.image_serving_url = serving_url
          controller.put()
          logging.info('saving %s' % serving_url)
        output['image_key'] = serving_url
      rows[-1].append(output)

    start = page * self.RESULTS_PER_PAGE
    data = {
        'end': start + len(controllers),
        'controller_rows': rows,
        'page_number': page + 1,  # back to 1 offset
        'start': start + 1,
        'total' : total,
    }
    if page:
      data['previous'] = page
    if start + len(controllers) < total:
      data['next'] = page + 2
    return data


class BaseSearchHandler(common.BasePageHandler):
  """The base class for controller searches."""
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
    data['controllers'] = self.GetResults()
    return data


class SearchByManufacturer(BaseSearchHandler):
  """Search by Manfacturer."""
  TEMPLATE = 'templates/manufacturer_controller_search.tmpl'

  def Init(self):
    self._manufacturer_id = self.ConvertToInt(self.request.get('manufacturer'))

  def GetSearchData(self):
    manufacturer_list = memcache.get(memcache_keys.MANUFACTURER_CONTROLLER_COUNTS)
    if not manufacturer_list:
      manufacturer_list = []
      query = Manufacturer.all()
      query.order('name')
      for manufacturer in query:
        controllers = manufacturer.controller_set.count()
        if controllers:
          manufacturer_list.append({
              'id': manufacturer.esta_id,
              'name': manufacturer.name,
              'controller_count': controllers,
          })
      memcache.set(memcache_keys.MANUFACTURER_CONTROLLER_COUNTS,
                   manufacturer_list)

    return {
        'manufacturers': manufacturer_list,
        'current_id': self._manufacturer_id,
    }

  def GetResults(self):
    if self._manufacturer_id is not None:
      query = Manufacturer.all()
      query.filter('esta_id = ', self._manufacturer_id)

      for manufacturer in query.fetch(1):
        responder_query = manufacturer.controller_set
        responder_query.order('name')
        return responder_query
    return []


class SearchByTag(BaseSearchHandler):
  """Search by Tag."""
  TEMPLATE = 'templates/tag_controller_search.tmpl'

  def Init(self):
    self._tag = self.request.get('tag')

  def GetSearchData(self):
    tag_list = memcache.get(memcache_keys.TAG_CONTROLLER_COUNTS)
    if not tag_list:
      tag_list = []
      query = ControllerTag.all()
      query.order('label')
      for tag in query:
        controllers = tag.controller_set.count()
        if controllers and not tag.exclude_from_search:
          tag_list.append({
              'label': tag.label,
              'controller_count': controllers,
          })
      memcache.set(memcache_keys.TAG_CONTROLLER_COUNTS, tag_list)

    return {
        'tags': tag_list,
        'current_tag': self._tag,
    }

  def GetResults(self):
    if self._tag is not None:
      query = ControllerTag.all()
      query.filter('label = ', self._tag)
      tags = query.fetch(1)

      if tags:
        tag_relationships = tags[0].controller_set
        return [r.controller for r in tag_relationships]
    return []


class DisplayController(common.BasePageHandler):
  """Display information about a particular controller."""

  TEMPLATE = 'templates/display_controller.tmpl'

  def GetTemplateData(self):
    controller = Controller.get(self.request.get('key'))
    if not controller:
      self.error(404)
      return

    self.response.headers['Content-Type'] = 'text/plain'

    output = {
      'name': controller.name,
      'manufacturer': controller.manufacturer.name,
    }
    # link is optional
    if controller.link:
      output['link'] = controller.link

    # tags
    for tag in controller.tag_set:
      tags = output.setdefault('tags', [])
      tags.append(tag.tag.label)

    if controller.image_data:
      serving_url = controller.image_serving_url
      if not serving_url:
        serving_url = images.get_serving_url(controller.image_data.key())
        controller.image_serving_url = serving_url
        controller.put()
        logging.info('saving %s' % serving_url)
      output['image_key'] = serving_url
    return output


controller_application = webapp.WSGIApplication(
  [
    ('/controller/browse', BrowseControllers),
    ('/controller/manufacturer', SearchByManufacturer),
    ('/controller/tag', SearchByTag),
    ('/controller/display', DisplayController),
  ],
  debug=True)
