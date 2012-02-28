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

import logging
from google.appengine.api import images
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from model import Controller, Responder
from image_fetcher import ImageFetcher


class FetchResponderImage(webapp.RequestHandler):
  """Fetch the image for a responder entity."""
  def get(self):
    key = self.request.get('key')
    responder = Responder.get(key)
    if not responder:
      return 200

    if responder.image_url and not responder.image_data:
      fetcher = ImageFetcher()
      blob_key = fetcher.FetchAndSaveImage(responder.image_url)

      if blob_key:
        responder.image_data = blob_key
        responder.image_serving_url = images.get_serving_url(blob_key)
        responder.put()
    return 200


class FetchControllerImage(webapp.RequestHandler):
  """Fetch the image for a controller entity."""
  def get(self):
    key = self.request.get('key')
    controller = Controller.get(key)
    if not controller:
      return 200

    if controller.image_url and not controller.image_data:
      fetcher = ImageFetcher()
      blob_key = fetcher.FetchAndSaveImage(controller.image_url)

      if blob_key:
        controller.image_data = blob_key
        controller.image_serving_url = images.get_serving_url(blob_key)
        controller.put()
    return 200


class RankDevices(webapp.RequestHandler):
  """Rank the devices according to a simple scoring algorithm."""
  def get(self):
    for device in Responder.all():
      score = 0
      if device.image_data is not None:
        # 10 point boost for having an image
        score += 10
      if device.link is not None:
        # 10 point boost for having a link
        score += 1
      if device.software_version_set.count():
        # 10 point boost for having version information
        score += 10

      if device.score_penalty:
        score -= device.score_penalty

      device.score = score
      device.put()
    return 200


application = webapp.WSGIApplication(
  [
    ('/tasks/fetch_image', FetchResponderImage),
    ('/tasks/fetch_controller_image', FetchControllerImage),
    ('/tasks/rank_devices', RankDevices),
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
