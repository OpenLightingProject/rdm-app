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
# product_loader.py
# Copyright (C) 2011 Simon Newton
# Load the product id entities

import logging
from model import Manufacturer, Product
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache

items = [
    {'manufacturer': 0x7a70,
     'model_id': 1,
     'model_description': 'Dummy Model',
    },
    {'manufacturer': 0x7a70,
     'model_id': 2,
     'model_description': 'Arduino RGB Mixer',
    },
]


class LoadHandler(webapp.RequestHandler):
  """Return the list of all manufacturers."""

  def getManufacturer(self, manufacturer_id):
    manufacturer_q = Manufacturer.all()
    manufacturer_q.filter('esta_id =', manufacturer_id)
    return manufacturer_q.fetch(1)[0]

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    manufacturers = {}

    for params in items:
      manufacturer_id = params['manufacturer']
      if manufacturer_id not in manufacturers:
        manufacturers[manufacturer_id] = self.getManufacturer(manufacturer_id)
      product = Product(manufacturer = manufacturers[manufacturer_id],
                        device_model_id = params['model_id'],
                        model_description = params['model_description'])
      product.put()

    memcache.delete('products')
    self.response.out.write('ok')


class ClearHandler(webapp.RequestHandler):
  """Return the list of all manufacturers."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    for item in Product.all():
      item.delete()
    self.response.out.write('ok')


application = webapp.WSGIApplication(
  [
    ('/load_pro', LoadHandler),
    ('/clear_pro', ClearHandler),
  ],
  debug=True)

def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
