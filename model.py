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

from google.appengine.ext import db

SUBDEVICE_RANGE_DICT = {
  0: 'Root device only (0x0)',
  1: 'Root or all sub-devices (0x0 - 0x200, 0xffff)',
  2: 'Root or sub devices (0x0 - 0x200)',
  3: 'Only sub-devices (0x1 - 0x200)',
}


class Manufacturer(db.Model):
  """Represents a Manufacturer."""
  esta_id = db.IntegerProperty(required=True)
  name = db.StringProperty(required=True)


class MessageItem(db.Model):
  """Represents a item within a message."""
  name = db.StringProperty(required=True)
  type = db.StringProperty(
      required=True,
      choices=set(['bool', 'uint8', 'uint16', 'uint32', 'string']))
  size = db.IntegerProperty()


class Message(db.Model):
  """Represents a request or response."""
  is_repeated = db.BooleanProperty(required=True)
  max_repeats = db.IntegerProperty()
  # this holds a list of MessageItem keys
  items = db.ListProperty(db.Key, required=True)


class Command(db.Model):
  """Represents a GET or SET Command Description."""
  sub_device_range = db.IntegerProperty(
      required=True,
      choices=set(xrange(4)))
  request = db.ReferenceProperty(Message, collection_name='request_set')
  response = db.ReferenceProperty(Message, collection_name='response_set')


class Pid(db.Model):
  """Represents a PID."""
  manufacturer = db.ReferenceProperty(Manufacturer, required=True)
  pid_id = db.IntegerProperty(required=True)
  name = db.StringProperty(required=True);
  link = db.LinkProperty();
  notes = db.TextProperty()
  get_command = db.ReferenceProperty(Command,
                                     collection_name='pid_get_command_set')
  set_command = db.ReferenceProperty(Command,
                                     collection_name='pid_set_command_set')
  update_time = db.DateTimeProperty(auto_now=True)
