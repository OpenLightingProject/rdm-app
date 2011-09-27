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
  0x7a70: [{'device_model': 1,
            'model_description': 'Dummy Model',
           },
           {'device_model': 2,
            'model_description': 'Arduino RGB Mixer'}],
  161: [{'device_model': 258,
         'model_description': 'SLAMMO',
         'personality_count': 4,
         'product_category': 1289,
         'software_version': 16909060}],
  19541: [{'device_model': 4661,
           'model_description': 'DALI/DSI Interface',
           'personality_count': 3,
           'product_category': 2050,
           'software_version': 4},
          {'device_model': 257,
           'model_description': 'CRMX Nova TX2 RDM',
           'personality_count': 5,
           'product_category': 2049,
           'software_version': 131328}],
  21324: [{'device_model': 13828,
           'model_description': '3604PWM CV DRIVER Interface',
           'personality_count': 4,
           'product_category': 1289,
           'software_version': 33816835}],
}
