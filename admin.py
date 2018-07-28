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

import common
from common import BasePageHandler
from data.controller_data import CONTROLLER_DATA
from data.manufacturer_data import MANUFACTURER_DATA
from data.manufacturer_links import MANUFACTURER_LINKS
from data.model_data import DEVICE_MODEL_DATA
from data.node_data import NODE_DATA
from data.pid_data import ESTA_PIDS, MANUFACTURER_PIDS
from data.product_categories import PRODUCT_CATEGORIES
from data.software_data import SOFTWARE_DATA
from data.splitter_data import SPLITTER_DATA
import datetime
import html_differ
import logging
import memcache_keys
import model_loader
import product_loader
import timestamp_keys
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.db import BadValueError
from google.appengine.ext.webapp import template
from model import *
from utils import StringToInt
from pid_loader import PidLoader


def UpdateModificationTime(timestamp_name):
  """Update a particular timestamp."""
  query = LastUpdateTime.all()
  query.filter('name = ', timestamp_name)
  result = query.fetch(1)
  if not result:
    result = LastUpdateTime(name=timestamp_name)
  else:
    result = result[0]
  result.update_time = datetime.datetime.now()
  result.put()

  # delete the index info cache
  memcache.delete(memcache_keys.INDEX_INFO)


class BaseAdminPageHandler(BasePageHandler):
  """The base handler for admin requests."""
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


