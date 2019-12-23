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
# manufacturer_handler.py
# Copyright (C) 2012 Simon Newton
# Product search / display handlers

import common
from model import Manufacturer
from google.appengine.ext import webapp


class ListManufacturersHandler(common.BasePageHandler):
  """Display a list of manufacturers."""
  TEMPLATE = 'templates/manufacturers.tmpl'

  def GetTemplateData(self):
    manufacturers = []
    query = Manufacturer.all()
    query.order('name')
    for manufacturer in query:
      if manufacturer.esta_id in [0, 0xffff]:
        continue

      manufacturers.append({
        'name': manufacturer.name,
        'id': manufacturer.esta_id,
      })

    data = {
        'manufacturers': manufacturers,
    }
    return data


class DisplayManufacturersHandler(common.BasePageHandler):
  """Display a manufacturer page."""
  TEMPLATE = 'templates/display_manufacturer.tmpl'

  def GetTemplateData(self):
    manufacturer = common.GetManufacturer(self.request.get('manufacturer'))
    if not manufacturer:
      self.error(404)
      return

    device_query = manufacturer.responder_set
    device_query.order('model_description')
    pid_query = manufacturer.pid_set
    pid_query.order('name')

    data = {
        'manufacturer': manufacturer.name,
        'id': manufacturer.esta_id,
        'url': manufacturer.link,
        'image_url': manufacturer.image_serving_url,
        'devices': device_query.fetch(None),
        'pids': pid_query.fetch(None),
    }
    for product in manufacturer.product_set:
      data.setdefault(product.class_name().lower(), []).append(product)
    return data


app = webapp.WSGIApplication(
  [
    ('/manufacturer/list', ListManufacturersHandler),
    ('/manufacturer/display', DisplayManufacturersHandler),
  ],
  debug=True)
