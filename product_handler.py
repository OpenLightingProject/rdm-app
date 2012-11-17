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

  def GetAll(self, page):
    """
    Returns:
      count, products
    """
    query = self.ProductType().all()
    query.order('-image_url')
    total = query.count()
    products = query.fetch(limit=self.RESULTS_PER_PAGE,
                           offset=page * self.RESULTS_PER_PAGE)
    return total, products

  def FilterByTag(self, page, tag):
    query = ProductTag.all()
    query.filter('label = ', tag)
    query.filter('product_type = ', self.ProductType().class_name())
    tags = query.fetch(1)

    if not tags:
      return 0, []

    query = tags[0].product_set
    total = query.count()
    tag_relationships = query.fetch(limit=self.RESULTS_PER_PAGE,
                                     offset=page * self.RESULTS_PER_PAGE)
    return total, [r.product for r in tag_relationships]

  def FilterByManufacturer(self, page, manufacturer):
    manufacturer_id = StringToInt(manufacturer)
    manufacturer = common.GetManufacturer(manufacturer_id)
    if manufacturer is None:
      return 0, []

    query = self.ProductType().all()
    query.filter('manufacturer = ', manufacturer.key())
    query.order('name')
    total = query.count()
    return total, query.fetch(None)

  def GetTemplateData(self):
    page = StringToInt(self.request.get('page'), False)
    if page is None:
      page = 1
    # 0 offset
    page -= 1

    data = {
      'page_number': page + 1,  # back to 1 offset
      'product_type': self.ProductType().class_name().lower(),
    }

    total = 0
    products = []
    tag = self.request.get('tag')
    manufacturer = self.request.get('manufacturer');
    if tag:
      data['tag'] = tag
      total, products = self.FilterByTag(page, tag)
    elif manufacturer:
      data['manufacturer'] = manufacturer
      total, products = self.FilterByManufacturer(page, manufacturer)
    else:
      total, products = self.GetAll(page)

    data['total'] = total
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
    data['end'] = start + len(products)
    data['product_rows'] =  rows
    data['start'] = start + 1

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

class DisplayController(DisplayProduct):
  def ProductType(self):
    return Controller

# Nodes
class BrowseNodes(BrowseProducts):
  def ProductType(self):
    return Node

class DisplayNode(DisplayProduct):
  def ProductType(self):
    return Node

# Software
class BrowseSoftware(BrowseProducts):
  def ProductType(self):
    return Software

class DisplaySoftware(DisplayProduct):
  def ProductType(self):
    return Software

# Splitters
class BrowseSplitters(BrowseProducts):
  def ProductType(self):
    return Splitter

class DisplaySplitters(DisplayProduct):
  def ProductType(self):
    return Splitter


app = webapp.WSGIApplication(
  [
    ('/controller/browse', BrowseController),
    ('/controller/display', DisplayController),
    ('/node/browse', BrowseNodes),
    ('/node/display', DisplayNode),
    ('/software/browse', BrowseSoftware),
    ('/software/display', DisplaySoftware),
    ('/splitter/browse', BrowseSplitters),
    ('/splitter/display', DisplaySplitters),
  ],
  debug=True)