class AdminPageHandler(BaseAdminPageHandler):
  """Admin functions."""
  def UpdateManufacturers(self):
    new_data = {}
    for id, name in MANUFACTURER_DATA:
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
      manufacturer = Manufacturer(esta_id=manufacturer_id,
                                  name=manufacturer_name)
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

  def UpdateManufacturerLinks(self):
    # TODO(Peter): Add ability to remove links if not present in data?
    new_data = {}
    for id, name in MANUFACTURER_LINKS:
      new_data[id] = name

    present_manufacturers = set()
    # invalidate the cache now
    memcache.delete(memcache_keys.MANUFACTURER_CACHE_KEY)
    added = updated = missing = errors = 0

    for manufacturer in Manufacturer.all():
      id = manufacturer.esta_id
      if id in new_data:
        present_manufacturers.add(id)
        new_link = new_data[id]
        if not(manufacturer.link) or (new_link != manufacturer.link):
          try:
            # add/update if required
            manufacturer.link = new_link
            manufacturer.put()
            if manufacturer.link:
              logging.info('Updating link for %d (%s) %s -> %s' %
                           (id, manufacturer.name, manufacturer.link, new_link))
              updated += 1
            else:
              logging.info('Adding link for %d (%s) - %s' %
                           (id, manufacturer.name, new_link))
              added += 1
          except BadValueError as e:
            logging.error('Failed to add link for 0x%hx (%s) - %s: %s' %
                          (id, manufacturer.name, new_link, e))
            errors += 1
            continue

    # link no manufacturer
    missing_manufacturers = set(new_data.keys()) - present_manufacturers
    for manufacturer_id in sorted(missing_manufacturers):
      logging.error('Failed to add link for 0x%hx as manufacturer missing: %s' %
                    (manufacturer_id, new_data[manufacturer_id]))
      missing += 1

    logging.info('update complete')
    UpdateModificationTime(timestamp_keys.MANUFACTURERS)
    return ('Manufacturer links: added %d, updated %d, missing %d, errors %d' %
            (added, updated, missing, errors))

  def ClearPids(self):
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
    memcache.delete(memcache_keys.MANUFACTURER_PID_COUNTS)
    for item in Command.all():
      item.delete()

    for item in Pid.all():
      item.delete()
    return ''

  def ClearManufacturerPids(self):
    manufacturer_id = StringToInt(self.request.get('manufacturer'))
    manufacturer = common.GetManufacturer(manufacturer_id)

    count = 0
    if manufacturer is not None:
      memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
      memcache.delete(memcache_keys.MANUFACTURER_PID_COUNTS)

      for pid in manufacturer.pid_set:
        if pid.discovery_command:
          pid.discovery_command.delete()
        if pid.get_command:
          pid.get_command.delete()
        if pid.set_command:
          pid.set_command.delete()
        pid.delete()
        count += 1
    return 'Deleted %d PIDs' % count

  def FlushCache(self):
    keys = [
        memcache_keys.PRODUCT_COUNT_KEY,
        memcache_keys.MANUFACTURER_MODEL_COUNTS,
        memcache_keys.CATEGORY_MODEL_COUNTS,
        memcache_keys.TAG_MODEL_COUNTS,
        memcache_keys.INDEX_INFO
    ]
    for key in keys:
      memcache.delete(key)
    return ''

  def LoadPids(self):
    loader = PidLoader()
    modified = 0
    for pid in ESTA_PIDS:
      if loader.UpdateIfRequired(pid):
        modified += 1

    if modified > 0:
      UpdateModificationTime(timestamp_keys.PIDS)
      memcache.delete(memcache_keys.MANUFACTURER_PID_COUNTS)

    return 'Added / Updated %d PIDs' % modified

  def BuildResponderPidIndex(self):
    task = taskqueue.Task(method='GET', url='/tasks/build_pid_responder_index')
    task.add()

  def RankDevices(self):
    task = taskqueue.Task(method='GET', url='/tasks/rank_devices')
    task.add()

  def LoadManufacturerPids(self):
    loader = PidLoader()
    modified = 0
    for manufacturer in MANUFACTURER_PIDS:
      for pid in manufacturer['pids']:
        if loader.UpdateIfRequired(pid, manufacturer['id']):
          modified += 1

    if modified > 0:
      UpdateModificationTime(timestamp_keys.PIDS)
      memcache.delete(memcache_keys.MANUFACTURER_PID_COUNT_KEY)
      memcache.delete(memcache_keys.MANUFACTURER_PID_COUNTS)

    return 'Modified %d PIDs' % modified

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
    loader = model_loader.ModelLoader(DEVICE_MODEL_DATA)
    added, updated = loader.Update()
    if added or updated:
      memcache.delete(memcache_keys.INDEX_INFO)
      memcache.delete(memcache_keys.PRODUCT_COUNT_KEY)
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
    for name, id in PRODUCT_CATEGORIES:
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
      category = ProductCategory(id=category_id,
                                 name=new_data[category_id])
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

    deleted_product_tags = []
    for tag in ProductTag.all():
      products = tag.product_set.fetch(1)
      if products == []:
        deleted_product_tags.append(tag.label)
        tag.delete()

    output = ''
    if deleted_responder_tags:
      output += ('Deleted Responder tags: \n%s\n' %
                 '\n'.join(deleted_responder_tags))
    if deleted_product_tags:
      output += ('Deleted Product tags: \n%s\n' %
                 '\n'.join(deleted_product_tags))

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

    for product in Product.all():
      image_blob = product.image_data
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

    for product in Product.all():
      if product.image_url and not product.image_data:
        url = '/tasks/fetch_product_image?key=%s' % product.key()
        task = taskqueue.Task(method='GET', url=url)
        task.add()
        urls.append(product.image_url)

    if urls:
      return 'Fetching urls: \n%s' % '\n'.join(urls)
    else:
      return 'No images to fetch'

  def ClearProductType(self, product_class):
    """Delete all instances of a product class."""
    for splitter in product_class.all():
      for tag in splitter.tag_set:
        tag.delete()
      splitter.delete()
    return ''

  def LoadProductType(self, data, product_type, memcache_keys, timestamp_key):
    """Load products from data.

    Args:
      data: The data to load
      product_type: the subclass to use
      memcache_keys: a list of keys to invalidate after loading
      timestamp_key: a timestamp key to update.
    """
    loader = product_loader.ProductLoader(data, product_type)
    added, updated = loader.Update()
    if added or updated:
       for key in memcache_keys:
         memcache.delete(key)

    UpdateModificationTime(timestamp_key)
    return ('Products:\nAdded: %s\nUpdated: %s' %
            (', '.join(added), ', '.join(updated)))

  def ClearControllers(self):
    return self.ClearProductType(Controller)

  def UpdateControllers(self):
    return self.LoadProductType(
        CONTROLLER_DATA,
        Controller,
        [memcache_keys.MANUFACTURER_CONTROLLER_COUNTS,
         memcache_keys.TAG_CONTROLLER_COUNTS],
        timestamp_keys.CONTROLLERS)

  def ClearNodes(self):
    return self.ClearProductType(Node)

  def UpdateNodes(self):
    return self.LoadProductType(
        NODE_DATA,
        Node,
        [memcache_keys.MANUFACTURER_NODE_COUNTS,
         memcache_keys.TAG_NODE_COUNTS],
        timestamp_keys.NODES)

  def ClearSplitters(self):
    return self.ClearProductType(Splitter)

  def UpdateSplitters(self):
    return self.LoadProductType(
        SPLITTER_DATA,
        Splitter,
        [memcache_keys.MANUFACTURER_SPLITTER_COUNTS,
         memcache_keys.TAG_SPLITTER_COUNTS],
        timestamp_keys.SPLITTERS)

  def ClearSoftware(self):
    return self.ClearProductType(Software)

  def UpdateSoftware(self):
    return self.LoadProductType(
        SOFTWARE_DATA,
        Software,
        [memcache_keys.MANUFACTURER_SOFTWARE_COUNTS,
         memcache_keys.TAG_SOFTWARE_COUNTS],
        timestamp_keys.SOFTWARE)

  def HandleRequest(self):
    ACTIONS = {
        'clear_controllers': self.ClearControllers,
        'clear_models': self.ClearModels,
        'clear_nodes': self.ClearNodes,
        'clear_p': self.ClearPids,
        'clear_mp': self.ClearManufacturerPids,
        'clear_software': self.ClearSoftware,
        'clear_splitters': self.ClearSplitters,
        'flush_cache': self.FlushCache,
        'gc_blobs': self.GarbageCollectBlobs,
        'gc_tags': self.GarbageCollectTags,
        'initiate_image_fetch': self.InitiateImageFetch,
        'load_mp': self.LoadManufacturerPids,
        'load_p': self.LoadPids,
        'rank_devices': self.RankDevices,
        'responder_pid_index': self.BuildResponderPidIndex,
        'update_categories': self.UpdateProductCategories,
        'update_controllers': self.UpdateControllers,
        'update_m': self.UpdateManufacturers,
        'update_m_links': self.UpdateManufacturerLinks,
        'update_models': self.UpdateModels,
        'update_nodes': self.UpdateNodes,
        'update_software': self.UpdateSoftware,
        'update_splitters': self.UpdateSplitters,
    }

    action = self.request.get('action')
    output = ''
    if action in ACTIONS:
      output = ACTIONS[action]()

    pending_uploads = UploadedResponderInfo.all().filter('processed = ',
                                                         False).count()
    template_data = self.IndexInfo()
    template_data['logout_url'] = users.create_logout_url("/")
    template_data['responders_to_moderate'] = pending_uploads

    if output:
      template_data['output'] = output
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render('templates/admin.tmpl',
                                            template_data))


