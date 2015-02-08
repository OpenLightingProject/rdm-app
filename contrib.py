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
# contrib.py
# Copyright (C) 2012 Simon Newton
# The handlers for the contrib page.

import common
import logging
import datetime
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from model import *


class BaseContribPageHandler(webapp.RequestHandler):
  """The base handler for contrib requests."""
  ALLOWED_USERS = [
      'nomis52@gmail.com',
      'simon@nomis52.net',
      'peterjnewman@gmail.com',
  ]

  def get(self):
    self.do_request()

  def post(self):
    self.do_request()

  def do_request(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    if user.email() not in self.ALLOWED_USERS:
      self.error(403)
      return
    self.HandleRequest()


class ContribPageHandler(BaseContribPageHandler):
  """Contrib menu."""
  def HandleRequest(self):
    template_data = {
      'logout_url': users.create_logout_url("/"),
    }

    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render('templates/contrib.tmpl',
                                            template_data))


class AddInfoResponderHandler(BaseContribPageHandler):
  """Displays the UI for adding responder info."""
  def HandleRequest(self):
    # the responders without data
    # we fetch ones so we don't have consistency problems
    responders = self.GetMissingResponders()
    if self.request.get('update'):
      self.SaveChanges(responders)

    template_data = {
      'logout_url': users.create_logout_url("/"),
      'responders': self.BuildResponderList(responders),
    }

    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(
      'templates/contrib-add-responder-info.tmpl',
      template_data))

  def GetMissingResponders(self):
    responders = []
    for responder in Responder.all():
      if responder.link and responder.image_url:
        continue
      responders.append(responder)
    return responders

  def BuildResponderList(self, responders):
    output = []
    for responder in responders:
      if responder.link and responder.image_url:
        continue
      output.append({
        'id': responder.device_model_id,
        'image': responder.image_url,
        'manufacturer': responder.manufacturer.name,
        'manufacturer_id': responder.manufacturer.esta_id,
        'model': responder.model_description,
        'url': responder.link,
      })
    return output

  def GetURLOrNone(self, param):
    url = self.request.get(param)
    if not url or not url.startswith('http://'):
      return None
    return url


  def SaveChanges(self, responders):
    added = 0
    for responder in responders:
      key = '%d_%d' % (responder.manufacturer.esta_id,
                       responder.device_model_id)
      image = self.GetURLOrNone('%s_image' % key)
      url = self.GetURLOrNone('%s_url' % key)

      if not (image or url):
        continue

      responder_obj = UploadedResponderInfo(
        manufacturer_id = responder.manufacturer.esta_id,
        device_model_id = responder.device_model_id,
        upload_time = datetime.datetime.now()
      )
      if image:
        responder_obj.image_url = image
      if url:
        responder_obj.link_url = url
      logging.info('Added %s' % responder.model_description)
      responder_obj.put()
      added += 1
    common.MaybeSendEmail(added)

app = webapp.WSGIApplication(
  [
    ('/contrib', ContribPageHandler),
    ('/contrib/add_responder_info', AddInfoResponderHandler),
  ],
  debug=True)
