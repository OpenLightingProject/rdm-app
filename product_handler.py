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
# splitter_handler.py
# Copyright (C) 2012 Simon Newton
# Product search / display handlers

import common
import logging
import memcache_keys
import re
from model import *
from utils import StringToInt
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class BrowseProducts(common.BasePageHandler):
  """Show products & pictures.

  The sub class products a ProductType() method which tells us what model class
  to use.
  """
  TEMPLATE = 'templates/browse_products.tmpl'
  ROWS = 4
  COLUMNS = 4
  RESULTS_PER_PAGE = ROWS * COLUMNS

  def GetTemplateData(self):
    page = StringToInt(self.request.get('page'), False)
    if page is None:
      page = 1
    # 0 offset
    page -= 1

    query = self.ProductType().all()
    query.order('-image_url')
    total = query.count()
    products = query.fetch(limit=self.RESULTS_PER_PAGE,
                           offset=page * self.RESULTS_PER_PAGE)
    rows = []
    for product, index in zip(products, range(len(products))):
      if index % self.COLUMNS == 0:
        rows.append([])

      output = {
          'name': product.name,
          'key': product.key(),
      }
      if product.image_data:
        serving_url = product.image_serving_url
        if not serving_url:
          serving_url = images.get_serving_url(product.image_data.key())
          product.image_serving_url = serving_url
          product.put()
          logging.info('saving %s' % serving_url)
        output['image_key'] = serving_url
      rows[-1].append(output)

    start = page * self.RESULTS_PER_PAGE
    data = {
        'end': start + len(products),
        'product_rows': rows,
        'page_number': page + 1,  # back to 1 offset
        'product_type': self.ProductType().class_name().lower(),
        'start': start + 1,
        'total' : total,
    }
    if page:
      data['previous'] = page
    if start + len(products) < total:
      data['next'] = page + 2
    return data


class BaseSearchHandler(common.BasePageHandler):
  """The base class for product searches."""
  def Init(self):
    pass

  def GetTemplateData(self):
    self.Init()
    data = self.GetSearchData()
    data['products'] = self.GetResults()
    data['product_type'] = self.ProductType().class_name().lower()
    return data


class SearchByManufacturer(BaseSearchHandler):
  """Search by Manfacturer."""
  TEMPLATE = 'templates/manufacturer_product_search.tmpl'

  def Init(self):
    self._manufacturer_id = StringToInt(self.request.get('manufacturer'))
    self._manufacturer = common.GetManufacturer(self._manufacturer_id)

  def GetSearchData(self):
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
            'product_count': 0,
          }
        manufacturer_by_id[manufacturer.esta_id]['product_count'] += 1
      manufacturer_list = manufacturer_by_id.values()
      manufacturer_list.sort(key=lambda x: x['name'])
      memcache.set(self.MemcacheKey(), manufacturer_list)

    return {
        'manufacturers': manufacturer_list,
        'current_id': self._manufacturer_id,
    }

  def GetResults(self):
    if self._manufacturer is not None:
      query = self.ProductType().all()
      query.filter('manufacturer = ', self._manufacturer.key())
      query.order('name')
      return query
    return []


class SearchByTag(BaseSearchHandler):
  """Search by Tag."""
  TEMPLATE = 'templates/tag_product_search.tmpl'

  def Init(self):
    self._tag = self.request.get('tag')

  def GetSearchData(self):
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
              'product_count': products,
          })
      memcache.set(self.MemcacheKey(), tag_list)
    return {
        'tags': tag_list,
        'current_tag': self._tag,
    }

  def GetResults(self):
    if self._tag is not None:
      query = ProductTag.all()
      query.filter('label = ', self._tag)
      query.filter('product_type = ', self.ProductType().class_name())
      tags = query.fetch(1)

      if tags:
        tag_relationships = tags[0].product_set
        return [r.product for r in tag_relationships]
    return []


class DisplayProduct(common.BasePageHandler):
  """Display information about a particular product.

  The sub class products a ProductType() method which tells us what model class
  to use.
  """

  TEMPLATE = 'templates/display_product.tmpl'

  def GetTemplateData(self):
    product = self.ProductType().get(self.request.get('key'))
    if not product:
      self.error(404)
      return

    self.response.headers['Content-Type'] = 'text/plain'

    output = {
      'name': product.name,
      'manufacturer': product.manufacturer.name,
      'manufacturer_id': product.manufacturer.esta_id,
    }
    # link is optional
    if product.link:
      output['link'] = product.link

    # tags
    for tag in product.tag_set:
      tags = output.setdefault('tags', [])
      tags.append(tag.tag.label)

    if product.image_data:
      serving_url = product.image_serving_url
      if not serving_url:
        serving_url = images.get_serving_url(product.image_data.key())
        product.image_serving_url = serving_url
        product.put()
        logging.info('saving %s' % serving_url)
      output['image_key'] = serving_url
    return output


# The classes for each Product type.
# Controllers
class BrowseController(BrowseProducts):
  def ProductType(self):
    return Controller

class ControllerByManufacturer(SearchByManufacturer):
  def ProductType(self):
    return Controller

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_CONTROLLER_COUNTS

class ControllerByTag(SearchByTag):
  def ProductType(self):
    return Controller

  def MemcacheKey(self):
    return memcache_keys.TAG_CONTROLLER_COUNTS

class DisplayController(DisplayProduct):
  def ProductType(self):
    return Controller


# Software
class BrowseSoftware(BrowseProducts):
  def ProductType(self):
    return Software

class SoftwareByManufacturer(SearchByManufacturer):
  def ProductType(self):
    return Software

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_SOFTWARE_COUNTS

class SoftwareByTag(SearchByTag):
  def ProductType(self):
    return Software

  def MemcacheKey(self):
    return memcache_keys.TAG_SOFTWARE_COUNTS

class DisplaySoftware(DisplayProduct):
  def ProductType(self):
    return Software

# Splitters
class BrowseSplitters(BrowseProducts):
  def ProductType(self):
    return Splitter

class SplitterByManufacturer(SearchByManufacturer):
  def ProductType(self):
    return Splitter

  def MemcacheKey(self):
    return memcache_keys.MANUFACTURER_SPLITTER_COUNTS

class SplitterByTag(SearchByTag):
  def ProductType(self):
    return Splitter

  def MemcacheKey(self):
    return memcache_keys.TAG_SPLITTER_COUNTS

class DisplaySplitters(DisplayProduct):
  def ProductType(self):
    return Splitter


app = webapp.WSGIApplication(
  [
    ('/controller/browse', BrowseController),
    ('/controller/display', DisplayController),
    ('/controller/manufacturer', ControllerByManufacturer),
    ('/controller/tag', ControllerByTag),
    ('/software/browse', BrowseSoftware),
    ('/software/display', DisplaySoftware),
    ('/software/manufacturer', SoftwareByManufacturer),
    ('/software/tag', SoftwareByTag),
    ('/splitter/browse', BrowseSplitters),
    ('/splitter/display', DisplaySplitters),
    ('/splitter/manufacturer', SplitterByManufacturer),
    ('/splitter/tag', SplitterByTag),
  ],
  debug=True)
