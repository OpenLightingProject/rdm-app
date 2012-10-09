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
# pid_handler.py
# Copyright (C) 2011 Simon Newton
# PID search / display handlers.

import datetime
import json
import logging
from model import *
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class HandleModelData(webapp.RequestHandler):
  """Handle model data uploads.

  Requests are in the form:
    model_data=<model data as a python dict>
  """
  TEMPLATE = 'templates/upload_model_confirm.tmpl'

  def get(self):
    model_data = self.request.get('model_data')
    status = self.VerifyAndStoreData(model_data)
    self.WriteResponse({
        'responders': status,
    })

  def post(self):
    model_data = self.request.get('model_data')
    status = self.VerifyAndStoreData(model_data)
    self.WriteResponse({
        'responders': status,
    })

  def WriteResponse(self, output):
    # Update template data
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(self.TEMPLATE, output))

  def VerifyAndStoreData(self, data):
    """Check the data look reasonable and if it does, store it.

    Returns:
      A list of dicts in the form:
      [{
        'key': key,
      }]
    """
    if not data:
      return []

    try:
      evaled_data = eval(data, {})
    except Exception as e:
      logging.info(data)
      logging.error(e)
      return []

    responder_obj_ids = []
    for manufacturer_id, responders in evaled_data.iteritems():
      try:
        manufacturer_id = int(manufacturer_id)
      except ValueError:
        logging.error('Invalid manufacturer id %s' % manufacturer_id)
        continue

      # See if we can get the manufacturer name
      manufacturer_name = None
      manufacturer_query = Manufacturer.all()
      manufacturer_query.filter('esta_id = ', manufacturer_id)
      results = manufacturer_query.fetch(1)
      if results:
        manufacturer_name = results[0].name

      for responder in responders:
        if 'device_model' not in responder:
          logging.error('Missing device_model from data')
          continue
        try:
          device_model_id = int(responder['device_model'])
        except ValueError:
          logging.error('Invalid device model %s' % responder['device_model'])
          continue

        # ok, that's all the required fields
        del responder['device_model']

        responder_obj = UploadedResponderInfo(
          manufacturer_id = manufacturer_id,
          device_model_id = device_model_id,
          info = str(responder),
          upload_time = datetime.datetime.now()
        )
        responder_obj.put()

        responder_obj_ids.append({
          'device_model_id': device_model_id,
          'key': str(responder_obj.key()),
          'manufacturer': manufacturer_name,
          'manufacturer_id': manufacturer_id,
          'model_description': responder.get('model_description', ''),
        })

    return responder_obj_ids


class UpdateModelData(webapp.RequestHandler):
  """Handle updates to model data.

  Requests are in the form:
    data=<model data as json>
  """
  TEMPLATE = 'templates/upload_model_confirm.tmpl'

  def get(self):
   self.response.headers['Content-Type'] = 'text/json'
   self.response.out.write(json.dumps({}))

  def post(self):
    new_data = self.request.get('data')
    email = self.request.get('email')

    errors = self.UpdateResponders(new_data, email)
    output = {
      'ok': errors == [],
      'errors': errors,
    };
    self.response.out.write(json.dumps(output))

  def UpdateResponders(self, data, email):
    if not data:
      return []

    try:
      evaled_data = eval(data, {})
    except Exception as e:
      logging.info(data)
      logging.error(e)
      return ['Bad Data']

    for responder_data in evaled_data:
      key = responder_data.get('key')
      if not key:
        continue

      uploaded_data = UploadedResponderInfo.get(key)
      if not uploaded_data:
        logging.error('Invalid key %s' % key)
        continue

      save = False
      url = responder_data.get('url')
      if (uploaded_data.link_url is None and url and url != 'http://'):
        uploaded_data.link_url = url
        save = True

      url = responder_data.get('image')
      if (uploaded_data.image_url is None and url and url != 'http://'):
        uploaded_data.image_url = url
        save = True

      if uploaded_data.email_or_name is None and email:
        uploaded_data.email_or_name = email
        save = True

      if save:
        uploaded_data.put()

    return []


incoming_application = webapp.WSGIApplication(
  [
    ('/incoming/model_data', HandleModelData),
    ('/incoming/update_model_data', UpdateModelData),
  ],
  debug=True)
