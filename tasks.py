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
# tasks.py
# Copyright (C) 2011 Simon Newton
# Defines the task queue handlers.

from google.appengine.api import images
from google.appengine.ext import webapp
from image_fetcher import ImageFetcher
from model import Product, Responder
from pid_index_builder import PidIndexBuilder


class FetchResponderImage(webapp.RequestHandler):
  """Fetch the image for a responder entity."""
  def get(self):
    key = self.request.get('key')
    responder = Responder.get(key)
    if not responder:
      return

    if responder.image_url and not responder.image_data:
      fetcher = ImageFetcher()
      blob_key = fetcher.FetchAndSaveImage(responder.image_url)

      if blob_key:
        responder.image_data = blob_key
        responder.image_serving_url = images.get_serving_url(blob_key)
        responder.put()
    return


class FetchProductImage(webapp.RequestHandler):
  """Fetch the image for a product entity."""
  def get(self):
    key = self.request.get('key')
    product = Product.get(key)
    if not product:
      return

    if product.image_url and not product.image_data:
      fetcher = ImageFetcher()
      blob_key = fetcher.FetchAndSaveImage(product.image_url)

      if blob_key:
        product.image_data = blob_key
        product.image_serving_url = images.get_serving_url(blob_key)
        product.put()
    return


class RankDevices(webapp.RequestHandler):
  """Rank the devices according to a simple scoring algorithm."""
  def get(self):
    for device in Responder.all():
      score = 0
      if device.image_data is not None:
        # 10 point boost for having an image
        score += 10
      if device.link is not None:
        # 1 point boost for having a link
        score += 1
      if device.software_version_set.count():
        # 10 point boost for having version information
        score += 10

      if device.score_penalty:
        score -= device.score_penalty

      # up to +20 pts for having test results
      if device.rdm_responder_rating is not None:
        score += int(device.rdm_responder_rating / 5)

      device.score = score
      device.put()
    return


class BuildPidResponderIndex(webapp.RequestHandler):
  """Build the mappings between PIDs and the responders which support the
     PID.
  """
  def get(self):
    builder = PidIndexBuilder()
    builder.BuildIndex()
    return


tasks_application = webapp.WSGIApplication(
  [
    ('/tasks/fetch_image', FetchResponderImage),
    ('/tasks/fetch_product_image', FetchProductImage),
    ('/tasks/rank_devices', RankDevices),
    ('/tasks/build_pid_responder_index', BuildPidResponderIndex),
  ],
  debug=True)
