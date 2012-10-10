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
# admin.py
# Copyright (C) 2011 Simon Newton
# The handlers for the admin page.

import controller_data
import controller_loader
import datetime
import logging
import manufacturer_data
import memcache_keys
import model_data
import model_loader
import pid_data
import product_categories
import timestamp_keys
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import template
from model import *
from pid_loader import PidLoader


def UpdateModificationTime(timestamp_name):
  """Update a particular timestamp."""
  query = LastUpdateTime.all()
  query.filter('name = ', timestamp_name)
  result = query.fetch(1)
  if not result:
    result = LastUpdateTime(name = timestamp_name)
  else:
    result = result[0]
  result.update_time = datetime.datetime.now()
  result.put()

  # delete the index info cache
  memcache.delete(memcache_keys.INDEX_INFO)


def LookupProductCategory(id_str):
  """Lookup a ProductCategory entity by id.

  Returns:
    The entity object, or None if not found.
  """
  try:
    id = int(id_str)
  except ValueError:
    return None

  query = ProductCategory.all()
  query.filter('id = ', id)
  for category in query.fetch(1):
    return category
  return None


class BaseAdminPageHandler(webapp.RequestHandler):
  """The base handler for admin requests."""
  ALLOWED_USERS = [
      'nomis52@gmail.com',
      'simon@nomis52.net',
  ]

  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    if user.email() not in self.ALLOWED_USERS:
      self.error(403)
      return

    self.HandleRequest()


