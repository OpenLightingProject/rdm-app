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
# pid_test.py
# Copyright (C) 2015 Simon Newton

import unittest
import json
import jsonspec.validators

# This is from an early version of E1.37-5.
PID_VALIDATOR = {
  '$schema': 'http://json-schema.org/draft-04/schema#',
  'definitions': {
    'command': {
      'type': 'object',
      'properties': {
        'items': {
          'type': 'array',
          'additionalItems': {
            '$ref': '#/definitions/item'
          }
        }
      },
      'required': ['items']
    },
    'item': {
      'type': 'object',
      'properties': {
        'name': {
          'type': 'string',
          'minLength': 1
        },
        'max_size': {
          'type': 'integer',
          'minimum': 0,
          'exclusiveMinimum': True
        },
        'min_size': {
          'type': 'integer',
          'minimum': 0
        },
        'prefix': {
          'type': 'integer',
          'maximum': 255,
          'minimum': 0
        },
        'type': {
          'enum': ['bool', 'group', 'int16', 'int32', 'int64', 'int8',
                   'ipv4','string', 'uid', 'uint16', 'uint32',
                   'uint64', 'uint8'],
          'type': 'string'
        },
        'unit': {
          'type': 'integer',
          'maximum': 255,
          'minimum': 0
        },
        'labels': {
          'type': 'array',
          'additionalItems': {
            '$ref': '#/definitions/label'
          }
        },
        'ranges': {
          'type': 'array',
          'additionalItems': {
            '$ref': '#/definitions/range'
          }
        },
        'items': {
          'type': 'array',
          'additionalItems': {
            '$ref': '#/definitions/field'
          }
        }
      },
      'required': ['name', 'type']
    },
    'label': {
      'type': 'object',
      'properties': {
        'label': {
          'minLength': 1,
          'type': 'string'
        },


        'value': {
          'type': 'integer',
          'maximum': 4294967295,
          'minimum': 0
        }
      },
      'required': ['label', 'value']
    },
    'range': {
      'type': 'object',
      'properties': {
        'lower': {
          'type': 'integer'
        },
        'upper': {
          'type': 'integer'
        }
      },
      'required': ['lower', 'upper']
    }
  },
  'dependencies': {
    'discovery_request': ['discovery_response', 'discovery_sub_device_range'],
    'discovery_response': ['discovery_request', 'discovery_sub_device_range'],
    'discovery_sub_device_range': ['discovery_request', 'discovery_response'],
    'get_request': ['get_response', 'get_sub_device_range'],
    'get_response': ['get_request', 'get_sub_device_range'],
    'get_sub_device_range': ['get_request', 'get_response'],
    'set_request': ['set_response', 'set_sub_device_range'],
    'set_response': ['set_request', 'set_sub_device_range'],
    'set_sub_device_range': ['set_request', 'set_response']
  },
  'properties': {
    'discovery_request': {
      '$ref': '#/definitions/command'
    },
    'discovery_response': {
      '$ref': '#/definitions/command'
    },
    'discovery_sub_device_range': {
      'maximum': 3,
      'minimum': 0,
      'type': 'integer'
    },
    'get_request': {
      '$ref': '#/definitions/command'
    },
    'get_response': {
      '$ref': '#/definitions/command'
    },
    'get_sub_device_range': {
      'maximum': 3,
      'minimum': 0,
      'type': 'integer'
    },
    'link': {
      'type': 'string',
      'format': 'uri',
    },
    'name': {
      'minLength': 1,
      'type': 'string'
    },
    'set_request': {
      '$ref': '#/definitions/command'
    },
    'set_response': {
      '$ref': '#/definitions/command'
    },
    'set_sub_device_range': {
      'maximum': 3,
      'minimum': 0,
      'type': 'integer'
    },
    'value': {
      'maximum': 65535,
      'minimum': 0,
      'type': 'integer'
    },
  },
  'required': ['name', 'value'],
  'type': 'object'
}

MANUFACTURER_VALIDATOR = {
  '$schema': 'http://json-schema.org/draft-04/schema#',
  'properties': {
    'id': {
      'maximum': 65535,
      'minimum': 0,
      'type': 'integer'
    },
    'name': {
      'minLength': 1,
      'type': 'string'
    },
    'pids': {
      'type': 'array',
      'minimum': 1,
    }
  },
  'required': ['id', 'pids'],
  'type': 'object'
}

class TestPiddata(unittest.TestCase):
  """ Test the PID data file is valid."""
  def setUp(self):
    globals = {}
    locals = {}
    execfile("data/pid_data.py", globals, locals)
    self.manufacturer_pids = locals['MANUFACTURER_PIDS']
    self.plasa_pids = locals['ESTA_PIDS']
    self.pid_validator = jsonspec.validators.load(PID_VALIDATOR)
    self.manufacturer_validator = jsonspec.validators.load(
        MANUFACTURER_VALIDATOR)

  def test_PlasaPids(self):
    self.assertEqual(list, type(self.plasa_pids))
    for pid in self.plasa_pids:
      try:
        self.pid_validator.validate(pid)
      except jsonspec.validators.ValidationError as e:
        self.fail(e)

      self.assertFalse(0x8000 <= pid['value'] <= 0xFFDF)

  def test_ManufacturerPids(self):
    self.assertEqual(list, type(self.manufacturer_pids))

    seen_manufacturer_ids = set()
    for manufacturer_data in self.manufacturer_pids:
      try:
        self.manufacturer_validator.validate(manufacturer_data)
      except jsonspec.validators.ValidationError as e:
        self.fail(e)

      pids = manufacturer_data['pids']
      self.assertNotIn(manufacturer_data['id'], seen_manufacturer_ids)
      seen_manufacturer_ids.add(manufacturer_data['id'])


      seen_pids = set()
      for pid in pids:
        try:
          self.pid_validator.validate(pid)
        except jsonspec.validators.ValidationError as e:
          self.fail(e)

        self.assertTrue(0x8000 <= pid['value'] <= 0xFFDF)
        self.assertNotIn(pid['value'], seen_pids)
        seen_pids.add(pid['value'])


if __name__ == '__main__':
  unittest.main()
