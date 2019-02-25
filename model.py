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
# model.py
# Copyright (C) 2011 Simon Newton
# The datastore model

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

SUBDEVICE_RANGE_DICT = {
  0: 'Root device only (0x0000)',
  1: 'Root or all sub-devices (0x0000 - 0x0200, 0xffff)',
  2: 'Root or sub devices (0x0000 - 0x0200)',
  3: 'Only sub-devices (0x0001 - 0x0200)',
}


class LastUpdateTime(db.Model):
  """Tracks the last update time for each section of the index."""
  name = db.StringProperty(required=True)
  update_time = db.DateTimeProperty()


class Manufacturer(db.Model):
  """Represents a Manufacturer."""
  esta_id = db.IntegerProperty(required=True)
  name = db.StringProperty(required=True)
  # link to the manufacturer website
  link = db.LinkProperty()
  # url of the source image
  image_url = db.LinkProperty()
  # the blob for the image data
  image_data = blobstore.BlobReferenceProperty()
  # the url we're serving the image on
  image_serving_url = db.LinkProperty()


class ProductCategory(db.Model):
  id = db.IntegerProperty(required=True)
  name = db.StringProperty(required=True)


class Responder(db.Model):
  """Represents a particular RDM product / device."""
  manufacturer = db.ReferenceProperty(Manufacturer, required=True)
  # The Device Model ID field from DEVICE_INFO
  device_model_id = db.IntegerProperty()
  # Description can't be required, as DEVICE_MODEL_DESCRIPTION is not a
  # mandatory PID.
  model_description = db.StringProperty(default=None)
  # The product category
  product_category = db.ReferenceProperty(ProductCategory,
                                          collection_name='responder_set')
  # link to the responder product page
  link = db.LinkProperty()
  # url of the source image
  image_url = db.LinkProperty()
  # the blob for the image data
  image_data = blobstore.BlobReferenceProperty()
  # the url we're serving the image on
  image_serving_url = db.LinkProperty()
  # the scoring rank
  score = db.IntegerProperty()
  # the score penalty, used to demote responders
  score_penalty = db.IntegerProperty()
  # test score, this is updated with the latest score
  rdm_responder_rating = db.RatingProperty()


class ResponderTag(db.Model):
  """Tags that can be applied to responders."""
  # the tag label
  label = db.StringProperty(required=True)
  exclude_from_search = db.BooleanProperty(default=False)


class ResponderTagRelationship(db.Model):
  """The glue that maps tags to responders."""
  tag = db.ReferenceProperty(ResponderTag,
                             required=True,
                             collection_name='responder_set')
  responder = db.ReferenceProperty(Responder,
                                   required=True,
                                   collection_name='tag_set')


class SoftwareVersion(db.Model):
  """Represents a particular software version on a responder."""
  # Version id
  version_id = db.IntegerProperty(required=True)
  # Version label should be required, as SOFTWARE_VERSION_LABEL is a mandatory
  # PID but we've had real world devices without it, or there could be issues
  # with their implementation such as it being empty (which App Engine treats
  # as not present)
  label = db.StringProperty(default=None)
  # supported params
  supported_parameters = db.ListProperty(int)
  # reference to the responder this version is associated with
  responder = db.ReferenceProperty(Responder,
                                   required=True,
                                   collection_name='software_version_set')


class ResponderPersonality(db.Model):
  """Represents a personality of a responder."""
  # Description can't be required, as DMX_PERSONALITY_DESCRIPTION is not a
  # mandatory PID.
  description = db.StringProperty(default=None)
  index = db.IntegerProperty(required=True)
  # Sometimes we know a personality exists, but not the description or the slot
  # count.
  slot_count = db.IntegerProperty()
  # reference to the responder this version is associated with
  sw_version = db.ReferenceProperty(SoftwareVersion,
                                    required=True,
                                    collection_name='personality_set')


class ResponderSensor(db.Model):
  """Represents a Sensor on a responder."""
  # Sensor description should be required, as the description field is part of
  # the SENSOR_DEFINITION PID but there may be real world devices with issues
  # with their implementation such as it being empty (which App Engine treats
  # as not present)
  description = db.StringProperty(default=None)
  index = db.IntegerProperty(required=True)
  type = db.IntegerProperty(required=True)
  supports_min_max_recording = db.BooleanProperty()
  supports_recording = db.BooleanProperty()
  sw_version = db.ReferenceProperty(SoftwareVersion,
                                    required=True,
                                    collection_name='sensor_set')


class Product(polymodel.PolyModel):
  """A RDM Product."""
  manufacturer = db.ReferenceProperty(Manufacturer, required=True)
  name = db.StringProperty(required=True)
  # link to the product page
  link = db.LinkProperty()
  # image url
  image_url = db.LinkProperty()
  # the blob for the image data
  image_data = blobstore.BlobReferenceProperty()
  # the url we're serving the image on
  image_serving_url = db.LinkProperty()


class ProductTag(db.Model):
  """Tags that can be applied to a product."""
  # the tag label
  label = db.StringProperty(required=True)
  exclude_from_search = db.BooleanProperty(default=False)
  # the sub-class of Product that this tag is associated with
  # we need to store this since we can't do joins in the data store
  product_type = db.StringProperty(required=True)


class ProductTagRelationship(db.Model):
  """The glue that maps tags to products."""
  tag = db.ReferenceProperty(ProductTag,
                             required=True,
                             collection_name='product_set')
  product = db.ReferenceProperty(Product,
                                 required=True,
                                 collection_name='tag_set')


class Controller(Product):
  """Represents an RDM Controller."""
  pass


class Node(Product):
  """Extra node properties can go here."""
  pass


class Software(Product):
  """Extra software properties can go here."""
  pass


class Splitter(Product):
  """Extra splitter properties can go here."""
  pass


# About Enums & Ranges:
# If neither enums nor ranges are specified, the valid values is the range of
#   the data type.
# If enums are specified, and ranges aren't, the valid values are the enums
# If ranges are specified, the valid values are those which fall into the range
#   (inclusive).
# If both are specified, the enum values must fall into the specified ranges.

class Command(db.Model):
  """Represents a GET or SET Command Description."""
  sub_device_range = db.IntegerProperty(
      required=True,
      choices=set(xrange(4)))
  request = db.TextProperty()
  response = db.TextProperty()


class Pid(db.Model):
  """Represents a PID."""
  manufacturer = db.ReferenceProperty(Manufacturer, required=True)
  pid_id = db.IntegerProperty(required=True)
  name = db.StringProperty(required=True)
  link = db.LinkProperty()
  notes = db.TextProperty()
  draft = db.BooleanProperty(default=False)
  discovery_command = db.ReferenceProperty(
      Command,
      collection_name='pid_discovery_command_set')
  get_command = db.ReferenceProperty(Command,
                                     collection_name='pid_get_command_set')
  set_command = db.ReferenceProperty(Command,
                                     collection_name='pid_set_command_set')
  # A list of responder keys that support this PID.
  responders = db.ListProperty(db.Key)


class UploadedResponderInfo(db.Model):
  # This doesn't link to a Manufacturer, since we may not know about all
  # manufacturers.
  manufacturer_id = db.IntegerProperty()
  device_model_id = db.IntegerProperty()
  info = db.TextProperty()
  link_url = db.LinkProperty()
  image_url = db.LinkProperty()
  email_or_name = db.TextProperty()
  upload_time = db.DateTimeProperty()
  processed = db.BooleanProperty(default=False)
