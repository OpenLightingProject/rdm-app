# -*- coding: utf-8 -*-
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
# model_data.py
# Copyright (C) 2011 Simon Newton
# Data for the device models.

DEVICE_MODEL_DATA = {
 8482L: [{'device_model': 38,
          'model_description': 'LED BAR',
          'product_category': 1289,
          'software_versions': {1: {
#                                    'label': 'V1.02 \x00LED BAR\x00BRITEQ',
                                    'languages': [],
                                    'manufacturer_pids': [],
                                    'personalities': [{'description': '   \x00\x08',
                                                       'index': 1,
                                                       'slot_count': 3},
                                                      {'description': '   \x00\x08',
                                                       'index': 2,
                                                       'slot_count': 4},
                                                      {'description': '   \x00\x08',
                                                       'index': 3,
                                                       'slot_count': 5},
                                                      {'description': '   \x00\x08',
                                                       'index': 4,
                                                       'slot_count': 6},
                                                      {'description': '   \x00\x08',
                                                       'index': 5,
                                                       'slot_count': 12},
                                                      {'description': '   \x00\x08',
                                                       'index': 6,
                                                       'slot_count': 15},
                                                      {'description': '   \x000',
                                                       'index': 7,
                                                       'slot_count': 16}],
                                    'sensors': [{'description': 'Temperature',
                                                 'index': 0,
                                                 'supports_recording': 0,
                                                 'type': 0}],
                                    'supported_parameters': [512,
                                                             513,
                                                             128,
                                                             129,
                                                             130,
                                                             224,
                                                             225,
                                                             1024]}},
          'sub_device_count': 0}],
 25711L: [{'device_model': 30,
#           'model_description': 'LinearDC720W',
           'product_category': 1289,
           'software_versions': {254: {'label': '254',
                                       'languages': [],
                                       'manufacturer_pids': [],
                                       'personalities': [],
                                       'sensors': [{'description': 'TNTC',
                                                    'index': 0,
                                                    'supports_recording': 0,
                                                    'type': 0}],
                                       'supported_parameters': [128,
                                                                129,
                                                                512,
                                                                513]}},
           'sub_device_count': 0}],
}
