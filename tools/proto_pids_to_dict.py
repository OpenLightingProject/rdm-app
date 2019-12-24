#!/usr/bin/python
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# proto_pids_to_dict.py
# Copyright (C) 2014 Simon Newton

'''Convert the proto PIDs format to a Python dict format.'''

__author__ = 'nomis52@gmail.com (Simon Newton)'

import sys
import pprint

from google.protobuf import text_format
from ola import Pids_pb2

TYPES = {
  Pids_pb2.BOOL: 'bool',
  Pids_pb2.UINT8: 'uint8',
  Pids_pb2.UINT16: 'uint16',
  Pids_pb2.UINT32: 'uint32',
  Pids_pb2.STRING: 'string',
  Pids_pb2.GROUP: 'group',
  Pids_pb2.INT8: 'int8',
  Pids_pb2.INT16: 'int16',
  Pids_pb2.INT32: 'int32',
  Pids_pb2.IPV4: 'ipv4',
  Pids_pb2.UID: 'uid',
  Pids_pb2.MAC: 'mac',
  Pids_pb2.IPV6: 'ipv6',
}


def LoadProto(pid_file_name):
  pid_file = open(pid_file_name, 'r')
  lines = pid_file.readlines()
  pid_file.close()

  pid_store = Pids_pb2.PidStore()

  text_format.Merge('\n'.join(lines), pid_store)
  return pid_store


def FieldToDict(field):
  output = {
    'name': field.name.encode('ascii', 'ignore'),
    'type': TYPES.get(field.type, '')
  }

  for label in ['min_size', 'max_size', 'multiplier']:
    if field.HasField(label):
      output[label] = getattr(field, label)

  if field.type == Pids_pb2.GROUP:
    output['items'] = []
    for sub_field in field.field:
       output['items'].append(FieldToDict(sub_field))

  if field.range:
    output['range'] = []
    ranges = output['range']
    for range_item in field.range:
      ranges.append((range_item.min, range_item.max))

  if field.label:
    output['labels'] = []
    labels = output['labels']
    for label in field.label:
      labels.append((label.value, label.label.encode('ascii', 'ignore')))

  return output


def AddCommand(pid_dict, pid, prefix):
  request = '%s_request' % prefix
  response = '%s_response' % prefix
  subdevice_range = '%s_sub_device_range' % prefix

  if pid.HasField(request) != pid.HasField(response):
    print 'Warning: Missing %s_request or %s_response for %s' % (
      prefix, prefix, pid.name)
  elif pid.HasField(request):
    # The proto uses 1-offset but the RDM Web App uses 0-offset
    pid_dict[subdevice_range] = getattr(pid, subdevice_range) - 1

    for msg_type in [request, response]:
      msg = getattr(pid, msg_type)

      items = []
      for field in msg.field:
        items.append(FieldToDict(field))

      pid_dict[msg_type] = {
        'items': items
      }


def main():
  if len(sys.argv) != 2:
    print 'Usage: %s <pid_file>' % sys.argv[0]
    sys.exit()

  pid_store = LoadProto(sys.argv[1])

  manufacturer_pids = []
  for manufacturer in pid_store.manufacturer:
    manufacturer_dict = {
        'id': manufacturer.manufacturer_id,
        'name': manufacturer.manufacturer_name.encode('ascii', 'ignore'),
        'pids': []
    }
    output_pids = manufacturer_dict['pids']

    for pid in manufacturer.pid:
      pid_dict = {
        'name': pid.name.encode('ascii', 'ignore'),
        'value': pid.value,
      }

      AddCommand(pid_dict, pid, 'get')
      AddCommand(pid_dict, pid, 'set')
      output_pids.append(pid_dict)

    manufacturer_pids.append(manufacturer_dict)

  pp = pprint.PrettyPrinter(indent=2, width=100)
  pp.pprint(manufacturer_pids)


if __name__ == '__main__':
  main()
