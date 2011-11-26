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

import logging
import manufacturer_data
import memcache_keys
import model_data
import os
import pid_data
import product_categories
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import *
from pid_loader import PidLoader


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


class AdminPageHandler(webapp.RequestHandler):
  """Admin functions."""
  def UpdateManufacturers(self):
    new_data = {}
    for id, name in manufacturer_data.MANUFACTURER_DATA:
      new_data[id] = name

    existing_manufacturers = set()
    manufacturers_to_delete = []
    # invalidate the cache now
    memcache.delete(memcache_keys.MANUFACTURER_CACHE_KEY)
    added = removed = updated = 0

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
      logging.info('adding %d (%s)' %
                   (manufacturer_id, new_data[manufacturer_id]))
      manufacturer = Manufacturer(esta_id = manufacturer_id,
                                  name = new_data[manufacturer_id])
      manufacturer.put()
      added += 1

    # remove any extra manufacturers
    for manufacturer in manufacturers_to_delete:
      logging.info('removing %s' % manufacturer.name)
      manufacturer.delete()
      removed += 1
    logging.info('update complete')
    return ('Manufacturers: added %d, removed %d, updated %d' %
            (added, removed, updated))

  def ClearPids(self):
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
    for item in MessageItem.all():
      item.delete()

    for item in Message.all():
      item.delete()

    for item in Command.all():
      item.delete()

    for item in Pid.all():
      item.delete()

    for item in EnumValue.all():
      item.delete()

    for item in AllowedRange.all():
      item.delete()
    return ''

  def LoadPids(self):
    loader = PidLoader()
    added = 0
    for pid in pid_data.ESTA_PIDS:
      loader.AddPid(pid)
      added += 1
    return 'Added %d PIDs' % added

  def LoadManufacturerPids(self):
    loader = PidLoader()
    added = 0
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
    for manufacturer in pid_data.MANUFACTURER_PIDS:
      for pid in manufacturer['pids']:
        loader.AddPid(pid, manufacturer['id'])
        added += 1
    return 'Added %d PIDs' % added

  def ClearModels(self):
    memcache.delete(memcache_keys.DEVICE_MODEL_COUNT_KEY)
    for item in Responder.all():
      item.delete()

    for item in SoftwareVersion.all():
      item.delete()

    for item in ResponderTag.all():
      item.delete()

    for item in ResponderTagRelationship.all():
      item.delete()
    return ''

  def LoadModels(self):
    memcache.delete(memcache_keys.DEVICE_MODEL_COUNT_KEY)
    manufacturers = {}
    added = 0
    def getManufacturer(manufacturer_id):
      if manufacturer_id not in manufacturers:
        manufacturer_q = Manufacturer.all()
        manufacturer_q.filter('esta_id =', manufacturer_id)
        manufacturers[manufacturer_id] = manufacturer_q.fetch(1)[0]
      return manufacturers[manufacturer_id]

    tag_to_entity = {}
    product_categories = {}

    for manufacturer_id, models in model_data.DEVICE_MODEL_DATA.iteritems():
      manufacturer = getManufacturer(manufacturer_id)
      for info in models:
        device = Responder(manufacturer = manufacturer,
                           device_model_id = info['device_model'],
                           model_description = info['model_description'])

        # add product_category if it exists
        if 'product_category' in info:
          category_id = info['product_category']
          category = product_categories.get(category_id)
          if not category:
            category = LookupProductCategory(category_id)
            product_categories[category_id] = category
          if category:
            device.product_category = category

        # add link and image_url if they exist, image data is fetched on demand
        if 'link' in info:
          device.link = info['link']
        if 'image_url' in info:
          device.image_url = info['image_url']

        added += 1
        device.put()

        # add software version information
        software_versions = info.get('software_versions')
        if software_versions:
          for version_id, version_info in software_versions.iteritems():
            # create the new version object and store it
            version_obj = SoftwareVersion(version_id = version_id,
                                          label = version_info['label'],
                                          responder = device)
            supported_params = version_info.get('supported_parameters')
            if supported_params:
              version_obj.supported_parameters = supported_params
            version_obj.put()

          personalities = version_info.get('personalities', [])
          for personality_info in personalities:
            personality = ResponderPersonality(
                description = personality_info['description'],
                index = personality_info['index'],
                slot_count = personality_info['slot_count'],
                sw_version = version_obj)
            personality.put()

          sensors = version_info.get('sensors', [])
          for offset, sensor_info in zip(range(len(sensors)), sensors):
            sensor = ResponderSensor(
                description = sensor_info['description'],
                index = offset,
                type = sensor_info['type'],
                supports_recording = bool(sensor_info['supports_recording']),
                sw_version = version_obj)
            sensor.put()

        # add any tags
        if 'tags' in info:
          for tag_label in info['tags']:
            tag_entity = tag_to_entity.get(tag_label)
            if not tag_entity:
              tag_entity = ResponderTag(label= tag_label)
              tag_entity.put()
              tag_to_entity[tag_label] = tag_entity
              logging.info('added %s -> %s' % (tag_label, tag_entity))
            relationship = ResponderTagRelationship(
                tag = tag_entity,
                responder = device)
            relationship.put()
    return 'Models: added %d' % added


  def UpdateProductCategories(self):
    """Update the list of Product Categories."""
    added = removed = updated = 0
    new_data = {}
    for name, id in product_categories.PRODUCT_CATEGORIES.iteritems():
      new_data[id] = name

    existing_categories = set()
    categories_to_delete = []
    # invalidate the cache now
    memcache.delete(memcache_keys.PRODUCT_CATEGORY_CACHE_KEY)

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
    return ('Categories: added %d, removed %d, updated %d' %
            (added, removed, updated))

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

    if urls:
      return 'Fetching urls: \n%s' % '\n'.join(urls)
    else:
      return 'No images to fetch'

  def get(self):
    ACTIONS = {
        'update_m': self.UpdateManufacturers,
        'clear_p': self.ClearPids,
        'load_p': self.LoadPids,
        'load_mp': self.LoadManufacturerPids,
        'clear_models': self.ClearModels,
        'load_models': self.LoadModels,
        'update_categories': self.UpdateProductCategories,
        'gc_blobs': self.GarbageCollectBlobs,
        'initiate_image_fetch': self.InitiateImageFetch,
    }

    ALLOWED_USERS = [
        'nomis52@gmail.com',
        'simon@nomis52.net',
    ]

    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    if user.email() not in ALLOWED_USERS:
      self.error(403)
      return

    action = self.request.get('action')
    output = ''
    if action in ACTIONS:
      output = ACTIONS[action]()

    template_data = {
        'logout_url': users.create_logout_url("/"),
    }

    if output:
      template_data['output'] = output
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render('templates/admin.tmpl',
                                            template_data))


application = webapp.WSGIApplication(
  [
    ('/admin', AdminPageHandler),
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.INFO)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
