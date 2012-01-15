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
# controller_loader.py
# Copyright (C) 2012 Simon Newton
# Loads controller data

import logging
from model import *


class ControllerLoader(object):
  """Load Controller definition into the datastore."""
  def __init__(self, controller_data):
    self._controller_data = controller_data
    # manufacturer_id to Manufacturer object
    self._manufacturers = {}
    # string to ControllerTag objects
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

  def _LookupOrAddTag(self, tag_label):
    """Lookup a ControllerTag or add it if it doesn't exist.

    Returns:
      The entity object, or None if not found.
    """
    if tag_label not in self._tags:
      query = ControllerTag.all()
      query.filter('label = ', tag_label)
      tags = query.fetch(1)
      if tags:
        self._tags[tag_label] = tags[0]
      else:
        tag_entity = ControllerTag(label=tag_label)
        tag_entity.put()
        self._tags[tag_label] = tag_entity
        logging.info('added %s -> %s' % (tag_label, tag_entity))

    return self._tags[tag_label]

  def _LookupController(self, manufacturer_key, controller_name):
    """Given a manufacturer key and controller name, lookup the Controller
    entity.
    """
    controllers = Controller.all()
    controllers.filter('name = ', controller_name)
    controllers.filter('manufacturer = ', manufacturer_key)

    if controllers.count() > 1:
      logging.error('More than one controller exists for %s and 0x%hx' %
          (controller_name, manufacturer_key.esta_id))
    controller_data = controllers.fetch(1)
    if not controller_data:
      return None
    return controller_data[0]

  def _UpdateController(self, controller, controller_info):
    """Update this controller entity if there is new data.

    Returns:
      True if this entity was updated, false otherwise.
    """
    modified = False

    # update link url
    link_url = controller_info.get('link')
    if link_url is not None and link_url != controller.link:
      controller.link = link_url
      modified = True

    # update image url
    image_url = controller_info.get('image_url')
    if image_url is not None and image_url != controller.image_url:
      controller.image_url = image_url
      controller.image_data = None
      modified = True

    if modified:
      controller.put()
    return modified

  def _AddController(self, manufacturer, controller_info):
    """Add a controller to the data store.

    Args:
      manufacturer:
      controller_info: The dict with the controller information

    Returns:
      The new Controller entity.
    """
    controller = Controller(
        manufacturer = manufacturer,
        name = controller_info['name'])

    # add link and image_url if they exist
    link_url = controller_info.get('link')
    if link_url:
      controller.link = link_url
    image_url = controller_info.get('image_url')
    if image_url:
      controller.image_url = image_url

    controller.put()
    return controller

  def _UpdateTags(self, controller, new_tags):
    """Update the tags for a controller

    Args:
      controller: The Controller entity to update
      new_tags: a list of new tags

    Returns:
      True if the controller was modified, false otherwise.
    """
    new_tags = set(new_tags)
    modified = False

    for relationship in controller.tag_set:
      label = relationship.tag.label
      if label in new_tags:
        new_tags.remove(label)
      else:
        logging.info('Deleting %s from %s' % (label, controller.name))
        relationship.delete()
        modified = True

    for tag_label in new_tags:
      tag_entity = self._LookupOrAddTag(tag_label)
      relationship = ControllerTagRelationship(
          tag = tag_entity,
          controller = controller)
      relationship.put()
      modified = True

    return modified

  def Update(self):
    """Update the datastore with the new data.

    This doesn't remove old controllers since why would we want to do that?

    Returns:
      A tuple in the form (added, updated), with the number of entities added
      or updated.
    """
    added = []
    updated = []

    logging.info( self._controller_data)
    for manufacturer_id, controllers in self._controller_data.iteritems():
      manufacturer = self._LookupManufacturer(manufacturer_id)
      if not manufacturer:
        logging.error('No manufacturer found for %hx' % manufacturer_id)
        continue

      for controller_info in controllers:
        was_added = False
        was_modified = False
        name = controller_info['name']
        controller = self._LookupController(manufacturer.key(), name)
        if controller:
          # update
          if self._UpdateController(controller, controller_info):
            logging.info(' controller changed')
            was_modified = True
        else:
          # add a new one
          controller = self._AddController(manufacturer, controller_info)
          was_added = True

        # add / update any tags
        # we act conservatively here and don't delete unless we get an empty
        # list
        if 'tags' in controller_info:
          if self._UpdateTags(controller, controller_info['tags']):
            was_modified = True

        if was_added:
          added.append(name)
        elif was_modified:
          updated.append(name)

    return added, updated