class ResponderModerator(BaseAdminPageHandler):
  """Displays the UI for moderating responder data."""
  def EvalData(self, data):
    try:
      evaled_data = eval(data, {})
      return evaled_data
    except Exception as e:
      logging.info(data)
      logging.error(e)
      return {}

  def ApplyChanges(self, key, fields):
    responder_info = UploadedResponderInfo.get(key)
    if not responder_info:
      return 'Invalid key'
    logging.info(responder_info)

    fields_to_update = set(fields.split(','))
    logging.info(fields_to_update)
    data_dict = self.EvalData(responder_info.info)

    # same format as in data/model_data.py
    model_data = {
      'device_model': responder_info.device_model_id
    }

    if ('model_description' in fields_to_update and
        'model_description' in data_dict):
      model_data['model_description'] = data_dict['model_description']
    if 'image_url' in fields_to_update and responder_info.image_url:
      model_data['image_url'] = responder_info.image_url
    if 'url' in fields_to_update and responder_info.link_url:
      model_data['link'] = responder_info.link_url
    if ('product_category' in fields_to_update and
        'product_category' in data_dict):
      model_data['product_category'] = data_dict['product_category']

    if 'software_versions' in data_dict:
      for version_id, version_data in data_dict['software_versions'].iteritems():
        if type(version_id) in (int, long):
          version_dict = self.BuildVersionDict(version_id, version_data,
                                               fields_to_update)
          if version_dict:
            versions = model_data.setdefault('software_versions', {})
            versions[version_id] = version_dict

    logging.info(model_data)

    manufacturer = common.GetManufacturer(responder_info.manufacturer_id)
    if manufacturer is None:
      return 'Invalid manufacturer_id %d' % responder_info.manufacturer_id

    updater = model_loader.ModelUpdater()
    was_added, was_changed = updater.UpdateResponder(manufacturer, model_data)
    logging.info('Was added %s' % was_added)
    logging.info('Was changed %s' % was_changed)

    # finally mark this one as done
    responder_info.processed = True
    responder_info.put()
    return ''

  def BuildVersionDict(self, version_id, version_data, fields_to_update):
    version_dict = {}

    # sort supported params just in case
    if 'supported_parameters' in version_data:
      version_data['supported_parameters'].sort()
    logging.info(version_data)

    fields = ['label', 'personalities', 'sensors', 'supported_parameters']
    for field in fields:
      if (('%d_%s' % (version_id, field)) in fields_to_update and
          field in version_data):
        version_dict[field] = version_data[field]
    return version_dict

  def HandleRequest(self):
    template_data = {
      'logout_url': users.create_logout_url("/"),
    }

    # this is a bit of a hack
    self._differ = html_differ.HTMLDiffer('left', 'right')

    key = self.request.get('key')
    fields = self.request.get('fields')
    if key and fields is not None:
      error = self.ApplyChanges(key, fields)
      if error:
        template_data.setdefault('errors', []).append(error)

    query = UploadedResponderInfo.all()
    query.filter('processed = ', False)
    responder = query.fetch(1)
    if responder:
      template_data['key'] = responder[0].key()
      self.DiffResponder(responder[0], template_data)

    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(
      'templates/admin-moderate-responder.tmpl',
      template_data))

  def DiffProperty(self, name, key, left_dict, right_dict):
    """
    Args:
      name: The human name of this property
      key: the key by which to look up this property in both dicts.
      left_dict:
      right_dict:

    Returns:
      A dict in the form {

      }
    """
    left = left_dict.get(key)
    right = right_dict.get(key)
    if left and right:
      left_formatted, right_formatted = self._differ.Diff(str(left), str(right))
    else:
      left_formatted = left
      right_formatted = right
    return {
      'name': name,
      'key': key,
      'left': left_formatted,
      'different': left != right,
      'prefer_left': left is not None and right is None,
      'prefer_right': right is not None and left is None,
      'right': right_formatted,
    }

  def DiffProperties(self, fields, left_dict, right_dict):
    """

    Returns:
      changed_fields, unchanged_fields
    """
    changed_fields = []
    unchanged_fields = []
    for name, key in fields:
      field_dict = self.DiffProperty(name, key, left_dict, right_dict)
      if field_dict['different']:
        changed_fields.append(field_dict)
      else:
        unchanged_fields.append(field_dict)
    return changed_fields, unchanged_fields

  def DiffResponder(self, responder, template_data):
    errors = []

    template_data['device_id'] = responder.device_model_id
    template_data['manufacturer_id'] = responder.manufacturer_id

    if responder.email_or_name:
      template_data['contact'] = responder.email_or_name

    manufacturer = common.GetManufacturer(responder.manufacturer_id)
    template_data['manufacturer'] = manufacturer
    if not manufacturer:
      return

    template_data['manufacturer_name'] = manufacturer.name
    existing_model = common.LookupModel(responder.manufacturer_id,
                                        responder.device_model_id)

    # build a dict for the existing responder
    existing_responder_dict = {}
    if existing_model is not None:
      existing_responder_dict = {
          'model_description': existing_model.model_description,
          'image_url': existing_model.image_url,
          'url': existing_model.link,
      }
      category = existing_model.product_category
      if category:
        existing_responder_dict['product_category'] = category.name

    # Build a dict for the new responder
    new_responder_dict = self.EvalData(responder.info)
    new_responder_dict['image_url'] = responder.image_url or None
    new_responder_dict['url'] = responder.link_url or None
    if 'product_category' in new_responder_dict:
      category = common.LookupProductCategory(
          new_responder_dict['product_category'])
      if category:
        new_responder_dict['product_category'] = category.name
      else:
        errors.append('Unknown product category %d' %
                      new_responder_dict['product_category'])

    fields = [
        ('Model Description', 'model_description'),
        ('Image URL', 'image_url'),
        ('URL', 'url'),
        ('Product Category', 'product_category'),
    ]

    changed_fields, unchanged_fields = self.DiffProperties(
        fields, new_responder_dict, existing_responder_dict)

    template_data['changed_fields'] = changed_fields
    template_data['unchanged_fields'] = unchanged_fields

    # populate the model_description
    template_data['model_description'] = new_responder_dict.get(
        'model_description')
    if existing_model:
      template_data['model_description'] = existing_model.model_description

    # now work on the software versions
    new_software_versions = new_responder_dict.get('software_versions', {})
    if new_software_versions:
      versions = self.DiffVersions(new_software_versions, existing_model)
      template_data['versions'] = versions

    template_data.setdefault('errors', []).extend(errors)

  def DiffVersions(self, new_software_versions, existing_responder):
    """

    Args:
      new_software_versions: a dict of version_id : dict mappings
      existing_responder: A Responder Entity, or None

    Returns:
      [{
        'version': <int>'
        'fields': [ <fields> ],
      },
      ]
    """
    known_versions = {}  # version_id : SoftwareVersion mapping
    if existing_responder:
      for known_version in existing_responder.software_version_set:
        known_versions[known_version.version_id] = known_version

    output = []

    for version_id, data in new_software_versions.iteritems():
      if type(version_id) in (int, long):
        fields = self.DiffVersion(version_id, data,
                                  known_versions.get(version_id))
        if fields:
          output.append({
            'version': version_id,
            'fields': fields,
          })
      else:
        logging.error('Invalid version id %s' % version_id)
    return output

  def DiffVersion(self, version_id, new_data, current_version):
    """

    Args:
      version_id: The software version
      new_data: The dict of new data
      existing_version: A SoftwareVersion Entity or None
    """
    current_version_dict = {
      'personalities': self.BuildPersonalityList(current_version),
      'sensors': self.BuildSensorList(current_version),
    }
    if current_version:
      current_version_dict['label'] = current_version.label
      # we need to convert to int
      current_version_dict['supported_parameters'] = sorted(
          int(i) for i in current_version.supported_parameters)

    # sort supported params just in case
    if 'supported_parameters' in new_data:
      new_data['supported_parameters'].sort()

    fields = [
        ('Software Label', 'label'),
        ('Supported Parameters', 'supported_parameters'),
        ('Personalities', 'personalities'),
        ('Sensors', 'sensors'),
    ]

    changed_fields, unchanged_fields = self.DiffProperties(
        fields, new_data, current_version_dict)
    return changed_fields

  def BuildPersonalityList(self, software_version):
    if software_version is None:
      return None

    personalities = []
    for personality in software_version.personality_set:
      data = {
        'index': int(personality.index),
      }
      if personality.slot_count is not None:
        data['slot_count'] = int(personality.slot_count)
      if personality.description is not None:
        data['description'] = str(personality.description)
      personalities.append(data)
    personalities.sort(key=lambda i: i['index'])
    return personalities

  def BuildSensorList(self, software_version):
    if software_version is None:
      return None

    sensors = []
    for sensor in software_version.sensor_set:
      recording = 0
      if sensor.supports_recording:
        recording |= 1
      if sensor.supports_min_max_recording:
        recording |= 2

      sensors.append({
        'description': str(sensor.description),
        'index': int(sensor.index),
        'supports_recording': recording,
        'type': int(sensor.type),
      })
    sensors.sort(key=lambda i: i['index'])
    return sensors


class AdjustTestScore(BaseAdminPageHandler):
  """Displays the UI for adjusting a responder's test score.
    TODO(simon): automate all of this.
  """
  def HandleRequest(self):
    template_data = {
      'logout_url': users.create_logout_url("/"),
      'message': '',
    }

    responder = common.LookupModelFromRequest(self.request)
    rating = self.request.get('rating')
    if responder is not None and rating is not None:
      rating_int = StringToInt(rating, False)
      if rating_int >= 0 and rating_int <= 100:
        template_data['message'] = (
            'Set rating of %s to %d' %
            (responder.model_description, rating_int))
        responder.rdm_responder_rating = db.Rating(rating_int)
        responder.put()

    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(
      'templates/admin-adjust-test-score.tmpl',
      template_data))


app = webapp.WSGIApplication(
  [
    ('/admin', AdminPageHandler),
    ('/admin/moderate_responder_data', ResponderModerator),
    ('/admin/adjust_test_score', AdjustTestScore),
  ],
  debug=True)
