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
# page.py
# Copyright (C) 2011 Simon Newton
# Handlers for simple static pages

import common
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class ContactPageHandler(common.BasePageHandler):
  """Display the contact page."""
  TEMPLATE = 'templates/contact.tmpl'


class DisclaimerPageHandler(common.BasePageHandler):
  """Display the disclaimer page."""
  TEMPLATE = 'templates/disclaimer.tmpl'


application = webapp.WSGIApplication(
  [
    ('/contact', ContactPageHandler),
    ('/disclaimer', DisclaimerPageHandler),
  ],
  debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
