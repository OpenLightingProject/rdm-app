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
# proto_v1.py
# Copyright (C) 2012 Simon Newton
# Version 1 of the Proto API

from model import *
from google.appengine.ext import webapp


class ManufacturerList(webapp.RequestHandler):
  """Return the list of all manufacturers."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'

    output = []
    for manufacturer in Manufacturer.all():
      output.append("manufacturer {")
      output.append("  name: \"%s\"" % manufacturer.name)
      output.append("  id: %d" % manufacturer.esta_id)
      output.append("}")

    self.response.out.write('\n'.join(output))


app = webapp.WSGIApplication(
  [
    ('/api/proto/1/manufacturers', ManufacturerList),
  ],
  debug=True)
