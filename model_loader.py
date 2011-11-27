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
# model_loader.py
# Copyright (C) 2011 Simon Newton
# Loads model data

import logging
from model import *


class ModelLoader(object):
  """Load Model definition into the datastore."""
  def __init__(self, model_data):
    self._model_data = model_data
    # manufacturer_id to Manufacturer object
    self._manufacturers = {}
    # category_id to ProductCategory object
    self._product_categories = {}
    # string to ResponderTag object
    self._tags = {}

  def _LookupManufacturer(self, manufacturer_id):
    """Lookup a Manufacturer entity by id.

    Returns:
      The entity object, or None if not found.
    """
    if manufacturer_id not in self._manufacturers:
      query = Manufacturer.all()
      query.filter('esta_id =', manufacturer_id)
      manufacturers = query.fetch(1)
      if manufacturers:
        self._manufacturers[manufacturer_id] = manufacturers[0]
      else:
        self._manufacturers[manufacturer_id] = None
    return self._manufacturers[manufacturer_id]

  def _LookupProductCategory(self, category_id):
    """Lookup a ProductCategory entity by id.

    Returns:
      The entity object, or None if not found.
    """
    if category_id not in self._product_categories:
      query = ProductCategory.all()
      query.filter('id = ', category_id)
      categories = query.fetch(1)
      if categories:
        self._product_categories[category_id] = categories[0]
      else:
        self._product_categories[category_id] = None
    return self._product_categories[category_id]

  def _LookupOrAddTag(self, tag_label):
    """Lookup a ResponderTag or add it if it doesn't exist.

    Returns:
      The entity object, or None if not found.
    """
    if tag_label not in self._tags:
      query = ResponderTag.all()
      query.filter('label = ', tag_label)
      tags = query.fetch(1)
      if tags:
        self._tags[tag_label] = tags[0]
      else:
        tag_entity = ResponderTag(label=tag_label)
        tag_entity.put()
        self._tags[tag_label] = tag_entity
        logging.info('added %s -> %s' % (tag_label, tag_entity))

    return self._tags[tag_label]

  def _LookupResponder(self, manufacturer_key, model_id):
    """Given a manufacturer key and model_id, lookup the Responder entity."""
    models = Responder.all()
    models.filter('device_model_id = ', model_id)
    models.filter('manufacturer = ', manufacturer_key)

    model_data = models.fetch(1)
    if not model_data:
      return None
    return model_data[0]

  def _UpdateResponder(self, responder, model_info):
    """Update this responder entity if there is new data.

    Returns:
      True if this entity was updated, false otherwise.
    """
    modified = False
    model_description = model_info['model_description']
    if model_description != responder.model_description and model_description:
      responder.model_description = model_description
      modified = True

    product_category_id = model_info.get('product_category')
    if product_category_id is not None:
      current_category = responder.product_category
      if not (current_category and product_category_id == current_category.id):
        # requires update
        new_category = self._LookupProductCategory(product_category_id)
        if new_category:
          responder.product_category = new_category
          modified = True
        else:
          logging.info('No product category found for 0x%hx' %
              product_category_id)

    # update link url
    link_url = model_info.get('link')
    if link_url is not None and link_url != responder.link:
      responder.link = link_url
      modified = True

    # update image url
    image_url = model_info.get('image_url')
    if image_url is not None and image_url != responder.image_url:
      responder.image_url = image_url
      responder.image_data = None
      modified = True

    if modified:
      responder.put()
    return modified

  def _AddResponder(self, manufacturer, model_id, model_info):
    """Add a responder to the data store.

    Args:
      manufacturer:
      model_id:
      model_info: The dict with the responder information

    Returns:
      The new Responder entity.
    """
    responder = Responder(
        manufacturer = manufacturer,
        device_model_id = model_id,
        model_description = model_info['model_description'])

    # add product_category if there is one
    product_category_id = model_info.get('product_category')
    if product_category_id is not None:
      category = self._LookupProductCategory(product_category_id)
      if category:
        responder.product_category = category
      else:
        logging.info('No product category found for 0x%hx' %
            product_category_id)

    # add link and image_url if they exist
    link_url = model_info.get('link')
    if link_url:
      responder.link = link_url
    image_url = model_info.get('image_url')
    if image_url:
      responder.image_url = image_url

    responder.put()
    return responder

  def _AddSoftwareVersion(self, responder, version_id, version_info):
    """Add a software version to a responder.

    Args:
      responder: The Responder entity to update
      version_id: the id of the version
      version_info: the dict with the version information
    """
    # create the new version object and store it
    version_obj = SoftwareVersion(version_id = version_id,
                                  label = version_info['label'],
                                  responder = responder)
    supported_params = version_info.get('supported_parameters')
    if supported_params:
      # keep things sorted
      version_obj.supported_parameters = sorted(supported_params)
    version_obj.put()

    personalities = version_info.get('personalities', [])
    self._UpdatePersonalities(version_obj, personalities)

    sensors = version_info.get('sensors', [])
    self._UpdateSensors(version_obj, sensors)


  def _UpdatePersonalities(self, software_version, personalities):
    """Update the personalities for a SoftwareVersion entity.
    """
    modified = False
    new_personalities = {}
    for personality_info in personalities:
      new_personalities[personality_info['index']] = personality_info

    for personality in software_version.personality_set:
      personality_info = new_personalities.get(personality.index)
      if personality_info:
        # check for update
        save = False
        new_description = personality_info.get('description')
        if new_description and personality.description != new_description:
          personality.description = new_description
          save = True

        new_slot_count = personality_info.get('slot_count')
        if (new_slot_count is not None and
            personality.slot_count != new_slot_count):
          personality.slot_count = new_slot_count
          save = True

        if save:
          personality.put()
          modified = True
        del new_personalities[personality.index]

    # add any new personalities
    for index, personality_info in new_personalities.iteritems():
      personality = ResponderPersonality(
          description = personality_info['description'],
          index = index,
          slot_count = personality_info['slot_count'],
          sw_version = software_version)
      personality.put()
      modified = True

    return modified

  def _UpdateSensors(self, software_version, sensors):
    """Update the sensors for a SoftwareVersion entity.
    """
    modified = False
    new_sensors = {}
    for sensor, index in zip(sensors, range(len(sensors))):
      new_sensors[index] = sensor

    for sensor in software_version.sensor_set:
      sensor_info = new_sensors.get(sensor.index)
      if sensor_info:
        # check for update
        save = False
        new_description = sensor_info.get('description')
        if new_description and sensor.description != new_description:
          sensor.description = new_description
          save = True

        new_type = sensor_info.get('type')
        if new_type is not None and sensor.type != new_type:
          sensor.type = new_type
          save = True

        new_supports_recording = sensor_info.get('supports_recording')
        if new_supports_recording is not None:
          new_supports_recording = bool(new_supports_recording)
          if sensor.supports_recording != new_supports_recording:
            sensor.supports_recording = new_supports_recording
            save = True

        if save:
          sensor.put()
          modified = True
        del new_sensors[sensor.index]

    # add new sensors
    for offset, sensor_info in new_sensors.iteritems():
      sensor = ResponderSensor(
          description = sensor_info['description'],
          index = offset,
          type = sensor_info['type'],
          supports_recording = bool(sensor_info['supports_recording']),
          sw_version = software_version)
      sensor.put()
      modified = True

    return modified

  def _UpdateSoftwareVersions(self, responder, versions):
    """Update the software version info for a responder.

    This won't remove previous versions.

    Args:
      responder: The Responder entity to update
      versions: A dict of versions in the form {version_id: version_info}

    Returns:
      True if the responder was modified, false otherwise.
    """
    new_versions = set(versions.keys())
    modified = False

    for version in responder.software_version_set:
      version_id = version.version_id
      if version_id in new_versions:
        new_version_info = versions[version_id]

        # update supported_parameters if required
        new_supported_parameters = new_version_info['supported_parameters']
        supported_parameters = [int(i) for i in version.supported_parameters]
        if sorted(new_supported_parameters) != sorted(supported_parameters):
          version.supported_parameters = sorted(new_supported_parameters)
          version.put()
          modified = True

        # update personalities if required
        personalities = new_version_info.get('personalities')
        if personalities:
          if self._UpdatePersonalities(version, personalities):
            modified = True

        # update sensors if required
        sensors = new_version_info.get('sensors')
        if sensors:
          if self._UpdateSensors(version, sensors):
            modified = True

        new_versions.remove(version_id)

    # add any new versions
    for new_version in new_versions:
      logging.info('Adding %d for %s' %
                   (new_version, responder.model_description))
      self._AddSoftwareVersion(responder, new_version, versions[new_version])
      modified = True

    return modified

  def _UpdateTags(self, responder, new_tags):
    """Update the tags for a responder

    Args:
      responder: The Responder entity to update
      new_tags: a list of new tags

    Returns:
      True if the responder was modified, false otherwise.
    """
    new_tags = set(new_tags)
    modified = False

    for relationship in responder.tag_set:
      label = relationship.tag.label
      if label in new_tags:
        new_tags.remove(label)
      else:
        logging.info('Deleting %s from %s' %
                     (label, responder.model_description))
        relationship.delete()
        modified = True

    for tag_label in new_tags:
      tag_entity = self._LookupOrAddTag(tag_label)
      relationship = ResponderTagRelationship(
          tag = tag_entity,
          responder = responder)
      relationship.put()
      modified = True

    return modified

  def Update(self):
    """Update the datastore with the new data.

    This doesn't remove old models since why would we want to do that?

    Returns:
      A tuple in the form (added, updated), with the number of entities added
      or updated.
    """
    added = []
    updated = []

    for manufacturer_id, models in self._model_data.iteritems():
      manufacturer = self._LookupManufacturer(manufacturer_id)
      if not manufacturer:
        logging.error('No manufacturer found for %hx' % manufacturer_id)
        continue

      for model_info in models:
        was_added = False
        was_modified = False
        model_id = model_info['device_model']
        responder = self._LookupResponder(manufacturer.key(), model_id)
        if responder:
          # update
          if self._UpdateResponder(responder, model_info):
            logging.info(' responder changed')
            was_modified = True
        else:
          # add a new one
          responder = self._AddResponder(manufacturer, model_id, model_info)
          was_added = True

        # add software version information
        software_versions = model_info.get('software_versions')
        if software_versions:
          if self._UpdateSoftwareVersions(responder, software_versions):
            logging.info('updated versions for %s' %
                responder.model_description)
            was_modified = True

        # add / update any tags
        # we act conservatively here and don't delete unless we get an empty
        # list
        if 'tags' in model_info:
          if self._UpdateTags(responder, model_info['tags']):
            logging.info(' tag changed')
            was_modified = True

        if was_added:
          added.append(model_info['model_description'])
        elif was_modified:
          updated.append(model_info['model_description'])

    return added, updated
