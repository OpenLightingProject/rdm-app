#!/bin/bash
# Autogenerate data/manufacturer_data.py

# Ensure we fail with the worst pipe status
set -o pipefail

(
cat <<EOM
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
# manufacturer_data.py
# Copyright (C) 2011 Simon Newton
# The data for Manufacturers
#
# This file has been autogenerated by tools/make_manufacturer_data.sh, DO NOT EDIT.

EOM
echo -n "MANUFACTURER_DATA = "

# Fetch the manufacturer data, convert to Linux line endings
# Decode any HTML entities
# Tidy nbsp to space
# Tidy en and em dash to dash
# Convert UTF-8 characters to closest normal equivalent
# Convert extended characters to closest normal equivalent
# TODO(Peter): Check if rdm-app and OLA can handle extended characters (or fix
# if not) and start allowing them through
# Remove any consecutive duplicates within the file (e.g. stuff added twice by mistake)
# Remove duplicate entry for manufacturer 0x0000
# Remove duplicate entry for manufacturer 0x4C5A; keep the original owner of the ID
# Remove duplicate entry for manufacturer 0x0854; NEC is now a subsidiary of Sharp NEC
# Remove duplicate entry for manufacturer 0x5007; keep the original owner of the ID
# Remove any H's after the manufacturer IDs and generally sanitise the rows
# TODO(Peter): Comment out any invalid rows

# For further UTF-8 issues, copy the equivalent failing manufacturer from here:
# https://tsp.esta.org/tsp/working_groups/CP/mfctrIDs.php
# then URL encode that chunk
wget --quiet -O - http://tsp.esta.org/tsp/working_groups/CP/rdmids.php | \
tr --delete "\r" | \
perl -p -e 'use HTML::Entities; decode_entities($_);' | \
tr "\240" " " | \
sed -r -e 's/[\xe2\x80\x93\xe2\x80\x94]/-/g' | \
sed -r -e 's/[\xef\xbc\x88]/(/g' | \
sed -r -e 's/[\xef\xbc\x89]/)/g' | \
sed -r -e 's/\xc3\xa9/e/g' | \
sed -r -e 's/\xc3\xb6/o/g' | \
sed -r -e 's/\xc4\xb1/i/g' | \
sed -r -e 's/\xc5\x9f/s/g' | \
tr "\300-\305" "[A*]" | tr "\310-\313" "[E*]" | tr "\314-\317" "[I*]" | tr "\322-\326" "[O*]" | tr "\331-\334" "[U*]" | \
tr "\340-\345" "[a*]" | tr "\350-\353" "[e*]" | tr "\354-\357" "[i*]" | tr "\362-\366" "[o*]" | tr "\371-\374" "[u*]" | \
uniq | \
grep -v "(0x0000, \"PLASA\")," | grep -v "(0x4C5A, \"Sumolight GmbH\")," | grep -v "(0x0854, \"NEC Display Solutions, Ltd\.\")," | grep -v "(0x5007, \"Prizm Lighting (part of American Lighting Inc.)\")," | \
sed -r -e 's/^[[:space:]]*\([[:space:]]*0x([[:xdigit:]]{4,4})[Hh]?[[:space:]]*,[[:space:]]*"[[:space:]]*/(0x\1, "/' -e 's/[[:space:]]+"\),$/"),/' -e 's/^\(/  (/'
)
