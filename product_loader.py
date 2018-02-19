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
# product_loader.py
# Copyright (C) 2012 Simon Newton
# Loads product data

import common
import logging
from model import *


class ProductLoader(object):
  """Load Product definition into the datastore."""
  def __init__(self, data, product_type):
    self._product_data = data
    self._product_type = product_type
    # manufacturer_id to Manufacturer object
    self._manufacturers = {}
    # string to ProductTag objects
    self._tags = {}

  def _LookupManufacturer(self, manufacturer_id):
    """Lookup a Manufacturer entity by id and cache the result.

    Returns:
      The entity object, or None if not found.
    """
    if manufacturer_id not in self._manufacturers:
      self._manufacturers[manufacturer_id] = common.GetManufacturer(
          manufacturer_id)
    return self._manufacturers[manufacturer_id]

  def _LookupOrAddTag(self, tag_label):
    """Lookup a ProductTag or add it if it doesn't exist.

    Returns:
      The entity object, or None if not found.
    """
    if tag_label not in self._tags:
      query = ProductTag.all()
      query.filter('label = ', tag_label)
      query.filter('product_type = ', self._product_type.class_name())
      tags = query.fetch(1)
      if tags:
        self._tags[tag_label] = tags[0]
      else:
        tag_entity = ProductTag(label=tag_label,
                                product_type=self._product_type.class_name())
        tag_entity.put()
        self._tags[tag_label] = tag_entity
        logging.info('added %s -> %s' % (tag_label, tag_entity))

    return self._tags[tag_label]

  def _LookupProduct(self, manufacturer_key, product_name):
    """Given a manufacturer key and product name, lookup the Product.
    """
    products = self._product_type.all()
    products.filter('name = ', product_name)
    products.filter('manufacturer = ', manufacturer_key)

    if products.count() > 1:
      logging.error('More than one product exists for %s and 0x%hx' %
                    (product_name, manufacturer_key.esta_id))
    product_data = products.fetch(1)
    if not product_data:
      return None
    return product_data[0]

  def _UpdateProduct(self, product, product_info):
    """Update this product entity if there is new data.

    Returns:
      True if this entity was updated, false otherwise.
    """
    modified = False

    # update link url
    link_url = product_info.get('link')
    if link_url is not None and link_url != product.link:
      product.link = link_url
      modified = True

    # update image url
    image_url = product_info.get('image_url')
    if image_url is not None and image_url != product.image_url:
      product.image_url = image_url
      product.image_data = None
      modified = True

    if modified:
      product.put()
    return modified

  def _AddProduct(self, manufacturer, product_info):
    """Add a product to the data store.

    Args:
      manufacturer:
      product_info: The dict with the product information

    Returns:
      The new Product entity.
    """
    product = self._product_type(
        manufacturer=manufacturer,
        name=product_info['name'])

    # add link and image_url if they exist
    link_url = product_info.get('link')
    if link_url:
      product.link = link_url
    image_url = product_info.get('image_url')
    if image_url:
      product.image_url = image_url

    product.put()
    return product

  def _UpdateTags(self, product, new_tags):
    """Update the tags for a product

    Args:
      product: The Product entity to update
      new_tags: a list of new tags

    Returns:
      True if the product was modified, false otherwise.
    """
    new_tags = set(new_tags)
    modified = False

    for relationship in product.tag_set:
      label = relationship.tag.label
      if label in new_tags:
        new_tags.remove(label)
      else:
        logging.info('Deleting %s from %s' % (label, product.name))
        relationship.delete()
        modified = True

    for tag_label in new_tags:
      tag_entity = self._LookupOrAddTag(tag_label)
      relationship = ProductTagRelationship(
          tag=tag_entity,
          product=product)
      relationship.put()
      modified = True

    return modified

  def Update(self):
    """Update the datastore with the new data.

    Returns:
      A tuple in the form (added, updated), with the number of entities added
      or updated.
    """
    added = []
    updated = []

    logging.info(self._product_data)
    for manufacturer_id, products in self._product_data.iteritems():
      manufacturer = self._LookupManufacturer(manufacturer_id)
      if not manufacturer:
        logging.error('No manufacturer found for 0x%hx' % manufacturer_id)
        continue

      for product_info in products:
        was_added = False
        was_modified = False
        name = product_info['name']
        product = self._LookupProduct(manufacturer.key(), name)
        if product:
          # update
          if self._UpdateProduct(product, product_info):
            logging.info(' product changed')
            was_modified = True
        else:
          # add a new one
          product = self._AddProduct(manufacturer, product_info)
          was_added = True

        # add / update any tags
        # we act conservatively here and don't delete unless we get an empty
        # list
        if 'tags' in product_info:
          if self._UpdateTags(product, product_info['tags']):
            was_modified = True

        if was_added:
          added.append(name)
        elif was_modified:
          updated.append(name)

    return added, updated
