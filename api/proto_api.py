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
# proto_api.py
# Copyright (C) 2012 Simon Newton
# Version 1 and 2 of the Proto API

from model import Manufacturer
from google.appengine.ext import webapp


class ManufacturerList(webapp.RequestHandler):
  API_VERSION = 1

  """Return the list of all manufacturers."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.headers['Cache-Control'] = 'public; max-age=300;'

    output = []
    query = Manufacturer.all()
    if self.API_VERSION > 1:
      query.order('name')
    for manufacturer in query:
      output.append("manufacturer {")
      output.append("  name: \"%s\"" % manufacturer.name)
      output.append("  id: %d" % manufacturer.esta_id)
      if self.API_VERSION > 1 and manufacturer.link:
        output.append("  link: \"%s\"" % manufacturer.link)
      output.append("}")

    self.response.out.write('\n'.join(output))


class ManufacturerList2(ManufacturerList):
  API_VERSION = 2


app = webapp.WSGIApplication(
  [
    ('/api/proto/1/manufacturers', ManufacturerList),
    ('/api/proto/2/manufacturers', ManufacturerList2),
  ],
  debug=True)