class AdminPageHandler(BaseAdminPageHandler):
  """Admin functions."""
  def UpdateManufacturers(self):
    new_data = {}
    for id, name in manufacturer_data.MANUFACTURER_DATA:
      new_data[id] = name

    existing_manufacturers = set()
    manufacturers_to_delete = []
    # invalidate the cache now
    memcache.delete(memcache_keys.MANUFACTURER_CACHE_KEY)
    memcache.delete(memcache_keys.MANUFACTURER_MODEL_COUNTS)
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
    added = removed = updated = errors = 0

    for manufacturer in Manufacturer.all():
      id = manufacturer.esta_id
      if id in new_data:
        existing_manufacturers.add(id)
        # update if required
        new_name = new_data[id]
        if new_name != manufacturer.name:
          logging.info('Updating %s -> %s' % (manufacturer.name, new_name))
          manufacturer.name = new_name
          manufacturer.put()
          updated += 1
      else:
        manufacturers_to_delete.append(manufacturer)

    # add any new manufacturers
    manufacturers_to_add = set(new_data.keys()) - existing_manufacturers
    for manufacturer_id in sorted(manufacturers_to_add):
      try:
        manufacturer_name = new_data[manufacturer_id].decode()
      except UnicodeDecodeError as e:
        logging.error('Failed to add 0x%hx: %s' % (manufacturer_id, e))
        errors += 1
        continue

      logging.info('adding %d (%s)' % (manufacturer_id, manufacturer_name))
      manufacturer = Manufacturer(esta_id = manufacturer_id,
                                  name = manufacturer_name)
      manufacturer.put()
      added += 1

    # remove any extra manufacturers
    for manufacturer in manufacturers_to_delete:
      logging.info('removing %s' % manufacturer.name)
      manufacturer.delete()
      removed += 1
    logging.info('update complete')
    UpdateModificationTime(timestamp_keys.MANUFACTURERS)
    return ('Manufacturers: added %d, removed %d, updated %d, errors %d' %
            (added, removed, updated, errors))

  def ClearPids(self):
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNTS)
    for item in Command.all():
      item.delete()

    for item in Pid.all():
      item.delete()
    return ''

  def LoadPids(self):
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNTS)
    loader = PidLoader()
    added = 0
    for pid in pid_data.ESTA_PIDS:
      loader.AddPid(pid)
      added += 1
    UpdateModificationTime(timestamp_keys.PIDS)
    return 'Added %d PIDs' % added

  def RankDevices(self):
    task = taskqueue.Task(method='GET', url='/tasks/rank_devices')
    task.add()

  def LoadManufacturerPids(self):
    loader = PidLoader()
    added = 0
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNTS)
    for manufacturer in pid_data.MANUFACTURER_PIDS:
      for pid in manufacturer['pids']:
        loader.AddPid(pid, manufacturer['id'])
        added += 1
    UpdateModificationTime(timestamp_keys.PIDS)
    return 'Added %d PIDs' % added

  def ClearModels(self):
    memcache.delete(memcache_keys.MODEL_COUNT_KEY)
    for item in Responder.all():
      item.delete()

    for item in SoftwareVersion.all():
      item.delete()

    for item in ResponderTag.all():
      item.delete()

    for item in ResponderTagRelationship.all():
      item.delete()
    return ''

  def UpdateModels(self):
    loader = model_loader.ModelLoader(model_data.DEVICE_MODEL_DATA)
    added, updated = loader.Update()
    if added or updated:
      memcache.delete(memcache_keys.INDEX_INFO)
      memcache.delete(memcache_keys.MODEL_COUNT_KEY)
      memcache.delete(memcache_keys.MANUFACTURER_MODEL_COUNTS)
      memcache.delete(memcache_keys.CATEGORY_MODEL_COUNTS)
      memcache.delete(memcache_keys.TAG_MODEL_COUNTS)

    UpdateModificationTime(timestamp_keys.DEVICES)
    return ('Models:\nAdded: %s\nUpdated: %s' %
            (', '.join(added), ', '.join(updated)))

  def UpdateProductCategories(self):
    """Update the list of Product Categories."""
    added = removed = updated = 0
    new_data = {}
    for name, id in product_categories.PRODUCT_CATEGORIES.iteritems():
      new_data[id] = name

    existing_categories = set()
    categories_to_delete = []

    for category in ProductCategory.all():
      id = category.id
      if id in new_data:
        existing_categories.add(id)
        # update if required
        new_name = new_data[id]
        if new_name != category.name:
          logging.info('Updating %s -> %s' % (category.name, new_name))
          category.name = new_name
          category.put()
          updated += 1
      else:
        categories_to_delete.append(category)

    # add any new categories
    categories_to_add = set(new_data.keys()) - existing_categories
    for category_id in sorted(categories_to_add):
      logging.info('adding %d (%s)' %
                   (category_id, new_data[category_id]))
      category = ProductCategory(id = category_id,
                                 name = new_data[category_id])
      category.put()
      added += 1

    # remove any extra categories
    for category in categories_to_delete:
      logging.info('removing %s' % category.name)
      category.delete()
      removed += 1
    logging.info('update complete')
    return ('categories: added %d, removed %d, updated %d' %
            (added, removed, updated))

  def GarbageCollectTags(self):
    """Delete any tags that don't have Responders linked to them."""
    deleted_responder_tags = []
    for tag in ResponderTag.all():
      responders = tag.responder_set.fetch(1)
      if responders == []:
        deleted_responder_tags.append(tag.label)
        tag.delete()

    deleted_controller_tags = []
    for tag in ControllerTag.all():
      controllers = tag.controller_set.fetch(1)
      if controllers == []:
        deleted_controller_tags.append(tag.label)
        tag.delete()

    output = ''
    if deleted_responder_tags:
      output += ('Deleted Responder tags: \n%s\n' %
          '\n'.join(deleted_responder_tags))
    if deleted_controller_tags:
      output += ('Deleted Controller tags: \n%s\n' %
          '\n'.join(deleted_controller_tags))

    if output == '':
      output = 'No tags to delete'
    return output

  def GarbageCollectBlobs(self):
    keys_to_blobs = {}
    for blob in BlobInfo.all():
      keys_to_blobs[blob.key()] = blob

    for responder in Responder.all():
      image_blob = responder.image_data
      if image_blob:
        key = image_blob.key()
        if key in keys_to_blobs:
          del keys_to_blobs[key]

    for controller in Controller.all():
      image_blob = controller.image_data
      if image_blob:
        key = image_blob.key()
        if key in keys_to_blobs:
          del keys_to_blobs[key]

    for key, blob_info in keys_to_blobs.iteritems():
      logging.info('deleting %s' % key)
      blob_info.delete()

    if keys_to_blobs:
      return 'Deleted blobs: \n%s' % '\n'.join(str(k) for k in keys_to_blobs)
    else:
      return 'No blobs to delete'

  def InitiateImageFetch(self):
    """Add /fetch_image tasks for all responders missing image data."""
    urls = []
    for responder in Responder.all():
      if responder.image_url and not responder.image_data:
        url = '/tasks/fetch_image?key=%s' % responder.key()
        task = taskqueue.Task(method='GET', url=url)
        task.add()
        urls.append(responder.image_url)

    for controller in Controller.all():
      if controller.image_url and not controller.image_data:
        url = '/tasks/fetch_controller_image?key=%s' % controller.key()
        task = taskqueue.Task(method='GET', url=url)
        task.add()
        urls.append(controller.image_url)

    if urls:
      return 'Fetching urls: \n%s' % '\n'.join(urls)
    else:
      return 'No images to fetch'

  def ClearControllers(self):
    for item in Controller.all():
      item.delete()

    for item in ControllerTag.all():
      item.delete()

    for item in ControllerTagRelationship.all():
      item.delete()
    return ''

  def UpdateControllers(self):
    loader = controller_loader.ControllerLoader(
        controller_data.CONTROLLER_DATA)
    added, updated = loader.Update()
    if added or updated:
      memcache.delete(memcache_keys.MANUFACTURER_CONTROLLER_COUNTS)
      memcache.delete(memcache_keys.TAG_CONTROLLER_COUNTS)
      pass

    UpdateModificationTime(timestamp_keys.CONTROLLERS)
    return ('Controllers:\nAdded: %s\nUpdated: %s' %
            (', '.join(added), ', '.join(updated)))

  def HandleRequest(self):
    ACTIONS = {
        'clear_controllers': self.ClearControllers,
        'clear_models': self.ClearModels,
        'clear_p': self.ClearPids,
        'gc_blobs': self.GarbageCollectBlobs,
        'gc_tags': self.GarbageCollectTags,
        'initiate_image_fetch': self.InitiateImageFetch,
        'load_mp': self.LoadManufacturerPids,
        'load_p': self.LoadPids,
        'rank_devices': self.RankDevices,
        'update_categories': self.UpdateProductCategories,
        'update_m': self.UpdateManufacturers,
        'update_models': self.UpdateModels,
        'update_controllers': self.UpdateControllers,
    }

    action = self.request.get('action')
    output = ''
    if action in ACTIONS:
      output = ACTIONS[action]()

    template_data = {
        'logout_url': users.create_logout_url("/"),
        'responders_to_moderate': UploadedResponderInfo.all().count(),
    }

    if output:
      template_data['output'] = output
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render('templates/admin.tmpl',
                                            template_data))


class ResponderModerator(BaseAdminPageHandler):
  """Displays the UI for moderating responder data."""
  def HandleRequest(self):
    template_data = {
        'logout_url': users.create_logout_url("/"),
    }

    responder = UploadedResponderInfo.all().fetch(1)
    if (responder):
      self.DiffResponders(responder[0], template_data)

    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(
      'templates/admin-moderate-responder.tmpl',
      template_data))

  def DiffResponders(self, responder, template_data):
    template_data['manufacturer_id'] = responder.manufacturer_id
    template_data['device_id'] = responder.device_model_id

    manufacturer_query = Manufacturer.all().filter('esta_id = ', responder.manufacturer_id)
    results = manufacturer_query.fetch(1)

    if results:
      template_data['manufacturer_name'] = results[0].name

    return {}, {}


admin_application = webapp.WSGIApplication(
  [
    ('/admin', AdminPageHandler),
    ('/admin/moderate_responder_data', ResponderModerator),
  ],
  debug=True)
